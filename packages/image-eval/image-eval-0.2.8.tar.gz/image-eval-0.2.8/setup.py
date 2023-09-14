import os

from setuptools import setup, find_packages


def readfile(filename):
    with open(filename, 'r+') as f:
        return f.read()


lib_folder = os.path.dirname(os.path.realpath(__file__))
requirement_path = f"{lib_folder}/requirements.txt"
install_requires = []
if os.path.isfile(requirement_path):
    with open(requirement_path) as f:
        install_requires = f.read().splitlines()

setup(
    name="image-eval",
    version="0.2.8",
    description="A library for evaluating image generation models",
    long_description=readfile("README.md"),
    long_description_content_type="text/markdown",
    author="Storia AI",
    author_email="mihail@storia.ai",
    py_modules=["eval"],
    license=readfile("LICENSE"),
    packages=find_packages(include=["image_eval", "image_eval.*"]),
    entry_points={
        "console_scripts": [
            "image_eval= eval:main"
        ]
    },
    install_requires=[
        "image-reward==1.5",
        "lpips==0.1.4",
        "networkx==3.1",
        "nvidia-cuda-cupti-cu11==11.7.101",
        "nvidia-cuda-nvrtc-cu11==11.7.99",
        "nvidia-cuda-runtime-cu11==11.7.99",
        "nvidia-cudnn-cu11==8.5.0.96",
        "nvidia-cufft-cu11==10.9.0.58",
        "nvidia-curand-cu11==10.2.10.91",
        "nvidia-cusolver-cu11==11.4.0.1",
        "nvidia-cusparse-cu11==11.7.4.91",
        "nvidia-nccl-cu11==2.14.3",
        "nvidia-nvtx-cu11==11.7.91",
        "piq==0.8.0",
        "pytorch-lightning==2.0.8",
        "streamlit==1.26.0",
        "sympy==1.12",
        "tabulate==0.9.0",
        "torch-fidelity==0.3.0",
        "torchaudio==0.12.1+cu113",
        "triton==2.0.0"
    ]
)
