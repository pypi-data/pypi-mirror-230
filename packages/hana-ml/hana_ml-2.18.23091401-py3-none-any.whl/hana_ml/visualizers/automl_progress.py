"""
This module contains related classes for monitoring the pipeline progress status.

The following class is available:

    * :class:`PipelineProgressStatusMonitor`
"""

# pylint: disable=missing-function-docstring
# pylint: disable=missing-class-docstring
# pylint: disable=too-few-public-methods
# pylint: disable=too-many-instance-attributes
# pylint: disable=protected-access, bare-except
# pylint: disable=no-else-continue
# pylint: disable=broad-except
# pylint: disable=superfluous-parens
# pylint: disable=simplifiable-if-statement
# pylint: disable=no-self-use
# pylint: disable=no-else-break
import os
import threading
import uuid
import logging
import time
import html
import pandas as pd
try:
    from IPython.display import display, update_display, Javascript, HTML
except ImportError as error:
    logging.getLogger(__name__).error("%s: %s", error.__class__.__name__, str(error))
    pass
try:
    from jinja2 import Environment, PackageLoader
except ImportError as error:
    logging.getLogger(__name__).error("%s: %s", error.__class__.__name__, str(error))
    pass
from hana_ml.dataframe import ConnectionContext
from hana_ml.visualizers.model_report import TemplateUtil
from hana_ml.ml_exceptions import Error


def get_tempdir_path():
    template_name = 'pipeline_progress.html'
    file_path = Environment(loader=PackageLoader('hana_ml.visualizers', 'templates')).get_template(template_name).filename
    temp_dir = file_path.replace(template_name, 'temp')
    if os.path.exists(temp_dir) is False:
        os.mkdir(temp_dir)
    return temp_dir


def create_interrupt_file(frame_id):
    file = open(get_tempdir_path() + os.sep + frame_id, 'w')
    file.close()


def create_connection_context(original_connection_context: ConnectionContext) -> ConnectionContext:
    if original_connection_context.userkey is None:
        conn_str = original_connection_context.connection.__str__().replace('<dbapi.Connection Connection object : ', '')[:-1]
        if conn_str.count(',') >= 4:
            for i in range(0, conn_str.count(',') - 4):
                try:
                    url, remain_str = conn_str.split(',', 1)
                    port, remain_str = remain_str.split(',', 1)
                    user, remain_str = remain_str.split(',', 1)
                    password = remain_str.rsplit(',', i + 1)[0]
                    conn = ConnectionContext(url, port, user, password)
                    return conn
                except Exception as err:
                    if i < conn_str.count(',') - 5:
                        continue
                    else:
                        raise Error(err)
        conn_config = conn_str.split(',')
        url = conn_config[0]
        port = conn_config[1]
        user = conn_config[2]
        password = conn_config[3]
    try:
        if original_connection_context.userkey:
            conn = ConnectionContext(userkey=original_connection_context.userkey)
        else:
            conn = ConnectionContext(url, port, user, password)
    except:
        if original_connection_context.userkey:
            conn = ConnectionContext(userkey=original_connection_context.userkey, encrypt='true', sslValidateCertificate='false')
        else:
            conn = ConnectionContext(url, port, user, password, encrypt='true', sslValidateCertificate='false')
    return conn


class AutomaticObjProxy(object):
    def __init__(self, automatic_obj, connection_context: ConnectionContext):
        self.target_obj = automatic_obj
        self.connection_context = connection_context

        self.highlight_metric = None
        self.progress_indicator_id = None
        self.connection_id = None

    def reset_data(self):
        if self.target_obj.progress_indicator_id is None:
            self.target_obj.progress_indicator_id = "AutoML-{}".format(self.target_obj.gen_id)
        self.progress_indicator_id = self.target_obj.progress_indicator_id

        self.highlight_metric = self.target_obj._get_highlight_metric()
        self.target_obj.persist_progress_log()
        self.target_obj._status = 0

    def clear_data(self):
        self.target_obj.cleanup_progress_log(create_connection_context(self.connection_context))

    def cancel_task(self):
        # sql = "ALTER SYSTEM DISCONNECT SESSION '{}'"
        # sql = "ALTER SYSTEM CANCEL WORK IN SESSION '{}'"
        if self.connection_id is None:
            self.connection_id = self.target_obj.fit_data.connection_context.get_connection_id()
        cancel_task_connection_context = create_connection_context(self.connection_context)
        cancel_task_connection_context.execute_sql("ALTER SYSTEM CANCEL WORK IN SESSION '{}'".format(self.connection_id))
        cancel_task_connection_context.close()
        # avoid executing the same ID multiple times when send cancel command
        self.target_obj.progress_indicator_id = "cancelled_{}".format(self.progress_indicator_id)

    def get_status(self):
        return self.target_obj._status


