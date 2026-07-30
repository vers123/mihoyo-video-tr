from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="mihoyo-video-tr",
    version="2.0.0",
    author="vers123",
    description="Video frame & audio swapper with rhythm-based grouping",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/vers123/mihoyo-video-tr",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=[
        "opencv-python",
        "pydub",
        "audioop-lts",
    ],
    extras_require={
        "bpm": ["librosa"],
        "test": ["pytest>=7.0.0", "pytest-cov>=4.0.0"],
    },
    entry_points={
        "console_scripts": [
            "mihoyo-video-tr=mihoyo_video_tr.cli:main",
        ],
    },
)