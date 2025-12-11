
# import necessary Python modules
from atlite.gis import ExclusionContainer
from atlite.gis import shape_availability
from rasterio.plot import show
import matplotlib.pyplot as plt
import geopandas
import pandas
import atlite
import logging
import yaml



def build_corine_potentials(config_yaml, network_geojson, corine_dataset, resolution, component, csv_file, png_file, log):

    # load config yaml file representing the PyPSA-Eur configuration
    handle = open(config_yaml)
    config = yaml.safe_load(handle)
    handle.close()


    # configure log mechanism
    if log is True:
        logging.basicConfig(level = config["logging"]["level"])
        logger = logging.getLogger(__name__)
        logger.info("Calculate CORINE potentials for %s" % component)


    # load network geojson file representing the PyPSA-Eur network
    nodes_geojson = geopandas.read_file(network_geojson).set_index("name")


    # select CORINE Land Cover (CLC) codes (specified in the config yaml file)
    excluder = ExclusionContainer(crs = 3035, res = resolution)
    excluder.add_raster(corine_dataset, codes = config[component]["corine"], invert = True, crs = 3035)
    cell_area = excluder.res**2


    # calculate CORINE potential per node
    df = pandas.DataFrame(columns = ["node", "area [sqkm]", "potential [sqkm]"])
    for node in nodes_geojson.index:
        shape = nodes_geojson.to_crs(excluder.crs).loc[[node]].geometry
        band, transform = shape_availability(shape, excluder)
        area = shape.geometry.area.sum() / 1e6   # in sqkm
        selected_cells = band.sum() * cell_area / 1e6   # in sqkm
        df.loc[len(df)] = [node, area, selected_cells]
        if log is True:
            logger.info("Node=%s * Area=%0.f [sqkm] * Potential=%0.f [sqkm]" % (node, area, selected_cells))


    # save CORINE potentials into CSV file
    if csv_file is not None:
        if log is True:
            logger.info("Save CORINE potentials for %s into CSV file '%s'" % (component, csv_file))
        df.set_index("node", inplace = True)
        df.to_csv(csv_file)


    # save CORINE potentials into PNG file
    if png_file is not None:
        if log is True:
            logger.info("Save CORINE potentials for %s into PNG file '%s'" % (component, png_file))
        shape = nodes_geojson.to_crs(excluder.crs).geometry
        band, transform = shape_availability(shape, excluder)
        fig, ax = plt.subplots(figsize = (20, 23))
        ax.set_axis_off()
        shape.plot(ax = ax, color = "none")
        show(band, transform = transform, cmap = "Greens", ax = ax)
        plt.savefig(png_file)



if __name__ == "__main__":

    # build and save CORINE potentials into CSV and PNG files
    if "snakemake" in globals():
        build_corine_potentials("config/config.yaml", snakemake.input["network_geojson"], snakemake.input["corine_dataset"], snakemake.params["resolution"], snakemake.params["component"], snakemake.output["csv_file"], snakemake.output["png_file"], True)
    else:
        build_corine_potentials("config.yaml", "regions_onshore_base_s_39.geojson", "g250_clc06_V18_5.tif", 250, "afforestation", "afforestation_corine_potentials_s_39.csv", "afforestation_corine_potentials_s_39.png", True)


