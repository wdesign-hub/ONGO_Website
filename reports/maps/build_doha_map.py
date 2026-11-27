"""Build the ONGO 'All of Doha' coverage map with QGIS and export SVG + PNG.

Usage: QT_QPA_PLATFORM=offscreen python3.12 build_map.py <geo_dir> <out_dir>
"""
import os
import sys

from qgis.core import (
    Qgis,
    QgsApplication, QgsVectorLayer, QgsProject, QgsRectangle, QgsCoordinateReferenceSystem,
    QgsFillSymbol, QgsLineSymbol, QgsMarkerSymbol, QgsSingleSymbolRenderer, QgsRuleBasedRenderer,
    QgsPalLayerSettings, QgsTextFormat, QgsTextBufferSettings, QgsVectorLayerSimpleLabeling,
    QgsPrintLayout, QgsLayoutItemMap, QgsLayoutItemScaleBar, QgsLayoutItemLabel, QgsLayoutPoint,
    QgsLayoutSize, QgsUnitTypes, QgsLayoutExporter, QgsFeature, QgsGeometry, QgsPointXY, QgsField,
    QgsFeatureRequest, QgsLayoutItemPage, QgsLayoutMeasurement, QgsSimpleLineSymbolLayer, QgsSimpleMarkerSymbolLayer,
)
from qgis.PyQt.QtCore import QVariant
from qgis.PyQt.QtGui import QColor, QFont

GEO, OUT = sys.argv[1], sys.argv[2]
os.makedirs(OUT, exist_ok=True)

GREEN, LIME, INK = "#163200", "#A0E870", "#0E1411"
SEA, LAND, ZONE = "#DCE8EC", "#F7F9F3", "#16320024"

app = QgsApplication([], False)
app.initQgis()
proj = QgsProject.instance()
wgs = QgsCoordinateReferenceSystem("EPSG:4326")
utm = QgsCoordinateReferenceSystem("EPSG:32639")  # UTM 39N: true shapes for Qatar
proj.setCrs(utm)

# Land: all municipalities, light paper.
land = QgsVectorLayer(os.path.join(GEO, "ADM1_media.gpkg"), "Municipalities", "ogr")
land.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(
    {"color": LAND, "outline_color": "#16320040", "outline_width": "0.25"})))

# Service area: greater Doha's urban zones (Doha, Lusail/Al Daayen and the eastern Al Rayyan zones such as Al Waab),
# built by dissolving the official zone polygons whose centre lies in the urban belt.
zsrc = QgsVectorLayer(os.path.join(GEO, "ADM2_media.gpkg"), "zsrc", "ogr")
parts = []
for ft in zsrc.getFeatures():
    c = ft.geometry().centroid().asPoint()
    if c.x() >= 51.38 and 25.185 <= c.y() <= 25.46:
        parts.append(ft.geometry())
merged = QgsGeometry.unaryUnion(parts)
service = QgsVectorLayer("Polygon?crs=EPSG:4326", "Service area", "memory")
sf = QgsFeature()
sf.setGeometry(merged)
service.dataProvider().addFeature(sf)
service.updateExtents()
service.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(
    {"color": "160,232,112,95", "outline_color": GREEN, "outline_width": "0.6"})))

# Zones: faint lines that give the city its real street-block texture.
zones = QgsVectorLayer(os.path.join(GEO, "ADM2_media.gpkg"), "Zones", "ogr")
zones.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(
    {"color": "0,0,0,0", "outline_color": ZONE, "outline_width": "0.2"})))

# Major roads (Natural Earth): white casing over a soft line.
roads = QgsVectorLayer(os.path.join(GEO, "ne_roads.gpkg"), "Major roads", "ogr")
road_sym = QgsLineSymbol.createSimple({"line_color": "#16320055", "line_width": "1.1", "capstyle": "round"})
inner = QgsSimpleLineSymbolLayer.create({"line_color": "#ffffff", "line_width": "0.6", "capstyle": "round"})
road_sym.appendSymbolLayer(inner)
roads.setRenderer(QgsSingleSymbolRenderer(road_sym))

