---
name: multimodal-asset-engineering
description: Protocol and headless open-source toolkits for decompiling, inspecting, and surgically editing 3D meshes, 2D images, SVGs, typography fonts, and audio assets without blind procedural guessing.
---

# Multimodal Asset Engineering: Open-Source Decompilation & Inspection

> [!IMPORTANT]
> **SLOP-12: The LLM Asset Decompilation Law**:
> LLMs operate strictly in symbolic and mathematical spaces; they cannot procedurally sculpt 3D objects or rasterize visual art from raw code without producing stiff, plastic-looking artifacts.
> When working with digital media (3D meshes, images, vectors, fonts, audio), agents must never guess binary content. Instead, use headless open-source CLI tools to **decompile binary assets into structured ASTs, JSON schemas, or code components** that can be inspected and edited surgically.

---

## 1. The 6 Asset Modalities & Open-Source Toolkit Matrix

| Modality | Formats | Open-Source Toolkits | What The Agent Does |
| :--- | :--- | :--- | :--- |
| **1. 3D & Spatial Meshes** | `.glb`, `.gltf`, `.obj` | `glTF-Transform`, `gltfjsx`, `trimesh` | Inspect scene graphs, triangle counts, materials; decompile to JSX/Three.js code; Draco compress. |
| **2. 2D Raster Images** | `.png`, `.webp`, `.jpg` | `sharp`, `Pillow`, `vtracer`, `rembg` | Quantize palettes; convert rasters to SVG vectors; remove backgrounds; extract dominant hex colors. |
| **3. Vector Graphics** | `.svg`, Canvas | `svgo`, `paper.js`, `rough` | Parse SVG AST; sanitize and strip editor cruft; mutate fills, strokes, and viewBoxes programmatically. |
| **4. Typography & Fonts** | `.woff2`, `.ttf`, `.otf` | `fonttools` (`pyftsubset`), `opentype.js` | Subset glyphs (shrink 2MB fonts to 15KB); extract exact bezier curves for 3D extrusion/canvas rendering. |
| **5. Audio & Sound** | `.wav`, `.mp3`, `.opus` | `ffmpeg`, `Tone.js`, `howler.js` | Normalize loudness (-16 LUFS); slice audio sprites; synthesize procedural sound effects via Web Audio. |
| **6. Motion & Interactive** | Lottie JSON, Rive | `lottie-web`, `rive-wasm`, `GSAP` | Edit keyframe curves and vectors in JSON; wire reactive state machines under 50KB. |

---

## 2. Standard Operational Procedure (SOP) for Any Asset

1. **Step 1: Inspect (Decompile)**
   Run the headless inspector to extract dimensions, geometry, nodes, and chromatic palettes:
   ```bash
   python scripts/asset_inspector.py <path_to_asset>
   ```
2. **Step 2: Plan Surgical Mutation**
   Select the dedicated open-source CLI or library:
   - For 3D: `npx @gltf-transform/cli inspect <model.glb>` or `npx gltfjsx <model.glb> --transform`
   - For Raster: `vtracer` or `Pillow`
   - For SVG: `npx svgo input.svg -o cleaned.svg --pretty`
   - For Fonts: `pyftsubset font.ttf --text="..." --flavor=woff2`
3. **Step 3: Execute Deterministic Script**
   Write a small, focused 10-line Python or Node script to perform the exact mutation (e.g. palette recolor, texture swap, mesh decimation).
4. **Step 4: Verify Runtime Delivery**
   Confirm zero console warnings and verify rendering in the live preview workbench (`scripts/serve_preview.py`).
