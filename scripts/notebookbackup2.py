#import pypsa
import yaml
#import cartopy
#import sys
import re
#import os

import pandas as pd
import numpy as np
#import geopandas as gpd
import xarray as xr
#import cartopy.crs as ccrs
import matplotlib.pyplot as plt
#import matplotlib.cm as cm
import matplotlib as mpl

#from itertools import product
#from matplotlib.lines import Line2D
#from matplotlib.patches import FancyArrowPatch
#import matplotlib.patches as mpatches
from matplotlib.transforms import Bbox

#from vresutils.costdata import annuity

PATH = "co2_spatial_btl_biochar_heat_seg/"

#sys.path.append(os.path.join(PATH, ""))
#sys.path.insert(0, '/plot_temporal/')
from plot_summary import rename_techs

plt.style.use(["seaborn-v0_8-whitegrid"]) #, "matplotlibrc"])
xr.set_options(display_style="html")

%matplotlib inline
plt.style.available
CLUSTERS = 37
LV_OPTS = "3H-T-H-B-I-A-solar+p3-dist1-cb29.01ex0"
OUTPUT = PATH
slack = "0.05"
MAIN_SCENARIOS = PATH + f"allCC_slack{slack}/"
MINZERO_SCENARIOS = PATH + f"minzeroCC_slack{slack}/"
MAXZERO_SCENARIOS = PATH + f"maxzeroCC_slack{slack}/"
SEG_SCENARIOS = PATH + "/"
BASE_SCENARIOS = PATH + "base/"
# LV_SCENARIOS = PATH + "results/20221227-lv"
# ONW_SCENARIOS = PATH + "results/20221227-onw"
# GAS_SCENARIOS = PATH + "results/20221227-gas"
# IMP_SCENARIOS = PATH + "results/20221227-import"
# SHP_SCENARIOS = PATH + "results/20221227-shipping"
# COST_SCENARIOS = PATH + "results/20221227-costs"

# SPACE_SCENARIOS = PATH + "results/20221227-spatial"
# OLD_SCENARIOS = "../workflows-rev0/pypsa-eur-sec/results/20211218-181-h2"
def parse_index(c, with_resolution=False):

    clusters = c[0]
    opt = c[1]
    planning_horizon = c[2]
    # opt = c[2]
    # planning_horizon = c[3]

    match = re.search(r"onwind\+p([0-9.]*)", c[2])
    onw = 100.0 if match is None else 100 * float(match.groups()[0])

    h2 = "no H2 grid" if "noH2network" in c[2] else "H2 grid"

    to_return = (clusters, opt[0:1], planning_horizon)

    if with_resolution:
        match = c[3:5]
        to_return += (match[0],)

    return to_return

def rename_techs_tyndp(tech):
    # if "CHP CC" in tech:
    #     print("CHP CC:", tech)
    tech = rename_techs(tech)
    if "heat pump" in tech or "resistive heater" in tech:
        return "power-to-heat"
    elif tech in ["H2 Electrolysis"]:  # , "H2 liquefaction"]:
        return "power-to-hydrogen"
    # elif "H2 pipeline" in tech:
    #     return "H2 pipeline"
    # elif tech == "H2":
    #     return "H2 storage"
    elif tech in ["OCGT", "solid biomass CHP", "CHP", "gas boiler", "H2 Fuel Cell"]:
        return "gas-to-power/heat"
    elif "solar" in tech:
       return "solar"
    # elif tech in ["Fischer-Tropsch", "methanolisation"]:
    #     return "power-to-liquid"
    elif tech in ["solid biomass transport", "biomass boiler"]:
        return "biomass"
    elif tech in ["H2", "H2 pipeline", "SMR", "H2 Store"]:
        return "H2"
    elif "co2 biochar" in tech:
        return "biochar"
    elif "co2 afforestation" in tech:
        return "afforestation"
    elif tech in ["process emissions CC", "solid biomass for industry CC", "gas for industry CC"]:
        return "point source CC"
    elif tech == "solid biomass CHP CC":
        # print("BECC:",tech)
        return "BECC"
    # elif "SMR" in tech:
    #     return tech.replace("SMR", "steam methane reforming")
    # elif "DAC" in tech:
    #     return "direct air capture"
    # elif "CC" in tech or "sequestration" in tech:
    #     return "carbon capture"
    elif tech == "oil" or tech == "gas" or tech=="oil primary":
        return "fossil oil and gas"
    elif "wind" in tech:
        return "wind"
    elif tech == "rural gas boiler":
        return "gas boiler"
    elif tech== "EW store":
        return "EW"
    elif tech== "perennials store":
        return "perennials"
    else:
        return tech
preferred_order = pd.Index(
    [
        "transmission lines",
        "electricity distribution grid",
        "fossil oil and gas",
        "hydroelectricity",
        "hydro reservoir",
        "run of river",
        "pumped hydro storage",
        "solid biomass",
        "biogas",
        "onshore wind",
        "offshore wind",
        "offshore wind (AC)",
        "offshore wind (DC)",
        "solar PV",
        "solar thermal",
        "solar rooftop",
        "solar",
        "building retrofitting",
        "ground heat pump",
        "air heat pump",
        "heat pump",
        "resistive heater",
        "power-to-heat",
        "gas-to-power/heat",
        "CHP",
        "OCGT",
        "gas boiler",
        "gas",
        "natural gas",
        "helmeth",
        "methanation",
        "power-to-gas",
        "power-to-hydrogen",
        "H2 pipeline",
        "H2 liquefaction",
        "H2 storage",
        "hydrogen storage",
        "power-to-liquid",
        "battery storage",
        "hot water storage",
        "CO2 sequestration",
        "CCS",
        "carbon capture and sequestration",
        "DAC",
        "direct air capture",
    ]
)
with open(PATH + "config.base_s_39__24h10segp-T-H-B-I-A_2050.yaml") as file:
    config = yaml.safe_load(file)
tech_colors = config["plotting"]["tech_colors"]
tech_colors["battery electric vehicles"] = tech_colors["BEV charger"]
tech_colors["other"] = "#454545"
tech_colors["building heat demand"] = tech_colors["heat"]
tech_colors["ambient heat"] = tech_colors["heat pump"]
tech_colors["residential electricity demand"] = "#72709c"
tech_colors["industry electricity demand"] = tech_colors["electricity"]
tech_colors["hydrogen demand"] = tech_colors["land transport fuel cell"]
tech_colors["agriculture machinery"] = tech_colors["land transport fuel cell"]
#tech_colors["methane demand"] = tech_colors["helmeth"]
tech_colors["liquid hydrocarbon demand"] = tech_colors["kerosene for aviation"]
tech_colors["aviation fuels"] = tech_colors["kerosene for aviation"]
tech_colors["shipping fuels"] = tech_colors["shipping methanol"]
tech_colors["biomass demand"] = tech_colors["biogas"]
tech_colors["biogas upgrading"] = tech_colors["biogas"]
tech_colors["hydrogen for industry"] = tech_colors["H2 for industry"]
tech_colors["hydrogen-to-power/heat"] = tech_colors["gas-to-power/heat"]
tech_colors["hydrogen for land transport"] = "#8487e8"
tech_colors["fossil oil and gas"] = tech_colors["oil"]
tech_colors["power-to-hydrogen"] = tech_colors["H2 Electrolysis"]
tech_colors["carbon capture"] = tech_colors["CO2 sequestration"]
tech_colors["steam methane reforming"] = tech_colors["SMR"]
tech_colors["steam methane reforming CC"] = tech_colors["SMR"]
tech_colors["direct air capture"] = tech_colors["DAC"]
tech_colors["wind"] = tech_colors["offshore wind"]
tech_colors["biochar"] = tech_colors["co2 biochar"]
tech_colors["afforestation"] = tech_colors["co2 afforestation"]
tech_colors["point source CC"] = tech_colors["onshore wind"]
tech_colors["BECC"] = tech_colors["solar rooftop"]

