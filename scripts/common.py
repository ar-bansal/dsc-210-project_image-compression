import os
import dotenv
import pandas as pd
import cv2


def load_config():
    dotenv.load_dotenv()

    PROJECT_DIR = os.environ["PROJECT_DIR"]
    RAW_DATA_DIR = os.path.join(PROJECT_DIR, os.environ["RAW_DATA_DIR"])
    JP2K_DIR = os.path.join(PROJECT_DIR, os.environ["JP2_COMPRESSED_DIR"])
    SVD_DIR = os.path.join(PROJECT_DIR, os.environ["SVD_COMPRESSED_DIR"])
    
    return PROJECT_DIR, RAW_DATA_DIR, JP2K_DIR, SVD_DIR


def load_data():
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


def save_png(image, path):
    cv2.imwrite(path, cv2.cvtColor(image, cv2.COLOR_RGB2BGR))