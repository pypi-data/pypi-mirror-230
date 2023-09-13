"""
This module contains Python wrapper for PAL change-point detection algorithm.

The following class is available:

    * :class:`CPD`
    * :class:`BCPD`
    * :class:`OnlineBCPD`
"""
#pylint:disable=too-many-lines, line-too-long, too-many-arguments, too-few-public-methods, too-many-instance-attributes
#pylint:disable=too-many-locals, no-else-return, attribute-defined-outside-init, too-many-branches, too-many-statements
#pylint: disable=c-extension-no-member, super-with-arguments, invalid-name
import logging
import warnings
import uuid
try:
    import pyodbc
except ImportError as error:
    pass
from hdbcli import dbapi
from hana_ml.dataframe import quotename
from hana_ml.algorithms.pal.utility import check_pal_function_exist
from hana_ml.algorithms.pal.tsa.utility import _convert_index_from_timestamp_to_int, _is_index_int
from hana_ml.algorithms.pal.pal_base import (
    PALBase,
    ParameterTable,
    ListOfStrings,
    try_drop,
    require_pal_usable
)

logger = logging.getLogger(__name__)#pylint:disable=invalid-name


class CPD(PALBase):
    r"""
    Change-point detection (CPDetection) methods aim at detecting multiple abrupt changes such as change in mean,
    variance or distribution in an observed time-series data.

    Parameters
    ----------

    cost : {'normal_mse', 'normal_rbf', 'normal_mhlb', 'normal_mv', 'linear', 'gamma', 'poisson', 'exponential', 'normal_m', 'negbinomial'}, optional

        The cost function for change-point detection.

        Defaults to 'normal_mse'.

    penalty : {'aic', 'bic', 'mbic', 'oracle', 'custom'}, optional

        The penalty function for change-point detection.

        Defaults to
            (1)'aic' if ``solver`` is 'pruneddp', 'pelt' or 'opt',

            (2)'custom' if ``solver`` is 'adppelt'.

    solver : {'pelt', 'opt', 'adppelt', 'pruneddp'}, optional

        Method for finding change-points of given data, cost and penalty.

        Each solver supports different cost and penalty functions.

          - 1.  For cost functions, 'pelt', 'opt' and 'adpelt' support the following eight:
                'normal_mse', 'normal_rbf', 'normal_mhlb', 'normal_mv',
                'linear', 'gamma', 'poisson', 'exponential';
                while 'pruneddp' supports the following four cost functions:
                'poisson', 'exponential', 'normal_m', 'negbinomial'.
          - 2.  For penalty functions, 'pruneddp' supports all penalties, 'pelt', 'opt' and 'adppelt' support the following three:
                'aic','bic','custom', while 'adppelt' only supports 'custom' cost.

        Defaults to 'pelt'.

    lamb : float, optional

        Assigned weight of the penalty w.r.t. the cost function, i.e. penalization factor.

        It can be seen as trade-off between speed and accuracy of running the detection algorithm.

        A small values (usually less than 0.1) will dramatically improve the efficiency.

        Defaults to 0.02, and valid only when ``solver`` is 'pelt' or 'adppelt'.

    min_size : int, optional

        The minimal length from the very beginning within which change would not happen.

        Valid only when ``solver`` is 'opt', 'pelt' or 'adppelt'.

        Defaults to 2.

    min_sep : int, optional

        The minimal length of separation between consecutive change-points.

        Defaults to 1, valid only when ``solver`` is 'opt', 'pelt' or 'adppelt'.

    max_k : int, optional

        The maximum number of change-points to be detected.

        If the given value is less than 1, this number would be determined automatically from the input data.

        Defaults to 0, valid only when ``solver`` is 'pruneddp'.

    dispersion : float, optinal

        Dispersion coefficient for Gamma and negative binomial distribution.

        Valid only when `cost` is 'gamma' or 'negbinomial'.

        Defaults to 1.0.

    lamb_range : list of two numerical(float and int) values, optional(deprecated)

        User-defined range of penalty.

        Only valid when ``solver`` is 'adppelt'.

        Deprecated, please use ``range_penalty`` instead.

    max_iter : int, optional

        Maximum number of iterations for searching the best penalty.

        Valid only when ``solver`` is 'adppelt'.

        Defaults to 40.

    range_penalty : list of two numerical values, optional

        User-defined range of penalty.

        Valid only when ``solver`` is 'adppelt' and ``value_penalty`` is not provided.

        Defaults to [0.01, 100].

    value_penalty : float, optional

        Value of user-defined penalty.

        Valid when ``penalty`` is 'custom' or ``solver`` is 'adppelt'.

        No default value.

    Attributes
    ----------

    stats_ : DataFrame

        Statistics for running change-point detection on the input data, structured as follows:

        - 1st column: statistics name,
        - 2nd column: statistics value.

    Examples
    --------

    First check the input time-series DataFrame df:

    >>> df.collect()
      TIME_STAMP      SERIES
    0        1-1       -5.36
    1        1-2       -5.14
    2        1-3       -4.94
    3        2-1       -5.15
    4        2-2       -4.95
    5        2-3        0.55
    6        2-4        0.88
    7        3-1        0.95
    8        3-2        0.68
    9        3-3        0.86

    Now create a CPD instance with 'pelt' solver and 'aic' penalty:

    >>> cpd = CPD(solver='pelt',
    ...           cost='normal_mse',
    ...           penalty='aic',
    ...           lamb=0.02)

    Apply the above CPD instance to the input data, check the detection result and
    related statistics:

    >>> cp = cpd.fit_predict(data=df)
    >>> cp.collect()
          TIME_STAMP
    0            2-2

    >>> cpd.stats_.collect()
                 STAT_NAME    STAT_VAL
    0               solver        Pelt
    1        cost function  Normal_MSE
    2         penalty type         AIC
    3           total loss     4.13618
    4  penalisation factor        0.02

    Create another CPD instance with 'adppelt' solver and 'normal_mv' cost:

    >>> cpd = CPD(solver='adppelt',
    ...           cost='normal_mv',
    ...           range_penalty=[0.01, 100],
    ...           lamb=0.02)

    Again, apply the above CPD instance to the input data, check the detection result and
    related statistics:

    >>> cp.collect()
          TIME_STAMP
    0            2-2

    >>> cpd.stats_.collect()
                 STAT_NAME   STAT_VAL
    0               solver    AdpPelt
    1        cost function  Normal_MV
    2         penalty type     Custom
    3           total loss   -28.1656
    4  penalisation factor       0.02
    5            iteration          2
    6      optimal penalty    2.50974

    Create a third CPD instance with 'pruneddp' solver and 'oracle' penalty:

    >>> cpd = CPD(solver='pruneddp', cost='normal_m', penalty='oracle', max_k=3)

    Similar as before, apply the above CPD instance to the input data, check the detection result and
    related statistics:

    >>> cp = cpd.fit_predict(data=df)
    >>> cp.collect()
          TIME_STAMP
    0            2-2

    >>> cpd.stats_.collect()
                 STAT_NAME   STAT_VAL
    0               solver    AdpPelt
    1        cost function  Normal_MV
    2         penalty type     Custom
    3           total loss   -28.1656
    4  penalisation factor       0.02
    5            iteration          2
    6      optimal penalty    2.50974
    """

    solver_map = {'pelt':'Pelt', 'opt':'Opt', 'adppelt':'AdpPelt', 'pruneddp':'PrunedDP'}
    penalty_map = {'aic':'AIC', 'bic':'BIC', 'mbic':'mBIC', 'oracle':'Oracle', 'custom':'Custom'}
    cost_map = {'normal_mse':'Normal_MSE', 'normal_rbf':'Normal_RBF',
                'normal_mhlb':'Normal_MHLB', 'normal_mv':'Normal_MV',
                'linear':'Linear', 'gamma':'Gamma', 'poisson':'Poisson',
                'exponential':'Exponential', 'normal_m':'Normal_M',
                'negbinomial':'NegBinomial'}
    def __init__(self,#pylint: disable=too-many-arguments, too-many-locals, too-many-branches
                 cost=None,
                 penalty=None,
                 solver=None,
                 lamb=None,
                 min_size=None,
                 min_sep=None,
                 max_k=None,
                 dispersion=None,
                 lamb_range=None,
                 max_iter=None,
                 range_penalty=None,
                 value_penalty=None):
        super(CPD, self).__init__()
        self.cost = self._arg('cost', cost, self.cost_map)
        self.penalty = self._arg('penalty', penalty, self.penalty_map)
        self.solver = self._arg('solver', solver, self.solver_map)
        if self.solver in ('Pelt', 'Opt', None) and self.penalty not in ('AIC', 'BIC', 'Custom', None):
            msg = ("When 'solver' is 'pelt' or 'opt', "+
                   "only 'aic', 'bic' and 'custom' are valid penalty functions.")
            raise ValueError(msg)
        if self.solver == 'AdpPelt' and self.penalty not in ('Custom', None):
            msg = ("When 'solver' is 'adppelt', penalty function must be 'custom'.")
            raise ValueError(msg)
        cost_list_one = ['Normal_MSE', 'Normal_RBF', 'Normal_MHLB', 'Normal_MV',
                         'Linear', 'Gamma', 'Poisson', 'Exponential']
        cost_list_two = ['Poisson', 'Exponential', 'Normal_M', 'NegBinomial']
        if self.solver in ('Pelt', 'Opt', 'AdpPelt', None):
            if  self.cost is not None and self.cost not in cost_list_one:
                msg = ("'solver' is currently one of the following: pelt, opt and adppelt, "+
                       "in this case cost function must be one of the following: normal_mse, normal_rbf, "+
                       "normal_mhlb, normal_mv, linear, gamma, poisson, exponential.")
                raise ValueError(msg)
        elif self.cost is not None and self.cost not in cost_list_two:
            msg = ("'solver' is currently PrunedDP, in this case 'cost' must be assigned a valid value listed as follows: poisson, exponential, normal_m, negbinomial")
            raise ValueError(msg)
        self.lamb = self._arg('lamb', lamb, float)
        self.min_size = self._arg('min_size', min_size, int)
        self.min_sep = self._arg('min_sep', min_sep, int)
        self.max_k = self._arg('max_k', max_k, int)
        self.dispersion = self._arg('dispersion', dispersion, float)
        if lamb_range is not None:
            if isinstance(lamb_range, list) and len(lamb_range) == 2 and all(isinstance(val, (int, float)) for val in lamb_range):#pylint:disable=line-too-long
                self.lamb_range = lamb_range
            else:
                msg = ("Wrong setting for parameter 'lamb_range', correct setting "+
                       "should be a list of two numerical values that corresponds to "+
                       "lower- and upper-limit of the penelty weight.")
                raise ValueError(msg)
        else:
            self.lamb_range = None
        self.max_iter = self._arg('max_iter', max_iter, int)
        if range_penalty is not None:
            if isinstance(range_penalty, (list, tuple)) and len(range_penalty) == 2 and all(isinstance(val, (int, float)) for val in range_penalty):#pylint:disable=line-too-long
                self.lamb_range = list(range_penalty)
            else:
                msg = ("Wrong setting for parameter 'range_penalty', correct setting "+
                       "should be a list of two numerical values that corresponds to "+
                       "lower- and upper-limit of the penelty value.")
                raise ValueError(msg)
        else:
            self.lamb_range = None
        self.value_penalty = self._arg('value_penalty', value_penalty, float)

    def fit_predict(self, data, key=None, features=None):
        """
        Detecting change-points of the input data.

        Parameters
        ----------

        data : DataFrame

            Input time-series data for change-point detection.

        key : str, optional

            Column name for time-stamp of the input time-series data.

            If the index column of data is not provided or not a single column, and the key of fit_predict function is not provided,
            the default value is the first column of data.

            If the index of data is set as a single column, the default value of key is index column of data.

        features : str or list of str, optional

            Column name(s) for the value(s) of the input time-series data.

        Returns
        -------

        DataFrame

            Detected the change-points of the input time-series data.
        """
        conn = data.connection_context
        require_pal_usable(conn)
        cols = data.columns

        index = data.index
        key = self._arg('key', key, str)
        if index is not None:
            if key is None:
                if not isinstance(index, str):
                    key = cols[0]
                    warn_msg = "The index of data is not a single column and key is None, so the first column of data is used as key!"
                    warnings.warn(message=warn_msg)
                else:
                    key = index
            else:
                if key != index:
                    warn_msg = "Discrepancy between the designated key column '{}' ".format(key) +\
                    "and the designated index column '{}'.".format(index)
                    warnings.warn(message=warn_msg)
        else:
            if key is None:
                key = cols[0]

        if features is not None:
            if isinstance(features, str):
                features = [features]
            features = self._arg('features', features, ListOfStrings)
        else:
            cols.remove(key)
            features = cols
        used_cols = [key] + features
        if any(col not in data.columns for col in used_cols):
            msg = "'key' or 'features' parameter contains unrecognized column name."
            raise ValueError(msg)
        data_ = data[used_cols]
        param_rows = [
            ('COSTFUNCTION', None, None, self.cost),
            ('SOLVER', None, None, self.solver),
            ('PENALIZATION_FACTOR', None, self.lamb, None),
            ('MIN_SIZE', self.min_size, None, None),
            ('MIN_SEP', self.min_sep, None, None),
            ('MaxK', self.max_k, None, None),
            ('DISPERSION', None, self.dispersion, None),
            ('MAX_ITERATION', self.max_iter, None, None)]
        if (self.penalty == 'Custom' or self.solver == 'AdpPelt') and self.value_penalty is not None:
            param_rows.extend([('PENALTY', None, self.value_penalty, 'Custom')])
        elif self.penalty not in ['Custom', None]:
            param_rows.extend([('PENALTY', None, None, self.penalty)])
        if self.lamb_range is not None:
            param_rows.extend([('RANGE_PENALTIES', None, None, str(self.lamb_range))])
        unique_id = str(uuid.uuid1()).replace('-', '_').upper()
        tables = ['RESULT', 'STATS']
        tables = ["#PAL_CPDETECTION_{}_TBL_{}_{}".format(tbl, self.id, unique_id) for tbl in tables]
        result_tbl, stats_tbl = tables
        try:
            self._call_pal_auto(conn,
                                "PAL_CPDETECTION",
                                data_,
                                ParameterTable().with_data(param_rows),
                                *tables)
        except dbapi.Error as db_err:
            logger.exception(str(db_err))
            try_drop(conn, tables)
            raise
        except pyodbc.Error as db_err:
            logger.exception(str(db_err.args[1]))
            try_drop(conn, tables)
            raise
        self.stats_ = conn.table(stats_tbl)
        return conn.table(result_tbl)

