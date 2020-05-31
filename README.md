This repository contains the 'map page' or map cell extents for Finland ("karttalehtijako").

Many Finnish geospatial datasets are distributed so that the data is split according
to the map page or map cell subdivisions. The subdivisions originate from use in paper maps.

I couldn't find a good way to get the 'map pages' that I needed from given WGS84 coordinates,
so I opted to create this mapping to help with that.

# Preview

Check out [level1.geojson](level1.geojson) and [level2.geojson](level2.geojson) for the topmost two levels.

# Usage
The program runs without arguments and generates a newline-delimited GeoJSON output.
```bash
python epsg3067_map_pages.py > epsg3067_map_pages.geojsons
```

Dependencies: `pyproj`, `geojson`, `shapely`.

# GeoJSON properties

The produced GeoJSON file has a number of properties that can be used to narrow down the used map subdivisions:

`name` is the map page/cell name, like `V3` or `V3133A`.

`level` is the level of subdivisions, from 1 (top level) through 6 (e.g. `V3133A3` is level 6, and `V3` is level 1).

`center_e` is the easting coordinate of the center of the map cell in EPSG:3067.

`center_n` is the northing coordinate of the center of the map cell in EPSG:3067.

`scale_e` is the scale, and the length of the cell in EPSG:3067 coordinates, in the West/East direction.

`scale_n` is the scale, and the length of the cell in EPSG:3067 coordinates, in the South/North direction.

`actually_used` is a top-level only measure that shows if the top-level map cell actually spans Finland. The generated tiles are regularly spaces from K2 to Z6 but not all of them are used in practice since they don't intersect with Finland's bounds. Note that any level>1 are still shown as `actually_used`=`true` even if the lower levels don't intersect with Finland.


# Extracting subsets of the data

The file [level2.geojson](level2.geojson) in the repository is extracted as follows:
```bash
jq -c '. | select(.properties.level==2)' epsg3067_map_pages.geojsons |
    jq --slurp '{type:"FeatureCollection","features":.}' > level2.geojson
```
