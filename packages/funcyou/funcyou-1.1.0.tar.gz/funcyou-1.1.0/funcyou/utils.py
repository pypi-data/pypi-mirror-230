import io
import mimetypes
import os
import shutil
import sys
import tarfile
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import sklearn


def variable_memory():
    print(
        '''
    def sizeof_fmt(num, suffix="B"):
        """by Fred Cirera,  https://stackoverflow.com/a/1094933/1870254, modified"""
        for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
            if abs(num) < 1024.0:
                return "%3.1f %s%s" % (num, unit, suffix)
            num /= 1024.0
        return "%.1f %s%s" % (num, "Yi", suffix)
        
    
    for name, size in sorted(
        ((name, sys.getsizeof(value)) for name, value in locals().items()),
        key=lambda x: -x[1],
    )[:10]:
        print("{:>30}: {:>8}".format(name, sizeof_fmt(size)))
        '''
    )


def get_feature_names(column_transformer):
    """Get feature names from all transformers.
    Returns
    -------
    feature_names : list of strings
        Names of the features produced by transform.
    """
    # Remove the internal helper function
    # check_is_fitted(column_transformer)

    # Turn loopkup into function for better handling with pipeline later
    def get_names(trans):
        # >> Original get_feature_names() method
        if trans == "drop" or (hasattr(column, "__len__") and not len(column)):
            return []
        if trans == "passthrough":
            if hasattr(column_transformer, "_df_columns"):
                return (
                    column
                    if (
                        (not isinstance(column, slice))
                        and all(isinstance(col, str) for col in column)
                    )
                    else column_transformer._df_columns[column]
                )
            indices = np.arange(column_transformer._n_features)
            return ["x%d" % i for i in indices[column]]
        if not hasattr(trans, "get_feature_names"):
            # >>> Change: Return input column names if no method avaiable
            # Turn error into a warning
            warnings.warn(
                "Transformer %s (type %s) does not "
                "provide get_feature_names. "
                "Will return input column names if available"
                % (str(name), type(trans).__name__)
            )
            # For transformers without a get_features_names method, use the input
            # names to the column transformer
            return [] if column is None else [name + "__" + f for f in column]
        return [name + "__" + f for f in trans.get_feature_names()]

    ### Start of processing
    feature_names = []

    # Allow transformers to be pipelines. Pipeline steps are named differently, so preprocessing is needed
    if type(column_transformer) == sklearn.pipeline.Pipeline:
        l_transformers = [
            (name, trans, None, None)
            for step, name, trans in column_transformer._iter()
        ]
    else:
        # For column transformers, follow the original method
        l_transformers = list(column_transformer._iter(fitted=True))

    for name, trans, column, _ in l_transformers:
        if type(trans) == sklearn.pipeline.Pipeline:
            # Recursive call on pipeline
            _names = get_feature_names(trans)
            # if pipeline has no transformer that returns names
            if len(_names) == 0:
                _names = [name + "__" + f for f in column]
            feature_names.extend(_names)
        else:
            feature_names.extend(get_names(trans))

    return feature_names