class AutomaticEmptyObjProxy(object):
    def __init__(self, progress_indicator_id, connection_context: ConnectionContext):
        self.connection_context = connection_context

        self.highlight_metric = None
        self.progress_indicator_id = progress_indicator_id
        self.connection_id = None

    def reset_data(self):
        self.highlight_metric = ''

    def clear_data(self):
        pass

    def cancel_task(self):
        if self.connection_id is not None:
            cancel_task_connection_context = create_connection_context(self.connection_context)
            cancel_task_connection_context.execute_sql("ALTER SYSTEM CANCEL WORK IN SESSION '{}'".format(self.connection_id))
            cancel_task_connection_context.close()

    def get_status(self):
        return 0


class TaskManager(threading.Thread):
    def __init__(self, automatic_obj_proxy: AutomaticObjProxy, connection_context: ConnectionContext, update_ui_interval, fetch_table_interval, runtime_platform):
        threading.Thread.__init__(self)

        self.automatic_obj_proxy = automatic_obj_proxy

        self.completed = False   # fetch complete or obj end execute
        self.interrupted = False # raise exception
        self.cancelling = False   # fronted send cancel
        self.cancelled = False

        self.automatic_obj_proxy.reset_data()
        self.fetch_table_task = FetchProgressStatusFromSystemTableTask(self, fetch_table_interval, connection_context)
        self.update_to_ui_task = UpdateProgressStatusToUITask(self, update_ui_interval, runtime_platform)

    def is_interrupted(self):
        return self.interrupted

    def is_completed(self):
        return self.completed

    def is_cancelling(self):
        return self.cancelling

    def is_cancelled(self):
        return self.cancelled

    def set_interrupted(self):
        self.interrupted = True

    def set_completed(self):
        self.completed = True

    def set_cancelling(self):
        self.cancelling = True

    def set_cancelled(self):
        self.cancelled = True

    def check_status(self):
        if self.automatic_obj_proxy.get_status() < 0:
            self.set_interrupted()
        elif self.automatic_obj_proxy.get_status() > 0 or self.fetch_table_task.is_fetch_completed():
            self.set_completed()
        elif os.path.exists(self.update_to_ui_task.frame_file_path):
            self.set_cancelling()

    def remove_temp_file(self):
        if os.path.exists(self.update_to_ui_task.frame_file_path):
            os.remove(self.update_to_ui_task.frame_file_path)

    def run(self):
        self.fetch_table_task.start()
        self.update_to_ui_task.start()

        while True:
            self.check_status()
            if self.is_interrupted() or self.is_completed():
                # if self.update_to_ui_task.is_jupyter_platform is False:
                #     print('task.end: {}'.format(self.update_to_ui_task.frame_id))
                break
            if self.is_cancelling():
                self.automatic_obj_proxy.cancel_task()
                self.set_cancelled()
                break
        self.automatic_obj_proxy.clear_data()
        self.remove_temp_file()


