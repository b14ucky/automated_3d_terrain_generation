from setuptools import setup, Extension, find_packages

ext_modules = [
    Extension(
        "pyforest.pyforest",
        sources=["pyforest_src/pyforest/pyforest.cpp"],
        extra_compile_args=["-O3"],
        language="c++",
    )
]

setup(
    name="pyforest",
    version="1.0.0",
    packages=find_packages(where="pyforest_src"),
    package_dir={"": "pyforest_src"},
    ext_modules=ext_modules,
    include_package_data=True,
    install_requires=["numpy>=1.25"],
)