def dir_walk(directory, show_hidden_dir=False, exclude=None, include=None):
    """
    Walks through a directory and its subdirectories recursively and counts the number of files of each MIME type.

    Args:
        directory (str): The path to the directory.
        show_hidden_dir (bool): Whether to show hidden directories or not.
        exclude (list): A list of folder names to exclude.
        include (list): A list of folder names to include.

    Returns:
        pd.DataFrame: A dataframe containing the file counts.
    """
    if exclude is None:
        exclude = []
    if include is None:
        include = []
    final = []

    for root, dirs, files in os.walk(directory):
        dir_name = os.path.basename(root)

        # Exclude hidden directories
        if not show_hidden_dir:
            dirs[:] = [d for d in dirs if not d.startswith(".")]

        # Exclude directories in the exclude list
        if dir_name in exclude:
            dirs.clear()
            continue

        # Include only directories in the include list
        if include and dir_name not in include:
            # dirs.clear()
            continue

        file_counts = {
            "directory": root,
            "base": dir_name,
            "folders": len(dirs),
            "video": 0,
            "music": 0,
            "photos": 0,
            "application/zip": 0,
            "documents": 0,
            "others": 0,
            "total files": len(files),
        }

        for file in files:
            file_path = os.path.join(root, file)
            mime_type, _ = mimetypes.guess_type(file_path)
            if mime_type is None:
                file_counts["others"] += 1

            elif mime_type.startswith("video/"):
                file_counts["video"] += 1
            elif mime_type.startswith("audio/"):
                file_counts["music"] += 1
            elif mime_type.startswith("image/"):
                file_counts["photos"] += 1
            elif mime_type == "application/zip":
                file_counts["application/zip"] += 1
            elif (
                mime_type.startswith("text/")
                or mime_type.endswith("msword")
                or mime_type.endswith("pdf")
            ):
                file_counts["documents"] += 1
        final.append(file_counts)

    return pd.DataFrame(final)


def printt(
    *args, sep=" ", end="\n", terminal_width: int = 170, file=sys.stdout, flush=False
):
    if terminal_width is None:
        terminal_width = shutil.get_terminal_size().columns

    # Calculate the available width for each argument
    num_args = len(args)
    arg_width = terminal_width // num_args

    # Determine if there are any plots in the arguments
    has_plots = any(isinstance(arg, plt.Figure) for arg in args)

    # Determine the number of lines needed for each argument
    max_lines = max(
        max(str(arg).count("\n") + 1 for arg in args), 1 if has_plots else 0
    )

    # Loop through each line
    for line_num in range(max_lines):
        # Loop through each argument
        for i, arg in enumerate(args):
            # Convert argument to string
            arg_str = str(arg)

            # Check if the argument is a plot
            if isinstance(arg, plt.Figure):
                plt.figure(arg.number)
                plt.imshow(arg)
                plt.axis("off")
                plt.show()
                continue

            # Split the argument string into lines
            lines = arg_str.splitlines()

            # Get the current line or an empty string if there are no more lines
            line = lines[line_num] if line_num < len(lines) else ""

            # Calculate the width for this argument
            arg_width_adjusted = arg_width - len(sep)
            if i == num_args - 1:
                arg_width_adjusted -= len(end)

            # Truncate or pad the line to fit the width
            line_str = line[:arg_width_adjusted].ljust(arg_width_adjusted)

            # Print the line
            file.write(line_str)

            # Print the separator between arguments
            if i < num_args - 1:
                file.write(sep)

        # Print the end character/string
        file.write(end)

    # Flush the output if specified
    if flush:
        file.flush()


import json

import toml
import yaml
from yaml import SafeLoader
from yaml.constructor import ConstructorError


class DotDict(dict):
    def __init__(self, dictionary=None):
        if dictionary is not None:
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    value = DotDict(value)
                self[key] = value

    def __getattr__(self, key):
        if key in self:
            return self[key]
        else:
            raise AttributeError(f"'DotDict' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        self[key] = value

    def save_json(self, file_path):
        with open(file_path, "w") as file:
            json.dump(self, file, indent=4)

    def save_toml(self, file_path):
        with open(file_path, "w") as file:
            toml.dump(self, file)

    def save_yaml(self, file_path):
        with open(file_path, "w") as file:
            yaml.dump(self, file)

    @classmethod
    def from_json(cls, file_path):
        with open(file_path, "r") as file:
            data = json.load(file)
        return cls(data)

    @classmethod
    def from_toml(cls, file_path):
        with open(file_path, "r") as file:
            data = toml.load(file)
        return cls(data)


if __name__ == "__main__":
    print("main")


def main():
    ...


if __name__ == "__main__":
    main()
