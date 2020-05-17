'''Enumerate map pages for EPSG:3067 aka ETRS-TM35FIN

Knowing the boundaries of individual map pages are mainly useful
when source data has been split in those terms.
So it's easy to select just the regions of interest using these boundaries.

Source: http://docs.jhs-suositukset.fi/jhs-suositukset/JHS197/JHS197.html#H24


Map page subdivisions are defined as follows:

Top level (scale 1:200 000)
K-Z (without O) + 2-6, e.g. V3
K = southmost
2 = westmost

Next level (scale 1:100 000)
Subdivision: 1-4, e.g. V31

Next level (scale 1:50 000)
Subdivision: 1-4, e.g. V313

Next level (scale 1:25 000)
Subdivision: 1-4, e.g. V3133

Next level (scale 1:10 000)
Subdivision (8 parts): A-H, e.g. V3133A

Next level (scale 1:5 000, no further subdivisions after this)
Subdivision 1-4, e.g. V3133A3

NB: Subdivisions 1-4 go from bottom-left (1), to top-left (2), bottom-right (3), and top-right (4).
Alternatively, the left and right sides can be identified as 'L' and 'R', e.g. V313L or V3133R.

For subdivision 5 (ABCDEFGH), ABCD is collectively the left half, and EFGH the right half.
The halves are subdivided the same way as all other levels.
'''
from collections import namedtuple
from pyproj import Transformer
import geojson
import shapely.geometry
import sys
transformer = Transformer.from_crs(3067, 4326)

TOP_SCALE_N =  96_000
TOP_SCALE_E = 192_000

# The EPSG:3067 coordinates for the bottom-right corner of map page K4 are defined as:
K4R_N = 6_570_000
K4R_E = 500_000

# bottom-left corner of K2:
K2_E = K4R_E - 3*TOP_SCALE_E
K2_N = K4R_N

# These are the top-level map pages that actually span Finland.
actual_used_top_level_pages = '''
      X4 X5
   W3 W4 W5
   V3 V4 V5
      U4 U5
      T4 T5
      S4 S5
   R3 R4 R5
   Q3 Q4 Q5
   P3 P4 P5 P6
   N3 N4 N5 N6
   M3 M4 M5
L2 L3 L4 L5
K2 K3 K4 K5
'''.strip().split()

top_letter = 'KLMNPQRSTUVWXYZ'
top_num    = '23456'

Ns = [K2_N + i * TOP_SCALE_N  for i,_ in enumerate(top_letter)]
Es = [K2_E + i * TOP_SCALE_E for i,_ in enumerate(top_num)]


subdivisions = [None, '1234', '1234', '1234', 'ABCDEFGH', '1234']

Entry = namedtuple('Entry', 'page east north scale')

MAX_LEVEL = len(subdivisions) - 1
def dfs(page, level, E, N, scaleE, scaleN, subdiv):
    n_sub = len(subdiv)
    assert n_sub in (0,1,2,4,8)
    if n_sub > 2: # left vs right half
        yield from dfs(page, level, E,           N, scaleE // 2, scaleN, subdiv[:n_sub//2])
        yield from dfs(page, level, E+scaleE//2, N, scaleE // 2, scaleN, subdiv[n_sub//2:])
    elif n_sub == 2: # top vs bottom half
        yield from dfs(page, level, E, N,           scaleE, scaleN // 2, subdiv[0])
        yield from dfs(page, level, E, N+scaleN//2, scaleE, scaleN // 2, subdiv[1])
    else:
        yield Entry(page=page+subdiv, north=N, east=E, scale=(scaleE, scaleN))
        if level < MAX_LEVEL:
            yield from dfs(page+subdiv, level+1, E, N, scaleE, scaleN, subdivisions[level+1])


def entry_to_geojson(entry):
    E, N = entry.east, entry.north
    scaleE, scaleN = entry.scale
    name = entry.page

    coordinates_3067 = [
        (E,        N),
        (E+scaleE, N),
        (E+scaleE, N+scaleN),
        (E,        N+scaleN),
        (E,        N),
    ]

    lats, lons = transformer.transform(*zip(*coordinates_3067))
    coordinates_wgs84 = zip(lons, lats)

    p = shapely.geometry.shape(dict(
        type='Polygon',
        coordinates=[coordinates_wgs84],
    ))

    # GeoJSON like mapping, i.e. json.dumps(f) will be a valid GeoJSON geometry.
    f = shapely.geometry.mapping(p)
    properties = dict(
        name=name,
        actually_used=name[:2] in actual_used_top_level_pages,
        center_n=N + scaleN // 2,
        center_e=E + scaleE // 2,
        scale_n=scaleN,
        scale_e=scaleE,
        level=len(name) - 1,
    )
    return f, properties


top = [
    Entry(page=pos0+pos1, east=E, north=N, scale=(TOP_SCALE_E, TOP_SCALE_N))
    for pos0, N in zip(top_letter, Ns)
    for pos1, E in zip(top_num, Es)
]

features = []
for x in top:
    for z in dfs(x.page, 0, x.east, x.north, TOP_SCALE_E, TOP_SCALE_N, ''):
        geometry, properties = entry_to_geojson(z)
        f = geojson.Feature(id=properties['name'], geometry=geometry, properties=properties)
        geojson.dump(f, sys.stdout)
        print()

feature_collection = geojson.FeatureCollection([
    geojson.Feature(id=properties['name'], geometry=geometry, properties=properties)
    for geometry, properties in features
])
