from setuptools import setup, find_packages

setup(
    name='boolformer',
    version='0.1.0',
    description="Transformers for symbolic regression of Boolean functions",
    author="Stéphane d'Ascoli",
    author_email="stephane.dascoli@gmail.com",
    packages=find_packages(),
    license="MIT",
    install_requires=[
        "sympy==1.11.1",
        "matplotlib",
        "numpy",
        "pandas",
        "requests",
        "scikit-learn",
        "scipy",
        "seaborn",
        "setproctitle",
        "tqdm",
        "wandb",
        "gdown",
        "torch==2.0.0",
        "boolean.py==4.0",
        "graphviz",
        "treelib"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)