def load_main(
    scenarios=None, clusters=None, rename=True, with_resolution=False, with_space=False
):

    if scenarios is None:
        scenarios = MAIN_SCENARIOS

    if clusters is None:
        clusters = CLUSTERS

    #horizon = "2030" if "rev0" in scenarios else "2050"

    costs = pd.read_csv(
        scenarios + f"csvs/costs.csv", header=[0, 1, 2, 3], index_col=[0, 1, 2]
    )
    LV_OPTS = "base_s_39__24h10segp-T-H-B-I-A_2050"
    # costs = costs.xs(LV_OPTS, level="opt", axis=1)

    names = ["clusters", "opt", "planning_horizon"]
    if with_resolution:
        names += ("res",)

    costs.columns = pd.MultiIndex.from_tuples(
        [parse_index(c, with_resolution) for c in costs.columns], names=names
    )

    if not with_space:
        costs = costs.xs(str(clusters), level="clusters", axis=1)

    df = costs.groupby(level=2).sum().div(1e9)

    if rename:
        df = df.groupby(df.index.map(rename_techs_tyndp)).sum()

    to_drop = df.index[df.max(axis=1).fillna(0.0) < 1.2]
    print("to drop:", to_drop)
    df.drop(to_drop, inplace=True)

    order = preferred_order.intersection(df.index).append(
        df.index.difference(preferred_order)
    )
    df = df.loc[order]

    if "-imp" in scenarios:
        # imports for methanol, kerosene and naphtha at 120 €/MWh
        print("add import costs")
        df.loc["green e-fuel imports"] = (1026.64 + 546.36) * 120e6 / 1e9  # bn€/a
        tech_colors["green e-fuel imports"] = "#46caf0"

    return df
def plot_time_diff(
    df,
    reference,
    legend=False,
    label="cost",
    unit="bn€/a",
    scaler=50,
    threshold=False,
    label_scaler=15,
    rename=True,
    ylim=None,
):
    ref = df[reference]

    df = (df.T - df[reference]).drop(reference).T

    df.columns = [f"{d}" for d in df.columns]

    # fig, ax = plt.subplots(1, 1, figsize=(6, 3.4))
    fig, ax = plt.subplots(1, 1, figsize=(4, 3))

    if threshold:
        to_drop = df.index[df.abs().max(axis=1).fillna(0.0) < threshold]
        df.drop(to_drop, inplace=True)

    #ax.axhline(1, zorder=-1, alpha=0.1, linewidth=35, color="darkslategray")
    left = "reduced"
    right= "increased"
    # if label == "co2":
    #     left = "captured"
    #     right = "emitted"
    # if label == "co2 stored":
    #     left = "sequestered"
    #     right = "captured"
    df.round(1).T.plot.barh(
        ax=ax,
        stacked=True,
        color=tech_colors,
        xlabel=f"{left}"
        + r" $\leftarrow$ "
        + f"{label} [{unit}]"
        + r" $\rightarrow$ "
        + f"{right}",
        legend=legend,
    )
    ax.axvline(x=0, color="grey")
    net = df.sum()
    # ref = ref.xs('2', level="opt", axis=1)
    rel = df.sum() / ref.sum() * 100

    netcolor = "darkslategrey"
    # ax.scatter(net.values, net.index, s=10, c=netcolor, alpha=0.6, edgecolor="none")
    
    xmax = df[df > 0].sum().max()
    label_x = xmax * 1.05
    label_y_len = np.arange(len(net))
    label_y = dict(zip(net.index, label_y_len))
    ax.scatter(net.values, label_y_len, s=50, c="red", alpha=0.8, edgecolor="none")
    for x, y in net.items():
        #print(x, y, rel[x])
        ax.annotate(
            f"{y:.1f} | {rel[x]:.1f}%",
            (y, label_y[x]),
            xytext=(label_x, label_y[x]),
            ha = "left", va="center",
            # textcoords="offset points",
            color=netcolor,
            fontsize=9,
            bbox=dict(fc="0.85", boxstyle="square,pad=0.1"),
        )
        # ax.annotate(
        #     f"{y:.1f} | {rel[x]:.2f}%",
        #     (y, x),
        #     xytext=(-12, 13),
        #     textcoords="offset points",
        #     color=netcolor,
        #     fontsize=9,
        #     bbox=dict(fc="0.85", boxstyle="square,pad=0.1"),
        # )

    plt.grid(axis="x")

    if ylim is None:
        ylim = max(-df.where(df < 0).sum().min(), df.where(df > 0).sum().max())
        ylim = np.ceil(ylim / scaler) * scaler

    plt.xlim([df[df < 0].sum().min()-5, df[df > 0].sum().max()+5])
    print([df[df < 0].sum().min()-5, df[df > 0].sum().max()+5])
    #plt.ylim([-0.5, 5.8])
    plt.ylabel("")
    for bars in ax.containers:
        labels = [
            f"{abs(v):.0f}" if abs(v) > ylim / label_scaler else ""
            for v in bars.datavalues
        ]
        ax.bar_label(
            bars, labels=labels, label_type="center", color="#444444", fontsize=9
        )

    handles = [
        plt.Line2D(
            [],
            [],
            color=mpl.colors.to_rgba(netcolor, 0.5),
            marker=".",
            markeredgecolor="none",
            linestyle="None",
            markersize=10,
        )
    ]
    legend = ax.legend(
        handles,
        ["net difference"],
        labelcolor=netcolor,
        fontsize=10,
        frameon=False,
        loc=(1.05, -5),
    )
    ax.add_artist(legend)
    plt.tight_layout()

    # if legend:
    #     plt.legend(ncol=1, loc=(1.05, 0), labelspacing=0.2)
    if legend:
        plt.legend(ncol=2, loc=(0, 1.02), labelspacing=0.2)

    plt.savefig(
        OUTPUT + f"diff-{slack}-{label}.pdf", dpi=600, bbox_inches='tight'
        #bbox_inches=Bbox([[0, 0], [8.5, 3.4]]),
    )
grid ="2"
if "3" in PATH:
    grid="3"
if "seg" in PATH:
    grid = "7"
def get_new_index(filename, slack):
    vector = pd.read_csv(f"{PATH}/{filename}CC_slack{slack}/vector.csv", index_col=0)
    attributes = ["DAC", "BECC", "Prn", "aff", "EW", "char", "seq","PS CC"]
    vector = vector.T.drop_duplicates().T
    vector.rename(columns=dict(zip(vector.columns,attributes)), inplace=True)
    new_index = []
    for x in vector.index:
        labelsmax = ""
        labelsmin = ""
        labels = ""
        for y in range(len(vector.columns)):
            if vector.iloc[x,y] > 0:
                label = vector.columns[y] + ", "
                labelsmin = labelsmin + label
            elif vector.iloc[x,y] < 0:
                label = vector.columns[y] + ", "
                labelsmax = labelsmax + label
            else:
                label = ""
            labels = "min[" + labelsmin[:-2] + "] max[" + labelsmax[:-2] + "]"
        new_index.append(labels)
    keys = [str(x) for x in range(len(vector))]
    column_dict = dict(zip(keys,new_index))
    column_dict.update({"base":"base"})
    return column_dict
