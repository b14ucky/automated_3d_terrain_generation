import json
import numpy as np
from noise import pnoise2
from numpy.typing import NDArray
from dataclasses import dataclass, asdict


@dataclass
class PerlinNoiseConfig:
    height: int
    width: int
    scale: float = 50.0
    octaves: int = 4
    persistence: float = 0.5
    lacunarity: float = 2.0
    repeatx: float = 1024.0
    repeaty: float = 1024.0
    base: int = 0


@dataclass
class TerrainConfig:
    XSize: int
    YSize: int
    Scale: float
    ZMultiplier: float
    UVScale: float
    Heightmap: NDArray

    def export_to_json(self, filename: str = "config.json") -> None:
        with open(filename, "w") as file:
            json.dump(asdict(self), file)


def gaussian_2d(
    shape: tuple[int, int],
    center: tuple[int, int],
    sigma: float,
    amplitude: float = 1.0,
) -> NDArray:
    """Generate a 2D Gaussian array.

    Args:
        shape (tuple[int, int]): Output array shape (height, width).
        center (tuple[int, int]): Gaussian center coordinates (y, x).
        sigma (float): Standard deviation of the Gaussian.
        amplitude (float, optional): Peak amplitude. Defaults to 1.0.

    Returns:
        NDArray: 2D array containing the Gaussian function values.
    """

    y = np.arange(shape[0])[:, None]
    x = np.arange(shape[1])[None, :]
    cy, cx = center
    g = amplitude * np.exp(-((x - cx) ** 2 + (y - cy) ** 2) / (2 * sigma**2))
    return g


def generate_heightmap(
    config: PerlinNoiseConfig,
    mountains: list[tuple[int, int, float, float]] | None = None,
    terrain_amplifier: float = 0.5,
) -> NDArray:
    """
    Generates a heightmap using Perlin noise, optionally modified by mountain masks.

    Args:
        config (PerlinNoiseConfig): Configuration object containing Perlin noise parameters.
        mountains (list of tuples, optional): List of mountain parameters (y, x, sigma, amplitude) to modify the terrain.
        terrain_amplifier (float, optional): Amplification factor for the terrain. Default is 0.5.

    Returns:
        NDArray: A 2D array representing the generated heightmap.
    """

    mask = None

    if mountains:
        mask = np.zeros((config.height, config.width))
        for y, x, sigma, amp in mountains:
            mask += gaussian_2d(
                (config.height, config.width), (y, x), sigma, amplitude=amp
            )

        mask = (mask - mask.min()) / (mask.max() - mask.min())

    terrain = np.zeros((config.height, config.width))
    for i in range(config.height):
        for j in range(config.width):
            terrain[i, j] = pnoise2(
                i / config.scale,
                j / config.scale,
                octaves=config.octaves,
                persistence=config.persistence,
                lacunarity=config.lacunarity,
                repeatx=config.repeatx,
                repeaty=config.repeaty,
                base=config.base,
            )

    terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min())

    if mask is not None:
        return terrain * (terrain_amplifier + mask)

    return terrain
