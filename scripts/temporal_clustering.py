import pandas as pd

import logging
logger = logging.getLogger(__name__)

# check if module is installed
from importlib.util import find_spec
if find_spec('tsam') is None:
    raise ModuleNotFoundError("Optional dependency 'tsam' not found."
                              "Install via 'pip install tsam'")

import tsam.timeseriesaggregation as tsam

import numpy as np

def prepare_timeseries(n, normed):
    """
    returns time dependent data to determinate typcial timeseries
    """

    timeseries_df = pd.DataFrame(index=n.snapshots)
    
    for component in n.all_components:
        pnl = n.pnl(component)
        for key in pnl.keys():
            if not pnl[key].empty:
                timeseries_df = pd.concat([timeseries_df, pnl[key]], axis=1)

        if normed:
            timeseries_agg = timeseries_df / timeseries_df.max().replace(0,1)
        else:
            timeseries_agg = timeseries_df

    # consistency check
    to_drop = timeseries_agg.columns[timeseries_agg.isna().sum()!=0]
    if not to_drop.empty:
        logger.warning("There are nan values which are droped in the following columns: \n {}".format(to_drop))
        timeseries_agg.drop(to_drop, axis=1, inplace=True)
    to_drop = timeseries_agg.columns[timeseries_agg.columns.duplicated()]
    if not to_drop.empty:
        logger.warning("There are duplicated columns which are dropped : \n {}".format(to_drop))
        timeseries_agg.drop(to_drop, axis=1, inplace=True)

    return timeseries_agg 

def overwrite_time_dependent(n, df_t):
    """
    overwrite time dependent data of pypsa network according to typical time
    series of tsam module
    """
    for component in n.all_components:
            pnl = n.pnl(component)
            for key in pnl.keys():
                if not pnl[key].empty:
                    pnl[key] = df_t.reindex(columns= pnl[key].columns)

def aggregate_snapshots(n, n_periods=12, hours=24, normed=True, solver="glpk",
                        extremePeriodMethod="None", clusterMethod='hierarchical',
                        predefClusterOrder=None, overwrite_time_dfs=True):
    """
    this function aggregates the snapshots of the pypsa Network to a number of
    typical periods (n_periods) with a given length in hours (hours).
    The mapping from the original timeseries to the aggregated typical periods
    is saved in n.cluster

    Default is 12 typical days with hierachical clustering and without
    any extremePeriodMethod.

    Parameters
    ----------
    n :                 pypsa.Network
    n_periods:          int
                        number of typical periods
    hours:              int
                        hours per period
    extremePeriodMethod: {'None','append','new_cluster_center',
                           'replace_cluster_center'}, default: 'None'
                        Method how to integrate extreme periods into to the
                        typical period profiles.
                        None: No integration at all.
                        'append': append typical Periods to cluster centers
                        'new_cluster_center': add the extreme period as additional cluster
                             center. It is checked then for all Periods if they fit better
                            to the this new center or their original cluster center.
                        'replace_cluster_center': replaces the cluster center of the
                            cluster where the extreme period belongs to with the periodly
                            profile of the extreme period. (Worst case system design)
    clusterMethod:      {'averaging', 'k_medoids', 'k_means', 'hierarchical'},
                        default: 'hierachical'
    predefClusterOrder: list or array (default: None)
                        Instead of aggregating a time series, a predefined
                        grouping is taken which is given by this list.
    overwrite_time_dfs: Bool (default:True), if set to True, time-dependent
                        attributes in pypsa are replaced by typical periods from
                        tsam module


    Returns
    -------


    """


    # create pandas dataframe with all time-dependent data of the pypsa network
    timeseries_df = prepare_timeseries(n, normed)

    logger.info(("Aggregate snapshots to {} periods with {} hours using "
                 "cluster method: {}, extreme period method: {}"
                .format(n_periods, hours, clusterMethod, extremePeriodMethod)))

    # get typical periods
    n, timeseries_clustered = aggregate_timeseries(n, timeseries_df, n_periods, hours, extremePeriodMethod,
                                                                normed, clusterMethod, solver, predefClusterOrder)



    # set time dependent data according to typical tsam time series
    if overwrite_time_dfs:
        overwrite_time_dependent(n, timeseries_clustered)

    return n

