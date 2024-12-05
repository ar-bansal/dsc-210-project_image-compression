import numpy as np
import matplotlib.pyplot as plt


# def plot_image_comparison(original_image, compressed_image, title=None):
#     fig, axes = plt.subplots(1, 3, figsize=(17, 7))
#     if title:
#         fig.suptitle(title)
#     ax = axes[0]
#     ax.imshow(original_image)
#     ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
#     ax.set_title("Original Image")

#     ax = axes[1]
#     ax.imshow(compressed_image)
#     ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
#     ax.set_title("Compressed Image")

#     ax = axes[2]
#     ax.imshow(original_image - compressed_image)
#     ax.tick_params(left=False, bottom=False, labelleft=False, labelbottom=False)
#     ax.set_title("Difference of Images")


def _aggregate_metric(compressed, metric_name):
    metric_max = [compressed[param]["metrics"][metric_name].max() for param in compressed.keys()]
    metric_min = [compressed[param]["metrics"][metric_name].min() for param in compressed.keys()]
    metric_avg = [compressed[param]["metrics"][metric_name].mean() for param in compressed.keys()]

    return [metric_max, metric_min, metric_avg]

def _plot_metric(x, metric, ax, title, xlabel):
    ax.plot(x, metric[0], label="max", alpha=0.5)
    ax.plot(x, metric[1], label="min", alpha=0.5)
    ax.plot(x, metric[2], label="avg", alpha=0.5)
    ax.fill_between(x, metric[0], metric[1], alpha=0.1)
    ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.grid(alpha=0.5, ls="--")
    ax.legend()


def plot_compression_metrics(compressed, param_set, suptitle, xlabel):
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


def plot_image(img, ax, title, label=None):
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


def _format_stats(series):
    splits = str(series).split()
    keys, values = "", ""
    for i in range(0, len(splits), 2):
        keys += "{:8}\n".format(splits[i])
        values += "{:>8}\n".format(splits[i+1])

    return keys, values


def _plot_image_comparison_helper(original_image, compressed_image, title=None, stats=None):
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


def plot_image_comparison(imgs, compressed, param_name, idx, step=None):
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
