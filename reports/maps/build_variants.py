"""Build three ONGO 'All of Doha' map variants in QGIS and export SVG + PNG.

Usage: QT_QPA_PLATFORM=offscreen python3.12 build_variants.py <geo_dir> <out_dir> <variant>
Variants: streets (clean street map), zones (planning-style service map), night (dark street map).
Data: geoBoundaries (ADM1/ADM2), Overture Maps 2026-11-18 (roads, water, place points; OpenStreetMap-derived).
"""
import os
import sys

from qgis.core import (
    Qgis, QgsApplication, QgsVectorLayer, QgsProject, QgsRectangle, QgsCoordinateReferenceSystem,
    QgsCoordinateTransform, QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol, QgsSingleSymbolRenderer,
    QgsRuleBasedRenderer, QgsPalLayerSettings, QgsTextFormat, QgsTextBufferSettings,
    QgsTextBackgroundSettings, QgsVectorLayerSimpleLabeling, QgsPrintLayout, QgsLayoutItemMap,
    QgsLayoutItemScaleBar, QgsLayoutItemLabel, QgsLayoutItemShape, QgsLayoutPoint, QgsLayoutSize,
    QgsUnitTypes, QgsLayoutExporter, QgsFeature, QgsGeometry, QgsPointXY, QgsField, QgsLayoutMeasurement,
    QgsSimpleLineSymbolLayer, QgsSimpleMarkerSymbolLayer, QgsLinePatternFillSymbolLayer,
    QgsSimpleFillSymbolLayer, QgsPointPatternFillSymbolLayer,
)
from qgis.PyQt.QtCore import QVariant, QSizeF
from qgis.PyQt.QtGui import QColor, QFont

GEO, OUT, VARIANT = sys.argv[1], sys.argv[2], sys.argv[3]
os.makedirs(OUT, exist_ok=True)

# ONGO brand plus derived shades.
GREEN, GREEN_2, LIME, LIME_SOFT, PAPER, INK = "#163200", "#2E5A12", "#A0E870", "#EEF9E6", "#F7F9F3", "#0E1411"
P = {
    "streets": dict(sea="#E4ECE7", land="#FFFFFF", other_land="#F3F5F1", water="#CFE3DA", zone="0,0,0,0",
                    svc_fill="160,232,112,80", svc_line=GREEN, svc_w="0.55",
                    minor="22,50,0,34", minor_w=0.09, mid="94,143,58,150", mid_w=0.2, major="#5E8F3A", major_w=0.42,
                    label=INK, label_bg="#FFFFFF", dot=GREEN, halo="160,232,112,150", muni="#3F4A43", ink=INK),
    "zones": dict(sea="#D6E8E0", land=PAPER, other_land="#F1F3EE", water="#BFDCD1", zone="22,50,0,38",
                  svc_fill="160,232,112,150", svc_line=GREEN, svc_w="0.7",
                  minor=None, minor_w=0, mid=None, mid_w=0, major="#FFFFFF", major_w=1.1,
                  label=GREEN, label_bg="#FFFFFF", dot=GREEN, halo="160,232,112,170", muni="#3F4A43", ink=INK),
    "night": dict(sea="#060C07", land="#0F1B11", other_land="#0B140C", water="#0A1A14", zone="0,0,0,0",
                  svc_fill="160,232,112,26", svc_line="160,232,112,153", svc_w="0.45",
                  minor="160,232,112,34", minor_w=0.09, mid="160,232,112,90", mid_w=0.18, major=LIME, major_w=0.38,
                  label="#EEF6E9", label_bg="22,50,0,0", dot=LIME, halo="160,232,112,70", muni="#A9BBA9", ink="#EEF6E9"),
}[VARIANT]

# Real area positions from Overture/OSM place points.
AREAS = [
    ("West Bay", 51.5330, 25.3229),
    ("The Pearl", 51.5450, 25.3720),
    ("Lusail", 51.5197, 25.4229),
    ("Msheireb", 51.5273, 25.2853),
    ("Al Sadd", 51.5010, 25.2830),
    ("Al Waab", 51.4704, 25.2591),
]
EXT = QgsRectangle(51.392, 25.218, 51.628, 25.448)

app = QgsApplication([], False)
app.initQgis()
proj = QgsProject.instance()
wgs, utm = QgsCoordinateReferenceSystem("EPSG:4326"), QgsCoordinateReferenceSystem("EPSG:32639")
proj.setCrs(utm)
xf = QgsCoordinateTransform(wgs, utm, proj)


