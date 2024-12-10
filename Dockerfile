# Start with the Miniconda3 base image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /home

# Clone the repository
RUN git clone https://github.com/ar-bansal/dsc-210-project_image-compression.git

# Set the working directory to the cloned repo
WORKDIR /home/dsc-210-project_image-compression

# Update and upgrade system packages
RUN apt-get update && apt-get upgrade -y

# Create the conda environment from the environment.yaml file
RUN conda env create -f environment.yaml

# Install system dependencies
RUN apt-get install -y libopenjp2-7 libopenjp2-tools libgl1-mesa-glx

# Create necessary directories for the project (relative paths)
RUN mkdir -p image_data/compressed_jp2
RUN mkdir -p image_data/compressed_svd
RUN mkdir -p metrics/jp2
RUN mkdir -p metrics/svd

# Set the environment variables in the .env file
RUN sed -i "s|^PROJECT_DIR=.*|PROJECT_DIR=$(pwd)|" .env

# Activate the environment and start Jupyter Notebook
CMD ["conda", "run", "-n", "dsc210-project-team24", "jupyter", "notebook", "--ip=0.0.0.0", "--allow-root"]
