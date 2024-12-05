import numpy as np
import matplotlib.pyplot as plt


def _compute_svd(image: np.ndarray):
    """
    Compute the SVD of each channel of the input image. 
    """
    # Separate the channels of the image. 
    red_channel, green_channel, blue_channel = image[:, :, 0], image[:, :, 1], image[:, :, 2]

    # Compute the SVD for each channel separately. 
    red_svd = np.linalg.svd(red_channel, full_matrices=False)  
    green_svd = np.linalg.svd(green_channel, full_matrices=False)
    blue_svd = np.linalg.svd(blue_channel, full_matrices=False)

    return {
        "red": red_svd, 
        "green": green_svd, 
        "blue": blue_svd, 
    }


def _get_top_k_singular_values(sigma: np.ndarray, k: int) -> np.ndarray:
    """
    Returns an array of shape like sigma. The first k elements are those of sigma, and 
    the remaining are zeros. 
    """
    sigma_aux = np.zeros_like(sigma)
    sigma_aux[:k] = sigma[:k]
    return sigma_aux


def _get_explained_variance(sigma: np.ndarray) -> np.ndarray:
    """
    Get the cumulative explained variance from the SVD of a matrix.
    """
    total_variance = np.sum(sigma ** 2)
    variance_explained = (sigma ** 2) / total_variance
    cumulative_variance = np.cumsum(variance_explained)

    return cumulative_variance


def _reconstruct_channel(u, sigma, vt):
    """
    Reconstruct the an image from its SVD matrices. 
    """
    reconstructed_img = np.dot(u, np.dot(np.diag(sigma), vt))

    # Min-max scaling to ensure that the values lie within the valid range of [0, 255]
    min_val, max_val = np.min(reconstructed_img), np.max(reconstructed_img)
    scaled_img = ((reconstructed_img - min_val) * 255) / (max_val - min_val)

    # Converting the datatype to uint8 to match raw images datatype
    return scaled_img.astype(np.uint8)


def compress_image_using_svd(image: np.ndarray, explained_variance: float=0.975, k_components: int=None):
    """
    Compress the image using SVD. 

    Ensures that for each channel, at least 'explained_variance' percent of variance is explained. 
    If k_components is given, explained_variance is ignored. 
    """

    # Flag for k_components calculation. 
    k_given = False
    if k_components:
        k_given = True

    # Calculate the channel-wise SVD of the image. 
    svd = _compute_svd(image)

    reconstructed_channels = []
    metadata = {
        "variance_explained": dict(),
        "num_components": dict()
    }

    for color, (u, sigma, vt) in svd.items():
        cumulative_variance = _get_explained_variance(sigma)

        # If k_components is not given by user, calculate using explained_variance. 
        if not k_given:
            k_components = np.argmax(cumulative_variance >= explained_variance) + 1
        
        # Get the top/first 'k' components of sigma
        sigma_top_k = _get_top_k_singular_values(sigma, k_components)

        channel = _reconstruct_channel(u, sigma_top_k, vt) 
        reconstructed_channels.append(channel)

        metadata["variance_explained"][color] = float(cumulative_variance[k_components - 1])
        metadata["num_components"][color] = int(k_components)

    return np.stack(reconstructed_channels, axis=-1), metadata