class FetchProgressStatusFromSystemTableTask(threading.Thread):
    def __init__(self, manager: TaskManager, fetch_table_interval, connection_context: ConnectionContext):
        threading.Thread.__init__(self)

        self.manager = manager
        self.fetch_table_interval = fetch_table_interval
        self.connection_context = connection_context

        self.fetch_completed = False
        self.offset = 0
        self.limit = 1000
        self.connection_cursor = connection_context.connection.cursor()
        self.connection_cursor.setfetchsize(32000)

        self.initialized_progress_status = None
        self.fetch_sql = """
            SELECT {}
            from _SYS_AFL.FUNCTION_PROGRESS_IN_AFLPAL
            WHERE EXECUTION_ID='{}' limit {} offset {}
        """
        self.initialized_columns = ['FUNCTION_NAME', 'CONNECTION_ID', 'PROGRESS_CURRENT', 'PROGRESS_MESSAGE', 'PROGRESS_TIMESTAMP']
        self.simplified_columns = ['PROGRESS_CURRENT', 'PROGRESS_MESSAGE', 'PROGRESS_TIMESTAMP']

        self.progresscurrent_2_message = {}
        self.progresscurrent_2_status = {}
        self.can_read_max_progresscurrent = -1
        self.current_read_progresscurrent = -1
        self.read_completed = False

    def parse_fetched_data(self, fetched_data, fetched_columns):
        fetched_data_df = pd.DataFrame(fetched_data, columns=fetched_columns)

        if self.initialized_progress_status is None:
            head_row = fetched_data_df.head(1)
            self.initialized_progress_status = {
                'running': self.manager.update_to_ui_task.true_flag,
                'FUNCTION_NAME': str(list(head_row['FUNCTION_NAME'])[0])
            }
            self.manager.automatic_obj_proxy.connection_id = str(list(head_row['CONNECTION_ID'])[0])

        progress_current_list = list(fetched_data_df['PROGRESS_CURRENT'])
        progress_msg_list = list(fetched_data_df['PROGRESS_MESSAGE'])
        progress_timestamp_list = list(fetched_data_df['PROGRESS_TIMESTAMP'])
        for row_index in range(0, fetched_data_df.shape[0]): # row_count
            progress_current = progress_current_list[row_index]
            if progress_current >= 0: # fetch completed -1
                # when progress_current is 2, progress_current=1 can read
                self.can_read_max_progresscurrent = progress_current - 1
                progress_msg = progress_msg_list[row_index]
                progress_timestamp = progress_timestamp_list[row_index]
                if self.progresscurrent_2_message.get(progress_current) is None:
                    self.progresscurrent_2_message[progress_current] = []
                    self.progresscurrent_2_status[progress_current] = {
                        'PROGRESS_CURRENT': progress_current,
                        'PROGRESS_TIMESTAMP': str(progress_timestamp)
                    }
                if progress_msg is None or progress_msg.strip() == '':
                    pass
                else:
                    if progress_msg.find('early_stop') >= 0:
                        self.fetch_completed = True
                    self.progresscurrent_2_message[progress_current].append(progress_msg)
            elif progress_current == -1:
                self.fetch_completed = True

    def do_fetch(self, fetched_columns):
        sql = self.fetch_sql.format(', '.join(fetched_columns), self.manager.automatic_obj_proxy.progress_indicator_id, self.limit, self.offset)
        self.connection_cursor.execute(sql)
        fetched_data = self.connection_cursor.fetchall()
        fetched_count = len(fetched_data)
        if fetched_count > 0:
            self.parse_fetched_data(fetched_data, fetched_columns)
            self.offset = self.offset + fetched_count
        else:
            if self.manager.is_completed():
                self.can_read_max_progresscurrent = self.can_read_max_progresscurrent + 1
                self.set_fetch_completed()

    def fetch(self):
        if self.initialized_progress_status is None:
            self.do_fetch(self.initialized_columns)
        else:
            self.do_fetch(self.simplified_columns)

    def is_read_completed(self):
        if self.is_fetch_completed() and (self.current_read_progresscurrent + 1 > self.can_read_max_progresscurrent):
            return True
        else:
            return False

    def get_next_progress_status(self):
        next_progress_status = None
        if self.can_read_max_progresscurrent >= 0:
            if self.current_read_progresscurrent + 1 <= self.can_read_max_progresscurrent:
                next_progress_current = self.current_read_progresscurrent + 1
                if self.progresscurrent_2_message.get(next_progress_current) is not None:
                    progress_message = ''.join(self.progresscurrent_2_message.get(next_progress_current))
                    if progress_message.strip() == '':
                        progress_message = 'None'
                    next_progress_status = self.progresscurrent_2_status.get(next_progress_current)
                    next_progress_status['PROGRESS_MESSAGE'] = progress_message
                    self.current_read_progresscurrent = next_progress_current
                    next_progress_status.update(self.initialized_progress_status) # decorate progress status
        return next_progress_status

    def is_fetch_completed(self):
        return self.fetch_completed

    def set_fetch_completed(self):
        self.fetch_completed = True

    def run(self):
        while True:
            if self.manager.is_interrupted() or self.manager.is_cancelling() or self.is_fetch_completed():
                self.connection_context.close()
                break
            self.fetch()
            time.sleep(self.fetch_table_interval)


