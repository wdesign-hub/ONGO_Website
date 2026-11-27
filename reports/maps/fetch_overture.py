"""Fetch Overture Maps features inside a bbox by reading only matching Parquet row groups over HTTPS.

Usage: python3 fetch_overture.py <out_dir> <theme/type> [<theme/type> ...]
Writes <out_dir>/<type>.geojson
"""
import json
import os
import re
import sys
from concurrent.futures import ThreadPoolExecutor

import fsspec
import pyarrow.parquet as pq
import requests
from shapely import wkb
from shapely.geometry import mapping

BASE = "https://overturemaps-us-west-2.s3.amazonaws.com"
REL = "release/2026-11-18.0"
XMIN, YMIN, XMAX, YMAX = 51.36, 25.15, 51.68, 25.48

out_dir = sys.argv[1]
os.makedirs(out_dir, exist_ok=True)
fs = fsspec.filesystem("http", client_kwargs={"trust_env": True}, block_size=2 ** 20)


def list_keys(prefix):
    keys, token = [], None
    while True:
        url = f"{BASE}/?list-type=2&prefix={prefix}"
        if token:
            url += "&continuation-token=" + requests.utils.quote(token)
        t = requests.get(url, timeout=60).text
        keys += re.findall(r"<Key>([^<]+)</Key>", t)
        m = re.search(r"<NextContinuationToken>([^<]+)</NextContinuationToken>", t)
        if not m:
            return keys
        token = m.group(1)


def col_index(schema, path):
    for i in range(len(schema)):
        if schema.column(i).path == path:
            return i
    return None


def scan(key):
    url = f"{BASE}/{key}"
    rows = []
    with fs.open(url, "rb") as fh:
        pf = pq.ParquetFile(fh)
        md, sch = pf.metadata, pf.schema
        ix = {k: col_index(sch, f"bbox.{k}") for k in ("xmin", "xmax", "ymin", "ymax")}
        keep = []
        for rg in range(md.num_row_groups):
            g = md.row_group(rg)
            s = {k: g.column(i).statistics for k, i in ix.items()}
            if any(v is None or not v.has_min_max for v in s.values()):
                keep.append(rg)
                continue
            if s["xmin"].min <= XMAX and s["xmax"].max >= XMIN and s["ymin"].min <= YMAX and s["ymax"].max >= YMIN:
                keep.append(rg)
        if not keep:
            return rows
        names = [n for n in ("id", "geometry", "bbox", "class", "subclass", "subtype", "names", "road_flags") if n in pf.schema_arrow.names]
        for rg in keep:
            t = pf.read_row_group(rg, columns=names).to_pylist()
            for r in t:
                b = r["bbox"]
                if b["xmin"] > XMAX or b["xmax"] < XMIN or b["ymin"] > YMAX or b["ymax"] < YMIN:
                    continue
                rows.append(r)
    return rows


for tt in sys.argv[2:]:
    keys = [k for k in list_keys(f"{REL}/theme={tt.split('/')[0]}/type={tt.split('/')[1]}/") if k.endswith(".parquet") or "part-" in k]
    feats = []
    with ThreadPoolExecutor(8) as ex:
        for rows in ex.map(scan, keys):
            for r in rows:
                props = {"class": r.get("class"), "subclass": r.get("subclass"), "subtype": r.get("subtype")}
                nm = r.get("names") or {}
                props["name"] = nm.get("primary") if isinstance(nm, dict) else None
                feats.append({"type": "Feature", "geometry": mapping(wkb.loads(r["geometry"])), "properties": props})
    name = tt.split("/")[1]
    with open(os.path.join(out_dir, f"{name}.geojson"), "w") as f:
        json.dump({"type": "FeatureCollection", "features": feats}, f)
    print(tt, len(keys), "files ->", len(feats), "features", flush=True)
