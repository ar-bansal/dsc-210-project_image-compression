import numpy as np
from typing import Dict, Tuple, Union


__all__ = ["compress_image_using_svd"]


def _compute_svd(image: np.ndarray) -> Dict[str, Tuple[np.ndarray, np.ndarray, np.ndarray]]:
    """
    Compute the Singular Value Decomposition (SVD) of each channel of the input image.

    This function decomposes the input image into its red, green, and blue channels, 
    and computes the Singular Value Decomposition (SVD) for each channel separately.
    The SVD of each channel is returned as a tuple containing the U, Σ (singular values), 
    and V^T matrices.

    Parameters
    ----------
    image : np.ndarray
        The input image in RGB format (height, width, 3), where each pixel has a red, green, and blue value.

    Returns
    -------
    dict
        A dictionary where the keys are the color channels (`'red'`, `'green'`, `'blue'`), 
        and the values are tuples containing the SVD results for each channel:
        - The first element of the tuple is the U matrix.
        - The second element is the singular values (Σ).
        - The third element is the V^T matrix.

    Notes
    -----
    - The function performs the SVD independently for each RGB channel.
    - `np.linalg.svd` is used with `full_matrices=False` to return the reduced form of the SVD.
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
    Returns an array with the top k singular values and zeros for the remaining elements.

    This function creates a new array with the same shape as the input singular values array (`sigma`),
    where the first `k` elements are the first `k` singular values from `sigma`, and the remaining elements 
    are set to zero.

    Parameters
    ----------
    sigma : np.ndarray
        The array of singular values (1D array).
    k : int
        The number of top singular values to retain.

    Returns
    -------
    np.ndarray
        A 1D array of the same shape as `sigma`, where the first `k` values are the top `k` singular values 
        from `sigma` and the remaining values are zeros.

    Notes
    -----
    - If `k` is greater than the length of `sigma`, the function will return an array with zeros for all elements.
    """
    sigma_aux = np.zeros_like(sigma)
    sigma_aux[:k] = sigma[:k]
    return sigma_aux


def _get_explained_variance(sigma: np.ndarray) -> np.ndarray:
    """
    Get the cumulative explained variance from the singular values of a matrix.

    This function calculates the explained variance for each singular value, which is the square of the singular 
    values divided by the total variance (sum of squares of all singular values). Then, it computes the cumulative 
    explained variance by summing these individual explained variances.

    Parameters
    ----------
    sigma : np.ndarray
        The array of singular values (1D array) from the Singular Value Decomposition (SVD).

    Returns
    -------
    np.ndarray
        A 1D array containing the cumulative explained variance. Each element represents the cumulative 
        explained variance up to the corresponding singular value.

    Notes
    -----
    - The total variance is calculated as the sum of the squares of the singular values.
    - The explained variance for each singular value is its squared value divided by the total variance.
    - The cumulative explained variance is computed using the `np.cumsum` function.
    """
    total_variance = np.sum(sigma ** 2)
    variance_explained = (sigma ** 2) / total_variance
    cumulative_variance = np.cumsum(variance_explained)

    return cumulative_variance


def _reconstruct_channel(u: np.ndarray, sigma: np.ndarray, vt: np.ndarray) -> np.ndarray:
    """
    Reconstruct an image channel from its SVD matrices.

    This function reconstructs an image channel using its Singular Value Decomposition (SVD) components 
    (U, Sigma, V^T). It computes the product of U, the diagonal matrix of singular values, and V^T to 
    obtain the reconstructed image. The values are then scaled to the range [0, 255] to ensure the pixel 
    values are within the valid range for image representation.

    Parameters
    ----------
    u : np.ndarray
        The U matrix from the SVD of the image channel (2D array).
    sigma : np.ndarray
        The array of singular values from the SVD of the image channel (1D array).
    vt : np.ndarray
        The V^T matrix from the SVD of the image channel (2D array).

    Returns
    -------
    np.ndarray
        A 2D array representing the reconstructed image channel, with pixel values in the range [0, 255],
        converted to `np.uint8`.

    Notes
    -----
    - The reconstruction is performed by calculating the dot product of U, Sigma (as a diagonal matrix), and V^T.
    - Min-max scaling is applied to the reconstructed image to ensure that its pixel values lie within the range [0, 255].
    - The resulting image is converted to the `np.uint8` datatype to match the raw image format.
    """

    reconstructed_img = np.dot(u, np.dot(np.diag(sigma), vt))

    # Min-max scaling to ensure that the values lie within the valid range of [0, 255]
    min_val, max_val = np.min(reconstructed_img), np.max(reconstructed_img)
    scaled_img = ((reconstructed_img - min_val) * 255) / (max_val - min_val)

    # Converting the datatype to uint8 to match raw images datatype
    return scaled_img.astype(np.uint8)


def compress_image_using_svd(
        image: np.ndarray, 
        explained_variance: float = 0.975, 
        k_components: int = None
) -> Tuple[np.ndarray, Dict[str, Dict[str, Union[float, int]]]]:
    """
    Compress an image using Singular Value Decomposition (SVD).

    This function compresses each channel of the input image by retaining the most significant singular values 
    based on either the explained variance or the specified number of components (`k_components`). The compression 
    ensures that for each channel, at least `explained_variance` percent of the variance is preserved. If the 
    `k_components` parameter is provided, the explained variance is ignored, and the number of components is 
    fixed to `k_components`.

    Parameters
    ----------
    image : np.ndarray
        The input image to compress, represented as a 3D NumPy array (height, width, 3) in RGB format.
    explained_variance : float, optional
        The percentage of variance to retain for each channel. This value must be between 0 and 1. The default 
        value is 0.975 (97.5% variance explained).
    k_components : int, optional
        The number of singular value components to retain for each channel. If provided, `explained_variance` 
        is ignored.

    Returns
    -------
    np.ndarray
        A 3D NumPy array representing the compressed image with the same shape as the input image but with 
        reduced rank for each channel.
    dict
        A dictionary containing metadata about the compression process, including:
        - `"variance_explained"`: A dictionary mapping each color channel to the percentage of variance explained 
          by the retained singular values.
        - `"num_components"`: A dictionary mapping each color channel to the number of components retained.

    Notes
    -----
    - If `k_components` is not provided, the function calculates the minimum number of components required to 
      explain at least `explained_variance` percent of the total variance for each channel.
    - If `k_components` is provided, it overrides the `explained_variance` parameter.
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