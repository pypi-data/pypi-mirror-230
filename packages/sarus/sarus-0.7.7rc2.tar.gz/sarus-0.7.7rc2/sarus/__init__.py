"""SDK classes and functions."""
# flake8: noqa
import warnings

with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    from sarus import (
        imblearn,
        numpy,
        pandas,
        pandas_profiling,
        plotly,
        shap,
        sklearn,
        skopt,
        std,
        xgboost,
    )

    from .sarus import Client, Dataset
    from .utils import eval, eval_policy, floating, integer, length

VERSION = "0.7.7rc0"

__all__ = [
    "Dataset",
    "Client",
    "length",
    "eval",
    "eval_policy",
    "config",
    "floating",
    "integer",
]