# The six areas named on the ONGO site (approximate centre of each district, WGS84).
areas = [
    ("West Bay", 51.5290, 25.3225, "right"),
    ("The Pearl", 51.5505, 25.3710, "right"),
    ("Lusail", 51.4930, 25.4190, "left"),
    ("Msheireb", 51.5265, 25.2860, "right"),
    ("Al Sadd", 51.4985, 25.2830, "left"),
    ("Al Waab", 51.4560, 25.2580, "left"),
]
pts = QgsVectorLayer("Point?crs=EPSG:4326", "ONGO areas", "memory")
pr = pts.dataProvider()
pr.addAttributes([QgsField("name", QVariant.String), QgsField("side", QVariant.String)])
pts.updateFields()
for name, x, y, side in areas:
    f = QgsFeature(pts.fields())
    f.setGeometry(QgsGeometry.fromPointXY(QgsPointXY(x, y)))
    f["name"], f["side"] = name, side
    pr.addFeature(f)
pts.updateExtents()

halo = QgsMarkerSymbol.createSimple({"name": "circle", "color": "160,232,112,110", "outline_style": "no", "size": "7"})
dot = QgsSimpleMarkerSymbolLayer.create({"name": "circle", "color": GREEN, "outline_color": "#ffffff", "outline_width": "0.5", "size": "3.2"})
halo.appendSymbolLayer(dot)
pts.setRenderer(QgsSingleSymbolRenderer(halo))


def text_format(size, color, bold=True, buffer=True):
    tf = QgsTextFormat()
    font = QFont("Roboto")
    font.setBold(bold)
    tf.setFont(font)
    tf.setSize(size)
    tf.setColor(QColor(color))
    if buffer:
        b = QgsTextBufferSettings()
        b.setEnabled(True)
        b.setSize(1.0)
        b.setColor(QColor("#ffffff"))
        tf.setBuffer(b)
    return tf


lab = QgsPalLayerSettings()
lab.fieldName = "name"
lab.setFormat(text_format(10.5, INK))
lab.placement = QgsPalLayerSettings.OrderedPositionsAroundPoint
lab.dist = 2.2
lab.isExpression = False
pts.setLabelsEnabled(True)
pts.setLabeling(QgsVectorLayerSimpleLabeling(lab))

# Municipality name for the sea-side context (Doha / Al Daayen / Al Rayyan / Al Wakra) in quiet caps.
mlab = QgsPalLayerSettings()
mlab.isExpression = True
mlab.fieldName = "upper(\"shapeName\")"
tf = text_format(7.5, "#3F4A43", bold=False, buffer=False)
tf.setOpacity(0.7)
mlab.setFormat(tf)
mlab.placement = QgsPalLayerSettings.OverPoint
land.setLabelsEnabled(True)
land.setLabeling(QgsVectorLayerSimpleLabeling(mlab))

for lyr in (land, service, zones, roads, pts):
    if not lyr.isValid():
        raise SystemExit(f"layer failed: {lyr.name()}")
    proj.addMapLayer(lyr)

# Layout: 1200 x 900 px artboard (mm at 96 dpi).
layout = QgsPrintLayout(proj)
layout.initializeDefaults()
page = layout.pageCollection().page(0)
W, H = 317.5, 238.125  # 1200 x 900 px
page.setPageSize(QgsLayoutSize(W, H, QgsUnitTypes.LayoutMillimeters))

m = QgsLayoutItemMap(layout)
m.attemptMove(QgsLayoutPoint(0, 0, QgsUnitTypes.LayoutMillimeters))
m.attemptResize(QgsLayoutSize(W, H, QgsUnitTypes.LayoutMillimeters))
m.setCrs(utm)
m.setBackgroundColor(QColor(SEA))
m.setLayers([pts, roads, zones, service, land])
ext_wgs = QgsRectangle(51.385, 25.205, 51.625, 25.455)
from qgis.core import QgsCoordinateTransform
xf = QgsCoordinateTransform(wgs, utm, proj)
m.zoomToExtent(xf.transformBoundingBox(ext_wgs))
m.setFrameEnabled(False)
layout.addLayoutItem(m)