# df = (
#     load_main(SEG_SCENARIOS, clusters=39, with_resolution=True)
#     #.xs(grid, level="opt", axis=1)
#     .droplevel(["planning_horizon", "res"], axis=1)
# )
df = (
    load_main(BASE_SCENARIOS, clusters=39, with_resolution=True)
    .xs(grid, level="opt", axis=1)
    .droplevel("planning_horizon", axis=1)
)
df
plot_time_diff(df2,"2", rename=False, scaler=20, label_scaler=50, threshold=0.01, ylim=100, legend=True)
column_name = get_new_index("all", slack)
df = (
    load_main(MAIN_SCENARIOS, clusters=39, with_resolution=True)
    .xs(grid, level="opt", axis=1)
    .droplevel("planning_horizon", axis=1)
)
df.rename(columns=column_name, inplace=True)
# for col in df.columns:
#     df.rename(columns={col:"all"+col},inplace=True)
df2 = (
    load_main(MINZERO_SCENARIOS, clusters=39, with_resolution=True)
    .xs(grid, level="opt", axis=1)
    .droplevel("planning_horizon", axis=1)
)
column_name = get_new_index("minzero", slack)
df2.rename(columns=column_name, inplace=True)
# for col in df2.columns:
#     df2.rename(columns={col:"min"+col},inplace=True)
df3 = (
    load_main(MAXZERO_SCENARIOS, clusters=39, with_resolution=True)
    .xs(grid, level="opt", axis=1)
    .droplevel("planning_horizon", axis=1)
)
column_name = get_new_index("maxzero", slack)
df3.rename(columns=column_name, inplace=True)
# for col in df3.columns:
#     df3.rename(columns={col:"max"+col},inplace=True)
df_base = (
    load_main(BASE_SCENARIOS, clusters=39, with_resolution=True)
    .xs(grid, level="opt", axis=1)
    .droplevel("planning_horizon", axis=1)
)
column_name
df = pd.concat([df_base, df, df2, df3], axis=1)
df.fillna(0, inplace=True)
df
plot_time_diff(df,"base", rename=False, scaler=20, label_scaler=50, threshold=0.5, ylim=100, legend=True)
def load_main_supply_energy(
    scenarios=None,
    clusters=None,
    rename=True,
    with_resolution=False,
    with_space=False,
    carrier="co2",
):
    if scenarios is None:
        scenarios = MAIN_SCENARIOS

    if clusters is None:
        clusters = CLUSTERS

    #horizon = "2030" if "rev0" in scenarios else "2050"

    df = pd.read_csv(
        scenarios + "csvs/supply_energy.csv", index_col=[0, 1, 2], header=[0, 1, 2, 3]
    )

    co2_carriers = ["co2", "co2 stored", "process emissions"]
    if carrier == "energy":
        carrier = [i for i in df.index.levels[0] if i not in co2_carriers]

    df = df.loc[carrier].groupby(level=2).sum().div(1e6)  # TWh / MtCO2
    df.index = [
        i[:-1]
        if ((i not in ["co2", "NH3", "H2"]) and (i[-1:] in ["0", "1", "2", "3", "4"]))
        else i
        for i in df.index
    ]

    #df = df.xs(horizon, level="planning_horizon", axis=1)

    names = ["clusters", "opt", "planning_horizon"]
    if with_resolution:
        names += ("res",)
    print(df.head(1))
    print([parse_index(c, with_resolution) for c in df.columns])
    df.columns = pd.MultiIndex.from_tuples(
        [parse_index(c, with_resolution) for c in df.columns], names=names
    )

    if not with_space:
        df = df.xs(str(clusters), level="clusters", axis=1)

    if rename or callable(rename):
        func = rename if callable(rename) else rename_techs_tyndp
        df = df.groupby(df.index.map(func)).sum()

    to_drop = df.index[df.abs().max(axis=1).fillna(0.0) < 10]
    df.drop(to_drop, inplace=True)

    order = preferred_order.intersection(df.index).append(
        df.index.difference(preferred_order)
    )
    df = df.loc[order]

    if "-imp" in scenarios and carrier == "energy":
        # imports for methanol, kerosene and naphtha
        df.loc["green e-fuel imports"] = 1026.64 + 546.36  # TWh
        tech_colors["green e-fuel imports"] = "#46caf0"

    return df
df = (
    load_main_supply_energy(
        MAIN_SCENARIOS, carrier=["co2"], rename=True, clusters=39, with_resolution=True
    )
    .xs(grid, level="opt", axis=1)
    .droplevel(["planning_horizon"], axis=1)
)
# for col in df.columns:
#     df.rename(columns={col:"all"+col},inplace=True)
column_name = get_new_index("all", slack)
df.rename(columns=column_name, inplace=True)
df2 = (
    load_main_supply_energy(
        MINZERO_SCENARIOS, carrier=["co2"], rename=True, clusters=39, with_resolution=True
    )
    .xs(grid, level="opt", axis=1)
    .droplevel(["planning_horizon"], axis=1)
)
# for col in df2.columns:
#     df2.rename(columns={col:"min"+col},inplace=True)
column_name = get_new_index("minzero", slack)
df2.rename(columns=column_name, inplace=True)
df3 = (
    load_main_supply_energy(
        MAXZERO_SCENARIOS, carrier=["co2"], rename=True, clusters=39, with_resolution=True
    )
    .xs(grid, level="opt", axis=1)
    .droplevel(["planning_horizon"], axis=1)
)
column_name = get_new_index("maxzero", slack)
df3.rename(columns=column_name, inplace=True)
# for col in df3.columns:
#     df3.rename(columns={col:"max"+col},inplace=True)
df_base = (
    load_main_supply_energy(
        BASE_SCENARIOS, carrier=["co2"], rename=True, clusters=39, with_resolution=True)
    .xs(grid, level="opt", axis=1)
    .droplevel("planning_horizon", axis=1)
)
df = pd.concat([df_base, df, df2, df3], axis=1)
df.fillna(0, inplace=True)
df = abs(df)
df_unique = df.round(0).T.drop_duplicates().T
df.sum()
plot_time_diff(
    df_unique,
    "base",
    scaler=50,
    label_scaler=15,
    threshold=0.1,
    label="co2",
    unit=r"MtCO2",
    ylim=600,
)
df = (
    load_main_supply_energy(
        MAIN_SCENARIOS, carrier=["co2 stored"], rename=True, clusters=39, with_resolution=True
    )
    .xs(grid, level="opt", axis=1)
    .droplevel(["planning_horizon"], axis=1)
)
column_name = get_new_index("all", slack)
df.rename(columns=column_name, inplace=True)
# for col in df.columns:
#     df.rename(columns={col:"all"+col},inplace=True)
df2 = (
    load_main_supply_energy(
        MINZERO_SCENARIOS, carrier=["co2 stored"], rename=True, clusters=39, with_resolution=True
    )
    .xs(grid, level="opt", axis=1)
    .droplevel(["planning_horizon"], axis=1)
)
column_name = get_new_index("minzero", slack)
df2.rename(columns=column_name, inplace=True)
# for col in df2.columns:
#     df2.rename(columns={col:"min"+col},inplace=True)
df3 = (
    load_main_supply_energy(
        MAXZERO_SCENARIOS, carrier=["co2 stored"], rename=True, clusters=39, with_resolution=True
    )
    .xs(grid, level="opt", axis=1)
    .droplevel(["planning_horizon"], axis=1)
)
column_name = get_new_index("maxzero", slack)
df3.rename(columns=column_name, inplace=True)
# for col in df3.columns:
#     df3.rename(columns={col:"max"+col},inplace=True)