def fill(color, outline="0,0,0,0", w="0"):
    return QgsFillSymbol.createSimple({"color": color, "outline_color": outline, "outline_width": w, "outline_style": "solid" if w != "0" else "no"})


def tf(size, color, bold=True, buffer_color=None, bg=None):
    t = QgsTextFormat()
    f = QFont("Roboto")
    f.setBold(bold)
    t.setFont(f)
    t.setSize(size)
    t.setColor(QColor(color))
    if buffer_color:
        b = QgsTextBufferSettings()
        b.setEnabled(True)
        b.setSize(1.0)
        b.setColor(QColor(buffer_color))
        t.setBuffer(b)
    if bg:
        s = QgsTextBackgroundSettings()
        s.setEnabled(True)
        s.setType(QgsTextBackgroundSettings.ShapeRectangle)
        s.setSizeType(QgsTextBackgroundSettings.SizeBuffer)
        s.setSize(QSizeF(1.6, 0.9))
        s.setRadii(QSizeF(1.4, 1.4))
        s.setFillColor(QColor(bg))
        s.setStrokeColor(QColor(GREEN if VARIANT != "night" else LIME))
        s.setStrokeWidth(0.25 if VARIANT != "night" else 0.3)
        t.setBackground(s)
    return t


layers = []

# Land: Qatar municipalities.
land = QgsVectorLayer(os.path.join(GEO, "ADM1_media.gpkg"), "Land", "ogr")
land.setRenderer(QgsSingleSymbolRenderer(fill(P["other_land"])))
layers.append(land)

# Service area: dissolved urban zones of greater Doha.
zsrc = QgsVectorLayer(os.path.join(GEO, "ADM2_media.gpkg"), "zsrc", "ogr")
parts = [ft.geometry() for ft in zsrc.getFeatures()
         if ft.geometry().centroid().asPoint().x() >= 51.38 and 25.185 <= ft.geometry().centroid().asPoint().y() <= 25.46]
svc = QgsVectorLayer("Polygon?crs=EPSG:4326", "Service area", "memory")
f = QgsFeature()
f.setGeometry(QgsGeometry.unaryUnion(parts))
svc.dataProvider().addFeature(f)
svc.updateExtents()

svc_base = QgsVectorLayer("Polygon?crs=EPSG:4326", "Service base", "memory")
f2 = QgsFeature()
f2.setGeometry(QgsGeometry.unaryUnion(parts))
svc_base.dataProvider().addFeature(f2)
svc_base.setRenderer(QgsSingleSymbolRenderer(fill(P["land"])))
layers.append(svc_base)

# Zones (texture) for the planning style.
if VARIANT == "zones":
    zones = QgsVectorLayer(os.path.join(GEO, "ADM2_media.gpkg"), "Zones", "ogr")
    zones.setRenderer(QgsSingleSymbolRenderer(fill("0,0,0,0", P["zone"], "0.2")))

# Inland water.
water = QgsVectorLayer(os.path.join(GEO, "water.gpkg"), "Water", "ogr")
water.setSubsetString("class IN ('lake','pond','reservoir','canal','basin')")
water.setRenderer(QgsSingleSymbolRenderer(fill(P["water"])))
layers.append(water)

# Service area overlay.
if VARIANT == "zones":
    sym = fill(P["svc_fill"], P["svc_line"], P["svc_w"])
    hatch = QgsLinePatternFillSymbolLayer()
    hatch.setLineAngle(45)
    hatch.setDistance(1.6)
    hatch.setLineWidth(0.18)
    hatch.setColor(QColor(22, 50, 0, 70))
    # Hatch left out: Qt SVG clips pattern fills poorly, so stripes leaked into the sea in browsers.
    svc.setRenderer(QgsSingleSymbolRenderer(sym))
else:
    svc.setRenderer(QgsSingleSymbolRenderer(fill(P["svc_fill"], P["svc_line"], P["svc_w"])))

# Roads: rule-based by class.
roads = QgsVectorLayer(os.path.join(GEO, "roads.gpkg"), "Roads", "ogr")
root = QgsRuleBasedRenderer.Rule(None)


