import os
import numpy as np
import pandas as pd
import glymur
from scripts.svd import compress_image_using_svd
from scripts.metrics import calculate_metrics
from scripts.common import load_config, save_png
from typing import List, Sequence, Literal, Union, Dict


PROJECT_DIR, RAW_DATA_DIR, JP2_COMPRESSED_DIR, SVD_COMPRESSED_DIR = load_config()


__all__ = ["compress_images"]


def compress_images(
        images: List[np.ndarray], 
        image_names: Sequence[str], 
        method: Literal["jp2", "svd"], 
        param_set: Sequence[Union[int, float]], 
        num_images: int | None = None
) -> Dict[str, Union[List[np.ndarray], pd.DataFrame]]:
    """
    Compress a list of images using a specified compression method and parameter set.

    This function compresses the input images using either the Singular Value Decomposition (SVD) method or the JPEG2000 (JP2) method, 
    depending on the provided `method` argument. It processes a subset of the images (if specified by `num_images`), applies the compression 
    for each parameter in `param_set`, and returns the compressed images and their corresponding metrics.

    Parameters
    ----------
    images : List[np.ndarray]
        A list of images represented as numpy arrays to be compressed.
    
    image_names : Sequence[str]
        A sequence of image filenames (without extensions) corresponding to the input images.
    
    method : Literal["jp2", "svd"]
        The compression method to use. Can be either "svd" (Singular Value Decomposition) or "jp2" (JPEG2000).
    
    param_set : Sequence[Union[int, float]]
        A sequence of parameters to be used for the compression method. For SVD, this represents the explained variance; 
        for JP2, it represents the compression ratio.
    
    num_images : int, optional
        The number of images to process. If not provided, all images in the `images` list will be processed.

    Returns
    -------
    Dict[str, Union[List[np.ndarray], pd.DataFrame]]
        A dictionary where the keys are the parameter values from `param_set` and the values are dictionaries containing:
        - `compressed_images`: A list of the compressed images (numpy arrays).
        - `metrics`: A pandas DataFrame containing the compression metrics for each image, including metrics such as PSNR and compression ratio.

    Notes
    -----
    - The function supports two compression methods: "svd" and "jp2".
        - For "svd", the compression is done using Singular Value Decomposition with the specified explained variance parameter.
        - For "jp2", the compression is done using JPEG2000 with the specified compression ratio parameter.
    - If `num_images` is `None`, all the images will be processed.
    - The metrics for each image are calculated and stored in a pandas DataFrame.
    - The compressed images are saved to disk in the corresponding directories (`SVD_COMPRESSED_DIR` or `JP2_COMPRESSED_DIR`).
    """
    if not num_images:
        num_images = len(images)

    if not method in ["jp2", "svd"]:
        raise ValueError("method must be one of ['jp2', 'svd']")

    data = dict()

    for param in param_set:
        # Used for creating the metrics dataframe
        img_names_list = []
        compressed_imgs = []
        metrics_df = pd.DataFrame()

        for original_img, img_name in zip(images[:num_images], image_names[:num_images]):
            original_img_path = os.path.join(RAW_DATA_DIR, img_name)
            if method == "svd":
                name = f"{img_name[:-4]}_expvar{param}.png"
                compressed_img_path = os.path.join(SVD_COMPRESSED_DIR, name)
                compressed_img, metadata = compress_image_using_svd(original_img, explained_variance=param)
                save_png(compressed_img, compressed_img_path)
            else:
                name = f"{img_name[:-4]}_cratio{param}.jp2"
                compressed_img_path = os.path.join(JP2_COMPRESSED_DIR, name)
                glymur.Jp2k(compressed_img_path, original_img, cratios=[param])
                compressed_img = glymur.Jp2k(compressed_img_path)[:]

            compressed_imgs.append(compressed_img)
            img_names_list.append(name)

            metrics = pd.DataFrame([calculate_metrics(original_img_path, compressed_img_path)])
            metrics_df = pd.concat([metrics_df, metrics], axis=0).reset_index(drop=True)

        metrics_df.insert(0, "img_name", img_names_list)

        data[param] = dict(
            compressed_images=compressed_imgs, 
            metrics=metrics_df 
        )

    return data
