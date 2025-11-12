import numpy as np
from enum import Enum
from pyforest import pyforest  # type: ignore
import matplotlib.pyplot as plt
from numpy.typing import NDArray


class VegetationType(Enum):
    EMPTY = 0
    SEED = 1
    TREE = 2


class PyForest:
    """
    Python wrapper around the C++ pyforest module for forest generation.

    This class encapsulates the simulation of trees and seeds, handling
    seeding, growth, decay, and visualization in a Python-friendly interface.

    Attributes:
        _width (int): Width of the forest.
        _height (int): Height of the forest.
        _desired_coverage (float): Target fraction of the forest to be covered by trees.
    """

    def __init__(
        self,
        width: int,
        height: int,
        initial_trees: int = 5,
        seed_radius: int = 15,
        seed_strength: float = 0.05,
        seed_decay_rate: float = 0.2,
        desired_coverage: float = 0.05,
    ) -> None:
        """
        Initialize the forest simulation.

        This initializes the C++ pyforest backend with the specified parameters
        and runs the simulation until the desired coverage is reached.

        Args:
            width (int): Width of the forest grid.
            height (int): Height of the forest grid.
            initial_trees (int, optional): Number of initial trees. Defaults to 5.
            seed_radius (int, optional): Radius around trees to generate seeds. Defaults to 15.
            seed_strength (float, optional): Probability of a seed growing into a tree. Defaults to 0.05.
            seed_decay_rate (float, optional): Rate at which seed strength decays each step. Defaults to 0.2.
            desired_coverage (float, optional): Target coverage fraction (0-1). Defaults to 0.05.
        """

        pyforest.init_forest(
            width,
            height,
            initial_trees,
            seed_radius,
            seed_strength,
            seed_decay_rate,
        )

        self._width = width
        self._height = height
        self._desired_coverage = desired_coverage

        self._generate()

    def _generate(self) -> None:
        """
        Run the simulation until the desired coverage is reached.

        This repeatedly seeds trees, grows seeds into trees, and decays seeds
        until the target coverage fraction is achieved.
        """

        while pyforest.get_coverage() < self._desired_coverage:
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

        trees = forest_map == VegetationType.TREE.value
        seeds = forest_map == VegetationType.SEED.value

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
                     0 = EMPTY, 1 = SEED, 2 = TREE
        """
        pyforest.remove_seeds()
        return np.array(pyforest.get_map())