class BCPD(PALBase):
    r"""
    Bayesian  Change-point detection (BCPD) detects abrupt changes in the time series.
    It, to some extent, can been assumed as an enhanced version of seasonality test in additive mode.

    Parameters
    ----------

    max_tcp : int

        Maximum number of trend change points to be detected.

    max_scp : int

        Maximum number of season change points to be detected.

    trend_order : int, optional

        Order of trend segments that used for decomposition

        Defaults to 1.

    max_harmonic_order : int, optional

        Maximum order of harmonic waves within seasonal segments.

        Defaults to 10.

    min_period : int, optional

        Minimum possible period within seasonal segments.

        Defaults to 1.

    max_period : int, optional

        Maximum possible period within seasonal segments.

        Defaults to half of the data length.

    random_seed : int, optional

        Indicates the seed used to initialize the random number generator:

        - 0: Uses the system time.
        - Not 0: Uses the provided value.

        Defaults to 0.

    max_iter : int, optional

        BCPD is iterative, the more iterations, the more precise will the result be rendered.

        Defaults to 5000.

    interval_ratio : float, optional

        Regulates the interval between change points, which should be larger than the corresponding portion of total length.

        Defaults to 0.1.

    Examples
    --------
    >>> df.collect()
      TIME_STAMP      SERIES
    0          1       -5.36
    1          2       -5.14
    2          3       -4.94
    3          4       -5.15
    4          5       -4.95
    5          6        0.55
    6          7        0.88
    7          8        0.95
    8          9        0.68
    9         10        0.86

    >>> bcpd = BCPD(max_tcp=5, max_scp=5)
    >>> tcp, scp, period, components = bcpd.fit_predict(data=df)
    >>> scp.collect()
          ID      SEASON_CP
    0      1              4
    1      2              5
    """

    def __init__(self,#pylint: disable=too-many-arguments, too-many-locals, too-many-branches
                 max_tcp,
                 max_scp,
                 trend_order=None,
                 max_harmonic_order=None,
                 min_period=None,
                 max_period=None,
                 random_seed=None,
                 max_iter=None,
                 interval_ratio=None):

        if max_scp > 0 and max_harmonic_order is None:
            warn_msg = "Please enter a positive value of max_harmonic_order when max_scp is larger than 0!"
            warnings.warn(message=warn_msg)
        super(BCPD, self).__init__()
        self.trend_order = self._arg('trend_order', trend_order, int)
        self.max_tcp = self._arg('max_tcp', max_tcp, int)
        self.max_scp = self._arg('max_scp', max_scp, int)
        self.max_harmonic_order = self._arg('max_harmonic_order', max_harmonic_order, int)
        self.min_period = self._arg('min_period', min_period, int)
        self.max_period = self._arg('max_period', max_period, int)
        self.random_seed = self._arg('random_seed', random_seed, int)
        self.max_iter = self._arg('max_iter', max_iter, int)
        self.interval_ratio = self._arg('interval_ratio', interval_ratio, float)

        self.is_index_int = None

    def fit_predict(self, data, key=None, endog=None, features=None):
        """
        Detects change-points of the input data.

        Parameters
        ----------

        data : DataFrame

            Input time-series data for change-point detection.

        key : str, optional

            Column name for time-stamp of the input time-series data.

            If the index column of data is not provided or not a single column, and the key of fit_predict function is not provided,
            the default value is the first column of data.

            If the index of data is set as a single column, the default value of key is index column of data.

        endog : str, optional

            Column name for the value of the input time-series data.
            Defaults to the first non-key column.

        features : str or list of str, optional (*deprecated*)
            Column name(s) for the value(s) of the input time-series data.

        Returns
        -------

        DataFrame 1

            The detected the trend change-points of the input time-series data.

        DataFrame 2

            The detected the season change-points of the input time-series data.

        DataFrame 3

            The detected the period within each season segment of the input time-series data.

        DataFrame 4

            The decomposed components.

        """
        conn = data.connection_context
        require_pal_usable(conn)
        cols = data.columns
        index = data.index
        key = self._arg('key', key, str)
        if index is not None:
            if key is None:
                if not isinstance(index, str):
                    key = cols[0]
                    warn_msg = "The index of data is not a single column and key is None, so the first column of data is used as key!"
                    warnings.warn(message=warn_msg)
                else:
                    key = index
            else:
                if key != index:
                    warn_msg = "Discrepancy between the designated key column '{}' ".format(key) +\
                    "and the designated index column '{}'.".format(index)
                    warnings.warn(message=warn_msg)
        else:
            if key is None:
                key = cols[0]

        if endog is not None:
            features = endog
        if features is not None:
            if not isinstance(features, str):
                msg = "BCPD currently only supports one column of endog!"
                raise ValueError(msg)
        else:
            cols.remove(key)
            features = cols[0]
        used_cols = [key] + [features]
        if any(col not in data.columns for col in used_cols):
            msg = "'key' or 'endog' parameter contains unrecognized column name."
            raise ValueError(msg)
        data_ = data[used_cols]

        self.is_index_int = _is_index_int(data_, key)
        if not self.is_index_int:
            data_ = _convert_index_from_timestamp_to_int(data_, key)

        param_rows = [
            ('TREND_ORDER', self.trend_order, None, None),
            ('MAX_TCP_NUM', self.max_tcp, None, None),
            ('MAX_SCP_NUM', self.max_scp, None, None),
            ('MAX_HARMONIC_ORDER', self.max_harmonic_order, None, None),
            ('MIN_PERIOD', self.min_period, None, None),
            ('MAX_PERIOD', self.max_period, None, None),
            ('RANDOM_SEED', self.random_seed, None, None),
            ('MAX_ITER', self.max_iter, None, None),
            ('INTERVAL_RATIO', None, self.interval_ratio, None)]
        unique_id = str(uuid.uuid1()).replace('-', '_').upper()
        outputs = ['TREND_CHANGE_POINT', 'SEASON_CHANGE_POINT', 'PERIOD_LIST', 'DECOMPOSED']
        outputs = ["#PAL_BCPD_{}_TBL_{}_{}".format(tbl, self.id, unique_id) for tbl in outputs]
        tcp_tbl, scp_tbl, period_tbl, decompose_tbl = outputs
        try:
            self._call_pal_auto(conn,
                                "PAL_BCPD",
                                data_,
                                ParameterTable().with_data(param_rows),
                                *outputs)
        except dbapi.Error as db_err:
            logger.exception(str(db_err))
            try_drop(conn, outputs)
            raise
        except pyodbc.Error as db_err:
            logger.exception(str(db_err.args[1]))
            try_drop(conn, outputs)
            raise
        decompose_df = conn.table(decompose_tbl)
        tcp_df = conn.table(tcp_tbl)
        scp_df = conn.table(scp_tbl)
        period_df = conn.table(period_tbl)

        if not self._disable_hana_execution:
            decom_cols = decompose_df.columns
            # ID is timestamp
            if not self.is_index_int:
                if tcp_df.shape[0] > 0:
                    tcp_cols = tcp_df.columns
                    tcp_int = tcp_df.sort('TREND_CP')
                    data_int = data.sort(key).add_id('ID_DATA')
                    tcp_timestamp = tcp_int.join(data_int, 'TREND_CP=ID_DATA').select(tcp_cols[0], key).sort(tcp_cols[0]).rename_columns({key:'TREND_CP'})
                else:
                    tcp_timestamp = tcp_df

                if scp_df.shape[0] > 0:
                    scp_cols = scp_df.columns
                    scp_int = scp_df.sort('SEASON_CP')
                    data_int = data.sort(key).add_id('ID_DATA')
                    scp_timestamp = scp_int.join(data_int, 'SEASON_CP=ID_DATA').select(scp_cols[0], key).sort(scp_cols[0]).rename_columns({key:'SEASON_CP'})
                else:
                    scp_timestamp = scp_df
                decompose_int = decompose_df.rename_columns({'ID':'ID_RESULT'})
                data_int = data.add_id('ID_DATA', ref_col=key)
                decompose_timestamp = decompose_int.join(data_int, 'ID_RESULT=ID_DATA').select(key, decom_cols[1], decom_cols[2], decom_cols[3])
                return(tcp_timestamp,
                       scp_timestamp,
                       period_df,
                       decompose_timestamp)

            # ID is INT
            decompose_int_sql = """
                            SELECT {0} AS {5},
                            {1},
                            {2},
                            {3}
                            FROM {4}
                            """.format(quotename(decom_cols[0]),
                                       quotename(decom_cols[1]),
                                       quotename(decom_cols[2]),
                                       quotename(decom_cols[3]),
                                       decompose_tbl,
                                       quotename(key))
            decompose_int = conn.sql(decompose_int_sql)
            return (tcp_df,
                    scp_df,
                    period_df,
                    decompose_int)
        return None

