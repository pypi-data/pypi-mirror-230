"""
This module contains Python wrapper for PAL time series outlier detection algorithm.

The following function is available:

    * ：class：`OutlierDetectionTS`
"""
#pylint:disable=line-too-long, too-many-arguments, too-few-public-methods
#pylint: disable=invalid-name, unused-argument, too-many-locals, too-many-statements
#pylint: disable=attribute-defined-outside-init, unused-variable
#pylint: disable=too-many-branches, c-extension-no-member
import logging
import uuid
import warnings
try:
    import pyodbc
except ImportError as error:
    pass
from hdbcli import dbapi
from hana_ml.algorithms.pal.utility import check_pal_function_exist
from hana_ml.algorithms.pal.pal_base import (
    PALBase,
    ParameterTable,
    pal_param_register,
    try_drop
)
from hana_ml.algorithms.pal.tsa.utility import _convert_index_from_timestamp_to_int, _is_index_int
from hana_ml.algorithms.pal.sqlgen import trace_sql
logger = logging.getLogger(__name__)

class OutlierDetectionTS(PALBase):#pylint:disable=too-many-instance-attributes
    r"""
    Outlier detection for time-series.

    Parameters
    ----------

    auto : bool, optional

        - True : automatic method to get residual.
        - False : manual method to get residual.

        Defaults to True.

    detect_intermittent_ts : bool, optional

        - True : detects whether the time series is intermittent.
        - False : does not detect whether the time series is intermittent.

        only valid when ``auto`` is True. If input data is intermittent time series, it will not do outlier detection

        Defaults to False.

    smooth_method : str, optional
        the method to get the residual.

        - 'median' : median filter.
        - 'loess' : LOESS (locally estimated scatterplot smoothing) or LOWESS (locally weighted scatterplot smoothing) is a locally weighted linear regression method. This method is applicable to the time series which is non-seasonal. This method is also suitable for non-smooth time series.
        - 'super' : super smoother. This method combines a set of LOESS methods. Like LOESS, this method is applicable to non-seasonal time series. This method is also suitable for non-smooth time series.

        only valid when ``auto`` is False.

        Defaults to 'median'.

    window_size : int, optional
        Odd number, the window size for median filter, not less than 3.

        The value 1 means median filter is not applied. Only valid when ``auto`` is False and ``smooth_method`` is 'median'.

        Defaults to 3.

    loess_lag : int, optional
        Odd number, the lag for LOESS, not less than 3.

        Only valid when ``auto`` is False and ``smooth_method`` is 'loess'.

        Defaults to 7.

    current_value_flag : bool, optional
        Whether to take the current data point when using LOESS smoothing method.

        - True : takes the current data point.
        - False : does not take the current data point.

        For example, to estimate the value at time t with the window [t-3, t-2, t-1, t, t+1, t+2, t+3], taking the current data point means estimating the value at t with the real data points at [t-3, t-2, t-1, t, t+1, t+2, t+3], while not taking the current data point means estimating the value at t with the real data points at [t-3, t-2, t-1, t+1, t+2, t+3], without the real data point at t.

        Only valid when ``auto`` is False and ``smooth_method`` is 'median'.

        Defaults to False.

    outlier_method : str, optional

        The method for calculate the outlier score from residual.

        - 'z1' : Z1 score.
        - 'z2' : Z2 score.
        - 'iqr' : IQR score.
        - 'mad' : MAD score.
        - 'isolationforest' : isolation forest score.
        - 'dbscan' : DBSCAN.

        Defaults to 'z1'.

    threshold : float, optional
        The threshold for outlier score. If the absolute value of outlier score is beyond the
        threshold, we consider the corresponding data point as an outlier.

        Only valid when ``outlier_method`` = 'iqr', 'isolationforest', 'mad', 'z1', 'z2'. For ``outlier_method`` = 'isolationforest', when ``contamination`` is provided, ``threshold`` is not valid and outliers are decided by ``contamination``.

        Defaults to 3 when ``outlier_method`` is 'mad', 'z1' and 'z2'.
        Defaults to 1.5 when ``outlier_method`` is 'iqr'.
        Defaults to 0.7 when ``outlier_method`` is 'isolationforest'.

    detect_seasonality : bool, optional
        When calculating the residual,

        - False: Does not consider the seasonal decomposition.
        - True: Considers the seasonal decomposition.

        Only valid when ``auto`` is False and ``smooth_method`` is 'median'.

        Defaults to False.

    alpha : float, optional
        The criterion for the autocorrelation coefficient. The value range is (0, 1).

        A larger value indicates a stricter requirement for seasonality.

        Only valid when ``detect_seasonality`` is True.

        Defaults to 0.2 if ``auto`` is False and defaults to 0.4 if `auto`` is True.

    extrapolation : bool, optional
        Specifies whether to extrapolate the endpoints.
        Set to True when there is an end-point issue.

        Only valid when ``detect_seasonality`` is True.

        Defaults to False if ``auto`` is False and defaults to True if `auto`` is True.

    periods : int, optional
        When this parameter is not specified, the algorithm will search the seasonal period.
        When this parameter is specified between 2 and half of the series length, autocorrelation value
        is calculated for this number of periods and the result is compared to ``alpha`` parameter.
        If correlation value is equal to or higher than ``alpha``, decomposition is executed with the value of ``periods``.
        Otherwise, the residual is calculated without decomposition. For other value of parameter ``periods``, the residual is also calculated without decomposition.

        Only valid when ``detect_seasonality`` is True. If the user knows the seasonal period, specifying ``periods`` can speed up the calculation, especially when the time series is long.

        No Default value.

    random_state : int, optional
        Specifies the seed for random number generator.

        - 0: Uses the current time (in second) as seed.
        - Others: Uses the specified value as seed.

        Only valid when ``outlier_method`` is 'isolationforest'.

        Default to 0.

    n_estimators : int, optional
        Specifies the number of trees to grow.

        Only valid when ``outlier_method`` is 'isolationforest'.

        Default to 100.

    max_samples : int, optional
        Specifies the number of samples to draw from input to train each tree.
        If ``max_samples`` is larger than the number of samples provided,
        all samples will be used for all trees.

        Only valid when ``outlier_method`` is 'isolationforest'.

        Default to 256.

    bootstrap : bool, optional
        Specifies sampling method.

        - False: Sampling without replacement.
        - True: Sampling with replacement.

        Only valid when ``outlier_method`` is 'isolationforest'.

        Default to False.

    contamination : double, optional
        The proportion of outliers in the data set. Should be in the range (0, 0.5].

        Only valid when ``outlier_method`` is 'isolationforest'. When ``outlier_method`` is 'isolationforest' and ``contamination`` is specified, ``threshold`` is not valid.

        No Default value.

    minpts : int, optional
        Specifies the minimum number of points required to form a cluster. The point itself is not included in ``minpts``.

        Only valid when ``outlier_method`` is 'dbscan'.

        Defaults to 1.

    eps : float, optional
        Specifies the scan radius.

        Only valid when ``outlier_method`` is 'dbscan'.

        Defaults to 0.5.

    thread_ratio : float, optional
        The ratio of available threads.

        - 0: single thread.
        - 0~1: percentage.
        - Others: heuristically determined.

        Only valid when ``detect_seasonality`` is True or ``outlier_method`` is 'isolationforest' or 'dbscan' or `auto`` is True.

        Defaults to -1.

    References
    ----------
    Outlier detection methods implemented in this class are commonly consisted of two steps:

        #. :ref:`Residual Extraction<residual_extraction-label>`
        #. :ref:`Outlier Detection from Residual<odt_residual-label>`

    Please refer to the above links for detailed description of all methods as well as related parameters.

    Attributes
    ----------
    stats_ : DataFrame
        Data statistics, structured as follows:

        - STAT_NAME : Name of statistics.
        - STAT_VALUE : Value of statistics.

    metrics_ : DataFrame
        Relevant metrics, structured as follows:

        - NAME : Metric name.
        - VALUE : Metric value.


    Examples
    --------
    Time series DataFrame df:

    >>> df.collect()
        ID  RAW_DATA
    0    1       2.0
    1    2       2.5
    2    3       3.2
    3    4       2.8
    ......
    14  15       5.3
    15  16      10.0
    16  17       4.6
    17  18       4.4
    18  19       4.8
    19  20       5.1

    Initialize the class:

    >>> tsod = OutlierDetectionTS(detect_seasonality=False,
                                  outlier_method='z1',
                                  window_size=3,
                                  threshold=3.0)
    >>> res = tsod.fit_predict(data=df,
                               key='ID',
                               endog='RAW_DATA')

    Outputs and attributes:

    >>> res.collect()
        TIMESTAMP  RAW_DATA  RESIDUAL  OUTLIER_SCORE  IS_OUTLIER
    0           1       2.0       0.0      -0.297850           0
    1           2       2.5       0.0      -0.297850           0
    2           3       3.2       0.4      -0.010766           0
    ......
    13         14       5.1       0.0      -0.297850           0
    14         15       5.3       0.0      -0.297850           0
    15         16      10.0       4.7       3.075387           1
    16         17       4.6       0.0      -0.297850           0
    17         18       4.4      -0.2      -0.441392           0
    18         19       4.8       0.0      -0.297850           0
    19         20       5.1       0.0      -0.297850           0

    >>> tsod.stats_.collect()
                STAT_NAME STAT_VALUE
    0  DETECT_SEASONALITY          0
    1          OutlierNum          1
    2                Mean      0.415
    3  Standard Deviation    1.39332
    4          HandleZero          0

    """
    method_map = {'z1':0, 'z2':1, 'iqr':2, 'mad':3, 'isolationforest':4, 'dbscan':5}
    smooth_method_map = {'median':0, 'loess':1, 'super':2}
    def __init__(self,
                 auto=None,
                 detect_intermittent_ts=None,
                 smooth_method=None,
                 window_size=None,
                 loess_lag=None,
                 current_value_flag=None,
                 outlier_method=None,
                 threshold=None,
                 detect_seasonality=None,
                 alpha=None,
                 extrapolation=None,
                 periods=None,
                 random_state=None,
                 n_estimators=None,
                 max_samples=None,
                 bootstrap=None,
                 contamination=None,
                 minpts=None,
                 eps=None,
                 thread_ratio=None):
        if not hasattr(self, 'hanaml_parameters'):
            setattr(self, 'hanaml_parameters', pal_param_register())
        super().__init__()

        self.auto                   = self._arg('auto', auto, bool)
        self.detect_intermittent_ts = self._arg('detect_intermittent_ts', detect_intermittent_ts, bool)
        self.smooth_method          = self._arg('smooth_method', smooth_method, self.smooth_method_map)
        self.window_size            = self._arg('window_size', window_size, int)
        self.loess_lag              = self._arg('loess_lag', loess_lag, int)
        self.current_value_flag     = self._arg('current_value_flag', current_value_flag, bool)
        self.outlier_method         = self._arg('outlier_method', outlier_method, self.method_map)
        self.threshold              = self._arg('threshold', threshold, float)
        self.detect_seasonality     = self._arg('detect_seasonality', detect_seasonality, bool)
        self.alpha                  = self._arg('alpha', alpha, float)
        self.extrapolation          = self._arg('extrapolation', extrapolation, bool)
        self.periods                = self._arg('periods', periods, int)
        self.random_state           = self._arg('random_state', random_state, int)
        self.n_estimators           = self._arg('n_estimators', n_estimators, int)
        self.max_samples            = self._arg('max_samples', max_samples, int)
        self.bootstrap              = self._arg('bootstrap', bootstrap, bool)
        self.contamination          = self._arg('contamination', contamination, float)
        self.minpts                 = self._arg('minpts', minpts, int)
        self.eps                    = self._arg('eps', eps, float)
        self.thread_ratio           = self._arg('thread_ratio', thread_ratio, float)

        self.op_name = 'Outlier'
        stats_ = None
        metrics_ = None
        self.is_index_int = None

    @trace_sql
    def fit_predict(self, data, key=None, endog=None):
        r"""
        Detection of outliers in time-series data.

        Parameters
        ----------

        data : DataFrame

            Input data containing the target time-series.

            ``data`` should have at least two columns: one is ID column,
            the other is raw data.

        key : str, optional
            Specifies the ID column, in this case the column that shows the order
            of time-series.

            It is recommended that you always specifies this column manually.

            Defaults to the first column of data if the index column of data is not provided.
            Otherwise, defaults to the index column of data.

        endog : str, optional
            Specifies the column that contains the values of time-series to be tested.

            Defaults to the first non-key column.

        Returns
        -------
        DataFrame
            Outlier detection result, structured as follows:

            - TIMESTAMP : ID of data.
            - RAW_DATA : Original value.
            - RESIDUAL : Residual.
            - OUTLIER_SCORE : Outlier score.
            - IS_OUTLIER : 0: normal, 1: outlier.

        """
        setattr(self, 'hanaml_fit_params', pal_param_register())
        conn = data.connection_context
        key = self._arg('key', key, str)
        endog = self._arg('endog', endog, str)
        if not self._disable_hana_execution:
            cols = data.columns
            if len(cols) < 2:
                msg = ("Input data should contain at least 2 columns: " +
                       "one for ID, another for raw data.")
                logger.error(msg)
                raise ValueError(msg)
            if key is not None and key not in cols:
                msg = ('Please select key from name of columns!')
                logger.error(msg)
                raise ValueError(msg)
            index = data.index
            if index is not None:
                if key is None:
                    if not isinstance(index, str):
                        key = cols[0]
                        warn_msg = ("The index of data is not a single column and key is None, " +
                        "so the first column of data is used as key!")
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
            if endog is not None:
                if endog not in cols:
                    msg = 'Please select endog from name of columns!'
                    logger.error(msg)
                    raise ValueError(msg)
            else:
                endog = cols[0]
            data_ = data[[key] + [endog]]
            self.is_index_int = _is_index_int(data_, key)
            if not self.is_index_int:
                data_ = _convert_index_from_timestamp_to_int(data_, key)
        else:
            data_ = data
        unique_id = str(uuid.uuid1()).replace('-', '_').upper()
        outputs = ['RESTULT', 'STATS', 'METRICS']
        outputs = ['#PAL_TS_OUTLIER_{}_TBL_{}_{}'.format(name, self.id, unique_id) for name in outputs]
        res_tbl, stats_tbl, metrics_tbl = outputs

        param_rows = [('AUTO', self.auto, None, None),
                      ('DETECT_INTERMITTENT_TS', self.detect_intermittent_ts, None, None),
                      ('SMOOTH_METHOD', self.smooth_method, None, None),
                      ('WINDOW_SIZE', self.window_size, None, None),
                      ('LOESS_LAG', self.loess_lag, None, None),
                      ('CURRENT_VALUE_FLAG', self.current_value_flag, None, None),
                      ('OUTLIER_METHOD', self.outlier_method, None, None),
                      ('THRESHOLD', None, self.threshold, None),
                      ('DETECT_SEASONALITY', self.detect_seasonality, None, None),
                      ('ALPHA', None, self.alpha, None),
                      ('EXTRAPOLATION', self.extrapolation, None, None),
                      ('PERIODS', self.periods, None, None),
                      ('SEED', self.random_state, None, None),
                      ('N_ESTIMATORS', self.n_estimators, None, None),
                      ('MAX_SAMPLES', self.max_samples, None, None),
                      ('BOOTSTRAP', self.bootstrap, None, None),
                      ("CONTAMINATION", None, self.contamination, None),
                      ('MINPTS', self.minpts, None, None),
                      ('RADIUS', None, self.eps, None),
                      ('THREAD_RATIO', None, self.thread_ratio, None)]

        try:
            if self._disable_hana_execution or check_pal_function_exist(conn,
                                                                        '%OUTLIERDETECTIONFORTIMESERIES%',
                                                                        like=True):
                self._call_pal_auto(conn,
                                    'PAL_OUTLIER_DETECTION_FOR_TIME_SERIES',
                                    data_,
                                    ParameterTable().with_data(param_rows),
                                    *outputs)
            else:
                msg = 'The version of your SAP HANA does not support the outlier detection for time series!'
                logger.error(msg)
                raise ValueError(msg)
        except dbapi.Error as db_err:
            logger.exception(str(db_err))
            try_drop(conn, outputs)
            raise
        except pyodbc.Error as db_err:
            logger.exception(str(db_err.args[1]))
            try_drop(conn, outputs)
        self.stats_ = conn.table(stats_tbl)
        self.metrics_ = conn.table(metrics_tbl)
        res_df = conn.table(res_tbl)
        if not self._disable_hana_execution:
            if not self.is_index_int:
                res_cols = res_df.columns
                res_int = res_df.rename_columns({res_cols[0]:'ID_RESULT'})
                data_int = data.add_id('ID_DATA', ref_col=key)
                res_df = res_int.join(data_int, 'ID_RESULT=ID_DATA').select(key, res_cols[1], res_cols[2], res_cols[3], res_cols[4])
        return res_df
