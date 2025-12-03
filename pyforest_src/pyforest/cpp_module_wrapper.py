import numpy as np
from enum import IntEnum
from pyforest import pyforest  # type: ignore
import matplotlib.pyplot as plt
from numpy.typing import NDArray


class VegetationType(IntEnum):
    UNPLANTABLE = -1
    EMPTY = 0
    SEED = 1
    TREE = 2


class PyForest:
    """
    Python wrapper around the C++ pyforest module for forest generation.

    This class provides a Python-friendly interface for running the forest
    simulation implemented in the C++ backend. The simulation consists of
    repeatedly seeding trees, growing seeds into trees, and decaying seeds,
    over a fixed number of iterations.

    Attributes:
        _width (int): Width of the forest.
        _height (int): Height of the forest.
        _n_iterations (int): Number of simulation iterations (seed–grow–decay cycles).
    """

    def __init__(
        self,
        width: int,
        height: int,
        initial_trees: int = 5,
        seed_radius: int = 15,
        seed_strength: float = 0.05,
        seed_decay_rate: float = 0.2,
        n_iterations: int = 3,
        space_between_trees: int = 5,
    ) -> None:
        """
        Initialize the forest simulation.

        This initializes the C++ pyforest backend with the given parameters
        and executes a fixed number of simulation iterations. Each iteration
        performs: seeding around existing trees, growth of seeds into trees
        based on their strength, and decay of remaining seeds.

        Args:
            width (int): Width of the forest grid.
            height (int): Height of the forest grid.
            initial_trees (int, optional): Number of initial trees to place randomly. Defaults to 5.
            seed_radius (int, optional): Maximum distance around a tree where seeds may spawn. Defaults to 15.
            seed_strength (float, optional): Initial probability of a seed growing into a tree. Defaults to 0.05.
            seed_decay_rate (float, optional): Fraction of seed strength lost per iteration. Defaults to 0.2.
            n_iterations (int, optional): Number of simulation cycles to run. Defaults to 3.
            space_between_trees (int, optional): Minimum distance between tree centers. Defaults to 5.
        """

        pyforest.init_forest(
            width,
            height,
            initial_trees,
            seed_radius,
            seed_strength,
            seed_decay_rate,
            space_between_trees,
        )

        self._width = width
        self._height = height
        self._n_iterations = n_iterations

        self._generate()

    def _generate(self) -> None:
        """
        Run the forest simulation for the configured number of iterations.

        Each iteration performs:
        - Seeding around existing trees
        - Growing seeds into trees with probability proportional to seed strength
        - Decaying remaining seeds

        The simulation stops after the fixed iteration count.
        """

        for _ in range(self._n_iterations):
            pyforest.seed_trees()
            pyforest.grow_trees()
            pyforest.decay_seeds()

    def display_forest(self, plot_seeds: bool = False) -> None:
        """
        Display the forest using matplotlib.

        Args:
            plot_seeds (bool, optional): Whether to display seed positions. Defaults to False.

        The forest is displayed with:
        - Trees as green triangles
        - Seeds (optional) as brown dots
        - Coverage fraction in the title
        """

        forest_map: NDArray = np.array(pyforest.get_map())

        trees = forest_map == VegetationType.TREE
        seeds = forest_map == VegetationType.SEED

        y_trees, x_trees = np.where(trees)
        y_seeds, x_seeds = np.where(seeds)

        plt.figure(figsize=(5, 5))
        plt.suptitle(f"Coverage: {pyforest.get_coverage():.2f}")
        if plot_seeds:
            plt.scatter(x_seeds, y_seeds, marker=".", color="brown")
        plt.scatter(x_trees, y_trees, marker="^", color="green")
        plt.xlim(0, self._width)
        plt.ylim(0, self._height)
        plt.axis("off")

        plt.show()

    def get_map(self) -> NDArray:
        """
        Return the forest map as a NumPy array.

        All seeds are removed from the map before returning.

        Returns:
            NDArray: 2D NumPy array of integers representing the forest grid.
                     Values correspond to VegetationType Enum:
                     -1 = UNPLANTABLE, 0 = EMPTY, 1 = SEED, 2 = TREE
        """
        pyforest.clear_map()
        return np.array(pyforest.get_map())