sb = QgsLayoutItemScaleBar(layout)
sb.setStyle("Single Box")
sb.setLinkedMap(m)
sb.setUnits(QgsUnitTypes.DistanceKilometers)
sb.setUnitLabel("km")
sb.setNumberOfSegments(2)
sb.setNumberOfSegmentsLeft(0)
sb.setUnitsPerSegment(2.0)
sb.setTextFormat(text_format(8, INK, bold=False, buffer=False))
sb.setFillColor(QColor(GREEN))
sb.setFillColor2(QColor("#ffffff"))
sb.setLineColor(QColor(GREEN))
sb.attemptMove(QgsLayoutPoint(12, H - 22, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(sb)

north = QgsLayoutItemLabel(layout)
north.setText("N ↑")
north.setTextFormat(text_format(11, GREEN))
north.adjustSizeToText()
north.attemptMove(QgsLayoutPoint(W - 22, 10, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(north)

credit = QgsLayoutItemLabel(layout)
credit.setText("Boundaries: geoBoundaries · Roads: Natural Earth · Area points approximate")
credit.setTextFormat(text_format(6.5, "#3F4A43", bold=False, buffer=False))
credit.setMarginX(2.5)
credit.setMarginY(1.5)
credit.adjustSizeToText()
credit.setBackgroundEnabled(True)
credit.setBackgroundColor(QColor(255, 255, 255, 230))
credit.attemptMove(QgsLayoutPoint(W - credit.rect().width() - 6, H - credit.rect().height() - 5, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(credit)

# Inset: all of Qatar, with the main map's extent outlined.
qland = QgsVectorLayer(os.path.join(GEO, "ADM1_media.gpkg"), "Qatar", "ogr")
qland.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(
    {"color": "#EAF0E6", "outline_color": "#16320055", "outline_width": "0.15"})))
box = QgsVectorLayer("Polygon?crs=EPSG:4326", "Extent", "memory")
bf = QgsFeature()
bf.setGeometry(QgsGeometry.fromRect(ext_wgs))
box.dataProvider().addFeature(bf)
box.setRenderer(QgsSingleSymbolRenderer(QgsFillSymbol.createSimple(
    {"color": "160,232,112,150", "outline_color": GREEN, "outline_width": "0.5"})))
proj.addMapLayer(qland, False)
proj.addMapLayer(box, False)
inset = QgsLayoutItemMap(layout)
IW, IH = 46, 58
inset.attemptMove(QgsLayoutPoint(10, 10, QgsUnitTypes.LayoutMillimeters))
inset.attemptResize(QgsLayoutSize(IW, IH, QgsUnitTypes.LayoutMillimeters))
inset.setCrs(utm)
inset.setLayers([box, qland])
inset.zoomToExtent(xf.transformBoundingBox(QgsRectangle(50.70, 24.42, 51.72, 26.22)))
inset.setBackgroundColor(QColor(SEA))
inset.setFrameEnabled(True)
inset.setFrameStrokeColor(QColor("#ffffff"))
inset.setFrameStrokeWidth(QgsLayoutMeasurement(0.8, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(inset)
qlabel = QgsLayoutItemLabel(layout)
qlabel.setText("QATAR")
qlabel.setTextFormat(text_format(7, "#3F4A43", bold=True, buffer=False))
qlabel.adjustSizeToText()
qlabel.attemptMove(QgsLayoutPoint(13, 12, QgsUnitTypes.LayoutMillimeters))
layout.addLayoutItem(qlabel)

exp = QgsLayoutExporter(layout)
svg = QgsLayoutExporter.SvgExportSettings()
svg.exportAsLayers = False
svg.forceVectorOutput = True
svg.textRenderFormat = Qgis.TextRenderFormat.AlwaysText  # keep labels as real, editable text
svg.exportMetadata = False
r1 = exp.exportToSvg(os.path.join(OUT, "ongo-doha-coverage-map.svg"), svg)
img = QgsLayoutExporter.ImageExportSettings()
img.dpi = 192
r2 = exp.exportToImage(os.path.join(OUT, "ongo-doha-coverage-map.png"), img)
print("svg", r1, "png", r2)
app.exitQgis()
