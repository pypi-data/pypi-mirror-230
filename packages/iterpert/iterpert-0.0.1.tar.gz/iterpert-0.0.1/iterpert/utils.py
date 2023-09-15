
from .query_strategies import KMeansSampling, kernel_based_active_learning, TypiClust
import os
import pickle

def get_strategy(name):
    
    if name == "KMeansSampling":
        return KMeansSampling
    elif name =="kernel_based_active_learning":
        return kernel_based_active_learning
    elif name == "TypiClust":
        return TypiClust
    else:
        raise NotImplementedError
    

def load_kernel(dataset_name, kernel_name):
    if dataset_name == 'replogle_k562_gw_1000hvg':
        kernel_path = '/home/huangk28/scratch/knowledge_kernels_gw/'
    elif dataset_name == 'replogle_k562_essential_1000hvg+pert_in_gene':
        kernel_path = '/home/huangk28/scratch/knowledge_kernels/'
    elif dataset_name == 'replogle_rpe1_essential_1000hvg':
        kernel_path = '/home/huangk28/scratch/knowledge_kernels_rpe1/'
    else:
        kernel_path = '/home/huangk28/scratch/knowledge_kernels_1k/'
    if not os.path.exists(kernel_path + kernel_name):
        raise ValueError('Kernel does not exist')
    with open(kernel_path + kernel_name + '/pert_list.pkl', 'rb') as f:
        pert_list = pickle.load(f)
    with open(kernel_path + kernel_name + '/kernel.pkl', 'rb') as f:
        kernel_npy = pickle.load(f)
    with open(kernel_path + kernel_name + '/feat.pkl', 'rb') as f:
        feat = pickle.load(f)
    return pert_list, kernel_npy, feat