df_base = (
    load_main_supply_energy(BASE_SCENARIOS, carrier=["co2 stored"], rename=True, clusters=39, with_resolution=True)
    .xs(grid, level="opt", axis=1)
    .droplevel("planning_horizon", axis=1)
)

df = pd.concat([df_base, df, df2, df3], axis=1)
df.fillna(0, inplace=True)
df = abs(df)
df_unique = df.round(0).T.drop_duplicates().T
df_unique
plot_time_diff(
    df_unique,
    "base",
    scaler=50,
    label_scaler=15,
    threshold=0.1,
    label="co2 stored",
    unit=r"MtCO2",
    ylim=600,
    legend=True
)
def load_main_capacities(
    scenarios=None,
    clusters=None,
    rename=True,
    with_resolution=False,
    with_space=False,
    merge=True,
):
    if scenarios is None:
        scenarios = MAIN_SCENARIOS

    if clusters is None:
        clusters = CLUSTERS

    horizon = "2030" if "rev0" in scenarios else "2050"

    df = pd.read_csv(
        scenarios + f"csvs/capacities.csv", header=[0, 1, 2, 3], index_col=[0, 1]
    )

    #df = df.xs(horizon, level="planning_horizon", axis=1)

    names = ["clusters", "opt", "planning_horizon"]
    if with_resolution:
        names += ("res",)

    df.columns = pd.MultiIndex.from_tuples(
        [parse_index(c, with_resolution) for c in df.columns], names=names
    )

    if not with_space:
        df = df.xs(str(clusters), level="clusters", axis=1)

    if rename:
        grouper = [
            df.index.get_level_values(0),
            df.index.get_level_values(1).map(rename_techs_tyndp),
        ]
        df = df.groupby(grouper).sum()

    to_drop = df.index[df.max(axis=1).fillna(0.0) < 10]
    df.drop(to_drop, inplace=True)

    twh = df.xs("stores", level=0).div(1e6)  # TWh

    to_drop = [
        #"CCS",
        "biogas",
        #"co2",
        "fossil oil and gas",
        #"solid biomass",
    ]
    twh.drop(twh.index.intersection(to_drop), inplace=True)

    gw = df.drop(["stores", "lines"]).div(1e3)  # GW

    if merge:
        gw = gw.groupby(level=1).sum()
        techs = gw.index
        kwargs = dict()
    else:
        techs = gw.index.levels[1]
        kwargs = dict(level=1)

    to_drop = [
        "fossil oil and gas",
        "transmission lines",
        #"DAC",
        #"direct air capture",
        "H2 pipeline",
        "H2 pipeline retrofitted",
        #"CCS",
        #"carbon capture" "biogas",
        "gas for industry",
        "hot water storage",
        #"solid biomass for industry",
        #"process emissions",
    ]
    gw.drop(techs.intersection(to_drop), **kwargs, inplace=True)

    return gw, twh
# gw, twh = load_main_capacities(TIME_SCENARIOS, clusters=39, with_resolution=True)
gw, twh = load_main_capacities(MAIN_SCENARIOS, clusters=39, with_resolution=True)


plt.plot(gw.loc["BECC"],gw.loc["afforestation"])
gw.loc[["BECC", "perennials"]].round(0).plot()
import numpy as np
import matplotlib.pyplot as plt
from scipy.spatial import ConvexHull

# Take BECC and perennials (shape: 2 × 26)
subset = gw.loc[["BECC", "perennials"]]

# Transpose to get 26 × 2 points
points = subset.T.to_numpy()

plt.figure()

# --- Hull with all points ---
hull_full = ConvexHull(points)
plt.plot(points[:, 0], points[:, 1], 'o', color="blue", label="n+1 points")
for simplex in hull_full.simplices:
    plt.plot(points[simplex, 0], points[simplex, 1], 'b-')

# --- Hull excluding one point ---
mask = np.ones(len(points), dtype=bool)
mask[10] = False  # remove point[10, :]
points_reduced = points[mask]

hull_reduced = ConvexHull(points_reduced)
plt.plot(points_reduced[:, 0], points_reduced[:, 1], 'o', color="red", label="n points")
for simplex in hull_reduced.simplices:
    plt.plot(points_reduced[simplex, 0], points_reduced[simplex, 1], 'r--')

# Highlight the removed point
plt.plot(points[10, 0], points[10, 1], 'ks', markersize=8, label="Excluded point")

plt.xlabel("BECC capacity [GW]")
plt.ylabel("Perennials capacity [GW]")
plt.title("Convex hull expansion")
plt.legend()
plt.savefig(f"{PATH}examplevolume.png", dpi=600, bbox_inches='tight')       
plt.show()

