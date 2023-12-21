# paperless_bt

To run this software you need `pdm`. You can install it with `pipx` or your favorite distribution package.

To run the server
````
# create the venv
pdm sync
. ./venv/bin/activate
paperless_bt run french_mnc.csv site_mobiles_gps.csv
````

If for some reasons you need to regenate the csv file with GPS cooardinates:
````
paperless_bt generate site_mobiles.csv site_mobiles_gps.csv
````

