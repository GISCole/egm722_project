"""A tool for assessing whether Ancient Woodland (AW) has been retained effectively

The aim of this module is to create a tool that assesses whether AW present in the
Ancient Woodland Inventory -
https://naturalengland-defra.opendata.arcgis.com/datasets/a14064ca50e242c4a92d020764a6d9df_0/about for England
is likely to still be present based on LIDAR and/or Radar assessments of vegetation cover.


Start off by filling in your area of interest, this much be a ceremonial county of England
"""
aoi = "Wiltshire"



##Import Packages
import os
import pandas as pd
import geopandas as gpd
import shapely
from shapely.geometry import Polygon
from shapely.geometry import box
import rasterio as rio
from rasterio.windows import Window
import rasterio.merge
import numpy as np
import earthaccess
import rasterstats
import shapely.geometry
from rasterstats import zonal_stats

##Importing counties shapefile to act as location framework
counties = gpd.read_file('Data/gb_counties.shp')
#print(counties.head(5)) #check head
print(f'Number of counties in dataset: {len(counties)}') # Check length should be 91
print(f'CRS of Counties dataset: {counties.crs}')# check crs should be EPSG:27700
pcrs = counties.crs ## Defining project CRS
#print(counties.columns)

# Identify the Area of Interest region and assign it as the study area from the counties shapefile
study_area = counties[counties['Name'] == aoi]
#Checking that CRS is correct and then calculating the area in hectares

def crs_check(shape, pcrs):
    """
    This checks the CRS of the shape which is a geodataframe and converts it to the project crs if neccesary

    Args:
    shape: the gpd geodataframe that needs checking
    pcrs: project coordinate reference system, defined earlier in the code

    Returns:
    The geodataframe that has been checked and converted to the project crs if necesary
    """
    if shape.crs != pcrs: #checking if the shape crs is the same as the project crs
        shape = shape.to_crs(pcrs) # if it isnt it is converted to the project crs
        print('Your CRS was amended')
    else:
        print('Your CRS was correct')

    return shape # amended shape


study_area = crs_check(study_area,pcrs) # double checking that nothing weird has happened when getting the study area and
                            # testing the function


# Calculates the area of the county
study_area_ha = (study_area.area)/10000

# This shows that it has recognised the correct county and the area shows it has loaded a valid shape
print(f"Your study area is {study_area['Name'].values[0]} which is {study_area_ha.values[0]:.2f} hectares")

"""
The AWI is due for an update in 2025, pulling from the API means this tool stays valid as the dataset updates
The API does not handle a request for the whole of England so the spatial envelope needs to be defined
As this is going to be clipped after the layer is loaded it doesnt matter if there are woodlands called from outside the AOI
Query URL from NE API explorer - https://naturalengland-defra.opendata.arcgis.com/datasets/a14064ca50e242c4a92d020764a6d9df_0/api
"""
# Calculate the bounding box of the study area variable
# The API needs coordinatees in decimal degrees which are 3 decimal places long
##study_area_wgs84 = study_area.to_crs(epsg=4326) #convert to decimal degrees
##xmin, ymin, xmax, ymax = study_area_wgs84.total_bounds # Get the bounding box
##xmin_formatted = f"{xmin:.3f}"# convert to correct decimal places
##ymin_formatted = f"{ymin:.3f}"
##xmax_formatted = f"{xmax:.3f}"
##ymax_formatted = f"{ymax:.3f}"

#Making the above a function as it will be needed multiple times
def get_api_bb(study_area):
    """
    This gets the bounding box of the study area and converts it to EPSG:4326 in order to return decimal
    degrees for the x&y min&max which is required for defining the area we are requesting data from the API,
    this limits the amount of data we need to call and lowers processing time.

    Args:
   study_area: geodataframe dervived from counties database and user defined area of interest (aoi)
    Returns: xmin, ymin, xmax, ymax in decimal degrees to 3 decimal places

    """
    study_area_wgs84 = study_area.to_crs(epsg=4326) #convert to decimal degrees
    xmin, ymin, xmax, ymax = study_area_wgs84.total_bounds  # Get the bounding box
    return f"{xmin:.3f},{ymin:.3f},{xmax:.3f},{ymax:.3f}"


#Use the function defined above to get he bounding box of the study area and converted to EPSG:4326
awi_bb = get_api_bb(study_area)

# Creating the API request URL with the bounding box parameters
#awi_url = f"https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services/Ancient_Woodland_England/FeatureServer/0/query?where=1%3D1&outFields=*&geometry={xmin_formatted},{ymin_formatted},{xmax_formatted},{ymax_formatted}&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outSR=4326&f=json"
awi_url = f"https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services/Ancient_Woodland_England/FeatureServer/0/query?where=1%3D1&outFields=*&geometry={awi_bb}&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outSR=4326&f=json"

print(f'Check this URL by pasting into a browser search bar:{awi_url}') ## Used to check the URL works, paste it into a browser

##Importing the AWI dataset from the natural england data portal through their API
awi = gpd.read_file(awi_url)

print(awi.loc[0])

#Checking if the crs is correct with the crs_check function
awi= crs_check(awi, pcrs)
#print(awi.crs)

#Clipping awi to user defined study area
awi_clipped = gpd.clip(awi, study_area)
awi_clipped.to_file('Data/awi_clipped.shp')
print(f'Number of Ancient Woodlands within {aoi}: {len(awi_clipped)}')

