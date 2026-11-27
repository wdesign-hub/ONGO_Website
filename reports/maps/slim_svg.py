"""Shrink a Qt/QGIS SVG export: drop empty groups, round path coordinates, tidy metadata.

Usage: python3 slim_svg.py <in.svg> <out.svg> <title>
"""
import re
import sys

src, dst, title = sys.argv[1], sys.argv[2], sys.argv[3]
s = open(src, encoding="utf-8").read()

# Empty self-closing groups carry no drawing.
s = re.sub(r"<g [^>]*/>\s*", "", s)

num = re.compile(r"-?\d+\.\d+")


def round_d(m):
    return m.group(1) + num.sub(lambda n: ("%.1f" % float(n.group())).rstrip("0").rstrip("."), m.group(2)) + m.group(3)


s = re.sub(r'(\sd=")([^"]*)(")', round_d, s)
s = re.sub(r'(\spoints=")([^"]*)(")', round_d, s)
s = s.replace('font-family="Inter"', 'font-family="Roboto"')
s = re.sub(r"<title>.*?</title>", f"<title>{title}</title>", s, count=1)
s = re.sub(r"<desc>.*?</desc>",
           "<desc>Made in QGIS 3.34. Map data © OpenStreetMap contributors via Overture Maps; boundaries: geoBoundaries.</desc>",
           s, count=1)
s = re.sub(r'height="[\d.]+mm"', 'height="1000"', s, count=1)
s = re.sub(r'width="[\d.]+mm"', 'width="1200"', s, count=1)
s = re.sub(r">\s+<", "><", s)
open(dst, "w", encoding="utf-8").write(s)
print(dst, len(s))
