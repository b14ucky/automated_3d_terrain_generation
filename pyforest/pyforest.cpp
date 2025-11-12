#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <vector>
#include <random>

enum VegetationType {
    EMPTY = 0,
    SEED = 1,
    TREE = 2
};

struct Seed {
    int x, y;
    double strength;
};

struct Tree {
    int x, y;
};

struct Forest {
    int width = 0;
    int height = 0;
    int seed_radius = 5;
    double seed_strength = 0.05;
    double seed_decay_rate = 0.2;

    std::vector<int> map;
    std::vector<Tree> trees;
    std::vector<Seed> seeds;

    std::mt19937_64 rng;
    std::uniform_real_distribution<double> uni01;

    Forest() : rng(std::random_device{}()), uni01(0.0, 1.0) {}

    inline int idx(int x, int y) const {return y * width + x;}

    void init(int w,
        int h,
        int initial_trees,
        int seed_radius_,
        double seed_strength_,
        double seed_decay_rate_
    ) {
        width = w;
        height = h;
        seed_radius = seed_radius_;
        seed_strength = seed_strength_;
        seed_decay_rate = seed_decay_rate_;

        map.assign(width * height, VegetationType::EMPTY);
        trees.clear();
        seeds.clear();

        std::uniform_int_distribution<int> dx(0, width - 1);
        std::uniform_int_distribution<int> dy(0, height - 1);

        for (int i = 0; i < initial_trees; ++i) {
            int x = dx(rng);
            int y = dy(rng);
            if (map[idx(x, y)] != VegetationType::TREE) {
                map[idx(x, y)] = VegetationType::TREE;
                trees.push_back(Tree{x, y});
            }
        }
    }

    void seed_trees() {
        for (const Tree &tree : trees) {
            for (int x = tree.x - seed_radius; x <= tree.x + seed_radius; ++x) {
                if (x < 0 || x >= width) continue;

                for (int y = tree.y - seed_radius; y <= tree.y + seed_radius; ++y) {
                    if (y < 0 || y >= height) continue;

                    int dx = x - tree.x;
                    int dy = y - tree.y;
                    if (dx * dx + dy * dy > seed_radius * seed_radius) continue;
                    if (map[idx(x, y)] == VegetationType::TREE) continue;

                    int id = idx(x, y);
                    if (map[id] == VegetationType::SEED) {
                        // TODO: test what gives better forests - increasing seed's strength or not
                        // probably not increasing its strength is better
                        // for (auto &seed : seeds) {
                        //     if (seed.x == x && seed.y == y) {seed.strength += seed_strength; break;}
                        // }
                    } else {
                        Seed seed{x, y, seed_strength};
                        seeds.push_back(seed);
                        map[id] = VegetationType::SEED;
                    }
                }
            }
        }
    }

    void grow_trees() {
        // iterate backwards over seed to safely remove
        for (int i = (int)seeds.size() - 1; i >= 0; --i) {
            const Seed &seed = seeds[i];
            double r = uni01(rng);
            if (r < seed.strength) {
                // becomes tree
                if (map[idx(seed.x, seed.y)] != VegetationType::TREE) {
                    map[idx(seed.x, seed.y)] = VegetationType::TREE;
                    trees.push_back(Tree{seed.x, seed.y});
                }

                // remove seed by swapping with last and pop_back because it is faster
                seeds[i] = seeds.back();
                seeds.pop_back();
            }
        }
    }

    void decay_seeds() {
        for (auto &seed : seeds) {
            seed.strength -= (seed_decay_rate * seed_strength);
        }

        std::vector<Seed> kept;
        kept.reserve(seeds.size());
        for (const auto &seed : seeds) {
            if (seed.strength > 0.0) {
                kept.push_back(seed);
            } else {
                int id = idx(seed.x, seed.y);
                if (map[id] == VegetationType::SEED) map[id] = VegetationType::EMPTY;
            }
        }

        seeds.swap(kept);
    }

    void remove_seeds() {
        for (int x = 0; x < width; ++x) {
            for (int y = 0; y < height; ++y) {
                int id = idx(x, y);
                if (map[id] == VegetationType::SEED) map[id] = VegetationType::EMPTY; 
            }
        }

        seeds.clear();
    }

    double get_coverage() const {
        // percent of width * height matrix covered in trees
        double denom = (double)map.size();
        if (denom == 0.0) return 0.0;
        return (double)trees.size() / denom;
    }

    PyObject* get_trees_py() const {
        PyObject* list = PyList_New((Py_ssize_t)trees.size());
        for (size_t i = 0; i < trees.size(); ++i) {
            PyObject *tuple = Py_BuildValue("(ii)", trees[i].x, trees[i].y);
            PyList_SetItem(list, (Py_ssize_t)i, tuple);
        }

        return list;
    }