class UpdateProgressStatusToUITask(object):
    __TEMPLATE = TemplateUtil.get_template('pipeline_progress.html')

    def __init__(self, manager: TaskManager, update_ui_interval, runtime_platform):
        self.manager = manager
        self.update_ui_interval = update_ui_interval

        self.self_timer = None

        self.is_jupyter_platform = False
        self.is_sap_bas_platform = False
        self.is_vscode_platform = False
        supported_platform = ['jupyter', 'sap_bas', 'vscode']
        if runtime_platform in supported_platform:
            if runtime_platform == supported_platform[0]:
                self.is_jupyter_platform = True
            elif runtime_platform == supported_platform[1]:
                self.is_sap_bas_platform = True
            elif runtime_platform == supported_platform[2]:
                self.is_vscode_platform = True
        else:
            raise ValueError("The value of runtime platform parameter can only be taken as 'jupyter', sap_bas', or 'vscode'")

        self.frame_id = '{}'.format(uuid.uuid4()).replace('-', '_').upper()
        tempdir_path = get_tempdir_path()
        self.frame_file_path = tempdir_path + os.sep + self.frame_id

        # if self.is_jupyter_platform is False:
        #     msg1 = 'If you want to cancel the current task, please copy the following first line to the first line of the current input cell.'
        #     msg2 = 'task.start: {}: {}'.format(tempdir_path + os.sep, self.frame_id)
        #     print('{}\n# task.cancel: {}\n{}'.format(msg1, self.frame_id, msg2))

        self.true_flag = '__js_true'
        self.false_flag = '__js_false'

    def build_frame_html(self):
        html_str = UpdateProgressStatusToUITask.__TEMPLATE.render(
            executionId=self.manager.automatic_obj_proxy.progress_indicator_id,
            frameId=self.frame_id,
            highlighted_metric_name=self.manager.automatic_obj_proxy.highlight_metric)
        self.frame_html = """
            <iframe
                id="{iframe_id}"
                width="{width}"
                height="{height}"
                srcdoc="{src}"
                style="border:1px solid #ccc"
                allowfullscreen="false"
                webkitallowfullscreen="false"
                mozallowfullscreen="false"
                oallowfullscreen="false"
                msallowfullscreen="false"
            >
            </iframe>
        """.format(
            iframe_id=self.frame_id,
            width='100%',
            height='1000px',
            src=html.escape(html_str)
        )

    def display(self, js_str):
        if self.is_sap_bas_platform:
            display(Javascript("{}".format(js_str)))
        else:
            display(Javascript("{}".format(js_str)), display_id=self.frame_id)

    def update_display(self, js_str):
        if self.is_sap_bas_platform:
            display(Javascript("{};".format(js_str)))
        elif self.is_jupyter_platform:
            update_display(Javascript("{};".format(js_str)), display_id=self.frame_id)
        elif self.is_vscode_platform:
            vscode_script = "const scripts = document.getElementsByTagName('script');for (let i = 0; i < scripts.length; i++) {const hanamlPipelinePNode = scripts[i].parentNode;if(hanamlPipelinePNode.tagName == 'DIV' && scripts[i].innerText.indexOf('hanamlPipelinePNode') >= 0){hanamlPipelinePNode.remove();}}"
            update_display(Javascript("{};{};".format(js_str, vscode_script)), display_id=self.frame_id)

    def send_msgs(self, msgs):
        msgs_str = str(msgs).replace("'{}'".format(self.true_flag), 'true').replace("'{}'".format(self.false_flag), 'false')
        js_str = "targetWindow['{}']={}".format('FRAME_P_S', msgs_str)
        js_str = "for (let i = 0; i < window.length; i++) {const targetWindow = window[i];if(targetWindow['frameId']){if(targetWindow['frameId'] === '" + self.frame_id + "'){" + js_str + "}}}"
        self.update_display(js_str)

    def get_progress_status_list(self):
        msgs = []
        size = 0
        while (size <= 100):
            # next_progress_status: None | 'xxx'
            next_progress_status = self.manager.fetch_table_task.get_next_progress_status()
            if next_progress_status is None:
                break
            else:
                msgs.append(next_progress_status)
                size = size + 1
        if len(msgs) == 0:
            return None
        else:
            return msgs

    def __task(self):
        if self.manager.is_cancelled():
            self.send_msgs([{'cancelled': self.true_flag}])
            return

        if self.manager.is_interrupted():
            self.update_display("document.getElementById('{}').style.display = 'none';".format(self.frame_id))
            return

        if self.manager.fetch_table_task.is_read_completed():
            self.send_msgs([{'running': self.false_flag}])
            return

        if self.manager.is_cancelling():
            self.send_msgs([{'cancelling': self.true_flag}])
        else:
            msgs = self.get_progress_status_list()
            if msgs is not None:
                self.send_msgs(msgs)
        self.__run()

    def __run(self):
        self.self_timer = threading.Timer(self.update_ui_interval, self.__task)
        self.self_timer.start()

    def start(self):
        self.display("")
        self.build_frame_html()
        display(HTML(self.frame_html))
        self.self_timer = threading.Timer(self.update_ui_interval, self.__task)
        self.self_timer.start()


