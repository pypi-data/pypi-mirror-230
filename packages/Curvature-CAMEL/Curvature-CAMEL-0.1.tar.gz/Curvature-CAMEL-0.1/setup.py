from setuptools import setup, find_packages
import os

# Read the README file's content
with open(os.path.join(os.path.dirname(__file__), 'README.md'), 'r') as f:
    long_description = f.read()

setup(
    name='Curvature-CAMEL',
    version='0.1',
    author='Your Name',
    author_email='your.email@example.com',
    description='A brief description of CAMEL',
    long_description=long_description,
    long_description_content_type="text/markdown", 
    url='https://github.com/yourusername/camel',  
    packages=find_packages(),
    install_requires=[
        'numpy',
        'scipy',
        'sklearn',
        'pynndescent',
        'numba'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  
)

