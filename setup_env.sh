#!/bin/bash

# Create conda environment using the environment.yaml file
conda create env create -f environment.yaml


sudo apt update -y 
sudo apt upgrade -y


# Install OpenJPEG to use Glymur
sudo apt install libopenjp2-7 libopenjp2-tools
