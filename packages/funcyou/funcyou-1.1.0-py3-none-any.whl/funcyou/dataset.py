import json
import os
import random
import re
import shutil
from pathlib import Path


# make data splitstr
def make_data_split(
    main_path,
    test=True,
    test_split_ratio: float = 0.2,
    val=True,
    val_split_ratio: float = 0.1,
    shuffle=True,
):
    """
    Make data split Train/test/val
    Note: keep a copy of the ORIGINAL DATASET

    Args:
        main_path = Dataset directory that has class subdirectory
        test_split_ratio = float value between 0 to 1
        val = bool to split for validation data
        val_split_ratio = float value for split
        shuffle = shuffle

    Returns:
        Splited DATASET (train/test/validation)

    """
    main = Path(main_path)
    class_names = sorted([i.name for i in main.iterdir()])
    print(class_names)
    total_files = len(os.listdir(main / class_names[0]))
    try:
        # create train/test/validation
        os.makedirs(main / "train")

        # creating test set
        if test:
            os.makedirs(main / "test")
            test_image_num = 0
            test_image_num = int(total_files * test_split_ratio)
            print("test images:", test_image_num)
            for class_name in class_names:
                class_path = main / class_name
                if shuffle:
                    sample_images = random.sample(
                        os.listdir(class_path), test_image_num
                    )

                else:
                    sample_images = sorted(os.listdir(class_path))[:test_image_num]

                sample_images = [class_path / i for i in sample_images]
                test_class = str(main / "test" / class_name)
                os.makedirs(test_class)
                for file in sample_images:
                    shutil.move(str(file), test_class)

        # creating validation dataset
        val_image_num = 0
        if val:
            os.makedirs(main / "validation")
            val_image_num = int(total_files * val_split_ratio)
            print("val images:", val_image_num)
            for class_name in class_names:
                class_path = main / class_name
                if shuffle:
                    sample_images = random.sample(os.listdir(class_path), val_image_num)

                else:
                    sample_images = sorted(os.listdir(class_path))[:val_image_num]

                sample_images = [class_path / i for i in sample_images]
                test_class = str(main / "validation" / class_name)
                os.makedirs(test_class)
                for file in sample_images:
                    shutil.move(str(file), test_class)

        for class_name in class_names:
            shutil.move(str(main / class_name), str(main / "train" / class_name))

        print("train images:", total_files - test_image_num - val_image_num)
    except Exception as e:
        print("Exception Occured: ", e)


def download_kaggle_resource(resource, download_path="dataset", kaggle_json_path=None):
    """
    Downloads a Kaggle dataset or competition using the Kaggle API key stored in kaggle.json.

    Args:
        resource (str): URL of the Kaggle dataset/competition or API command.
        download_path (str): Path where the resource will be downloaded.
        kaggle_json_path (str, optional): Path to the kaggle.json file containing the API key.
    """

    # Find the path to kaggle.json if not provided
    default_path = Path(os.path.expanduser("~/.kaggle/kaggle.json"))
    default_path.parent.mkdir(exist_ok=True)
    if not default_path.exists():
        if kaggle_json_path is not None:
            shutil.copy(kaggle_json_path, default_path)
        else:
            raise ValueError(
                "kaggle.json not found in default location and kaggle_json_path not provided."
            )

    # Load the Kaggle API key from kaggle.json
    with open(default_path) as f:
        kaggle_credentials = json.load(f)

    # Configure the Kaggle API
    from kaggle.api.kaggle_api_extended import KaggleApi

    api = KaggleApi()
    api.authenticate()

    if resource.startswith("kaggle "):
        # Run the provided API command directly
        os.system(resource)
        return

    # Handle URL-based resource
    url_parts = resource.split("/")

    if "datasets" in url_parts:
        resource_type = "datasets"
        dataset_part_index = url_parts.index("datasets") + 1
    elif "competitions" in url_parts:
        resource_type = "competitions"
        competition_part_index = url_parts.index("competitions") + 1
    else:
        raise ValueError("Invalid Kaggle URL")

    # Extract resource name from the URL
    resource_name = url_parts[-1]

    # Define the download path for the resource
    resource_download_path = Path(download_path) / resource_name

    # Create the directory if it doesn't exist
    resource_download_path.mkdir(parents=True, exist_ok=True)

    # Download the resource
    if resource_type == "datasets":
        dataset_path = "/".join(url_parts[dataset_part_index:])
        api.dataset_download_files(dataset_path, path=resource_download_path)
    elif resource_type == "competitions":
        competition_path = "/".join(url_parts[competition_part_index:])
        api.competition_download_files(competition_path, path=resource_download_path)

    print(f"Resource downloaded to: {resource_download_path}")


if __name__ == "__main__":
    print("hello world")
