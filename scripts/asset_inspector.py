#!/usr/bin/env python3
"""
Universal Asset Inspector & Manipulator (Harness Tool)
Inspects and decodes any multimodal asset (3D, 2D/Image, SVG, Font, Audio)
into structured human/LLM-readable JSON metadata, exposing its internal AST
and properties so the agent can understand and edit it programmatically.
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def inspect_image(file_path):
    from PIL import Image
    with Image.open(file_path) as img:
        info = {
            "type": "IMAGE",
            "format": img.format,
            "mode": img.mode,
            "width": img.width,
            "height": img.height,
            "aspect_ratio": round(img.width / max(1, img.height), 3),
            "has_transparency": img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info),
        }
        # Extract dominant color palette
        try:
            small = img.convert("RGB").resize((64, 64))
            colors = small.getcolors(maxcolors=4096)
            if colors:
                sorted_colors = sorted(colors, key=lambda c: c[0], reverse=True)[:6]
                info["dominant_colors_hex"] = [
                    f"#{c[1][0]:02x}{c[1][1]:02x}{c[1][2]:02x}" for c in sorted_colors
                ]
        except Exception as e:
            info["palette_error"] = str(e)
        return info

def inspect_svg(file_path):
    import xml.etree.ElementTree as ET
    tree = ET.parse(file_path)
    root = tree.getroot()
    # Strip namespaces for simple inspection
    tag = root.tag.split("}")[-1] if "}" in root.tag else root.tag
    view_box = root.attrib.get("viewBox", "N/A")
    width = root.attrib.get("width", "auto")
    height = root.attrib.get("height", "auto")
    
    paths = [elem for elem in root.iter() if elem.tag.endswith("path")]
    circles = [elem for elem in root.iter() if elem.tag.endswith("circle")]
    rects = [elem for elem in root.iter() if elem.tag.endswith("rect")]
    texts = [elem for elem in root.iter() if elem.tag.endswith("text")]

    fills = set()
    strokes = set()
    for elem in root.iter():
        f = elem.attrib.get("fill")
        if f and f != "none": fills.add(f)
        s = elem.attrib.get("stroke")
        if s and s != "none": strokes.add(s)

    return {
        "type": "SVG_VECTOR",
        "tag": tag,
        "viewBox": view_box,
        "width": width,
        "height": height,
        "element_counts": {
            "paths": len(paths),
            "circles": len(circles),
            "rectangles": len(rects),
            "text_elements": len(texts)
        },
        "color_fills": list(fills)[:8],
        "color_strokes": list(strokes)[:8]
    }

def inspect_font(file_path):
    from fontTools.ttLib import TTFont
    font = TTFont(file_path)
    glyph_names = font.getGlyphOrder()
    # Read name table for family and style
    family = "Unknown"
    style = "Unknown"
    if "name" in font:
        for record in font["name"].names:
            if record.nameID == 1:
                family = record.toUnicode()
            elif record.nameID == 2:
                style = record.toUnicode()
    
    upem = font["head"].unitsPerEm if "head" in font else 1000
    return {
        "type": "FONT",
        "family": family,
        "style": style,
        "units_per_em": upem,
        "glyph_count": len(glyph_names),
        "sample_glyphs": glyph_names[:15]
    }

def inspect_audio(file_path):
    cmd = [
        "ffmpeg", "-i", file_path,
        "-hide_banner"
    ]
    res = subprocess.run(cmd, stderr=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    output = res.stderr
    return {
        "type": "AUDIO",
        "ffmpeg_probe": [line.strip() for line in output.splitlines() if "Duration" in line or "Stream" in line][:4]
    }

def inspect_3d(file_path):
    # Use npx @gltf-transform/cli inspect
    cmd = ["npx.cmd", "@gltf-transform/cli", "inspect", file_path]
    res = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    return {
        "type": "3D_GLTF",
        "gltf_transform_report": res.stdout[:1500] if res.stdout else res.stderr[:500]
    }

def inspect_asset(path_str):
    path = Path(path_str)
    if not path.exists():
        return {"error": f"File does not exist: {path_str}"}

    size_kb = round(path.stat().st_size / 1024, 2)
    ext = path.suffix.lower()

    result = {
        "file_name": path.name,
        "file_size_kb": size_kb,
        "extension": ext
    }

    try:
        if ext in (".png", ".jpg", ".jpeg", ".webp", ".avif", ".bmp"):
            result.update(inspect_image(path))
        elif ext == ".svg":
            result.update(inspect_svg(path))
        elif ext in (".ttf", ".otf", ".woff", ".woff2"):
            result.update(inspect_font(path))
        elif ext in (".mp3", ".wav", ".ogg", ".opus", ".m4a"):
            result.update(inspect_audio(str(path)))
        elif ext in (".glb", ".gltf"):
            result.update(inspect_3d(str(path)))
        else:
            result["type"] = "GENERIC_BINARY"
            result["notice"] = f"Generic asset with extension {ext}"
    except Exception as e:
        result["inspection_error"] = str(e)

    return result

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/asset_inspector.py <path_to_asset>")
        sys.exit(1)

    target_path = sys.argv[1]
    data = inspect_asset(target_path)
    print(json.dumps(data, indent=2))
