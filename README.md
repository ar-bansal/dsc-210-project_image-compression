# dsc-210-project_image-compression

A systematic comparison of linear algebra-based and state of the art image compression techniques

**Course:** DSC 210 - Numerical Linear Algebra  
**Instructor:** Dr. Tsui-Wei Weng

The aim of this project is to compare SVD-based image compression with the state of the art method, JPEG2000. For this, we used the Kodak Lossless True Color Image Suite, which is a widely used benchmark in image compression research.

For SVD, we used `numpy`, and for JPEG2000, we utilized the implementation in `Glymur`. 


# Results

## SVD-based Image Compression
![SVD Metrics](assets/svd_metrics.png)  
*For SVD, the parameter used to control the compression was the explained variance. A higher explained variance leads to lower compression ratios.*

SVD based compression achieved poor results, with compression ratios up to 2.2. Even at 97% variance, the PSNR, on average, was below 20 dB, and SSIM was under 0.7, indicating poor quality.

### SVD-based compression with a retained variance of 95%
![SVD 95% Comparison](assets/svd_95_comparison.png)  
*Here we have SVD-based compression at an explained variance of 95%. As evidenced by the difference of images, there was a significant loss of detail. This is why the compressed image does not look anything like the original image.*

### SVD-based compression with a retained variance of 99.9%
![SVD 99.9% Comparison](assets/svd_999_comparison.png)  
*If we increase the retained variance to 99%, the difference between images is minimal. We achieve a better quality image, but the compression ratio is close to 1.*

## JPEG2000
![JPEG2000 Metrics](assets/jp2_metrics.png)  
*The JPEG2000 compression was controlled by the compression ratio.*

JPEG2000 achieved compression ratios as high as 70, which is a 70 times reduction in file size, with high PSNR and structural similarity, indicating excellent compression quality.

### JPEG2000 compression with a compression ratio of 5
![JPEG2000 Compression Ratio 5](assets/jp2k_5_comparison.png)  
*Looking at the JPEG2000 compressed image at a compression ratio of 5, no discernable details were lost. This results in a better compression without loss of visual quality.*

### JPEG2000 compression with a compression ratio of 100
![JPEG2000 Compression Ratio 100](assets/jp2k_100_comparison.png)  
*Even at a compression ratio of 100, there was no blurring or loss of detail, demonstrating efficient compression without visual degradation.*


# Instructions for running the project:
## Prerequisites
    - Ubuntu 20.04+ on Linux/WSL/Docker
    - Active installation of conda

## Setting up the project
1. Clone the repository and navigate to the project's root directory.

2. Setting up the environment
    - Give execution permission to `setup_env.sh`:
    ```
    chmod +x setup_env.sh
    ```

    - Run `setup_env.sh`
    ```
    ./setup_env.sh
    ```

3. Set the paths in `.env`
    - `PROJECT_DIR` needs to be set to the current working directory. DO NOT change the other variables.

## Running the code
1. Select the `dsc210-project-team24` environment to create a kernel.

2. Run the `image_compression.ipynb` notebook.
