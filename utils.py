import json
import numpy as np
from pathlib import Path
from noise import pnoise2
from pyforest import PyForest, VegetationType
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
class TerrainTransformConfig:
    max_height: float
    min_height: float
    flatness: float
    slope_x_begin: float
    slope_x_end: float
    slope_y_begin: float
    slope_y_end: float

@dataclass
class TerrainConfig:
    XSize: int
    YSize: int
    Scale: float
    ZMultiplier: float
    UVScale: float
    Heightmap: list[float]
    VegetationMap: list[int]
    bWaterOn: bool
    WaterHeight: float
    bFogOn: bool
    FogHeightOffset: float
    FogDensity: float

    def export_to_json(self, path: str | Path = "config.json") -> None:
        with open(path, "w") as file:
            json.dump(asdict(self), file)


@dataclass
class PyForestConfig:
    width: int
    height: int
    initial_trees: int = 3
    seed_radius: int = 15
    seed_strength: float = 0.05
    seed_decay_rate: float = 0.2
    n_iterations: int = 3
    space_between_trees: int = 5
    min_height: float = 0.35,
    max_height: float = 0.6,
    max_slope: float = 0.7,


@dataclass
class Mountain:
    x: int
    y: int
    sigma: float
    hole: bool = False
    amplitude: float = 1.0


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
    transform: TerrainTransformConfig,
    mountains: list[Mountain] | None = None,
    terrain_amplifier: float = 0.5,
) -> NDArray:
    """
    Generates a heightmap using Perlin noise, optionally modified by mountain masks.

    Args:
        config (PerlinNoiseConfig): Configuration object containing Perlin noise parameters.
        mountains (list[Mountain], optional): List of Mountain objects used to modify the terrain.
        terrain_amplifier (float, optional): Amplification factor for the terrain. Default is 0.5.

    Returns:
        NDArray: A 2D array representing the generated heightmap.
    """

    mask = None

    if mountains:
        mask = np.zeros((config.height, config.width))
        for mountain in mountains:
            mask += gaussian_2d(
                (config.height, config.width),
                (mountain.y, mountain.x),
                mountain.sigma,
                amplitude=mountain.amplitude,
            ) * (1 + mountain.hole * -2)

        mask = (mask - mask.min()) / (mask.max() - mask.min())

    terrain = np.zeros((config.height, config.width))
    for i in range(config.height):
        for j in range(config.width):
            terrain[i, j] =pnoise2(
                i / config.scale,
                j / config.scale,
                octaves=config.octaves,
                persistence=config.persistence,
                lacunarity=config.lacunarity,
                repeatx=config.repeatx,
                repeaty=config.repeaty,
                base=config.base,
            )

    tranformation_mask = np.zeros((config.height, config.width))
    slope_x = np.linspace(transform.slope_x_begin, transform.slope_x_end, config.width)
    slope_y = np.linspace(transform.slope_y_begin, transform.slope_y_end, config.height)
    for i in range(config.height):
        for j in range(config.width):
            tranformation_mask[i, j] = slope_x[i] + slope_y[j]
    terrain = terrain + tranformation_mask
    terrain = (terrain - terrain.min()) / (terrain.max() - terrain.min())
    terrain[terrain < transform.min_height] = transform.min_height
    terrain[terrain > transform.max_height] = transform.max_height

    terrain = terrain/transform.flatness

    if mask is not None:
        return terrain * (terrain_amplifier + mask * transform.flatness)

    return terrain


def generate_forest_adapted_to_terrain(
    config: PyForestConfig,
    heightmap: NDArray,
) -> NDArray:
    """
    Generates a forest distribution using the PyForest module and adapts it to the given terrain.

    The function initializes a PyForest simulation using the provided configuration,
    generates a forest map, and filters vegetation based on the heightmap data.
    Trees are removed from regions that exceed the allowed slope or fall outside
    the specified height range. This results in a more natural forest layout that
    matches the underlying terrain shape.

    Args:
        config (PyForestConfig): Configuration object for the PyForest generator.
        heightmap (NDArray): 2D array representing the terrain height values.
        min_height (float, optional): Minimum normalized height threshold below which trees are removed. Defaults to 0.35.
        max_height (float, optional): Maximum normalized height threshold above which trees are removed. Defaults to 0.6.
        max_slope (float, optional): Maximum normalized slope value allowed for tree placement. Defaults to 0.7.

    Returns:
        NDArray: A 2D array representing the filtered forest map, where cell values correspond to vegetation types:
            - -1: UNPLANTABLE
            - 0: EMPTY
            - 1: SEED
            - 2: TREE
    """

    forest = PyForest(
        width=config.width,
        height=config.height,
        initial_trees=config.initial_trees,
        seed_radius=config.seed_radius,
        seed_strength=config.seed_strength,
        n_iterations=config.n_iterations,
        space_between_trees=config.space_between_trees,
    )

    forest_map = forest.get_map()

    dx, dy = np.gradient(heightmap)
    slope = np.sqrt(dx**2 + dy**2)
    slope = (slope - slope.min()) / (slope.max() - slope.min())

    forest_map[
        (slope > config.max_slope) | (heightmap > config.max_height) | (heightmap < config.min_height)
    ] = VegetationType.EMPTY
    return forest_map


def resolve_paths() -> tuple[Path, Path | None]:
    """
    Resolve runtime paths based on the execution context.

    If a .uproject file is present, the script is assumed to run in development mode.
    If a .exe is present, the script is assumed to run in production mode.

    Returns:
        tuple[Path, Path | None]:
            - Path: Path to the project's config.json file.
            - Path | None: Path to the built executable in production mode, or None in development mode.
    """

    base_dir = Path(__file__).resolve().parent

    uprojects = list(base_dir.glob("*.uproject"))
    if uprojects:
        project_dir = base_dir

        return project_dir / "config.json", None

    exes = list(base_dir.glob("*.exe"))
    if exes:
        exe_path = exes[0]
        project_name = exe_path.stem
        project_dir = base_dir / project_name

        return project_dir / "config.json", exe_path

    raise RuntimeError(f".uproject nor .exe not found in {base_dir}")
