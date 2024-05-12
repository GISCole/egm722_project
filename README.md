# egm722_project
AWI_Checker.py
This code aims to automate the assessment of ancient woodland, highlighting those woodlands that have suffered a reduction in vegetation height and so are likely to have undergone some disturbance or clearance and should warrant further assessment. 
Fork and clone the main branch repository so you have a local version, this should include a folder called “AWI_project” which contains a python code called “AWI_tester.py” and a Data folder with a “gb_counties.shp” shapefile and its ancillary files. There should also be an “environment.yml” file with the list of dependencies required for running the code which can be imported as and Anaconda environment through navigator. 
To access the raster files for vegetation height required for assessing the state of the ancient woodland the user will need a NASA EarthData account (register at: https://urs.earthdata.nasa.gov/) once you have this account you need to set up a .netrc file. In a text file copy and complete the following: 
machine urs.earthdata.nasa.gov login ‘username’ password ‘password’
Save this as .netrc in ‘C:\Users\<your_username>’. 
In the properties for this file, disable inheritance, remove the SYSTEM and Administrators permissions and remove full control from your username. Alternatively, download and run the Earthdata script for creating a .netrc file (available here - https://urs.earthdata.nasa.gov/documentation/for_users/data_access/create_net_rc_file)

The AWI_tester.py code starts by asking the user to define their area of interest (AOI), this needs to be a ceremonial county of England in the south, a full list of valid AOI’s can be seen below

Berkshire
Buckinghamshire
City and County of the City of London
Cornwall
Devon
Dorset
East Sussex
Essex
Gloucestershire
Greater London
Hampshire
Hertfordshire
Isle of Wight
Kent
Oxfordshire
Somerset
Surrey
West Sussex
Wiltshire