# ref = gw.iloc[:,6:]
# newdf = gw.iloc[:,:6].copy()
# for i in range(6):
#     newdf.iloc[:,i] = gw.iloc[:,i].T - ref.iloc[:,i] #(df.T - df[reference]).drop(reference).T
# #newdf.columns = newdf.columns.get_level_values(0)
# newdf.columns = [f"{c}-hourly\n{d}" for a,c,d in newdf.columns]
# newdf.sum(axis=1)/gw.iloc[:,:6].sum(axis=1)*100
# newdf.sum(axis=1)
# plot_time_diff(
#     newdf,
#     ref,
#     scaler=50,
#     label_scaler=15,
#     threshold=0.1,
#     label="capacity",
#     unit=r"GW",
#     ylim=200,
# )
def load_nodal_supply_energy(
    scenarios=None,
    clusters=None,
    group="location",
    carrier=None,
    rename=True
    # carrier_pos = ["co2 stored", "AC", "co2", "oil"]
):
    if scenarios is None:
        scenarios = MAIN_SCENARIOS

    if clusters is None:
        clusters = CLUSTERS
    
    if carrier is None:
        carrier = slice(None)

    #horizon = "2030" if "rev0" in scenarios else "2050"

    df = pd.read_csv(
        scenarios + "csvs/nodal_supply_energy.csv", index_col=[0, 1, 2,3], header=[0, 1, 2, 3]
    ) 
    if type(carrier) != slice:
        for car in carrier: 
            if car in ["co2 stored", "AC", "co2", "oil", "H2"]:
                new_values = df.loc[car, :, :, :].map(lambda x: x if x >= 0 else None).mul(-1).values
                df.loc[car, :, :, :] = new_values
            else:
                new_values = df.loc[car, :, :, :].map(lambda x: x if x <= 0 else None).values
                df.loc[car, :, :, :] = new_values 

    df_reset = df.reset_index()
    
    df_reset[['location', 'bus_carrier']] = df_reset['level_2'].str.split(pat=" ", n=1, expand=True)

    df_reset = df_reset.drop(columns=['level_2'])

    df_reset = df_reset.set_index(
    ['level_0', 'level_1', 'location', 'bus_carrier', 'level_3']
)


    if group:
        df = df_reset.loc[carrier].groupby("location").sum().div(1e6)
    else:
        df = df_reset.loc[carrier] #.groupby("location").sum().drop(columns="level_3").div(1e6)
        new_level3 = [i[:-1] 
                      if ((i not in ["co2", "NH3", "H2"]) and (i[-1:] in ["0", "1", "2", "3", "4"])) 
                      else i for i in df.index.levels[4]] 
        df = df.rename(index=dict(zip(df.index.levels[4],new_level3)), level=4)
        new_level3 = [i[2:] 
                      if ((i not in ["co2", "NH3", "H2"]) and  (i[:1] in ["0", "1", "2", "3", "4"])) 
                      else i for i in df.index.levels[3]] 
        df = df.rename(index=dict(zip(df.index.levels[3],new_level3)), level=3)
        df = df.droplevel(["bus_carrier"], axis=0)
        if rename or callable(rename):
            func = rename if callable(rename) else rename_techs_tyndp
            newname = [func(key) for key in df.index.levels[3]]
            df = df.rename(index=dict(zip(df.index.levels[3],newname)), level=3)
            to_drop = df.index[df.abs().max(axis=1).fillna(0.0) < 10]
            df.drop(to_drop, inplace=True)
        

    # df.index = [
    #     i[:-1]
    #     if ((i not in ["co2", "NH3", "H2"]) and (i[-1:] in ["0", "1", "2", "3", "4"]))
    #     else i
    #     for i in df.index
    # ]

  
    #.sum().div(1e6)  # TWh / MtCO2



    # #df = df.xs(horizon, level="planning_horizon", axis=1)

    # names = ["clusters", "opt", "planning_horizon"]
    # if with_resolution:
    #     names += ("res",)
    # print(df.head(1))
    # print([parse_index(c, with_resolution) for c in df.columns])
    # df.columns = pd.MultiIndex.from_tuples(
    #     [parse_index(c, with_resolution) for c in df.columns], names=names
    # )

    # if not with_space:
    #     df = df.xs(str(clusters), level="clusters", axis=1)

    # if rename or callable(rename):
    #     func = rename if callable(rename) else rename_techs_tyndp
    #     df = df.groupby(df.index.map(func)).sum()
    # print(df.head())
    # to_drop = df.index[df.abs().max(axis=1).fillna(0.0) < 10]
    # df.drop(to_drop, inplace=True)

    # order = preferred_order.intersection(df.index).append(
    #     df.index.difference(preferred_order)
    # )
    # df = df.loc[order]

    return df
df = (
    load_nodal_supply_energy(
        BASE_SCENARIOS, carrier=["co2 stored", "co2 afforestation", "co2 biochar", "perennials store", "co2"], group=None, clusters=39
    ).droplevel(["planning_horizon", "cluster", "opt"], axis=1)
    )
df2 = (
    load_nodal_supply_energy(
        BASE_SCENARIOS, carrier=slice(None), group=None, clusters=39
    ).droplevel(["planning_horizon", "cluster", "opt"], axis=1)
    )

carrier = slice(None)
if type(carrier) != slice:
    print("agfhls")
df.index.get_level_values("level_3").unique()
df2.index.get_level_values("level_3").unique()
values = df.loc["co2 stored", :, :, :].map(lambda x: x if x >= 0 else None).mul(-1).values
#[val*(-1) for val in values]
values

df_test =df.groupby(["level_0", "level_1", "location","level_3"]).sum()
df_test.index.levels[0]
df = (
    load_nodal_supply_energy(
        MAIN_SCENARIOS, carrier=["co2 stored", "co2 afforestation", "co2 biochar", "perennials store"], clusters=39
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)

)
column_name = get_new_index("all", slack)
df.rename(columns=column_name, inplace=True)

df2 = (
    load_nodal_supply_energy(
        MINZERO_SCENARIOS, carrier=["co2 stored", "co2 afforestation", "co2 biochar", "perennials store"], clusters=39
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)

)
column_name = get_new_index("minzero", slack)
df2.rename(columns=column_name, inplace=True)

df3 = (
    load_nodal_supply_energy(
        MAXZERO_SCENARIOS, carrier=["co2 stored", "co2 afforestation", "co2 biochar", "perennials store"], clusters=39, 
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)

)
column_name = get_new_index("maxzero", slack)
df3.rename(columns=column_name, inplace=True)

df_base = (
    load_nodal_supply_energy(
        BASE_SCENARIOS, carrier=["co2 stored", "co2 afforestation", "co2 biochar", "perennials store"], clusters=39, 
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)

)
df = pd.concat([df_base, df, df2, df3], axis=1)
df.fillna(0, inplace=True)

df
df_countries = df.drop(labels=["co2", "EU"])
fig, ax = plt.subplots(1, 1, figsize=(20, 4))

ax.set_xticks(np.arange(len(df_countries)))
ax.set_xticklabels(df_countries.index)
df_countries.plot(ax=ax, label=df_countries.columns)
ax.set_ylabel("captured CO2 [MtCO2] ")
ax.legend()
plt.tight_layout()

plt.savefig(
    OUTPUT + f"diff-{slack}-co2percountry.pdf", dpi=600, bbox_inches='tight'
    #bbox_inches=Bbox([[0, 0], [8.5, 3.4]]),
)

df1 = (
    load_nodal_supply_energy(
        MAIN_SCENARIOS, carrier=["co2 stored", "co2 afforestation", "co2 biochar", "perennials store", "EW", "co2 sequestered"], clusters=39, group=None,
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)
    # .xs(grid, level="opt", axis=1)
    #.droplevel(["planning_horizon"], axis=1)
)
column_name = get_new_index("all", slack)
df1.rename(columns=column_name, inplace=True)
# for col in df.columns:
#     df.rename(columns={col:"all"+col},inplace=True)
df =df1.groupby(["level_0", "level_1", "location","level_3"]).sum()
df2 = (
    load_nodal_supply_energy(
        MINZERO_SCENARIOS, carrier=["co2 stored", "co2 afforestation", "co2 biochar", "perennials store", "EW", "co2 sequestered"], clusters=39, group=None,
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)
    #.xs(grid, level="opt", axis=1)
    #.droplevel(["planning_horizon"], axis=1)
)
column_name = get_new_index("minzero", slack)
df2.rename(columns=column_name, inplace=True)
# for col in df2.columns:
#     df2.rename(columns={col:"min"+col},inplace=True)
df2 =df2.groupby(["level_0", "level_1", "location","level_3"]).sum()
df3 = (
    load_nodal_supply_energy(
        MAXZERO_SCENARIOS, carrier=["co2 stored", "co2 afforestation", "co2 biochar", "perennials store", "EW", "co2 sequestered"], clusters=39, group=None,
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)
    #.xs(grid, level="opt", axis=1)
    #.droplevel(["planning_horizon"], axis=1)
)
column_name = get_new_index("maxzero", slack)
df3.rename(columns=column_name, inplace=True)
# for col in df3.columns:
#     df3.rename(columns={col:"max"+col},inplace=True)
df3 =df3.groupby(["level_0", "level_1", "location","level_3"]).sum()
df_base = (
    load_nodal_supply_energy(
        BASE_SCENARIOS, carrier=["co2 stored", "co2 afforestation", "co2 biochar", "perennials store", "EW", "co2 sequestered"], clusters=39, group=None,
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)
    #.xs(grid, level="opt", axis=1)
    #.droplevel(["planning_horizon"], axis=1)
)
df_base =df_base.groupby(["level_0", "level_1", "location","level_3"]).sum()
df = pd.concat([df_base, df, df2, df3], axis=1)
df.fillna(0, inplace=True)
df1.xs(key="co2", level=2)
df1.index.levels[2]

