from handler_library.handler import PayloadHandler
from PySide2.QtCore import Signal
import numpy as np
from threading import Lock


class DataHandler(PayloadHandler):
    UpdatePlots = Signal(dict)

    def __init__(self, *args, plot_history_length=500, **kwargs):
        super().__init__(["DATA", "CYCLE"], *args, **kwargs)
        self.__plot_history_length = plot_history_length
        self.__plots_database = {
            "data": np.zeros((plot_history_length, 4)),
            "timestamp": list(el * (-1) for el in range(plot_history_length))[::-1],
            "pressure": list(0 for _ in range(plot_history_length)),
            "flow": list(0 for _ in range(plot_history_length)),
            "volume": list(0 for _ in range(plot_history_length)),
            "cycle_pressure": list(0 for _ in range(plot_history_length)),
            "cycle_flow": list(0 for _ in range(plot_history_length)),
            "cycle_volume": list(0 for _ in range(plot_history_length)),
            "pressure_axis_range": [0, 20],
            "flow_axis_range": [-40, 80],
            "volume_axis_range": [0, 80],
        }
        self.__plot_lock = Lock()
        self.__cycle_index: list = [
            plot_history_length,
            plot_history_length,
            plot_history_length,
        ]

    def active_payload(self, payload, *args, **kwargs):
        """
        Take the raw payload information into conveniently plotable forms and store them
        in self.__plots_database.
        """
        raw_data = self.get_db()

        if payload["type"] == "DATA":
            # The earliest index to plot for cycle plots needs to move back to keep pace
            # with the data.
            self.__cycle_index = [
                index - 1 if (index - 1 >= 0) else 0 for index in self.__cycle_index
            ]

            with self.__plot_lock:
                # Remove the oldest data and add the new data to the other end of the
                # array.
                self.__plots_database["data"] = np.append(
                    np.delete(self.__plots_database["data"], 0, 0),
                    [
                        [
                            raw_data["timestamp"],
                            raw_data["pressure_patient"],
                            raw_data["flow"],
                            raw_data["volume"],
                        ]
                    ],
                    axis=0,
                )

                # subtract latest timestamp and scale to seconds.
                self.__plots_database["timestamp"] = np.true_divide(
                    np.subtract(
                        self.__plots_database["data"][:, 0],
                        self.__plots_database["data"][-1, 0],
                    ),
                    1000,
                )

                # Pull out the specific properties we want to plot.
                self.__plots_database["pressure"] = self.__plots_database["data"][:, 1]
                self.__plots_database["flow"] = self.__plots_database["data"][:, 2]
                self.__plots_database["volume"] = self.__plots_database["data"][:, 3]
                self.__plots_database["cycle_pressure"] = self.__plots_database["data"][
                    self.__cycle_index[0] :, 1
                ]
                self.__plots_database["cycle_flow"] = self.__plots_database["data"][
                    self.__cycle_index[0] :, 2
                ]
                self.__plots_database["cycle_volume"] = self.__plots_database["data"][
                    self.__cycle_index[0] :, 3
                ]
        elif payload["type"] == "CYCLE":
            self.__cycle_index.pop(0)
            self.__cycle_index.append(self.__plot_history_length)

        return 0

    def send_update_plots_signal(self) -> int:
        """
        construct a dictionary of only the properties needed for plotting and emit the
        UpdatePlots signal containing it.
        """
        outdict = {}
        with self.__plot_lock:
            for key in [
                "flow",
                "pressure",
                "timestamp",
                "volume",
                "cycle_flow",
                "cycle_pressure",
                "cycle_volume",
            ]:
                outdict[key] = self.__plots_database[key]

        self.UpdatePlots.emit(outdict)
        return 0