class PipelineProgressStatusMonitor(object):
    """
    The instance of this class can monitor the progress of AutoML execution.

    Parameters
    ----------
    connection_context : :class:`~hana_ml.dataframe.ConnectionContext`
        The connection to the SAP HANA system.

        For example:

        .. only:: latex

            >>> from hana_ml.dataframe import ConnectionContext as CC
            >>> progress_status_monitor = PipelineProgressStatusMonitor(connection_context=CC(url, port, user, pwd),
                                                                        automatic_obj=auto_c)

        .. raw:: html

            <iframe allowtransparency="true" style="border:1px solid #ccc; background: #eeffcb;"
                src="_static/automl_progress_example.html" width="100%" height="100%">
            </iframe>

    automatic_obj : :class:`~hana_ml.algorithms.pal.auto_ml.AutomaticClassification` or :class:`~hana_ml.algorithms.pal.auto_ml.AutomaticRegression`
        An instance object of the AutomaticClassification type or AutomaticRegression type
        that contains the progress_indicator_id attribute.

    fetch_table_interval : float, optional
        Specifies the time interval of fetching the table of pipeline progress.

        Defaults to 1s.

    runtime_platform : {'jupyter', 'sap_bas', 'vscode'}, optional
        Specify the running environment of the monitor.

          - 'jupyter': running on the JupyterLab or Jupyter Notebook platform.
          - 'sap_bas': running on the SAP Business Application Studio platform.
          - 'vscode': running on the VSCode platform.

        Defaults to 'jupyter'.

    Examples
    --------
    Create an AutomaticClassification instance:

    >>> progress_id = "automl_{}".format(uuid.uuid1())
    >>> auto_c = AutomaticClassification(generations=2,
                                         population_size=5,
                                         offspring_size=5,
                                         progress_indicator_id=progress_id)
    >>> auto_c.enable_workload_class("MY_WORKLOAD")

    Invoke a PipelineProgressStatusMonitor:

    >>> progress_status_monitor = PipelineProgressStatusMonitor(connection_context=dataframe.ConnectionContext(url, port, user, pwd),
                                                                automatic_obj=auto_c)
    >>> progress_status_monitor.start()
    >>> auto_c.fit(data=df_train)

    Output:

    .. image:: image/progress_classification.png

    """
    def __init__(self, connection_context: ConnectionContext, automatic_obj, fetch_table_interval=1, runtime_platform='jupyter'):
        self.new_connection_context = create_connection_context(connection_context)
        self.automatic_obj = automatic_obj
        # Specifies the time interval of updating the UI of pipeline progress.
        self.update_ui_interval = fetch_table_interval
        self.fetch_table_interval = fetch_table_interval
        self.runtime_platform = runtime_platform

    def start(self):
        """
        Call the method before executing the fit method of Automatic Object.
        """
        TaskManager(
            AutomaticObjProxy(self.automatic_obj, self.new_connection_context),
            self.new_connection_context,
            self.update_ui_interval,
            self.fetch_table_interval,
            self.runtime_platform).start()
