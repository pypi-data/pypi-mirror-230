# Iterative Perturb-seq

<p align="center"><img src="img/illustration.png" alt="logo" width="600px" /></p>

# Install

```
pip install iterpert
```

# API interface

```python

from iterpert.iterpert import IterPert
strategy = 'IterPert' # choose from 'Random', 'BALD', 'BatchBALD', 'BAIT', 'ACS-FW', 'Core-Set', 'BADGE', 'LCMD', 'IterPert'
interface = IterPert(weight_bias_track = True, 
                     exp_name = strategy,
                     device = 'cuda:0', 
                     seed = 1)

path = '/home/huangk28/scratch/perturb_seq_data/gears_data/'
interface.initialize_data(path = path,
                          dataset_name='replogle_k562_essential_1000hvg',
                          batch_size = 256)

interface.initialize_model(epochs = 20, hidden_size = 64)
interface.initialize_active_learning_strategy(strategy = strategy)

interface.start(n_init_labeled = 100, n_round = 5, n_query = 100)

```

# Reproduce experiments
Please refer to `reproduce_repo` directory to reproduce each experiment. Notably, `reproduce_script.sh` contains sh files to generate all experiments. `figX.ipynb` is the notebook that produces the figures.