    PyObject* get_seeds_py() const {
        PyObject* list = PyList_New((Py_ssize_t)seeds.size());
        for (size_t i = 0; i < seeds.size(); ++i) {
            PyObject *tuple = Py_BuildValue("(iid)", seeds[i].x, seeds[i].y, seeds[i].strength);
            PyList_SetItem(list, (Py_ssize_t)i, tuple);
        }

        return list;
    }

    PyObject* get_map_py() const {
        PyObject *rows = PyList_New((Py_ssize_t)height);
        for (int y = 0; y < height; ++y) {
            PyObject *row = PyList_New((Py_ssize_t)width);
            for (int x = 0; x < width; ++x) {
                int value = map[idx(x, y)];
                PyObject *v = PyLong_FromLong((long)value);
                PyList_SetItem(row, (Py_ssize_t)x, v);
            }
            PyList_SetItem(rows, (Py_ssize_t)y, row);
        }

        return rows;
    }
};

static Forest g_forest;


// --- Python Wrappers ---

static PyObject* py_init_forest(PyObject*, PyObject* args, PyObject* kwargs) {
    int w, h, initial_trees = 5;
    int seed_radius = 5;
    double seed_strength = 0.05;
    double seed_decay_rate = 0.2;

    static const char *kwlist[] = {
        "width",
        "height",
        "initial_trees",
        "seed_radius",
        "seed_strength",
        "seed_decay_rate",
        NULL,
    };

    if (!PyArg_ParseTupleAndKeywords(args, kwargs, "ii|iidd", (char**)kwlist,
                                     &w, &h, &initial_trees, &seed_radius, &seed_strength, &seed_decay_rate)) {
        PyErr_Clear();
        if (!PyArg_ParseTuple(args, "iii", &w, &h, &initial_trees)) {
            PyErr_SetString(PyExc_TypeError, "Expected (width:int, height:int, initial_trees:int[, seed_radius:int, seed_strength:float, seed_decay_rate:float])");
            return NULL;
        }
    }

    g_forest.init(w, h, initial_trees, seed_radius, seed_strength, seed_decay_rate);

    Py_RETURN_NONE;
}

static PyObject* py_seed_trees(PyObject*, PyObject*) {
    g_forest.seed_trees();
    Py_RETURN_NONE;
}

static PyObject* py_grow_trees(PyObject*, PyObject*) {
    g_forest.grow_trees();
    Py_RETURN_NONE;
}

static PyObject* py_decay_seeds(PyObject*, PyObject*) {
    g_forest.decay_seeds();
    Py_RETURN_NONE;
}

static PyObject* py_remove_seeds(PyObject*, PyObject*) {
    g_forest.remove_seeds();
    Py_RETURN_NONE;
}

static PyObject* py_get_coverage(PyObject*, PyObject*) {
    double coverage = g_forest.get_coverage();
    return PyFloat_FromDouble(coverage);
}

static PyObject* py_get_trees(PyObject*, PyObject*) {
    return g_forest.get_trees_py();
}

static PyObject* py_get_seeds(PyObject*, PyObject*) {
    return g_forest.get_seeds_py();
}

static PyObject* py_get_map(PyObject*, PyObject*) {
    return g_forest.get_map_py();
}

static PyMethodDef ForestMethods[] = {
    {"init_forest", (PyCFunction)py_init_forest, METH_VARARGS | METH_KEYWORDS, "init_forest(width, height, initial_trees, seed_radius=5, seed_strength=0.05, seed_decay_rate=0.2, desired_coverage=0.15)"},
    {"seed_trees",  py_seed_trees, METH_NOARGS, "seed_trees()"},
    {"grow_trees",  py_grow_trees, METH_NOARGS, "grow_trees()"},
    {"decay_seeds", py_decay_seeds, METH_NOARGS, "decay_seeds()"},
    {"remove_seeds", py_remove_seeds, METH_NOARGS, "remove_seeds()"},
    {"get_coverage", py_get_coverage, METH_NOARGS, "get_coverage() => float"},
    {"get_trees", py_get_trees, METH_NOARGS, "get_trees() => list[(x,y), ...]"},
    {"get_seeds", py_get_seeds, METH_NOARGS, "get_seeds() => list[(x,y,strength), ...]"},
    {"get_map", py_get_map, METH_NOARGS, "get_map() => list[list[int]] rows"},
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef forestmodule = {
    PyModuleDef_HEAD_INIT,
    "pyforest",
    "Forest simulation module (C++ backend)",
    -1,
    ForestMethods
};

PyMODINIT_FUNC PyInit_pyforest(void) {
    return PyModule_Create(&forestmodule);
}