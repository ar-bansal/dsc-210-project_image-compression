import os
import dotenv
import numpy as np
import pandas as pd
import cv2
import glymur
from skimage.metrics import structural_similarity as ssim, peak_signal_noise_ratio as psnr
from typing import Dict, List, Union, Literal
from scripts.common import load_config


dotenv.load_dotenv()

PROJECT_DIR, _, _, _ = load_config()

SVD_METRICS_DIR = os.path.join(PROJECT_DIR, os.environ["SVD_METRICS_DIR"])
JP2_METRICS_DIR = os.path.join(PROJECT_DIR, os.environ["JP2_METRICS_DIR"])


__all__ = ["calculate_metrics", "save_metrics"]


def calculate_metrics(original_image_path: str, compressed_image_path: str) -> Dict[str, float]:
    """
    Calculate the compression metrics between the original and compressed images.

    This function computes three key metrics for image compression:
    - Compression ratio
    - Peak Signal-to-Noise Ratio (PSNR)
    - Structural Similarity Index (SSIM)

    The function reads the original and compressed images from their file paths, then calculates the above metrics. 
    The results are returned as a dictionary.

    Parameters
    ----------
    original_image_path : str
        The file path of the original image to compare.
    compressed_image_path : str
        The file path of the compressed image to compare.

    Returns
    -------
    dict
        A dictionary containing the following keys:
        - `compression_ratio`: The ratio of the original image size to the compressed image size.
        - `peak_signal_noise_ratio`: The PSNR value between the original and compressed images.
        - `structural_similarity`: The SSIM value between the original and compressed images.

    Notes
    -----
    - The function handles `.png` and `.jp2` formats for the compressed image.
    - PSNR and SSIM are computed using the original and compressed images.
    - The compression ratio is calculated as the ratio of file sizes.
    """

    original_image = cv2.cvtColor(cv2.imread(original_image_path), cv2.COLOR_BGR2RGB)
    if compressed_image_path.endswith(".png"):
        compressed_image = cv2.cvtColor(cv2.imread(compressed_image_path), cv2.COLOR_BGR2RGB)
    else:
        compressed_image = glymur.Jp2k(compressed_image_path)[:]

    rounder = lambda x, digits=4: round(x, digits)
    compression_ratio = rounder(os.path.getsize(original_image_path)/ os.path.getsize(compressed_image_path))
    peak_signal_noise_ratio = rounder(float(psnr(original_image, compressed_image)))
    structural_similarity = rounder(float(ssim(original_image, compressed_image, channel_axis=2)))
    
    metrics = {
        "compression_ratio": compression_ratio, 
        "peak_signal_noise_ratio": peak_signal_noise_ratio, 
        "structural_similarity": structural_similarity
    }

    return metrics


def save_metrics(compressed: Dict[str, Dict[str, Union[List[np.ndarray], pd.DataFrame]]], method: Literal["jp2", "svd"]) -> None:
    """
    Save the compression metrics to CSV files for each compression parameter.

    This function saves the metrics of compressed images into CSV files, categorized by the compression method (`svd` or `jp2`). 
    The metrics are saved as `metrics_expvar{param}.csv` or `metrics_cratio{param}.csv` files in the appropriate directories 
    based on the selected method.

    Parameters
    ----------
    compressed : dict
        A dictionary where the keys are compression parameters, and the values are dictionaries containing:
        - `compressed_images`: A list of compressed images.
        - `metrics`: A pandas DataFrame containing the metrics for the compressed images.
    method : str
        The compression method used, which must be one of ['svd', 'jp2'].

    Returns
    -------
    None
        The function does not return any value. It directly saves the metrics to CSV files.

    Raises
    ------
    ValueError
        If the provided `method` is not one of ['svd', 'jp2'].

    Notes
    -----
    - The `method` parameter determines the directory and parameter name for saving the metrics.
    - Metrics for the SVD method are saved in `SVD_METRICS_DIR` and include the `expvar` parameter.
    - Metrics for the JP2 method are saved in `JP2_METRICS_DIR` and include the `cratio` parameter.
    """
    if method == "svd":
        save_dir = SVD_METRICS_DIR
        param_name = "expvar"
    elif method == "jp2":
        save_dir = JP2_METRICS_DIR
        param_name = "cratio"
    else:
        raise ValueError("method must be one of ['jp2', 'svd']")

    for param, data_dict in compressed.items():
        metrics = data_dict["metrics"]
        name = f"metrics_{param_name}{param}.csv"
        metrics.to_csv(os.path.join(save_dir, name), index=False)