import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import random


class WindowData:
    """
    dataclass returns windows and horizons with given parameter

    -------------------
    Parameters:
        data:nd array       :   numpy array or pandas dataframe
        window_size:int     :   size of the window
        horizon_size:int    :   size of the horizon

        stride:int          :   how much window slides on data
        shift:int           :   gap between window and horizon(if needed)

    """

    def __init__(
        self,
        data: pd.DataFrame,
        window_size: int = 7,
        horizon_size: int = 1,
        label_columns_indices: list = None,
        label_columns_names: list = None,
        stride: int = 1,
        shift: int = 0,
    ):
        self.data = data
        self.window_size = window_size
        self.horizon_size = horizon_size
        self.label_columns_indices = label_columns_indices
        self.label_columns_names = label_columns_names
        self.stride = stride
        self.shift = shift

        ## getting label indices
        if type(self.data) == pd.core.frame.DataFrame:
            self.column_indices = {name: i for i, name in enumerate(self.data.columns)}

            if self.label_columns_names is not None:
                self.label_columns_indices = [
                    self.column_indices[name] for name in self.label_columns_names
                ]

            # converting dataframe to ndarray
            self.data = self.data.to_numpy()

        # create a array of window size
        self.window_size_array = np.arange(
            self.window_size + self.shift + self.horizon_size
        )

        # create array with a forward shift
        self.all_array_index = (
            np.arange(
                len(self.data)
                - (self.window_size + self.shift + self.horizon_size - 1),
                step=self.stride,
            ).reshape(-1, 1)
            + self.window_size_array
        )

        # Spliting index in window and horizon
        self.all_windows_index = self.all_array_index[:, : self.window_size]
        self.all_horizons_index = self.all_array_index[
            :, self.window_size + self.shift :
        ]

        # actuall values of horizon and windows
        self.all_windows = self.data[self.all_windows_index]
        self.all_horizons_full = self.data[
            self.all_horizons_index
        ]  # contains all the labels

        # Work out the label column indices.
        if self.label_columns_indices is not None:
            self.all_horizons = self.all_horizons_full[..., self.label_columns_indices]

        else:
            self.all_horizons = self.all_horizons_full

    def make_split(self):
        return self.all_windows, self.all_horizons

    def train_test_val(
        self, test_size: float = 0.1, val_size: float = None, shuffle: bool = True
    ):
        """
        returns  tuple of train and test or train, test, val

        test_size: float = 0.1
        val_size : float = None
        shuffle  : bool  = True

        if val_size is not None:
            train, test = train_test_val()
        else:
            train, test, val = train_test_val()

        """
        x, y = self.make_split()

        test_len = int(len(self.all_windows) * test_size)

        # shuffle
        np.random.shuffle(test_len) if shuffle else test_len

        xtrainrest, xtest, ytrainrest, ytest = (
            self.all_windows[:-test_len],
            self.all_windows[-test_len:],
            self.all_horizons[:-test_len],
            self.all_horizons[-test_len:],
        )
        if val_size is None:
            return (xtrainrest, ytrainrest), (xtest, ytest)
        else:
            val_len = int(len(xtrainrest) * val_size)
            xtrain, xval, ytrain, yval = (
                xtrainrest[:-val_len],
                xtrainrest[-val_len:],
                ytrainrest[:-val_len],
                ytrainrest[-val_len:],
            )
            return (xtrain, ytrain), (xtest, ytest), (xval, yval)

    def plot(self, plot_cols: list = None, model=None, figsize=(15, 5), **kwargs):
        # plots data
        plt.figure(figsize=figsize)

        for i, name in enumerate(plot_cols):
            plt.subplot(len(plot_cols), 1, i + 1)
            plt.grid(True)
            plt.plot(self.all_horizons_full[..., self.column_indices[name]], **kwargs)
            plt.title(name)
            # if model is not None:
            #     predictions = model.pred
            # plt.plot(self.all_horizons_full[...,self.columns_indices[name]])

        plt.tight_layout()
        plt.show()
