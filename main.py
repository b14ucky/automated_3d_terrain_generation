import streamlit as st
import matplotlib.pyplot as plt
from utils import PerlinNoiseConfig, generate_heightmap, Mountain


st.set_page_config(layout="wide")
left, right = st.columns([1, 2])

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

        x = st.slider(
            "X:",
            min_value=0,
            max_value=width,
            value=mountain["x"],
            key=f"x_mountain{active_idx}",
        )
        y = st.slider(
            "Y:",
            min_value=0,
            max_value=height,
            value=mountain["y"],
            key=f"y_mountain{active_idx}",
        )
        sigma = st.slider(
            "Sigma:",
            min_value=0.01,
            max_value=500.0,
            value=mountain["sigma"],
            key=f"s_mountain{active_idx}",
        )
        amplitude = st.slider(
            "Amplitude:",
            min_value=0.01,
            max_value=2.0,
            value=mountain["amplitude"],
            key=f"a_mountain{active_idx}",
        )

        mountain["x"] = x
        mountain["y"] = y
        mountain["sigma"] = sigma
        mountain["amplitude"] = amplitude

    mountains = (
        [Mountain(**m) for m in st.session_state.mountain_state]
        if "mountain_state" in st.session_state
        else None
    )


with left:
    with st.spinner("Generating..."):
        heightmap = generate_heightmap(
            config=config, mountains=mountains, terrain_amplifier=0.7
        )

    fig = plt.figure(figsize=(15, 15), frameon=False)
    plt.imshow(heightmap, cmap="terrain")
    st.pyplot(fig)
