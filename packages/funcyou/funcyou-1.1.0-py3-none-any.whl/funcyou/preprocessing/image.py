import os

import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from tqdm import tqdm


def resize_func(
    file_path: str,
    dest_path: str = None,
    px: int = 512,
    keep_aspect_ratio=True,
    quality: int = 100,
    format=None,
):
    """
    Resizes photos in a directory with given paramters

    -----------------------------

    Paramters-----------------
        file_path:str =  folder which contains files

        dest_path:str =  folder where to keep the resized folder (if not provided
                        resized files will be kept in file_path)

        px:int = max pixel range to resize upto

        keep_aspect_ratio =  keep aspect ratio ?

        format:str = default: None ['PNG','JPEG'] any one

        quality:int = quality range between 1 to 100
    """

    if dest_path == None:
        dest_path = file_path

    try:
        for item in tqdm(os.listdir(file_path)):
            img_path = os.path.join(file_path, item)
            img = Image.open(img_path)
            # Dimensions
            w, h = img.size
            #             print('height:', h, 'width: ', w)
            # ratio
            ratio = h / w
            #             print(ratio)

            filename, extension = os.path.splitext(item)
            #             print(filename, '   :  ', extension)

            if keep_aspect_ratio:
                if ratio < 1:
                    h = px * ratio
                    w = px

                else:
                    w = px / ratio
                    h = px
            else:
                h = px
                w = px

            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

            #             print('new height:', h, 'new width:',w)

            img_resized = img.resize((int(w), int(h)), Image.ANTIALIAS)
            img_resized.save(
                f"{dest_path}/{filename}_resized{extension}",
                format=format,
                quality=100,
            )

    except Exception as e:
        raise ("Exception Occured: ", e)


class Patcher:
    def __init__(self, patch_size: tuple):
        self.patch_size = patch_size

    def extract(self, images: np.array) -> np.array:
        if images.ndim == 3:
            images = np.expand_dims(images, axis=0)  # Convert a single image to a batch
        batch_size, height, width, channels = images.shape
        patch_height, patch_width = self.patch_size

        # Calculate the number of patches in the height and width dimensions
        num_patches_height = height // patch_height
        num_patches_width = width // patch_width

        patches = []

        for i in range(num_patches_height):
            for j in range(num_patches_width):
                patch = images[
                    :,
                    i * patch_height : (i + 1) * patch_height,
                    j * patch_width : (j + 1) * patch_width,
                    :,
                ]
                patches.append(patch.reshape(batch_size, -1))

        return np.stack(patches, axis=1)

    def show(self, patches: np.array, gap_size: int = 2) -> None:
        batch_size, num_patches, _ = patches.shape
        patch_height, patch_width = self.patch_size

        # Calculate the number of patches in the height and width dimensions
        num_patches_height = int(np.sqrt(num_patches))
        num_patches_width = num_patches // num_patches_height

        # Calculate the size of the gap between patches

        # Calculate the size of the grid image
        grid_height = num_patches_height * (patch_height + gap_size) - gap_size
        grid_width = num_patches_width * (patch_width + gap_size) - gap_size
        grid = np.zeros((batch_size, grid_height, grid_width, 3), dtype=np.uint8)

        for i in range(num_patches_height):
            for j in range(num_patches_width):
                patch_idx = i * num_patches_width + j
                patch = patches[:, patch_idx, :].reshape(
                    batch_size, patch_height, patch_width, 3
                )
                y_start = i * (patch_height + gap_size)
                y_end = y_start + patch_height
                x_start = j * (patch_width + gap_size)
                x_end = x_start + patch_width
                grid[:, y_start:y_end, x_start:x_end, :] = patch

        # Display the grid of patches as separate images
        for i in range(batch_size):
            plt.figure(figsize=(8, 8))
            plt.imshow(grid[i])
            plt.axis("off")
            plt.show()


def main():
    ...


if __name__ == "__main__":
    main()
