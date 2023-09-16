import torch.nn as nn


class Patcher(nn.Module):
    """
    A PyTorch module that patches a tensor into a batch of patches.

    Args:
        patch_size (tuple[int, int]): The size of the patches to be extracted.
    """

    def __init__(self, patch_size):
        super(Patcher, self).__init__()
        self.patch_size = patch_size

    def forward(self, images):
        """
        Patches a tensor into a batch of patches.

        Args:
            images (torch.Tensor): The input tensor.

        Returns:
            torch.Tensor: The tensor of patches.
        """
        if images.dim() == 3:
            images = images.unsqueeze(0)  # Convert a single image to a batch

        batch_size, channels, height, width = images.size()
        patch_height, patch_width = self.patch_size

        # Calculate the number of patches in the height and width dimensions
        num_patches_height = height // patch_height
        num_patches_width = width // patch_width
        num_patches = num_patches_height * num_patches_width

        # Extract patches from the image
        patches = images.unfold(2, patch_height, patch_height).unfold(
            3, patch_width, patch_width
        )
        patches = patches.contiguous().view(
            batch_size, channels, -1, patch_height, patch_width
        )

        # Transpose the patches to put them in the format (batch_size, num_patches, channels, patch_height, patch_width)
        patches = (
            patches.permute(0, 2, 3, 4, 1)
            .contiguous()
            .view(batch_size, num_patches, -1)
        )

        return patches
