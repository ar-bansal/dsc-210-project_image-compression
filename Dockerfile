# Start with the Miniconda3 base image
FROM continuumio/miniconda3

# Set the working directory
WORKDIR /home

# Clone the repository
RUN git clone https://github.com/ar-bansal/dsc-210-project_image-compression.git

# Set the working directory to the cloned repo
WORKDIR /home/dsc-210-project_image-compression

# Update and upgrade system packages and install system dependencies
RUN apt-get update && apt-get upgrade -y && \
apt-get install -y libopenjp2-7 libopenjp2-tools libgl1-mesa-glx

# Create the conda environment from the environment.yaml file
RUN conda env create -f environment.yaml

# Create necessary directories for the project (relative paths)
RUN mkdir -p image_data/compressed_jp2 image_data/compressed_svd metrics/jp2 metrics/svd

# Set the environment variables in the .env file
RUN sed -i "s|^PROJECT_DIR=.*|PROJECT_DIR=$(pwd)|" .env

# Install jupyter in the environment
RUN conda run -n dsc210-project-team24 pip install jupyter

# Activate the environment and start Jupyter Notebook
CMD ["conda", "run", "-n", "dsc210-project-team24", "jupyter", "notebook", "--ip=0.0.0.0", "--allow-root", "--NotebookApp.token=''", "--NotebookApp.password=''"]