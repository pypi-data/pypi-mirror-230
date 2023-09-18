from pprint import pprint
import numpy as np
import torch

def printvar(var):
    def formatvar(var):
        if isinstance(var, dict):
            for key, val in var.items():
                if 'name' in key: continue
                var[key] = formatvar(val)
            return var
        elif isinstance(var, (np.ndarray, torch.Tensor)):
            if len(var.shape) == 1 and var.shape[0] < 3: return var
            return f"shape{var.shape}" if isinstance(var, np.ndarray) else var.shape
        elif isinstance(var, list):
            if len(var) == 0: return var
            new_var = []
            if isinstance(var, (dict, np.ndarray)):
                new_var.append(formatvar(var))
            new_var.append(f"len({len(var)})")
            return new_var
        else:
            return var

    new_var = var.copy()
    pprint(formatvar(new_var))