def add_rule(expr, color, width, casing=None):
    if not color:
        return
    s = QgsLineSymbol.createSimple({"line_color": color, "line_width": str(width), "capstyle": "round", "joinstyle": "round"})
    if casing:
        s.insertSymbolLayer(0, QgsSimpleLineSymbolLayer.create(
            {"line_color": casing, "line_width": str(width + 0.6), "capstyle": "round", "joinstyle": "round"}))
    root.appendChild(QgsRuleBasedRenderer.Rule(s, 0, 0, expr))


if VARIANT == "zones":
    add_rule("\"class\" IN ('motorway','trunk','primary')", "#FFFFFF", 0.55, casing="22,50,0,70")
    add_rule("\"class\" IN ('secondary')", "255,255,255,200", 0.25)
else:
    add_rule("\"class\" IN ('residential','unclassified','living_street')", P["minor"], P["minor_w"])
    add_rule("\"class\" IN ('secondary','tertiary')", P["mid"], P["mid_w"])
    add_rule("\"class\" IN ('motorway','trunk','primary')", P["major"], P["major_w"])
roads.setRenderer(QgsRuleBasedRenderer(root))

order = [svc, roads] if VARIANT != "zones" else [roads, svc]
if VARIANT == "zones":
    order.insert(1, zones)

# Area points.
pts = QgsVectorLayer("Point?crs=EPSG:4326", "ONGO areas", "memory")
pts.dataProvider().addAttributes([QgsField("name", QVariant.String)])
pts.updateFields()
for n, x, y in AREAS:
    ft = QgsFeature(pts.fields())
    ft.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
    ft["name"] = n
    pts.dataProvider().addFeature(ft)
pts.updateExtents()
msym = QgsMarkerSymbol.createSimple({"name": "circle", "color": P["halo"], "outline_style": "no", "size": "8" if VARIANT != "night" else "10"})
msym.appendSymbolLayer(QgsSimpleMarkerSymbolLayer.create(
    {"name": "circle", "color": P["dot"], "outline_color": "#FFFFFF" if VARIANT != "night" else "#0F1B11", "outline_width": "0.6", "size": "3.4"}))
pts.setRenderer(QgsSingleSymbolRenderer(msym))
lab = QgsPalLayerSettings()
lab.fieldName = "name"
if VARIANT == "night":
    lab.setFormat(tf(10.5, P["label"], buffer_color="#0F1B11"))
else:
    lab.setFormat(tf(9.5, P["label"], bg=P["label_bg"]))
lab.placement = Qgis.LabelPlacement.OrderedPositionsAroundPoint
lab.dist = 3.0
pts.setLabelsEnabled(True)
pts.setLabeling(QgsVectorLayerSimpleLabeling(lab))

# Quiet municipality names.
mlab = QgsPalLayerSettings()
mlab.isExpression = True
mlab.fieldName = "upper(\"shapeName\")"
mf = tf(7.2, P["muni"], bold=False)
mf.setOpacity(0.65)
mlab.setFormat(mf)
mlab.placement = Qgis.LabelPlacement.OverPoint
land.setLabelsEnabled(True)
land.setLabeling(QgsVectorLayerSimpleLabeling(mlab))

for l in [land, svc_base, water, svc, roads, pts] + ([zones] if VARIANT == "zones" else []):
    assert l.isValid(), l.name()
    proj.addMapLayer(l)

render = [pts] + list(reversed(order)) + [water, svc_base, land]
# Draw order (top first): points, then roads/service per variant, water, base land.
if VARIANT == "zones":
    render = [pts, roads, zones, svc, water, svc_base, land]
else:
    render = [pts, roads, svc, water, svc_base, land]

layout = QgsPrintLayout(proj)
layout.initializeDefaults()
W, H = 317.5, 264.58  # 1200 x 1000 px
layout.pageCollection().page(0).setPageSize(QgsLayoutSize(W, H, QgsUnitTypes.LayoutMillimeters))

m = QgsLayoutItemMap(layout)
m.attemptMove(QgsLayoutPoint(0, 0, QgsUnitTypes.LayoutMillimeters))
m.attemptResize(QgsLayoutSize(W, H, QgsUnitTypes.LayoutMillimeters))
m.setCrs(utm)
m.setBackgroundColor(QColor(P["sea"]))
m.setLayers(render)
m.zoomToExtent(xf.transformBoundingBox(EXT))
m.setFrameEnabled(False)
layout.addLayoutItem(m)


