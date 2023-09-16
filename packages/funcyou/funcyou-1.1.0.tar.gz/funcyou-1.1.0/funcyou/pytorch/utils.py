from pathlib import Path

import numpy as np


def calculate_class_weights_from_directory(directory_path):
    """
    This function calculates the class weights for a given directory of images.

    Args:
      directory_path (str): The path to the directory of images.

    Returns:
      (list, list, np.ndarray): The class distribution, class weights, and bincount.
    """

    # Create a Path object for the directory
    directory = Path(directory_path)

    # Get a list of subdirectories (classes)
    classes = sorted([d.name for d in directory.iterdir() if d.is_dir()])

    # Initialize class_dist to store class labels
    class_dist = []

    # Iterate through each class directory
    for idx, class_name in enumerate(classes):
        class_path = directory / class_name
        num_files = len(list(class_path.glob("*")))
        class_dist.extend([idx] * num_files)

    # Calculate the class counts using bincount
    bincount = np.bincount(class_dist)

    # Calculate class weights as 1 / bincount for each class
    class_weights = 1.0 / bincount[class_dist]

    return class_dist, class_weights, bincount
