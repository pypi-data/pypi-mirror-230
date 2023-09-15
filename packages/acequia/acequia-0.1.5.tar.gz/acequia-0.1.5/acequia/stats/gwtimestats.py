
from collections import OrderedDict
import warnings
import numpy as np
from pandas import DataFrame, Series
import pandas as pd

from .. import gwseries
from .utils import maxfrq, ts1428

def gwtimestats(ts,ref=None,name=None):
    """Return table of groundwater head time series statistics

    Parameters
    ----------
    ts : pd.Series, aq.GwSeries
        Groundwater head time series
    ref : ['datum','surface','mp'], optional, default 'datum'
        Reference level vfor groundwater heads
    name : str, optional
        Groundwater heads series name

    Returns
    -------
    pd.DataFrame
    """

    gwstats = GwTimeStats(ts, ref=ref, name=name)
    return gwstats.stats()


class GwTimeStats:
    """ Return descriptive statistics of groundwater heads time series

    Parameters
    ----------
    ts : pd.Series, aq.GwSeries
        timeseries with groundwater head measurments

    ref : str, ['datum','surface'], optinal
        reference level for measurements

    name : str, optional
        ground water heads series name

    Examples
    --------
    ts = <valid groundwater heads series of GwSeries object>
    tsr = aq.TimeStats(ts)
    tsr.stats()

    Notes
    -----
    Custom function aq.timestats(ts) returns TimeStats.stats() directly.

    """

    def __init__(self, ts, ref=None, name=None):
        """Return TimeStats object"""

        self._ts = ts
        self._name = name


        if isinstance(self._ts,pd.Series):

            self._heads = self._ts
            if ref is not None:
                msg = (f'heads series is type pd.Series, ref={ref} '
                    f'is ignored')
                warnings.warn(msg)
                self._ref = ref

            if self._name is None: 
                self._name = self._ts.name

        if isinstance(self._ts,gwseries.GwSeries):

            self._ref = self._ts._validate_reference(ref)
            self._heads = self._ts.heads(ref=self._ref)

            if self._name is None:
                self._name = self._ts.name()

        if self._name is None:
            self._name = 'series'


    def stats(self):
        """Return time series desciptive statistics

        Returns
        -------
        pd.Dataframe

        """

        heads = self._heads
        stats = Series(name=self._name,dtype='object')

        if not heads.empty:
            stats['firstdate'] = heads.index.min().date()
            stats['lastdate'] = heads.index.max().date()
            stats['minyear'] = heads.index.min().year
            stats['maxyear'] = heads.index.max().year
            stats['yearspan'] = stats['maxyear']-stats['minyear']+1
            stats['nyears'] = len(set(heads.index.year))
            stats['maxfrq'] = maxfrq(heads)
            stats['mean'] = round(heads.mean(),2)
            stats['median'] = round(heads.median(),2)
            q05 = heads.quantile(q=0.05)
            q95 = heads.quantile(q=0.95)
            stats['q05'] = round(q05,2)
            stats['q95'] = round(q95,2)
            stats['dq0595'] = round(q95-q05,2)

        else:

            stats['firstdate'] = np.nan
            stats['lastdate'] = np.nan
            stats['minyear'] = np.nan
            stats['maxyear'] = np.nan
            stats['yearspan'] = np.nan
            stats['nyears'] = np.nan
            stats['maxfrq'] = np.nan
            stats['mean'] = np.nan
            stats['median'] = np.nan
            q05 = np.nan
            q95 = np.nan
            stats['q05'] = np.nan
            stats['q95'] = np.nan
            stats['dq0595'] = np.nan

        self._stats = stats
        return self._stats