def label(text, size, color, x, y, bold=True, spacing=None):
    it = QgsLayoutItemLabel(layout)
    it.setText(text)
    t = tf(size, color, bold=bold)
    if spacing:
        f = t.font()
        f.setLetterSpacing(QFont.AbsoluteSpacing, spacing)
        t.setFont(f)
    it.setTextFormat(t)
    it.adjustSizeToText()
    it.attemptResize(QgsLayoutSize(it.rect().width() + 40, it.rect().height(), QgsUnitTypes.LayoutMillimeters))
    it.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(it)
    return it


def box(x, y, w, h, color, stroke=None, radius=3):
    s = QgsLayoutItemShape(layout)
    s.setShapeType(QgsLayoutItemShape.Rectangle)
    s.attemptMove(QgsLayoutPoint(x, y, QgsUnitTypes.LayoutMillimeters))
    s.attemptResize(QgsLayoutSize(w, h, QgsUnitTypes.LayoutMillimeters))
    s.setCornerRadius(QgsLayoutMeasurement(radius, QgsUnitTypes.LayoutMillimeters))
    s.setSymbol(fill(color, stroke or "0,0,0,0", "0.3" if stroke else "0"))
    layout.addLayoutItem(s)


# Scale bar.
sb = QgsLayoutItemScaleBar(layout)
sb.setStyle("Line Ticks Up")
sb.setLinkedMap(m)
sb.setUnits(QgsUnitTypes.DistanceKilometers)
sb.setUnitLabel("km")
sb.setNumberOfSegments(2)
sb.setNumberOfSegmentsLeft(0)
sb.setUnitsPerSegment(2.0)
sb.setTextFormat(tf(7.5, P["ink"], bold=False))
ls = sb.lineSymbol().clone()
ls.setColor(QColor(P["ink"]))
sb.setLineSymbol(ls)
sb.attemptMove(QgsLayoutPoint(W - 52, H - 20, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(sb)

credit_color = "#3F4A43" if VARIANT != "night" else "#A9BBA9"
label("© OpenStreetMap contributors via Overture Maps · Boundaries: geoBoundaries", 6, credit_color, 10, H - 9, bold=False)

if VARIANT == "streets" and not os.environ.get("NO_TITLE"):
    # Poster-style title, after the third reference.
    box(10, 10, 92, 30, "255,255,255,238")
    label("ALL OF DOHA", 15, GREEN, 15, 13.5, spacing=2.2)
    label("QATAR  ·  25°17′N  51°32′E", 7.5, "#3F4A43", 15, 24, bold=False, spacing=1.2)
    label("A washer comes wherever you park", 7.5, INK, 15, 31, bold=False)
elif VARIANT == "zones":
    # Legend, after the first reference.
    box(10, 10, 74, 50, "255,255,255,242", stroke="22,50,0,34")
    label("Where ONGO washes", 10, INK, 15, 14)
    sw = QgsLayoutItemShape(layout)
    for i, (txt, kind) in enumerate([("Service area: all of Doha", "svc"), ("Main roads", "road"), ("Popular areas", "pt")]):
        y = 26 + i * 9.5
        if kind == "svc":
            box(15, y, 8, 5, "160,232,112,170", stroke=GREEN, radius=1)
        elif kind == "road":
            box(15, y + 1.6, 8, 1.8, "#FFFFFF", stroke="22,50,0,102", radius=0.9)
        else:
            box(17.2, y + 0.2, 4.6, 4.6, GREEN, stroke="#A0E870", radius=2.3)
        label(txt, 7.8, INK, 27, y + 0.2, bold=False)
elif VARIANT == "night":
    label("ALL OF DOHA", 15, LIME, 12, 12, spacing=2.4)
    label("Live washer coverage · 25°17′N 51°32′E", 7.5, "#A9BBA9", 12, 22.5, bold=False)

north = label("N", 10, P["ink"], W - 16, 10)

exp = QgsLayoutExporter(layout)
svg = QgsLayoutExporter.SvgExportSettings()
svg.forceVectorOutput = True
svg.textRenderFormat = Qgis.TextRenderFormat.AlwaysText
svg.exportMetadata = False
svg.simplifyGeometries = True
base = os.path.join(OUT, f"ongo-doha-map-{VARIANT}" + ("-embed" if os.environ.get("NO_TITLE") else ""))
print("svg", exp.exportToSvg(base + ".svg", svg))
img = QgsLayoutExporter.ImageExportSettings()
img.dpi = 144
print("png", exp.exportToImage(base + ".png", img))
sys.stdout.flush()
os._exit(0)  # skip QGIS teardown, which segfaults headless