''' This next section will load in Global Vegetation Height Metrics from GEDI and ICESat2 and calculate zonal statistics
    to get an idea of vegetation height in the ancient woodlands
    Low average vegetation height will highlight priority woodlands for further analysis
'''
study_area_wgs84 = study_area.to_crs(epsg=4326)

search_area_geo = study_area_wgs84['geometry'].iloc[0]

search_area_bounds = search_area_geo.bounds
print("Search area bounding box:", search_area_bounds)

search_area_list = list(search_area_bounds)
search_area_tuple = tuple(search_area_list) #converting to a tuple because that is what earth access is needing

#print(type(study_area_wgs84))
#print(type(search_area_geo))
#print(search_area_list)
#print(search_area_tuple)

#Earth access login
earthaccess.login(strategy='netrc')


###The below section allows us to find appropriate datasets, this has already been done, this returns the short name
###that we use in the next section
#datasets = earthaccess.search_datasets(
#    keyword='gedi vegetation', # search for datasets that match the keyword 'elevation'
#    bounding_box = search_area_tuple
#)

#dataset= datasets[0]

#ds_name = dataset.get_umm('ShortName')
#print('Dataset name:',ds_name)

#Searching for the granules
ds_name = 'GEDI_ICESAT2_Global_Veg_Height_2294' # using the short name found in the previous section, leave this as is
results = earthaccess.search_data( ##Searching for granules in our aoi
    short_name = ds_name,
    bounding_box = search_area_tuple,
)
os.makedirs(ds_name, exist_ok=True) # Making a directory for the dowloaded granules
print(type(results))
print(results[0])


##If we download the datasets just from these results we end up with a massive file (nearly 70gb)
##we need to filter the results list prior to downloading

# create an empty list to hold filtered datasets
filtered_datasets = []
# Iterate through each item in the results list
for result in results:
    meta_data = result.get('meta', {}) # get the metadata
    native_id = meta_data.get('native-id') # get the native-id for in metadata for each dataset

    if native_id and 'rh98_100m.tif' in native_id: ## Check if the native-id has rh98_100.tif in its name
        # This returns the values for the vegetation canopy at 100m resolution
        # If it does, add the it to the filtered datasets list
        filtered_datasets.append(result)


print(f"Filtered datasets ': {len(filtered_datasets)} ")

## This is still about 10gb and we dont want to redownload it every time we run this, so we will create another
## list filtering by what is not already in the directory

download_list = []
for dataset in filtered_datasets:
    meta_data = dataset.get('meta', {})
    native_id = meta_data.get('native-id')

    path = os.path.join(ds_name, native_id) #create filepath for check

    # Check if the file already exists in the download directory and add it to the download ist if its not there
    if not os.path.exists(path):
        download_list.append(dataset)

print(f"Datasets to download: {len(download_list)}")

#Download the files not already in the directory
downloaded_files = earthaccess.download(download_list, ds_name)



##Zonal stats

# Open the gedi rh98 100m tif
with rio.open('GEDI_ICESAT2_Global_Veg_Height_2294/gedi_rh98_100m.tif') as veg_dataset:
    # Get the crs and transformation
    crs = veg_dataset.crs
    affine_tfm = veg_dataset.transform
    nodata_value = veg_dataset.nodata
    print("Nodata value:", nodata_value)
    bounds = veg_dataset.bounds
    print(f"Raster data bounds: {bounds}")


    # Change the awi dataset to the crs of the gedi raster
    awi_clipped = awi_clipped.to_crs(crs)
    # setting the index as the object ID
    awi_clipped.set_index('OBJECTID', inplace=True)

    # create tile size
    window_width = 1000
    window_height = 1000

    # Defining raster dimensions
    raster_width = veg_dataset.width
    raster_height = veg_dataset.height

    # Get the bounds of the study area for which we need the tiles for
    xmin, ymin, xmax, ymax = awi_clipped.total_bounds

    # List to store zonal statistics results
    awi_stats_results = []

    # Iterate over tiles within the study area
    for row in range(0, raster_height, window_height):
        for col in range(0, raster_width, window_width):
            win = Window(col, row, window_width, window_height)

            ## Read the gedi raster in that window
            veg_raster = veg_dataset.read(1, window=win)

            # Clip the tile data to the study area and perform zonal statistics
            for object_id, woodland in awi_clipped.iterrows():
                # Check if the polygon intersects with the tile bounds
                if woodland.geometry.intersects(window_bounds):
                    # Perform zonal statistics for the polygon
                    stats = zonal_stats(
                        [woodland.geometry],
                        veg_raster,
                        affine=affine_tfm,
                        stats='mean',
                        nodata=nodata_value
                    )
                    # get the NAME column from awi_clipped
                    name = woodland['NAME']
                    # Create a dictionary with the zonal statistics, OBJECTID, and NAME
                    result = {
                        'OBJECTID': object_id,
                        'NAME': name,
                        'mean': stats[0]['mean'],
                    }

                    # Append the result to the list of zonal statistics results
                    awi_stats_results.append(result)

                # Optionally print the stats results
                # print(awi_stats_results)

##Convert the results to a dataframe
awi_stats_df = pd.DataFrame(awi_stats_results)
##Export to CSV
awi_stats_df.to_csv('Data/awi_stats_results.csv', index=False)









