import os
import pandas as pd
import glymur
from scripts.svd import compress_image_using_svd
from scripts.metrics import calculate_metrics
from scripts.common import load_config, save_png


PROJECT_DIR, RAW_DATA_DIR, JP2K_DIR, SVD_DIR = load_config()


def compress_images(images, image_names, method, param_set, num_images=None):
    # images is a list of images to compress
    # Method can be "svd" or "jp2"
    # param set is a list of params for the given method
    # TODO: Remove num_images 
    # TODO: Convert output data dict into a class
    if not num_images:
        num_images = len(images)

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
                compressed_img_path = os.path.join(SVD_DIR, name)
                compressed_img, metadata = compress_image_using_svd(original_img, explained_variance=param)
                save_png(compressed_img, compressed_img_path)
            else:
                name = f"{img_name[:-4]}_cratio{param}.jp2"
                compressed_img_path = os.path.join(JP2K_DIR, name)
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
