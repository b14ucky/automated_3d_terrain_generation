import subprocess
import numpy as np
import streamlit as st
import matplotlib.cm as cm
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
        width = st.number_input(
            "Width",
            min_value=100,
            value=250,
            help="Terrain width in units. Higher values create larger landscapes.",
        )
    with height_col:
        height = st.number_input(
            "Height",
            min_value=100,
            value=250,
            help="Terrain height in units. Higher values create larger landscapes.",
        )

    # perlin noise settings section
    st.divider()
    st.write("Perlin Noise Settings")

    pnoise_left, pnoise_right = st.columns(2)

    with pnoise_left:
        scale = st.slider(
            "Scale:",
            min_value=2.0,
            max_value=500.0,
            value=50.0,
            help="Controls the overall size of noise features. Larger values create bigger terrain variations.",
        )
        octaves = st.slider(
            "Octaves:",
            min_value=1,
            max_value=10,
            value=4,
            help="Number of noise layers. More octaves add finer detail but increase processing time.",
        )

    with pnoise_right:
        persistence = st.slider(
            "Persistence:",
            min_value=0.01,
            max_value=1.0,
            value=0.5,
            help="Controls how much each octave contributes. Higher values preserve detail at smaller scales.",
        )
        lacunarity = st.slider(
            "Lacunarity:",
            min_value=0.01,
            max_value=10.0,
            value=2.0,
            help="Frequency multiplier for each octave. Higher values create more varied terrain features.",
        )

    repeatx_col, repeaty_col, base_col = st.columns(3)

    with repeatx_col:
        repeatx = st.number_input(
            "Repeat x:",
            min_value=0.0,
            value=1024.0,
            help="Horizontal repeat distance for seamless noise tiling.",
        )
    with repeaty_col:
        repeaty = st.number_input(
            "Repeat y:",
            min_value=0.0,
            value=1024.0,
            help="Vertical repeat distance for seamless noise tiling.",
        )
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
        mountain_num = st.number_input(
            "Number of mountains:",
            min_value=0,
            step=1,
            help="Number of gaussian peaks to add to the terrain.",
        )

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
            help="Horizontal position of the mountain peak.",
        )

        st.slider(
            "Y:",
            min_value=0,
            max_value=height,
            value=mountain["y"],
            key=f"y_mountain{active_idx}",
            on_change=update_mountain_state,
            args=(active_idx, "y", f"y_mountain{active_idx}"),
            help="Vertical position of the mountain peak.",
        )

        st.slider(
            "Sigma:",
            min_value=0.01,
            max_value=500.0,
            value=mountain["sigma"],
            key=f"s_mountain{active_idx}",
            on_change=update_mountain_state,
            args=(active_idx, "sigma", f"s_mountain{active_idx}"),
            help="Width of the mountain (standard deviation). Lower values create sharper peaks.",
        )

        st.slider(
            "Amplitude:",
            min_value=0.01,
            max_value=2.0,
            value=mountain["amplitude"],
            key=f"a_mountain{active_idx}",
            on_change=update_mountain_state,
            args=(active_idx, "amplitude", f"a_mountain{active_idx}"),
            help="Height multiplier of the mountain peak. Higher values create taller mountains.",
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

    with trees_left:
        initial_trees = st.number_input(
            "Number of initial trees:",
            min_value=0,
            value=3,
            help="Starting number of trees placed randomly on the terrain.",
        )
        space_between_trees = st.number_input(
            "Space between trees:",
            min_value=5,
            help="Minimum distance required between tree centers to prevent overcrowding.",
        )
        n_iterations = st.number_input(
            "Number of iterations:",
            min_value=1,
            value=3,
            help="Number of growth cycles for the forest expansion algorithm.",
        )

    with trees_rigth:
        seed_radius = st.number_input(
            "Seeding radius:",
            min_value=0,
            value=15,
            help="Distance at which trees can spread seeds to new locations.",
        )
        seed_strength = st.number_input(
            "Seed strength:",
            min_value=0.00,
            max_value=1.00,
            value=0.05,
            step=0.01,
            help="Probability of a seed growing into a new tree. Lower values = sparser forests.",
        )
        seed_decay_rate = st.number_input(
            "Seed decay rate:",
            min_value=0.00,
            max_value=1.00,
            value=0.2,
            step=0.01,
            help="How quickly seed influence diminishes with distance. Higher values = more localized growth.",
        )

    forest_config = PyForestConfig(
        width=width,
        height=height,
        initial_trees=initial_trees,
        seed_radius=seed_radius,
        seed_strength=seed_strength,
        seed_decay_rate=seed_decay_rate,
        n_iterations=n_iterations,
        space_between_trees=space_between_trees,
    )

with left:
    with st.spinner("Generating..."):
        heightmap = generate_heightmap(
            config=config, mountains=mountains, terrain_amplifier=0.7
        )
        forest_map = generate_forest_adapted_to_terrain(
            config=forest_config, heightmap=heightmap
        )

    colored_map = cm.terrain(heightmap)  # type: ignore
    img_array = (colored_map[:, :, :3] * 255).astype("uint8")
    image = Image.fromarray(img_array)
    draw = ImageDraw.Draw(image)

    y_trees, x_trees = np.where(forest_map == VegetationType.TREE)

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
            if st.button("Refresh", width="stretch"):
                pass

        with col_right:
            if st.button("Export to Unreal", width="stretch"):
                config_path, exe_path = resolve_paths()

                TerrainConfig(
                    XSize=width,
                    YSize=height,
                    Scale=100.0,
                    ZMultiplier=7000.0,
                    UVScale=1.0,
                    Heightmap=heightmap.reshape(-1).tolist(),
                    VegetationMap=forest_map.reshape(-1).tolist(),
                ).export_to_json(config_path)

                if exe_path:
                    subprocess.run(exe_path)
