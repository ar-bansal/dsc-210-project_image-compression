import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, List, Sequence, Union, Tuple


__all__ = ["plot_image", "plot_image_comparison", "plot_compression_metrics"]


def _aggregate_metric(compressed: Dict[str, Dict[str, pd.DataFrame]], metric_name: str) -> List[np.ndarray]:
    """
    Aggregate the maximum, minimum, and average values of a specific metric across all compression parameters.

    This function computes the maximum, minimum, and average values of the given metric (e.g., compression ratio, 
    PSNR, SSIM) for all the compression parameters in the provided `compressed` dictionary.

    Parameters
    ----------
    compressed : dict
        A dictionary where each key is a compression parameter, and each value is a dictionary containing metrics.
        The metrics should include the specified `metric_name`.
    metric_name : str
        The name of the metric to aggregate (e.g., "compression_ratio", "peak_signal_noise_ratio", "structural_similarity").

    Returns
    -------
    list of np.ndarray
        A list containing three NumPy arrays: max values, min values, and avg values of the specified metric 
        across the compression parameters.
    """
    metric_max = [compressed[param]["metrics"][metric_name].max() for param in compressed.keys()]
    metric_min = [compressed[param]["metrics"][metric_name].min() for param in compressed.keys()]
    metric_avg = [compressed[param]["metrics"][metric_name].mean() for param in compressed.keys()]

    return [metric_max, metric_min, metric_avg]


def _plot_metric(x: np.ndarray, metric: List[np.ndarray], ax: plt.Axes, title: str, xlabel: str) -> None:
    """
    Plot a metric (max, min, avg) on the provided axis.

    This function plots the max, min, and average values of a metric on the same graph, with shaded 
    areas representing the range between the max and min values.

    Parameters
    ----------
    x : np.ndarray
        The x-axis values, usually the compression parameter set.
    metric : list of np.ndarray
        A list containing three arrays: the max, min, and avg values of the metric to plot.
    ax : matplotlib.axes.Axes
        The axis to plot the metric on.
    title : str
        The title for the plot.
    xlabel : str
        The label for the x-axis.

    Returns
    -------
    None

    Notes
    -----
    This function adds a legend, grid lines, and fills the area between the max and min values 
    to visually highlight the range of the metric.
    """
    ax.plot(x, metric[0], label="max", alpha=0.5)
    ax.plot(x, metric[1], label="min", alpha=0.5)
    ax.plot(x, metric[2], label="avg", alpha=0.5)
    ax.fill_between(x, metric[0], metric[1], alpha=0.1)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(alpha=0.5, ls="--")
    ax.legend()


def plot_compression_metrics(compressed: Dict[str, Dict], param_set: Sequence[Union[int, float]], suptitle: str, xlabel: str) -> None:
    """
    Plot compression metrics (compression ratio, PSNR, SSIM) for different compression parameters.

    This function generates subplots for the compression ratio, PSNR, and SSIM metrics, showing the 
    maximum, minimum, and average values for each compression parameter.

    Parameters
    ----------
    compressed : dict
        A dictionary containing compression data, with compression parameters as keys and corresponding 
        compression results (including metrics) as values.
    param_set : sequence of int or float
        A sequence of compression parameters used in the compression.
    suptitle : str
        The overall title for the figure.
    xlabel : str
        The label for the x-axis, typically describing the compression parameter.

    Returns
    -------
    None

    Notes
    -----
    - The function plots three subplots for the compression ratio, PSNR, and SSIM.
    - It uses shaded regions to represent the range between the max and min values for each metric.
    """

    true_cr = "True Compression Ratio"
    psnr = "Peak Signal to Noise Ratio"
    ssim = "Structural Similarity"
    metrics = {
        true_cr: _aggregate_metric(compressed, "compression_ratio"), 
        psnr: _aggregate_metric(compressed, "peak_signal_noise_ratio"), 
        ssim: _aggregate_metric(compressed, "structural_similarity")
    }

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    fig.suptitle(suptitle)
    line_alpha = 0.65
    fill_alpha = 0.15
    axes[0].axhline(1, c="k", ls="--", alpha=line_alpha)
    fill_upper_limit = 1
    fill_lower_limit = min(min(metrics[true_cr][1]), fill_upper_limit)
    axes[0].fill_between(param_set, [fill_upper_limit] * len(param_set), [fill_lower_limit] * len(param_set), alpha=fill_alpha, color="black")

    axes[1].axhline(20, c="k", ls="--", alpha=line_alpha)
    fill_upper_limit = 20
    fill_lower_limit = min(min(metrics[psnr][1]), fill_upper_limit)
    axes[1].fill_between(param_set, [fill_upper_limit] * len(param_set), [fill_lower_limit] * len(param_set), alpha=fill_alpha, color="black")

    axes[2].axhline(0.7, c="k", ls="--", alpha=line_alpha)
    fill_upper_limit = 0.7
    fill_lower_limit = min(min(metrics[ssim][1]), fill_upper_limit)
    axes[2].fill_between(param_set, [0.7] * len(param_set), [fill_lower_limit] * len(param_set), alpha=fill_alpha, color="black")
    for idx, (title, metric) in enumerate(metrics.items()):
        ax = axes[idx]
        _plot_metric(param_set, metric, ax, title, xlabel)