linestyles = ['-', '--', '-.', ':']  

df_countries = df.drop(level="location", labels=["EU"]) #, "co2"])
df_countries = df_countries.groupby(["level_0", "level_1", "location","level_3"]).sum()
df_countries.index = df_countries.index.remove_unused_levels()

for key in df_countries.index.levels[3]:
    fig, ax = plt.subplots(1, 1, figsize=(20, 4))
    locations = df_countries.index.get_level_values("location").unique()

    df_slice = df_countries.xs(key, level=3)
    df_slice = df_slice.div(-1E6)
    df_slice = df_slice.sub(df_slice["base"], axis=0)
    
    for i, col in enumerate(df_slice.columns):
        style = linestyles[i % len(linestyles)] 
        df_slice[col].plot(ax=ax, linestyle=style, label=col)
    
    ax.set_xticks(np.arange(len(locations)))
    ax.set_xticklabels(locations, rotation=90)
    ax.set_ylabel("diff captured CO2 to base [MtCO2]")
    ax.legend(ncol=6, loc=(0, 1.15), labelspacing=0.2)
    ax.set_xlabel("")
    #ax.set_ylim(df_countries.min().min())
    plt.tight_layout()
    plt.title(key)
    plt.savefig(
        OUTPUT + f"diff-{slack}-co2percountry-{key}.pdf", dpi=600, bbox_inches='tight'
    )
    plt.close(fig)

df_countries.index.levels[3]
df_slice.sub(df_slice["base"], axis=0)
df_slice #.div(df_slice["base"], axis=0)
plot_time_diff(
    df.groupby("level_3").sum().div(1e6).mul(-1),
    "base",
    scaler=50,
    label_scaler=15,
    threshold=0.1,
    label="co2 captured",
    unit=r"MtCO2",
    ylim=600,
    legend=True
)
df = (
    load_nodal_supply_energy(
        MAIN_SCENARIOS, carrier=slice(None), clusters=39, group=None,
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)
    # .xs(grid, level="opt", axis=1)
    #.droplevel(["planning_horizon"], axis=1)
)
column_name = get_new_index("all", slack)
df.rename(columns=column_name, inplace=True)
df = df.groupby(["level_0", "level_1", "location","level_3"]).sum()
df2 = (
    load_nodal_supply_energy(
        MINZERO_SCENARIOS, carrier=slice(None), clusters=39, group=None,
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)
    #.xs(grid, level="opt", axis=1)
    #.droplevel(["planning_horizon"], axis=1)
)
column_name = get_new_index("minzero", slack)
df2.rename(columns=column_name, inplace=True)
df2 = df2.groupby(["level_0", "level_1", "location","level_3"]).sum()
df3 = (
    load_nodal_supply_energy(
        MAXZERO_SCENARIOS, carrier=slice(None), clusters=39, group=None,
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)
    #.xs(grid, level="opt", axis=1)
    #.droplevel(["planning_horizon"], axis=1)
)
column_name = get_new_index("maxzero", slack)
df3.rename(columns=column_name, inplace=True)
df3 = df3.groupby(["level_0", "level_1", "location","level_3"]).sum()

df_base = (
    load_nodal_supply_energy(
        BASE_SCENARIOS, carrier=slice(None), clusters=39, group=None,
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)
    #.xs(grid, level="opt", axis=1)
    #.droplevel(["planning_horizon"], axis=1)
)
df_base = df_base.groupby(["level_0", "level_1", "location","level_3"]).sum()
df = pd.concat([df_base, df, df2, df3], axis=1)
df.fillna(0, inplace=True)
plot_time_diff(
    df.groupby("level_3").sum().div(1e6).mul(-1),
    "base",
    scaler=50,
    label_scaler=15,
    threshold=0.1,
    label="total balance",
    unit=r"TW",
    ylim=600,
    legend=True
)
df = (
    load_nodal_supply_energy(
        MAIN_SCENARIOS, carrier=["co2 stored", "co2 afforestation", "co2 biochar", "perennials store", "EW", "co2 sequestered"], clusters=39, group=None,
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)
    # .xs(grid, level="opt", axis=1)
    #.droplevel(["planning_horizon"], axis=1)
)
column_name = get_new_index("all", slack)
df.rename(columns=column_name, inplace=True)
df = df.groupby(["level_0", "level_1", "location","level_3"]).sum()
df2 = (
    load_nodal_supply_energy(
        MINZERO_SCENARIOS, carrier=["co2 stored", "co2 afforestation", "co2 biochar", "perennials store", "EW", "co2 sequestered"], clusters=39, group=None,
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)
    #.xs(grid, level="opt", axis=1)
    #.droplevel(["planning_horizon"], axis=1)
)
column_name = get_new_index("minzero", slack)
df2.rename(columns=column_name, inplace=True)
df2 = df2.groupby(["level_0", "level_1", "location","level_3"]).sum()
df3 = (
    load_nodal_supply_energy(
        MAXZERO_SCENARIOS, carrier=["co2 stored", "co2 afforestation", "co2 biochar", "perennials store", "EW", "co2 sequestered"], clusters=39, group=None,
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)
    #.xs(grid, level="opt", axis=1)
    #.droplevel(["planning_horizon"], axis=1)
)
column_name = get_new_index("maxzero", slack)
df3.rename(columns=column_name, inplace=True)
df3 = df3.groupby(["level_0", "level_1", "location","level_3"]).sum()

df_base = (
    load_nodal_supply_energy(
        BASE_SCENARIOS, carrier=["co2 stored", "co2 afforestation", "co2 biochar", "perennials store", "EW", "co2 sequestered"], clusters=39, group=None,
    )
    .droplevel(["planning_horizon", "cluster", "opt"], axis=1)
    #.xs(grid, level="opt", axis=1)
    #.droplevel(["planning_horizon"], axis=1)
)
df_base = df_base.groupby(["level_0", "level_1", "location","level_3"]).sum()
df = pd.concat([df_base, df, df2, df3], axis=1)
df.fillna(0, inplace=True)
df_unique = df.groupby("level_3").sum().div(1e6).round(0).T.drop_duplicates().T
df_unique
plot_time_diff(
    df_unique.mul(-1),
    "base",
    scaler=50,
    label_scaler=15,
    threshold=0.1,
    label="CO2 capture",
    unit=r"MtCO2",
    ylim=50,
    legend=True
)
def get_df(slack, carriers):
    slack = slack
    MAIN_SCENARIOS = PATH + f"allCC_slack{slack}/"
    MINZERO_SCENARIOS = PATH + f"minzeroCC_slack{slack}/"
    MAXZERO_SCENARIOS = PATH + f"maxzeroCC_slack{slack}/"
    df = (
        load_nodal_supply_energy(
            MAIN_SCENARIOS, carrier=carriers, clusters=39, group=None,
        )
        .droplevel(["planning_horizon", "cluster", "opt"], axis=1)

    )
    column_name = get_new_index("all", slack)
    df.rename(columns=column_name, inplace=True)
    df =df.groupby(["level_0", "level_1", "location","level_3"]).sum()

    df2 = (
        load_nodal_supply_energy(
            MINZERO_SCENARIOS, carrier=carriers, clusters=39, group=None,
        )
        .droplevel(["planning_horizon", "cluster", "opt"], axis=1)

    )
    column_name = get_new_index("minzero", slack)
    df2.rename(columns=column_name, inplace=True)
    df2 =df2.groupby(["level_0", "level_1", "location","level_3"]).sum()

    df3 = (
        load_nodal_supply_energy(
            MAXZERO_SCENARIOS, carrier=carriers, clusters=39, group=None,
        )
        .droplevel(["planning_horizon", "cluster", "opt"], axis=1)

    )
    column_name = get_new_index("maxzero", slack)
    df3.rename(columns=column_name, inplace=True)
    df3 =df3.groupby(["level_0", "level_1", "location","level_3"]).sum()

    df_base = (
        load_nodal_supply_energy(
            BASE_SCENARIOS, carrier=carriers, clusters=39, group=None,
        )
        .droplevel(["planning_horizon", "cluster", "opt"], axis=1)

    )
    column_name = get_new_index("maxzero", slack)
    df_base.rename(columns=column_name, inplace=True)
    df_base =df_base.groupby(["level_0", "level_1", "location","level_3"]).sum()

    dfnew = pd.concat([df_base, df, df2, df3], axis=1)
    dfnew.fillna(0, inplace=True)
    return dfnew
