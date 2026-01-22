import subprocess
import numpy as np
from enum import Enum
import streamlit as st
import matplotlib.cm as cm
from dataclasses import asdict
from PIL import Image, ImageDraw
from pyforest import VegetationType
from utils import (
    Mountain,
    resolve_paths,
    TerrainConfig,
    PyForestConfig,
    PerlinNoiseConfig,
    generate_heightmap,
    generate_forest_adapted_to_terrain,
)


st.set_page_config(page_title="Auto 3D Terrain Generator", layout="wide")
left, right = st.columns([1, 2])

st.markdown(
    """
    <style>
    div[data-testid="stColumn"]:first-child {
        position: sticky;
        top: 6rem;
        height: fit-content;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

with right:

    # basic setting section
    st.write("Basic Settings")
    width_col, height_col = st.columns(2)

    with width_col:
        width = st.number_input("Width", min_value=100, value=250)
    with height_col:
        height = st.number_input("Height", min_value=100, value=250)

    # perlin noise settings section
    st.divider()
    st.write("Perlin Noise Settings")

    pnoise_left, pnoise_right = st.columns(2)

    with pnoise_left:
        scale = st.slider("Scale:", min_value=2.0, max_value=500.0, value=50.0)
        octaves = st.slider("Octaves:", min_value=1, max_value=10, value=4)

    with pnoise_right:
        persistence = st.slider(
            "Persistence:", min_value=0.01, max_value=1.0, value=0.5
        )
        lacunarity = st.slider(
            "Lacunarity:", min_value=0.01, max_value=10.0, value=2.0
        )

    repeatx_col, repeaty_col, base_col = st.columns(3)

    with repeatx_col:
        repeatx = st.number_input("Repeat x:", min_value=0.0, value=1024.0)
    with repeaty_col:
        repeaty = st.number_input("Repeat y:", min_value=0.0, value=1024.0)
    with base_col:
        base = st.number_input(
            "Base:",
            min_value=0,
            help=(
                "Specifies a fixed offset for the noise coordinates. Useful for"
                + " generating different noise textures with the same repeat interval."
            ),
        )

    config = PerlinNoiseConfig(
        height=height,
        width=width,
        scale=scale,
        octaves=octaves,
        persistence=persistence,
        lacunarity=lacunarity,
        repeatx=repeatx,
        repeaty=repeaty,
        base=base,
    )

    # mountains settings section
    st.divider()
    st.write("Mountains")

    col_n, col_sel = st.columns([2, 1])

    with col_n:
        mountain_num = st.number_input("Number of mountains:", min_value=0, step=1)

    if "mountain_state" not in st.session_state:
        st.session_state.mountain_state = []

    while len(st.session_state.mountain_state) < mountain_num:
        st.session_state.mountain_state.append(
            {
                "x": width // 2,
                "y": height // 2,
                "sigma": 10.0,
                "amplitude": 1.0,
            }
        )

    if len(st.session_state.mountain_state) > mountain_num:
        st.session_state.mountain_state = st.session_state.mountain_state[
            :mountain_num
        ]

    with col_sel:
        active_idx = st.selectbox(
            "Edit mountain:",
            options=list(range(mountain_num)),
            format_func=lambda i: f"#{i + 1}",
            key="active_mountain_idx",
            placeholder="Choose a mountain",
        )

    if active_idx is not None:

        mountain = st.session_state.mountain_state[active_idx]

        def update_mountain_state(idx, param_name, widget_key):
            st.session_state.mountain_state[idx][param_name] = st.session_state[
                widget_key
            ]

        st.slider(
            "X:",
            min_value=0,
            max_value=width,
            value=mountain["x"],
            key=f"x_mountain{active_idx}",
            on_change=update_mountain_state,
            args=(active_idx, "x", f"x_mountain{active_idx}"),
        )

        st.slider(
            "Y:",
            min_value=0,
            max_value=height,
            value=mountain["y"],
            key=f"y_mountain{active_idx}",
            on_change=update_mountain_state,
            args=(active_idx, "y", f"y_mountain{active_idx}"),
        )

        st.slider(
            "Sigma:",
            min_value=0.01,
            max_value=500.0,
            value=mountain["sigma"],
            key=f"s_mountain{active_idx}",
            on_change=update_mountain_state,
            args=(active_idx, "sigma", f"s_mountain{active_idx}"),
        )

        st.slider(
            "Amplitude:",
            min_value=0.01,
            max_value=2.0,
            value=mountain["amplitude"],
            key=f"a_mountain{active_idx}",
            on_change=update_mountain_state,
            args=(active_idx, "amplitude", f"a_mountain{active_idx}"),
        )

    mountains = (
        [Mountain(**m) for m in st.session_state.mountain_state]
        if "mountain_state" in st.session_state
        else None
    )

    # forest settings section
    st.divider()
    st.write("Forest settings")

    trees_left, trees_rigth = st.columns(2)

    if "forest_config" not in st.session_state:
        st.session_state.forest_config = PyForestConfig(
            width=width,
            height=height,
        )

    def update_forest(key: str | None = None) -> None:
        forest_config_dict = asdict(st.session_state.forest_config)

        if key is not None:
            forest_config_dict[key] = st.session_state[key]
            st.session_state.forest_config = PyForestConfig(**forest_config_dict)

        # if "heightmap" in st.session_state:
        st.session_state.forest_map = generate_forest_adapted_to_terrain(
            config=st.session_state.forest_config,
            heightmap=st.session_state.heightmap,
        )

    with trees_left:
        initial_trees = st.number_input(
            "Number of initial trees:",
            min_value=0,
            value=3,
            key="initial_trees",
            on_change=update_forest,
            args=("initial_trees",),
        )
        space_between_trees = st.number_input(
            "Space between trees:",
            min_value=5,
            key="space_between_trees",
            on_change=update_forest,
            args=("space_between_trees",),
        )
        n_iterations = st.number_input(
            "Number of iterations:",
            min_value=1,
            value=3,
            key="n_iterations",
            on_change=update_forest,
            args=("n_iterations",),
        )

    with trees_rigth:
        seed_radius = st.number_input(
            "Seeding radius:",
            min_value=0,
            value=15,
            key="seed_radius",
            on_change=update_forest,
            args=("seed_radius",),
        )
        seed_strength = st.number_input(
            "Seed strength:",
            min_value=0.00,
            max_value=1.00,
            value=0.05,
            step=0.01,
            key="seed_strength",
            on_change=update_forest,
            args=("seed_strength",),
        )
        seed_decay_rate = st.number_input(
            "Seed decay rate:",
            min_value=0.00,
            max_value=1.00,
            value=0.2,
            step=0.01,
            key="seed_decay_rate",
            on_change=update_forest,
            args=("seed_decay_rate",),
        )

    # water settings section
    st.divider()
    st.write("Water settings")

    _, water_left, water_right = st.columns([0.5, 1, 3])

    with water_left:
        water_on = st.toggle("Water", help="Enable water coverage on the terrain")

    with water_right:
        water_position = st.slider(
            "Water level:",
            min_value=0.2,
            max_value=0.5,
            step=0.01,
            help="Determines the water level on the terrain. Higher values create more water coverage.",
            disabled=not water_on,
        )

    default_water_position = 0.2
    magic_water_level_multiplier = 1.75
    final_water_position = (
        (
            1.0
            - (water_position - default_water_position)
            * magic_water_level_multiplier
        )
        if water_on
        else 1
    )

    # fog settings section
    st.divider()
    st.write("Fog settings")

    _, fog_left, fog_right = st.columns([0.5, 1, 3])

    with fog_left:
        fog_on = st.toggle("Fog", help="Enable fog effect in the scene")

    with fog_right:
        fog_density = st.slider(
            "Fog density:",
            min_value=0,
            max_value=7,
            value=1,
            step=1,
            help="Controls fog opacity. Higher values make the fog denser and more opaque.",
            disabled=not fog_on,
        )

    final_fog_density = fog_density * 1000 - 1000

with left:
    with st.spinner("Generating..."):
        st.session_state.heightmap = generate_heightmap(
            config=config, mountains=mountains, terrain_amplifier=0.7
        )

        st.session_state.heightmap = (
            st.session_state.heightmap * final_water_position
            if water_on
            else st.session_state.heightmap + 0.2
        )

        if "forest_map" not in st.session_state:
            st.session_state.forest_map = generate_forest_adapted_to_terrain(
                config=st.session_state.forest_config,
                heightmap=st.session_state.heightmap,
            )

    colored_map = cm.terrain(st.session_state.heightmap)  # type: ignore
    img_array = (colored_map[:, :, :3] * 255).astype("uint8")
    image = Image.fromarray(img_array)
    draw = ImageDraw.Draw(image)

    y_trees, x_trees = np.where(st.session_state.forest_map == VegetationType.TREE)

    tree_size = 4
    for x, y in zip(x_trees, y_trees):
        coords = [
            (x, y - tree_size),
            (x - tree_size, y + tree_size),
            (x + tree_size, y + tree_size),
        ]
        draw.polygon(coords, fill="green", outline="darkgreen")

    st.image(image, caption="Terrain Preview", width="stretch")
    with st.container(horizontal_alignment="center"):
        col_left, col_right = st.columns(2)
        with col_left:
            if st.button("Update Forest", width="stretch"):
                update_forest()
                st.rerun()

        with col_right:
            if st.button("Export to Unreal", width="stretch"):
                config_path, exe_path = resolve_paths()

                TerrainConfig(
                    XSize=width,
                    YSize=height,
                    Scale=100.0,
                    ZMultiplier=7000.0,
                    UVScale=1.0,
                    Heightmap=st.session_state.heightmap.reshape(-1).tolist(),
                    VegetationMap=st.session_state.forest_map.reshape(-1).tolist(),
                    bWaterOn=water_on,
                    WaterHeight=water_position,
                    bFogOn=fog_on,
                    FogDensity=final_fog_density,
                ).export_to_json(config_path)

                if exe_path:
                    subprocess.run(exe_path)
