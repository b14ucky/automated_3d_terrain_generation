# PYFOREST

`pyforest` – fast forest simulation in C++ with Python interface.

---

## 1. Install

Instead of manually compiling, you can now install the module directly:

```bash
pip install .
```

This will build the C++ module and install the Python wrapper automatically.

---

## 2. Package structure

After installation, your local package folder should look like this:

```bash
pyforest/
│
├─ __init__.py
├─ cpp_module_wrapper.py  # Python wrapper around the C++ module
├─ pyforest.cpp           # C++ source file
└─ README.md              # this documentation
```

---

## 3. Using PyForest in Python

```python
from pyforest import PyForest, VegetationType

# Initialize the forest simulation
forest = PyForest(width=100, height=100, initial_trees=5)

# Display the forest at the initial state
forest.display_forest(plot_seeds=True)

# Access forest data
forest_map = forest.get_map()         # 2D NumPy array
trees = forest_map == VegetationType.TREE
seeds = forest_map == VegetationType.SEED
```

---

## 4. Notes

-   The C++ module is built automatically during `pip install .`
-   Make sure your Python architecture (64-bit vs 32-bit) matches the Visual Studio build environment
-   The `PyForest` class handles seeding, growth, decay, and provides visualization methods
-   `VegetationType` enum values:
    -   `UNPLANTABLE = -1`
    -   `EMPTY = 0`
    -   `SEED = 1`
    -   `TREE = 2`

---

## 5. Advanced usage

-   You can customize the forest generation by passing parameters to `PyForest()`:

    -   `width`, `height`: dimensions of the forest
    -   `initial_trees`: number of starting trees
    -   `seed_radius`: radius around each tree for seeding
    -   `seed_strength`: probability of seed growth
    -   `seed_decay_rate`: decay rate of seeds
    -   `n_iterations`: number of simulation cycles to run
    -   `space_between_trees`: minimum spacing between trees

-   The simulation is fast due to the C++ backend, allowing larger forests to be simulated efficiently.
