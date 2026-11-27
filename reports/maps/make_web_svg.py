"""Make a slim, web-ready SVG of greater Doha (same look as the QGIS Streets map) plus pin positions.

Usage: python3 make_web_svg.py <geo_dir> <out_svg> <out_pins_json>
Roads are merged into one path per class; small streets are left out to keep the file light.
"""
import json
import math
import sys

from shapely.geometry import box, shape, mapping
from shapely.ops import unary_union

GEO, OUT_SVG, OUT_PINS = sys.argv[1:4]
X0, Y0, X1, Y1 = 51.392, 25.218, 51.628, 25.448
LAT0 = (Y0 + Y1) / 2
KX, KY = math.cos(math.radians(LAT0)) * 111320, 110574
W = 1200
SCALE = W / ((X1 - X0) * KX)
H = round((Y1 - Y0) * KY * SCALE)
CLIP = box(X0, Y0, X1, Y1)
TOL = 0.9 / SCALE / KX  # ~0.9 px in degrees


def px(lon, lat):
    return (lon - X0) * KX * SCALE, (Y1 - lat) * KY * SCALE


def ring_d(coords, close):
    out, last = [], None
    for i, (x, y) in enumerate(coords):
        X, Y = px(x, y)
        pt = (round(X, 1), round(Y, 1))
        if pt == last:
            continue
        out.append(("M" if i == 0 else "L") + f"{pt[0]:g} {pt[1]:g}")
        last = pt
    return "".join(out) + ("Z" if close else "")


def geom_d(g):
    d = []
    t = g.geom_type
    if t == "Polygon":
        d.append(ring_d(g.exterior.coords, True))
        d += [ring_d(r.coords, True) for r in g.interiors]
    elif t in ("MultiPolygon", "GeometryCollection", "MultiLineString"):
        for p in g.geoms:
            d.append(geom_d(p))
    elif t == "LineString":
        d.append(ring_d(g.coords, False))
    return "".join(d)


def load(path):
    return [f for f in json.load(open(path))["features"]]


def clipped(geoms, tol=TOL):
    g = unary_union(geoms).intersection(CLIP)
    return g.simplify(tol, preserve_topology=True)


adm1 = load(f"{GEO}/ADM1_media.geojson")
adm2 = load(f"{GEO}/ADM2_media.geojson")
land = clipped([shape(f["geometry"]) for f in adm1])
zones = [shape(f["geometry"]) for f in adm2]
svc = clipped([z for z in zones if z.centroid.x >= 51.38 and 25.185 <= z.centroid.y <= 25.46])

water = [shape(f["geometry"]) for f in load(f"{GEO}/ov/water.geojson")
         if f["properties"]["class"] in ("lake", "pond", "reservoir", "canal", "basin")]
water = clipped([w for w in water if w.is_valid])

roads = {"major": [], "mid": [], "minor": []}
cls = {"motorway": "major", "trunk": "major", "primary": "major", "secondary": "mid", "tertiary": "minor"}
for f in load(f"{GEO}/ov/segment.geojson"):
    p = f["properties"]
    if p["subtype"] == "road" and p["class"] in cls:
        roads[cls[p["class"]]].append(shape(f["geometry"]))
road_d = {k: geom_d(clipped(v, TOL * 1.2)) for k, v in roads.items()}

AREAS = {
    "west-bay": ("West Bay", 51.5330, 25.3229),
    "the-pearl": ("The Pearl", 51.5450, 25.3720),
    "lusail": ("Lusail", 51.5197, 25.4229),
    "msheireb": ("Msheireb", 51.5273, 25.2853),
    "al-sadd": ("Al Sadd", 51.5010, 25.2830),
    "al-waab": ("Al Waab", 51.4704, 25.2591),
}
pins = {}
for k, (n, x, y) in AREAS.items():
    X, Y = px(x, y)
    pins[k] = {"name": n, "left": round(X / W * 100, 2), "top": round(Y / H * 100, 2)}

svg = (
    f'<svg class="dohamap" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" '
    f'aria-label="Map of greater Doha. The ONGO service area, shaded in lime, covers Lusail, The Pearl, West Bay, Msheireb, Al Sadd and Al Waab.">'
    f'<rect width="{W}" height="{H}" fill="#E4ECE7"/>'
    f'<path d="{geom_d(land)}" fill="#F3F5F1" fill-rule="evenodd"/>'
    f'<path d="{geom_d(svc)}" fill="#FFFFFF" fill-rule="evenodd"/>'
    f'<path d="{geom_d(svc)}" fill="#A0E870" fill-opacity=".31" stroke="#163200" stroke-width="1.6" stroke-linejoin="round" fill-rule="evenodd"/>'
    f'<path d="{geom_d(water)}" fill="#CFE3DA" fill-rule="evenodd"/>'
    f'<g fill="none" stroke-linecap="round" stroke-linejoin="round">'
    f'<path d="{road_d["minor"]}" stroke="#163200" stroke-opacity=".16" stroke-width=".7"/>'
    f'<path d="{road_d["mid"]}" stroke="#5E8F3A" stroke-opacity=".6" stroke-width="1"/>'
    f'<path d="{road_d["major"]}" stroke="#5E8F3A" stroke-width="2.2"/>'
    f'</g></svg>'
)
open(OUT_SVG, "w").write(svg)
json.dump({"w": W, "h": H, "pins": pins}, open(OUT_PINS, "w"))
print("svg bytes", len(svg), "size", W, H)
