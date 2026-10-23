"""Smoke tests: the package imports and every dependency is installed correctly."""


def test_package_imports():
    import aml  # noqa: F401


def test_dependencies_import():
    # xgboost on macOS needs the OpenMP runtime (libomp); importing it here
    # catches a broken install early instead of mid-experiment.
    import matplotlib  # noqa: F401
    import networkx  # noqa: F401
    import pandas  # noqa: F401
    import sklearn  # noqa: F401
    import xgboost  # noqa: F401
