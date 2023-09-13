from setuptools import find_packages, setup

setup(
    name="signs_detector",
    version="0.0.3",
    author="Invian Development team",
    author_email="your.email@example.com",  # idk
    description="Super tool",
    packages=find_packages(),
    install_requires=[
        "numpy==1.25.2",
        "opencv-python==4.8.0.76",
        "onnxruntime==1.15.1",
    ],
    keywords=['python', 'first package'],
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.11",
    ]
    # package_data={"signs_detection": ["__main__.py"]},
    # entry_points={
    #     "console_scripts": [
    #         "signs_detection=signs_detection.__main__:main",
    #     ],
    # },
)