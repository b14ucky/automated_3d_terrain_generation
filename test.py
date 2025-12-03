import numpy as np
from utils import PerlinNoiseConfig, generate_heightmap, TerrainConfig

width = height = 505

config = PerlinNoiseConfig(
    height=width,
    width=height,
    scale=150.0,
    octaves=4,
    persistence=0.5,
    lacunarity=2.0,
)

mountains = [
    (45, 50, 25.0, 1.0),  # (y, x, sigma, amplitude)
]

heightmap = generate_heightmap(
    config=config, mountains=mountains, terrain_amplifier=1
)

from PIL import Image

h_16 = np.round(heightmap * 65535.0).astype(np.uint16)
img = Image.fromarray(h_16, mode="I;16")
img.save("h_16.png", format="PNG")
