# Automated 3D Terrain Generation (Auto3DGen)

**Auto3DGen** is a hybrid Python–C++–Unreal Engine project for **procedural 3D terrain generation**.  
It combines:

-   **Python** for terrain and forest generation
-   **C++ (Python extension)** for fast forest simulation
-   **Unreal Engine 5.6** for real-time visualization and asset instancing

The system allows interactive terrain design, procedural vegetation placement adapted to terrain features, and seamless export into Unreal Engine.

---

## Features

-   Procedural terrain generation using **Perlin noise**
-   Manual mountain shaping via Gaussian height masks
-   Fast forest simulation using a **C++ backend (PyForest)**
-   Vegetation placement adapted to:
    -   terrain height
    -   terrain slope
-   Interactive **Streamlit UI**
-   One-click export to **Unreal Engine**
-   Efficient vegetation rendering using **Instanced Static Meshes**

---

## Architecture Overview

```bash
Python (UI & Generation)
│
├── Perlin Noise Terrain
├── Gaussian Mountains
├── Forest Simulation (C++ / PyForest)
│
└── config.json
↓
Unreal Engine 5
├── Terrain Loader (Blueprint + C++)
├── Landscape Builder
└── Vegetation Spawner (ISM)
```

---

## Project Structure

```bash
automated_3d_terrain_generation/
│
├── main.py                # Streamlit UI & pipeline controller
├── utils.py               # Terrain & forest generation logic
├── setup.py               # PyForest C++ extension build
├── requirements.txt
├── Auto3DGen.uproject     # Unreal Engine project
│
├── pyforest_src/          # C++ forest simulation (Python module)
│   └── pyforest/
│       ├── pyforest.cpp
│       ├── cpp_module_wrapper.py
│       └── README.md
│
├── Content/               # Unreal assets (Blueprints, Materials, Maps)
│
└── Source/Auto3DGen/      # Unreal C++ integration
    ├── TerrainLoader.*
    └── VegetationSpawner.*
```

---

## Installation & Setup

### Python environment

```bash
python -m venv venv
source venv/bin/activate # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Build PyForest (C++ extension)

```bash
pip install .
```

> Requires a C++ compiler compatible with your Python version  
> On Windows: **Visual Studio Build Tools**

---

## Running the Application

Start the interactive UI:

```bash
streamlit run main.py
```

You can:

-   adjust terrain resolution
-   tune Perlin noise parameters
-   place and edit mountains
-   configure forest growth simulation
-   preview terrain and vegetation
-   export directly to Unreal Engine

---

## Terrain Generation

Terrain heightmaps are generated using **Perlin noise**, normalized to `[0,1]`.

Optional **mountains** are applied using 2D Gaussian functions:

-   position `(x, y)`
-   spread (`sigma`)
-   amplitude

Final terrain:

```python
terrain = normalized_perlin * (terrain_amplifier + mountain_mask)
```

---

## Forest Generation (PyForest)

Forest simulation is implemented in **C++** for performance and exposed to Python.

Simulation steps:

1. Initial random trees
2. Seed spreading
3. Probabilistic growth
4. Seed decay
5. Spacing constraints

Vegetation is filtered based on terrain:

-   too steep slopes
-   too low or too high elevation

Vegetation map values:

-   `-1` – UNPLANTABLE
-   `0` – EMPTY
-   `1` – SEED
-   `2` – TREE

---

## Export to Unreal Engine

When **Export to Unreal** is clicked:

1. Terrain + vegetation data is saved as `config.json`
2. Unreal reads the file using `UTerrainLoader`
3. Landscape and vegetation are rebuilt automatically

### Unreal-side components:

-   `BP_LandscapeBuilder`
-   `AVegetationSpawner`
-   `InstancedStaticMeshComponent` for performance

---

## ️ Unreal Engine Version

-   **Unreal Engine 5.6**
-   Required plugin:
    -   `ModelingToolsEditorMode`

---

## Notes

-   Python and Unreal must share the same project directory
-   `config.json` is the communication bridge
-   Vegetation instancing is optimized for large terrains

---

## License

MIT License