def aggregate_timeseries(n, timeseries_df, n_periods, hours, extremePeriodMethod,
                         normed, clusterMethod, solver_name, predefClusterOrder):

    """
    aggregate timeseries with tsam module to a typical number of periods
    (n_periods) with each a lenght of hours
    Code adapted from Endogenous learning for green hydrogen in a sector-coupled energy model for Europe, Zeyen at al.
    """

    logger.info(f"Aggregating time series to {n_periods} segments with {hours} hours and {clusterMethod} method.")
    try:
        import tsam.timeseriesaggregation as tsam
    except ImportError:
        raise ModuleNotFoundError(
            "Optional dependency 'tsam' not found." "Install via 'pip install tsam'"
        )
    
    p_max_pu_norm = n.generators_t.p_max_pu.max()
    p_max_pu = n.generators_t.p_max_pu / p_max_pu_norm

    load_norm = n.loads_t.p_set.max()
    load = n.loads_t.p_set / load_norm

    inflow_norm = n.storage_units_t.inflow.max()
    inflow = n.storage_units_t.inflow / inflow_norm

    raw = pd.concat([p_max_pu, load, inflow], axis=1, sort=False)

    agg = tsam.TimeSeriesAggregation(
        timeseries_df, #raw,
        noTypicalPeriods=n_periods,
        extremePeriodMethod=extremePeriodMethod,
        rescaleClusterPeriods=False,
        hoursPerPeriod=hours,
        clusterMethod=clusterMethod,
        solver=solver_name,
        predefClusterOrder=predefClusterOrder,
    )

    clustered = agg.createTypicalPeriods()
    map_snapshots_to_periods = agg.indexMatching()
    map_snapshots_to_periods["day_of_year"] = (map_snapshots_to_periods.index - map_snapshots_to_periods.index[0]).days + 1
    cluster_weights = agg.clusterPeriodNoOccur
    clusterCenterIndices= agg.clusterCenterIndices


    # pandas Day of year starts at 1, clusterCenterIndices at 0
    new_snapshots = map_snapshots_to_periods[(map_snapshots_to_periods
                                                .day_of_year-1).isin(clusterCenterIndices)]
    new_snapshots["weightings"] = new_snapshots["PeriodNum"].map(cluster_weights).astype(float)
    clustered.set_index(new_snapshots.index, inplace=True)

    # last hour of typical period
    last_hour = new_snapshots[new_snapshots["TimeStep"]==hours-1]
    # first hour
    first_hour = new_snapshots[new_snapshots["TimeStep"]==0]

    # add typical period name and last hour to mapping original snapshot-> typical
    map_snapshots_to_periods["RepresentativeDay"] = map_snapshots_to_periods["PeriodNum"].map(last_hour.set_index(["PeriodNum"])["day_of_year"].to_dict())
    map_snapshots_to_periods["last_hour_RepresentativeDay"] = map_snapshots_to_periods["PeriodNum"].map(last_hour.reset_index().set_index(["PeriodNum"])["snapshot"].to_dict())
    map_snapshots_to_periods["first_hour_RepresentativeDay"] = map_snapshots_to_periods["PeriodNum"].map(first_hour.reset_index().set_index(["PeriodNum"])["snapshot"].to_dict())
    n.cluster = map_snapshots_to_periods

    n.set_snapshots(new_snapshots.index)
    n.snapshot_weightings = n.snapshot_weightings.mul(new_snapshots.weightings, axis=0)
    if normed:
        clustered[load.columns] = clustered[load.columns] * load_norm
        clustered[p_max_pu.columns] = clustered[p_max_pu.columns] * p_max_pu_norm
        clustered[inflow.columns] = clustered[inflow.columns] * inflow_norm



    return n, clustered