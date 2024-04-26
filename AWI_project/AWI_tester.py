"""A tool for assessing whether Ancient Woodland (AW) has been retained effectively

The aim of this module is to create a tool that assesses whether AW present in the
Ancient Woodland Inventory -
https://naturalengland-defra.opendata.arcgis.com/datasets/a14064ca50e242c4a92d020764a6d9df_0/about for England
is likely to still be present based on LIDAR and/or Radar assessments of vegetation cover.


Start off by filling in your area of interest, this much be a ceremonial county of England
"""
aoi = "Derbyshire" ## Will come back to make this validating based on a the unique values available in counties
##Loading packages for interactive figures
import geopandas as gpd
import shapely


##Importing counties shapefile to act as location framework
counties = gpd.read_file('Data/gb_counties.shp')
#print(counties.head(5)) #check head
print(len(counties)) # Check length should be 91
print(counties.crs)# check crs should be EPSG:27700
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
        shape = shape.to.crs(pcrs) # if it isnt it is converted to the project crs
        print('Your CRS was amended')
    else:
        print('Your CRS was correct')

    return shape # amended shape


crs_check(study_area,pcrs) # double checking that nothing weird has happened when getting the study area and
                            # testing the function

# Calculates the area of the county
study_area_ha = study_area.area/10000

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
study_area_wgs84 = study_area.to_crs(epsg=4326) #convert to decimal degrees
xmin, ymin, xmax, ymax = study_area_wgs84.total_bounds # Get the bounding box
xmin_formatted = f"{xmin:.3f}"# convert to correct decimal places
ymin_formatted = f"{ymin:.3f}"
xmax_formatted = f"{xmax:.3f}"
ymax_formatted = f"{ymax:.3f}"

# Creating the API request URL with the bounding box parameters
awi_url = f"https://services.arcgis.com/JJzESW51TqeY9uat/arcgis/rest/services/Ancient_Woodland_England/FeatureServer/0/query?where=1%3D1&outFields=*&geometry={xmin_formatted},{ymin_formatted},{xmax_formatted},{ymax_formatted}&geometryType=esriGeometryEnvelope&inSR=4326&spatialRel=esriSpatialRelIntersects&outSR=4326&f=json"

##print(awi_url) ## Used to check the URL works, paste it into a browser

##Importing the AWI dataset from the natural england data portal through their API
awi = gpd.read_file(awi_url)
print(len(awi))
print(awi.loc[0])
