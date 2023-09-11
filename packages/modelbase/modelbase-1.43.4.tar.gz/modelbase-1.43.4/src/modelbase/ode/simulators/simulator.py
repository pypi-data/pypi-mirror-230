from __future__ import annotations

__all__ = [
    "_Simulate",
]

import json
import pickle
import warnings
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Type, Union, cast

import numpy as np
from matplotlib.figure import Figure
from scipy.optimize import minimize

from ...core.utils import warning_on_one_line
from ...typing import Array, ArrayLike, Axis
from ...utils.plotting import plot
from ..integrators import AbstractIntegrator
from ..models import Model
from . import _BaseRateSimulator

warnings.formatwarning = warning_on_one_line  # type: ignore


def _get_file_type_from_path(path: Path, filetype: Optional[str]) -> str:
    if filetype is None:
        if not path.suffix:
            file_type = "json"
        else:
            file_type = path.suffix[1:]
    else:
        file_type = filetype
    return file_type


def _add_suffix(path: Path, filetype: str) -> Path:
    if not path.suffix:
        path = path.parent / (path.name + f".{filetype}")
    return path


class _Simulate(_BaseRateSimulator[Model]):
    """Simulator for ODE models."""

    def __init__(
        self,
        model: Model,
        integrator: Type[AbstractIntegrator],
        y0: Optional[ArrayLike] = None,
        time: Optional[List[Array]] = None,
        results: Optional[List[Array]] = None,
        parameters: List[Dict[str, float]] | None = None,
    ) -> None:
        """
        Parameters
        ----------
        kwargs
            {parameters}
        """
        super().__init__(
            model=model,
            integrator=integrator,
            y0=y0,
            time=time,
            results=results,
            parameters=parameters,
        )

    def fit_steady_state(
        self,
        p0: dict[str, float],
        data: ArrayLike,
    ) -> dict[str, float]:
        par_names = list(p0.keys())
        x0 = list(p0.values())
        p_orig = self.model.get_parameters().copy()

        def residual(par_values: ArrayLike, data: ArrayLike) -> float:
            self.clear_results()
            self.update_parameters(dict(zip(par_names, par_values)))
            y_ss = self.simulate_to_steady_state()[1]
            if y_ss is None:
                return cast(float, np.inf)
            return cast(float, np.sqrt(np.mean(np.square(data - y_ss.flatten()))))

        res = dict(zip(par_names, minimize(residual, x0=x0, args=(data,)).x))
        self.model.update_parameters(p_orig)
        return res

    def fit_time_series(
        self,
        p0: dict[str, float],
        data: ArrayLike,
        time_points: ArrayLike,
    ) -> dict[str, float]:
        par_names = list(p0.keys())
        x0 = list(p0.values())
        p_orig = self.model.get_parameters().copy()
        assert len(data) == len(time_points)

        def residual(
            par_values: ArrayLike, data: ArrayLike, time_points: ArrayLike
        ) -> float:
            self.clear_results()
            self.update_parameters(dict(zip(par_names, par_values)))
            _, y = self.simulate(time_points=time_points)
            if y is None:
                return cast(float, np.inf)
            return cast(float, np.sqrt(np.mean(np.square(data - y))))

        res = dict(zip(par_names, minimize(residual, x0=x0, args=(data, time_points)).x))
        self.model.update_parameters(p_orig)
        return res

    def plot(
        self,
        xlabel: str | None = None,
        ylabel: str | None = None,
        title: str | None = None,
        normalise: Union[float, ArrayLike] | None = None,
        grid: bool = True,
        tight_layout: bool = True,
        ax: Axis | None = None,
        figure_kwargs: Dict[str, Any] | None = None,
        subplot_kwargs: Dict[str, Any] | None = None,
        plot_kwargs: Dict[str, Any] | None = None,
        grid_kwargs: Dict[str, Any] | None = None,
        legend_kwargs: Dict[str, Any] | None = None,
        tick_kwargs: Dict[str, Any | None] | None = None,
        label_kwargs: Dict[str, Any] | None = None,
        title_kwargs: Dict[str, Any] | None = None,
    ) -> Tuple[Optional[Figure], Optional[Axis]]:
        """Plot simulation results for a selection of compounds."""
        compounds = self.model.get_compounds()
        y = self.get_full_results_df(normalise=normalise, concatenated=True)
        if y is None:
            return None, None
        return plot(
            plot_args=(y.loc[:, compounds],),
            legend=compounds,
            xlabel=xlabel,
            ylabel=ylabel,
            title=title,
            grid=grid,
            tight_layout=tight_layout,
            ax=ax,
            figure_kwargs=figure_kwargs,
            subplot_kwargs=subplot_kwargs,
            plot_kwargs=plot_kwargs,
            grid_kwargs=grid_kwargs,
            legend_kwargs=legend_kwargs,
            tick_kwargs=tick_kwargs,
            label_kwargs=label_kwargs,
            title_kwargs=title_kwargs,
        )

    def store_results_to_file(
        self, filename: str, filetype: Optional[str] = None
    ) -> None:
        time = self.get_time(concatenated=False)
        if time is None or self.results is None:
            raise ValueError(
                "Cannot save results, since none are stored in the simulator"
            )

        path = Path(filename)
        file_type = _get_file_type_from_path(path, filetype)
        path = _add_suffix(path, file_type)

        results = [i.tolist() for i in self.results]
        parameters = cast(List[Dict[str, float]], self.simulation_parameters)

        to_export = {
            "results": results,
            "time": [i.tolist() for i in time],
            "parameters": parameters,
        }

        if file_type == "json":
            with open(path, "w") as f:
                json.dump(obj=to_export, fp=f)
        elif file_type == "pickle" or file_type == "p":
            with open(path, "wb") as fb:
                pickle.dump(obj=to_export, file=fb)
        else:
            raise ValueError(f"Can only save to json or pickle, got {file_type}")

    def load_results_from_file(
        self, filename: str, filetype: Optional[str] = None
    ) -> None:
        path = Path(filename)
        file_type = _get_file_type_from_path(path, filetype)
        path = _add_suffix(path, file_type)

        if file_type == "json":
            with open(filename, "r") as f:
                to_import = json.load(fp=f)
        elif file_type == "pickle" or file_type == "p":
            with open(filename, "rb") as fb:
                to_import = pickle.load(file=fb)
        else:
            raise ValueError(f"Can only load from to json or pickle, got {file_type}")

        self.time = [np.array(i) for i in to_import["time"]]
        self.results = [np.array(i) for i in to_import["results"]]
        self.simulation_parameters = to_import["parameters"]