def plot_image(img: np.ndarray, ax: plt.Axes, title: str, label: str = None) -> None:
    """
    Display an image on the provided axis.

    This function displays an image on a given axis with an optional label. The axis ticks and 
    labels are removed for a cleaner image display. If a label is provided, it is annotated on 
    the center of the image.

    Parameters
    ----------
    img : np.ndarray
        The image to display, represented as a 3D NumPy array (height, width, channels).
    ax : matplotlib.axes.Axes
        The axis to display the image on.
    title : str
        The title for the image.
    label : str, optional
        The label to display at the center of the image, by default None.

    Returns
    -------
    None

    Notes
    -----
    If a label is provided, it will be displayed at the center of the image using `annotate`.
    """

    ax.imshow(img, label=label)
    ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
    ax.set_title(title)
    if not label is None:
        ax.annotate(
            label, 
            xy=(0.5, 0.5),
            xycoords='axes fraction', 
            textcoords='axes fraction', 
            ha='center', 
            va='center', 
            bbox=dict(boxstyle="round", fc="0.9", facecolor='black'), 
            family="monospace"
        )
        ax.set_axis_off()


def _plot_image_comparison_helper(original_image: np.ndarray, compressed_image: np.ndarray, title: str = None, stats: str = None) -> None:
    """
    Helper function to plot a comparison between the original and compressed images.

    This function plots the original image, compressed image, and the difference between 
    them in a 3-panel layout. If statistics are provided, they are displayed in a fourth panel.

    Parameters
    ----------
    original_image : np.ndarray
        The original image to display.
    compressed_image : np.ndarray
        The compressed version of the image to display.
    title : str, optional
        The title for the figure, by default None.
    stats : str, optional
        The statistics to display in the "Statistics" panel, by default None.

    Returns
    -------
    None

    Notes
    -----
    The function assumes that `original_image` and `compressed_image` are 3D numpy arrays.
    """

    ncols = 3
    if not stats is None:
        ncols = 4
    
    fig, axes = plt.subplots(1, ncols, figsize=(17, 5))
    if title:
        fig.suptitle(title)
        fig.subplots_adjust(top=0.85)

    plot_image(original_image, axes[0], "Original Image")
    plot_image(compressed_image, axes[1], "Compressed Image")
    plot_image(original_image - compressed_image, axes[2], "Difference of Images")

    if not stats is None:
        plot_image(np.ones_like(original_image) * 255, axes[3], "Statistics", label=str(stats))

    fig.tight_layout()
    fig.set_constrained_layout(True)


def plot_image_comparison(imgs: List[np.ndarray], compressed: Dict[str, Dict], param_name: str, idx: int, step: int = None) -> None:
    """
    Plot and compare an original image with its compressed versions for different parameter settings.

    This function visualizes the original image, its compressed versions for each compression parameter, 
    and the difference between the original and compressed images. Additionally, it can display the statistics 
    for each compression setting, if available.

    Parameters
    ----------
    imgs : List[np.ndarray]
        A list of original images (each represented as a NumPy array).
    compressed : Dict[str, Dict]
        A dictionary where each key corresponds to a compression parameter, and the value is another dictionary 
        containing the compressed images and their associated metrics for that parameter.
    param_name : str
        The name of the compression parameter, used for labeling the plots.
    idx : int
        The index of the image to compare in the `imgs` list.
    step : int, optional
        The step size for selecting which compression parameters to include in the comparison. Defaults to `None`, 
        meaning all parameters will be included. If provided, it determines the interval for selecting which images 
        are compared.

    Returns
    -------
    None
        This function directly generates and displays the comparison plots.
    
    Notes
    -----
    - For each parameter in `compressed`, the original and compressed images, along with their differences, are plotted.
    - If compression statistics are available, they are displayed on the last plot.
    - The function creates subplots and adjusts the layout for better visualization.
    """

    original_img = imgs[idx]
    compressed_imgs = [compressed[param]["compressed_images"][idx] for param in compressed.keys()]

    param_set = list(compressed.keys())
    if not step:
        step = 1

    for i in range(0, len(compressed_imgs), step):
        stats = compressed[param_set[i]]["metrics"].loc[idx].to_string()
        _plot_image_comparison_helper(
            original_img, 
            compressed_imgs[i], 
            f"{param_name} {param_set[i]}", 
            stats
        )
