"""A tool for assessing whether Ancient Woodland (AW) has been retained effectively

The aim of this module is to create a tool that assesses whether AW present in the
Ancient Woodland Inventory - https://naturalengland-defra.opendata.arcgis.com/datasets/a14064ca50e242c4a92d020764a6d9df_0/about for England
is likely to still be present based on LIDAR and/or Radar assessments of vegetation cover.

"""

##Loading packages for interactive figures
import os
import geopandas as gpd
import matplotlib.pyplot as plt
from cartopy.feature import ShapelyFeature
import cartopy.crs as ccrs
import matplotlib.patches as mpatches
import matplotlib.lines as mlines


