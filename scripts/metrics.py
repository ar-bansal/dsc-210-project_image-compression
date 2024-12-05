import os
import dotenv
import cv2
import glymur
from skimage.metrics import structural_similarity as ssim, peak_signal_noise_ratio as psnr
from scripts.common import load_config


dotenv.load_dotenv()

PROJECT_DIR, _, _, _ = load_config()

SVD_METRICS_DIR = os.path.join(PROJECT_DIR, os.environ["SVD_METRICS_DIR"])
JP2_METRICS_DIR = os.path.join(PROJECT_DIR, os.environ["JP2_METRICS_DIR"])


def calculate_metrics(original_image_path: str, compressed_image_path: str):
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


def save_metrics(compressed, method):
    if method == "svd":
        save_dir = SVD_METRICS_DIR
        param_name = "expvar"
    else:
        save_dir = JP2_METRICS_DIR
        param_name = "cratio"

    for param, data_dict in compressed.items():
        metrics = data_dict["metrics"]
        name = f"metrics_{param_name}{param}.csv"
        metrics.to_csv(os.path.join(save_dir, name), index=False)