class OnlineBCPD(PALBase):
    r"""
    Online Bayesian Change-point detection.

    Parameters
    ----------

    alpha : float, optional

        Parameter of t-distribution.

        Defaults to 0.1.
    beta : float, optional

        Parameter of t-distribution.

        Defaults to 0.01.
    kappa : float, optional

        Parameter of t-distribution.

        Defaults to 1.0.
    mu : float, optional

        Parameter of t-distribution.

        Defaults to 0.0.
    lamb : float, optional

        Parameter of constant hazard function.

        Defaults to 250.0.
    threshold : float, optional

        Threshold to determine a change point:

        - 0: Return the probability of change point for every time step.
        - 0~1: Only return the time step of which the probability is above the threshold.

        Defaults to 0.0.
    delay : int, optional

        Number of incoming time steps to determine whether the current time step is a change point.

        Defaults to 3.
    prune : bool, optional

        Reduce the size of model table after every run:

        - False: Do not prune.
        - True: Prune.

        Defaults to False.

    Examples
    --------
    Input Data:

    >>> df.collect()
       ID        VAL
    0   0   9.926943
    1   1   9.262971
    2   2   9.715766
    3   3   9.944334
    4   4   9.577682
    5   5  10.036977
    6   6   9.513112
    7   7  10.233246
    8   8  10.159134
    9   9   9.759518
    .......

    Create an OnlineBCPD instance:

    >>> obcpd = OnlineBCPD(alpha=0.1,
                           beta=0.01,
                           kappa=1.0,
                           mu=0.0,
                           delay=5,
                           threshold=0.5,
                           prune=True)

    Invoke fit_predict():

    >>> model, cp = obcpd.fit_predict(data=df, model=None)

    Output:

    >>> print(model.head(5).collect())
       ID  ALPHA        BETA  KAPPA         MU          PROB
    0   0    0.1    0.010000    1.0   0.000000  4.000000e-03
    1   1    0.6   71.013179    2.0   8.426338  6.478577e-05
    2   2    1.1   86.966340    3.0  10.732357  7.634862e-06
    3   3    1.6  100.514641    4.0  12.235038  1.540977e-06
    4   4    2.1  107.197565    5.0  13.052529  3.733699e-07
    >>> print(cp.collect())
       ID  POSITION  PROBABILITY
    0   0        58     0.989308
    1   1       249     0.991023
    2   2       402     0.994154
    3   3       539     0.981004
    4   4       668     0.994708

    """
    def __init__(self,
                 alpha=None,
                 beta=None,
                 kappa=None,
                 mu=None,
                 lamb=None,
                 threshold=None,
                 delay=None,
                 prune=None):

        super(OnlineBCPD, self).__init__()
        self.alpha = self._arg('alpha', alpha, float)
        self.beta = self._arg('beta', beta, float)
        self.kappa = self._arg('kappa', kappa, float)
        self.mu = self._arg('mu', mu, float)
        self.lamb = self._arg('lambda', lamb, float)
        self.threshold = self._arg('threshold', threshold, float)
        self.delay  = self._arg('delay', delay, int)
        self.prune  = self._arg('prune', prune, bool)

        self.model_ = None
        self.model_tbl_name = None
        self.conn = None

    def fit_predict(self, data, key=None, endog=None, model=None):
        r"""
        Detects change-points of the input data.

        Parameters
        ----------

        data : DataFrame

            Input time-series data for change-point detection.

        key : str, optional

            Column name for time-stamp of the input time-series data.

            If the index column of data is not provided or not a single column, and the key of fit_predict function is not provided,
            the default value is the first column of data.

            If the index of data is set as a single column, the default value of key is index column of data.

        endog : str, optional

            Column name for the value of the input time-series data.
            Defaults to the first non-key column.

        model : DataFrame, optional

            The model for change point detection.

            Defaults to self.model\_ (the default value of self.model\_ is None).

        Returns
        -------

        DataFrame 1

            Model.

        DataFrame 2

            The detected change points.

        """
        conn = data.connection_context
        require_pal_usable(conn)
        self.conn = conn
        cols = data.columns
        index = data.index
        key = self._arg('key', key, str)
        if index is not None:
            if key is None:
                if not isinstance(index, str):
                    key = cols[0]
                    warn_msg = "The index of data is not a single column and key is None, so the first column of data is used as key!"
                    warnings.warn(message=warn_msg)
                else:
                    key = index
            else:
                if key != index:
                    warn_msg = "Discrepancy between the designated key column '{}' ".format(key) +\
                    "and the designated index column '{}'.".format(index)
                    warnings.warn(message=warn_msg)
        else:
            if key is None:
                key = cols[0]

        cols.remove(key)

        if endog is None:
            endog = cols[0]

        used_cols = [key] + [endog]
        if any(col not in data.columns for col in used_cols):
            msg = "'key' or 'endog' parameter contains unrecognized column name."
            raise ValueError(msg)
        data_ = data[used_cols]

        self.is_index_int = _is_index_int(data_, key)
        if not self.is_index_int:
            data_ = _convert_index_from_timestamp_to_int(data_, key)

        param_rows = [
            ('ALPHA',       None, self.alpha,     None),
            ('BETA',        None, self.beta,      None),
            ('KAPPA',       None, self.kappa,     None),
            ('MU',          None, self.mu,        None),
            ('LAMBDA',      None, self.lamb,      None),
            ('THRESHOLD',   None, self.threshold, None),
            ('DELAY', self.delay,           None, None),
            ('PRUNE', self.prune,           None, None)]

        unique_id = str(uuid.uuid1()).replace('-', '_').upper()
        model_tbl = '#PAL_ONLINE_BCPD_MODEL_TBL_{}_{}'.format(self.id, unique_id)
        self.model_tbl_name = model_tbl
        cp_tbl    = '#PAL_ONLINE_BCPD_CHANGE_POINT_TBL_{}_{}'.format(self.id, unique_id)
        outputs = [model_tbl, cp_tbl]
        input_model = None

        try:
            if check_pal_function_exist(conn, '%ONLINE_BCPD%', like=True):
                if model:
                    input_model = model
                elif self.model_:
                    input_model = self.model_
                else:
                    empty_tbl = '#PAL_EMPTY_TBL_{}_{}'.format(self.id, unique_id)
                    conn.create_table(table=empty_tbl,
                                      table_structure={'ID'    : 'INTEGER',
                                                       'ALPHA' :  'DOUBLE',
                                                       'BETA'  :  'DOUBLE',
                                                       'KAPPA' :  'DOUBLE',
                                                       'MU'    :  'DOUBLE',
                                                       'PROB'  :  'DOUBLE'})
                    input_model = conn.table(empty_tbl)

                self._call_pal_auto(conn,
                                    "PAL_ONLINE_BCPD",
                                    data_,
                                    input_model,
                                    ParameterTable().with_data(param_rows),
                                    *outputs)
            else:
                msg = 'The version of your SAP HANA does not support online BCPD!'
                logger.error(msg)
                raise ValueError(msg)
        except dbapi.Error as db_err:
            logger.exception(str(db_err))
            try_drop(conn, outputs)
            raise
        except pyodbc.Error as db_err:
            logger.exception(str(db_err.args[1]))
            try_drop(conn, outputs)
            raise
        self.model_ = conn.table(model_tbl)
        cp_df = conn.table(cp_tbl)
        # ID is timestamp
        if not self.is_index_int:
            if cp_df.shape[0] > 0:
                cp_cols = cp_df.columns
                data_int = data.add_id('ID_DATA', ref_col=key)
                cp_timestamp = cp_df.join(data_int, 'POSITION=ID_DATA').select(cp_cols[0], key, cp_cols[2])
                cp_timestamp =  cp_timestamp.rename_columns({key:'POSITION'})
            else:
                cp_timestamp = cp_df
            return (self.model_, cp_timestamp)

        # ID is INT
        return (self.model_, cp_df)

    def get_stats(self):
        r"""
        Gets the statistics.

        Returns
        -------

        DataFrame

            Statistics.
        """
        if self.model_:
            return self.model_
        return None