slack_list = ["0.01", "0.03", "0.05"]
df = pd.DataFrame()
carriers = ["co2 stored", "co2 afforestation", "co2 biochar", "perennials store", "EW", "co2 sequestered"]
for slack in slack_list:
    df1 = get_df(slack, carriers).groupby("level_3").sum().div(1e6).mul(-1)
    dfbase = df1["base"]
    df2 = pd.concat([df1.iloc[:,1:]], keys=[slack], names=['slack'])
    df = pd.concat([df,df2])
dfdub = pd.DataFrame()
for col in df.columns:
    dfdub[col] = dfbase
dfbase = pd.concat([dfdub], keys=[0], names=['slack'])
df = pd.concat([dfbase, df])
df = df.reorder_levels(order=[1, 0])
slack_list.insert(0,"0")
x = [float(i)*100 for i in slack_list]    
df_co2_all = df.copy()
import pypsa
n = pypsa.Network()
n.import_from_netcdf(f"{PATH}base_s_39__750SEG-T-H-B-I-A_2050.nc")
df_co2_all = df.copy()
# df =df_co2_all.copy()
import matplotlib

latex_textwidth = 2*5.39049 #inches because matplotlib figsize is in inches
desired_fontsize = 10
final_figure_width = latex_textwidth
scaled_fontsize = (desired_fontsize/final_figure_width)*latex_textwidth
matplotlib.rcParams['font.size'] = str(scaled_fontsize)
matplotlib.rcParams['axes.labelsize'] = str(scaled_fontsize)
matplotlib.rcParams['axes.titlesize'] = str(scaled_fontsize)
golden = (1 + 5 ** 0.5) / 2

fig, ax = plt.subplots(1, len(df.index.levels[0].unique()), sharey=True, figsize=(final_figure_width,final_figure_width/golden) ,layout='constrained')
fig.supxlabel(f'budget increase [%]')
fig.supylabel('CO2 captured [MtCO2/year]')
#print("summed", summed_df)
for i in range(len(df.index.levels[0].unique())):
        idx = df.index.levels[0].unique()[i]
        ax[i].plot(x,df.loc[idx].min(axis=1), color="grey") #, marker="o")
        ax[i].plot(x,df.loc[idx].max(axis=1), color="grey") #, marker="o")
        
        ax[i].fill_between(x, df.loc[idx].min(axis=1), df.loc[idx].max(axis=1))
        for col in df.columns:                               
                ax[i].scatter(x, df.loc[(idx),col], marker="o",s=20, alpha=0.7, facecolor="grey", label="single solution" if (i==0 and counter) else "")
                counter = 0
        for idx2, style, color in zip(["DAC", "BECC"],["ox", "h1"], ["blue", "red"]):
                idxmax = df.loc[idx2].idxmax(axis=1)
                for ix, iy in zip(idxmax[1:],idxmax[1:].index):
                        ax[i].scatter(float(iy)*100, df.loc[(idx,iy),ix], marker=style[0],s=50, alpha=0.7, facecolor=color, label=f"max {idx2}" if (i==0 and iy=="0.01") else "")
        for idx2, style, color in zip(["afforestation", "co2 sequestered"],["so", "hv"], ["green", "black"]):      
                idxmin = df.loc[idx2].idxmin(axis=1)
                for ix, iy in zip(idxmin[1:],idxmin[1:].index):
                        ax[i].scatter(float(iy)*100, df.loc[(idx,iy),ix], marker=style[1],s=50, alpha=0.7, facecolor=color, label=f"min {idx2}" if (i==0 and iy=="0.01") else "")
        counter = 1

        ax[i].set_title(idx, pad=6+(i%2)*10)

        const = np.array([n.stores.e_nom_max.filter(like=idx).sum(), n.stores.e_nom.filter(like=idx).sum()])
        max_const = const[np.isfinite(const)].max()/1E6
        if idx == "co2 sequestered":
               max_const = 200.0
        if max_const > 0:
                # ax2 = ax[i].twinx()
                # print(df.loc[idx].max(axis=1).max(), max_const)
                max_perc = df.loc[idx].max(axis=1).max()/max_const
                # ax2.hlines(df.loc[idx].max(axis=1).max(), x[0], x[-1], colors="red", linestyles="--", label=f"{round(max_perc*100,2)}")
                # ax2.legend()
                if max_perc < 1:
                        colors = "blue"
                else:
                        colors = "red"
                hline = ax[i].hlines(df.loc[idx].max(axis=1).max(), x[0], x[-1], colors=colors, linestyles="--", label=f"{round(max_perc*100,2)} %")
                ax[i].legend(fontsize=8)
                hline.set_label("_")

fig.legend(ncols=5, loc='lower center', bbox_to_anchor=(0.5, -0.08))


plt.savefig(f"{PATH}CCslack_withminmax.png", dpi=600, bbox_inches='tight')        
plt.show()
dfminmax=pd.DataFrame()
for idx in ["DAC", "BECC"]:
    idxmax = df.loc[idx].idxmax(axis=1)
    for ix, iy in zip(idxmax[1:],idxmax[1:].index):
        dfmax = pd.DataFrame({f"max {idx} {iy}":df.loc[(slice(None),iy),ix].droplevel(1)})
        dfminmax = pd.concat([dfminmax, dfmax], axis=1)
for idx in ["afforestation", "co2 sequestered"]:
    idxmax = df.loc[idx].idxmin(axis=1)
    for ix, iy in zip(idxmax[1:],idxmax[1:].index):
        dfmax = pd.DataFrame({f"min {idx} {iy}":df.loc[(slice(None),iy),ix].droplevel(1)})
        dfminmax = pd.concat([dfminmax, dfmax], axis=1)
