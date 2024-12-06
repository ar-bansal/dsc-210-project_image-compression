import os
import dotenv
import pandas as pd
import cv2
import numpy as np
from typing import List, Tuple


__all__ = ["load_config", "load_data", "save_png"]


def load_config() -> Tuple[str, str, str, str]:
    """
    Loads environment variables from a `.env` file and returns directory paths for various project components.

    This function loads environment variables using `dotenv.load_dotenv()`, retrieves paths for the main project directory, 
    raw data directory, JPEG2000 compressed data directory, and SVD compressed data directory. The paths are returned as 
    strings.

    Parameters
    ----------
    None

    Returns
    -------
    Tuple[str, str, str, str]
        A tuple containing the following directory paths:
        - `PROJECT_DIR`: The main project directory path.
        - `RAW_DATA_DIR`: The directory path for raw data.
        - `JP2_COMPRESSED_DIR`: The directory path for JPEG2000 compressed data.
        - `SVD_COMPRESSED_DIR`: The directory path for SVD compressed data.

    Notes
    -----
    The function relies on the presence of environment variables `PROJECT_DIR`, `RAW_DATA_DIR`, 
    `JP2_COMPRESSED_DIR`, and `SVD_COMPRESSED_DIR` in the `.env` file. If these environment variables are not set,
    an exception will be raised. The function uses the `os.environ` to access the environment variables and 
    constructs paths based on the `PROJECT_DIR` base directory.
    """
    dotenv.load_dotenv()

    PROJECT_DIR = os.environ["PROJECT_DIR"]
    RAW_DATA_DIR = os.path.join(PROJECT_DIR, os.environ["RAW_DATA_DIR"])
    JP2_COMPRESSED_DIR = os.path.join(PROJECT_DIR, os.environ["JP2_COMPRESSED_DIR"])
    SVD_COMPRESSED_DIR = os.path.join(PROJECT_DIR, os.environ["SVD_COMPRESSED_DIR"])
    
    return PROJECT_DIR, RAW_DATA_DIR, JP2_COMPRESSED_DIR, SVD_COMPRESSED_DIR


def load_data() -> Tuple[List[np.ndarray], pd.DataFrame]:
    """
    Loads image data from PROJECT_DIR/image_data/raw_data, and returns a list of images and a DataFrame with metadata.

    This function reads all images in the PROJECT_DIR/image_data/raw_data directory, converts them to RGB format, 
    and stores their metadata (name, size in bytes, and shape) in a Pandas DataFrame. It returns a tuple consisting 
    of a list of image arrays and the DataFrame containing metadata for each image.

    Parameters
    ----------
    None

    Returns
    -------
    Tuple[List[np.ndarray], pd.DataFrame]
        A tuple where:
        - A list of numpy arrays, each representing an image in RGB format.
        - A DataFrame with the following columns:
            - `img_name`: The name of the image file.
            - `raw_img_size_in_bytes`: The size of the image file in bytes.
            - `img_shape`: The shape of the image array.

    Notes
    -----
    The images are loaded from a directory path specified by `RAW_DATA_DIR`, which is determined by 
    the `load_config()` function. The images are read using OpenCV, converted from BGR to RGB, and stored in a list.
    """
    _, RAW_DATA_DIR, _, _ = load_config()
    df = pd.DataFrame(
        columns=["img_name", "raw_img_size_in_bytes", "img_shape"], 
        dtype=object
    ).sort_values(by="img_name").reset_index(drop=True)

    imgs = []

    for idx, img_name in enumerate(sorted(os.listdir(RAW_DATA_DIR))):
        img_path = os.path.join(
            RAW_DATA_DIR, img_name
        )

        img = cv2.cvtColor(cv2.imread(img_path), cv2.COLOR_BGR2RGB)
        imgs.append(img)

        df.at[idx, "img_name"] = img_name
        df.at[idx, "raw_img_size_in_bytes"] = os.path.getsize(img_path) 
        df.at[idx, "img_shape"] = img.shape

    return imgs, df


def save_png(image: np.ndarray, path: str) -> None:
    """
    Saves a given image array as a PNG file at the specified path.

    This function takes a numpy array representing an image in RGB format, converts it to BGR format 
    (as required by OpenCV for saving), and saves it as a PNG file at the specified path.

    Parameters
    ----------
    image : np.ndarray
        A numpy array representing the image to be saved. The array should be in RGB format.
    
    path : str
        The path (including filename) where the image will be saved. The file extension should be `.png`.

    Returns
    -------
    None

    Notes
    -----
    The function uses OpenCV's `cv2.imwrite` method to save the image. Ensure that the provided path includes 
    the `.png` extension for proper saving.
    """
    cv2.imwrite(path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))