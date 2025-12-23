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

    mountains: list[Mountain] = []

    mountain_num = st.number_input("Number of mountains:", min_value=0)
    for i in range(mountain_num):
        with st.expander(f"#{i + 1}"):
            x = st.slider("X:", min_value=0, max_value=width, key=f"x_mountain{i}")
            y = st.slider("Y:", min_value=0, max_value=height, key=f"y_mountain{i}")
            sigma = st.slider(
                "Sigma:", min_value=0.01, max_value=500.0, key=f"s_mountain{i}"
            )
            amplitude = st.slider(
                "Amplitude:",
                min_value=0.01,
                max_value=2.0,
                key=f"a_mountain{i}",
                value=1.0,
            )
            mountains.append(
                Mountain(
                    x=x,
                    y=y,
                    sigma=sigma,
                    amplitude=amplitude,
                )
            )


with left:
    with st.spinner("Generating..."):
        heightmap = generate_heightmap(
            config=config, mountains=mountains, terrain_amplifier=0.7
        )

    fig = plt.figure(figsize=(15, 15), frameon=False)
    plt.imshow(heightmap, cmap="terrain")
    st.pyplot(fig)