base = pd.DataFrame({"base":df.xs(key=0, level=1).iloc[:,0]})
dfminmax = pd.concat([base,dfminmax], axis=1)
dfminmax[dfminmax.columns[dfminmax.columns.str.contains("DAC|base")]]
df.xs(key="0.05", level=1).min(axis=1)
104/200
for idx in ["DAC", "BECC", "afforestation", "co2 sequestered"]: 
    plot_time_diff(
        dfminmax[dfminmax.columns[dfminmax.columns.str.contains(f"{idx}|base")]],
        "base",
        scaler=50,
        label_scaler=15,
        threshold=0.1,
        label=f"{idx} CO2 capture",
        unit=r"MtCO2",
        ylim=50,
        legend=True
    )
slack_list = ["0.01", "0.03", "0.05"]
df = pd.DataFrame()
carriers = ["AC", "low voltage", "oil", "solid biomass", "H2", "co2"]
for slack in slack_list:
    df12 = get_df(slack, carriers)
    df_co2 = df12.loc["co2"].sum()
    df12 = df12.drop(labels=["co2"], level=0)
    df12.loc[('co2','all','EU','co2 emissions'), :] = df_co2
    df1 = df12.groupby("level_3", sort=False).sum().div(1e6).mul(-1)
    dfbase = df1["base"]
    df2 = pd.concat([df1.iloc[:,1:]], keys=[slack], names=['slack'])
    df = pd.concat([df,df2])
dfdub = pd.DataFrame()
for col in df.columns:
    dfdub[col] = dfbase
dfbase = pd.concat([dfdub], keys=[0], names=['slack'])
df = pd.concat([dfbase, df])
df = df.reorder_levels(order=[1, 0])
slack_list.insert(0,"0")
x = [float(i)*100 for i in slack_list]   
df.index.levels[0]
df = df.drop(labels=["transmission lines", "nuclear", "hydroelectricity", "gas-to-power/heat", "BECC",
                      "biochar", "electricity", "industry electricity", "point source CC"])
df.index = df.index.remove_unused_levels()
to_drop = df.index[df.abs().max(axis=1).fillna(0.0) < 100]
labels = to_drop.get_level_values(0).to_list()
new_labels = [i for i in labels if labels.count(i)<len(x) ]
to_drop = to_drop.drop(new_labels, level=0)
df.drop(to_drop, inplace=True)
df.index = df.index.remove_unused_levels()

df.xs(key="0.05", level=1).min(axis=1)
df_co2
import matplotlib

latex_textwidth = 2*5.39049 #inches because matplotlib figsize is in inches
desired_fontsize = 10
final_figure_width = latex_textwidth
scaled_fontsize = (desired_fontsize/final_figure_width)*latex_textwidth
matplotlib.rcParams['font.size'] = str(scaled_fontsize)
matplotlib.rcParams['axes.labelsize'] = str(scaled_fontsize)
matplotlib.rcParams['axes.titlesize'] = str(scaled_fontsize)
golden = (1 + 5 ** 0.5) / 2

fig, ax = plt.subplots(1, len(df.index.levels[0].unique()), sharey=True, figsize=(final_figure_width,final_figure_width/golden) ,layout='constrained')

fig.supxlabel(f'budget increase [%]')
fig.supylabel('Energy[TWh/year]')
#print("summed", summed_df)

for i in range(len(df.index.levels[0].unique())):
        idx = df.index.levels[0].unique()[i]
        ax[i].plot(x,df.loc[idx].min(axis=1), color="grey") #, marker="o")
        ax[i].plot(x,df.loc[idx].max(axis=1), color="grey") #, marker="o")
        # for idx2, style, color in zip(["DAC", "BECC", "afforestation", "co2 sequestered"],["ox", "h1", "so", "hv"], ["blue", "red", "green", "black"]):
        for col in df.columns:                               
                ax[i].scatter(x, df.loc[(idx),col], marker="o",s=20, alpha=0.7, facecolor="grey", label="single solution" if (i==0 and counter) else "")
                counter = 0
        for idx2, style, color in zip(["DAC", "BECC"],["ox", "h1"], ["blue", "red"]):
                idxmax = df_co2_all.loc[idx2].idxmax(axis=1)
                for ix, iy in zip(idxmax[1:],idxmax[1:].index):
                        ax[i].scatter(float(iy)*100, df.loc[(idx,iy),ix], marker=style[0],s=50, alpha=0.7, facecolor=color, label=f"max {idx2}" if (i==0 and iy=="0.01") else "")
        for idx2, style, color in zip(["afforestation", "co2 sequestered"],["so", "hv"], ["green", "black"]):      
                idxmin = df_co2_all.loc[idx2].idxmin(axis=1)
                for ix, iy in zip(idxmin[1:],idxmin[1:].index):
                        ax[i].scatter(float(iy)*100, df.loc[(idx,iy),ix], marker=style[1],s=50, alpha=0.7, facecolor=color, label=f"min {idx2}" if (i==0 and iy=="0.01") else "")
        counter = 1

        # for idx2, style, color in zip(["biochar"],["ox"], ["blue"]):
        #         idxmax = df_co2_all.loc[idx2].idxmax(axis=1)
        #         for ix, iy in zip(idxmax[1:],idxmax[1:].index):
        #                 ax[i].scatter(float(iy)*100, df.loc[(idx,iy),ix], marker=style[0],s=10, alpha=0.7, facecolor=color, label=f"max {idx2}" if (i==0 and iy=="0.01") else "")
        #         idxmin = df_co2_all.loc[idx2].idxmin(axis=1)
        #         for ix, iy in zip(idxmin[1:],idxmin[1:].index):
        #                 ax[i].scatter(float(iy)*100, df.loc[(idx,iy),ix], marker=style[1],s=50, alpha=0.7, facecolor=color, label=f"min {idx2}" if (i==0 and iy=="0.01") else "")
        ax[i].set_title(idx, pad=6+(i%2)*10)

        const = np.array([n.stores.e_nom_max.filter(like=idx).sum(), n.stores.e_nom.filter(like=idx).sum()])
        max_const = const[np.isfinite(const)].max()/1E6
        if idx == "co2 emissions":
               ax[i].set_ylabel("MtCO2/year")
        if max_const > 0:
                # ax2 = ax[i].twinx()
                # print(df.loc[idx].max(axis=1).max(), max_const)
                max_perc = df.loc[idx].max(axis=1).max()/max_const
                # ax2.hlines(df.loc[idx].max(axis=1).max(), x[0], x[-1], colors="red", linestyles="--", label=f"{round(max_perc*100,2)}")
                # ax2.legend()
                if max_perc < 1:
                        colors = "blue"
                else:
                        colors = "red"
                hline = ax[i].hlines(df.loc[idx].max(axis=1).max(), x[0], x[-1], colors=colors, linestyles="--", label=f"{round(max_perc*100,2)} %")
                ax[i].legend()
                hline.set_label("_")

fig.legend(ncols=4, loc='lower center', bbox_to_anchor=(0.5, -0.08))


plt.savefig(f"{PATH}/othersectorsslack.png", dpi=600, bbox_inches='tight')        
plt.show()
# libraries
import pandas
import matplotlib.pyplot as plt
from pandas.plotting import parallel_coordinates

# Take the iris dataset
import seaborn as sns
data = sns.load_dataset('iris')

# Make the plot
parallel_coordinates(df_unique.reset_index().drop("slack", axis=1), 'level_3', colormap=plt.get_cmap("Set2"))
plt.show()

df_par = df_co2_all.xs(key="0.05", level=1).T
df_par
df_unique = df_par.round(0)
df_unique = df_co2_all.round(0).T.drop_duplicates().T
df_unique.reset_index().drop("slack", axis=1).T