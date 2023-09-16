[![PyPI](https://img.shields.io/pypi/v/boolformer.svg)](
https://pypi.org/project/boolformer/)
# Boolformer: symbolic regression of Boolean functions with transformers

This repository contains code for the paper [Boolformer: symbolic regression of Boolean functions with transformers]().

## Installation
This package is installable via pip:

```pip install boolformer```

## Demo

We include a small notebook that loads a pre-trained model you can play with in ```example.ipynb```

## Usage

Import the model in a few lines of code:
```python 
from boolformer import load_boolformer
boolformer_noiseless = load_boolformer('noiseless')
boolformer_noisy     = load_boolformer('noisy')
```

Using the model:
```python
import numpy as np
inputs = np.array([  
    [False, False],
    [False, True ],
    [True , False],
    [True , True ],
])
outputs1 = np.array([False, False, False, True])
outputs2 = np.array([True, False, False, True])
inputs = [inputs, inputs]
outputs = [outputs1, outputs2]
pred_trees, error_arr, complexity_arr = boolformer_noiseless.fit(inputs, outputs, verbose=False, beam_size=10, beam_type="search")

for pred_tree in pred_trees:
    pred_tree.treelib().show()
```


## Training and evaluation

To launch a model training with additional arguments (arg1,val1), (arg2,val2):
```python train.py --arg1 val1 --arg2 --val2```

All hyper-parameters related to training are specified in ```parsers.py```, and those related to the environment are in ```envs/environment.py```.


## Citation

If you want to reuse this material, please considering citing the following:
```
@article{kamienny2022end,
  title={End-to-end symbolic regression with transformers},
  author={Kamienny, Pierre-Alexandre and d'Ascoli, St{\'e}phane and Lample, Guillaume and Charton, Fran{\c{c}}ois},
  journal={arXiv preprint arXiv:2204.10532},
  year={2022}
}
```

## License

This repository is licensed under MIT licence.
