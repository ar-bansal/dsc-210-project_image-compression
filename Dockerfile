# Start with the Miniconda3 base image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /home

# Update and upgrade system packages and install system dependencies
RUN apt-get update && apt-get upgrade -y && \
apt-get install -y libopenjp2-7 libopenjp2-tools libgl1-mesa-glx

# Clone the main branch from the repository
RUN git config --global http.postBuffer 524288000
RUN git clone --depth 1 https://github.com/ar-bansal/dsc-210-project_image-compression.git

# Set the working directory to the cloned repo
WORKDIR /home/dsc-210-project_image-compression

# Create necessary directories for the project (relative paths)
RUN mkdir -p image_data/compressed_jp2 image_data/compressed_svd metrics/jp2 metrics/svd

# Set the environment variables in the .env file
RUN sed -i "s|^PROJECT_DIR=.*|PROJECT_DIR=$(pwd)|" .env

# Create the conda environment from the environment.yaml file
RUN conda env create -f environment.yaml

# Install jupyter in the environment
RUN conda run -n dsc210-project-team24 pip install jupyter

EXPOSE 8888

# Activate the environment and start Jupyter Notebook
CMD ["sh", "-c", "echo 'Jupyter is running at: http://localhost:8888' && conda run -n dsc210-project-team24 jupyter notebook --ip=0.0.0.0 --allow-root --NotebookApp.token='' --NotebookApp.password=''"]