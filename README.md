This repository contains the 'map page' or map cell extents for Finland ("karttalehtijako").

Many Finnish geospatial datasets are distributed so that the data is split according
to the map page or map cell subdivisions. The subdivisions originate from use in paper maps.

I couldn't find a good way to get the 'map pages' that I needed from given WGS84 coordinates,
so I opted to create this mapping to help with that.

# Usage
The program runs without arguments and generates a newline-delimited GeoJSON output.
```bash
python epsg3067_map_pages.py > epsg3067_map_pages.geojsons
```

Dependencies: `pyproj`, `geojson`, `shapely`.
