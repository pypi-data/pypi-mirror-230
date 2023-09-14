from typing import Optional, Sequence, Any

import pandas as pd
import quantities as pq
from matplotlib import pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure

from openmnglab.datamodel.pandas.model import PandasContainer
from openmnglab.functions.base import FunctionBase
from openmnglab.util.dicts import setfactory
from openmnglab.util.pandas import ensure_dataframe, iterdfcols


class ContinuousPlotFunc(FunctionBase):

    def __init__(self, columns: Optional[Sequence[str]] = None,
                 general_args: Optional[dict] = None, fig_args: Optional[dict] = None,
                 color_dict: Optional[dict[str, str]] = None,
                 specific_dict: Optional[dict[str, dict[str, Any]]] = None):
        self._data: dict[str, tuple[pd.Series, pq.Quantity, pd.Index, pq.Quantity]] = None
        self.columns = columns
        self.into_one = False
        self.color_dict = color_dict
        self.general_args = general_args if general_args is not None else dict()
        self.specific_dict = specific_dict if specific_dict is not None else dict()
        self.figargs = fig_args if fig_args is not None else dict()
        if color_dict is not None:
            for k, v in color_dict.items():
                setfactory(self.specific_dict, k, dict)["color"] = v

    def plot_single(self, ax: Axes, item_name: str):
        data, unit, x_ax, x_unit = self._data[item_name]
        kwargs = self.general_args.copy()
        kwargs.update(self.specific_dict.get(data.name, dict()))
        ax.plot(x_ax.values, data.values, **kwargs)
        if not self.into_one:
            ax.set_title(item_name)
            ax.set_xlabel(f"{x_ax.name} [{x_unit.dimensionality.latex}]")
            ax.set_ylabel(f"{item_name} [{unit.dimensionality.latex}]")

    async def execute(self) -> Figure:
        subplots = 1 if self.into_one else len(self._data)
        fig, axs = plt.subplots(subplots, 1, sharex=True, **self.figargs)
        axs = (axs,) if isinstance(axs, Axes) else axs
        for column, ax in zip(self._data.keys(), axs):
            self.plot_single(ax, column)
        return fig

    def set_input(self, *data_containers: PandasContainer):
        self._data = dict()
        i = 0
        for data_container in data_containers:
            df = ensure_dataframe(data_container.data)
            idx = df.index.levels[-1] if isinstance(df.index, pd.MultiIndex) else df.index
            for col_name, col in iterdfcols(df):
                item_name = col_name
                self._data[item_name] = (col, data_container.units[col_name], idx, data_container.units[idx.name])
