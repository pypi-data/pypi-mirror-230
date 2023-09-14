import torch
from memory_profiler import profile
import pyqtorch.modules as pyq
from pyqtorch.core.utils import _apply_gate, _apply_batch_gate
from timeit import timeit
import time
from itertools import product


batch_size = 1
N_QUBITS = 25
thetas = torch.rand(batch_size)
QUBIT = 0


# rxsparsemat = _fill_identities(rxmat,(0,), [i for i in range(10)]).squeeze(0).to_sparse()

rx = pyq.RX([0], N_QUBITS)



def run_mem_script():
    state = pyq.zero_state(N_QUBITS, batch_size)
    for i in range(2):
        state = _apply_gate(state, rx.matrices(thetas).squeeze(-1), rx.qubits, rx.n_qubits)


# @timeit
def run_time_script():
    _vmap_gate(state, rx.matrices(thetas), rx.qubits, rx.n_qubits,batch_size)


@profile
def matmul():

    pass


def find_indices_of_bitstrings_with_zero_at_i(N:int, i:int, bit:str ='0'):
    if i >= N or i < 0:
        raise ValueError("Index i must be in the range [0, N-1]")
    
    indices = []
    for idx, p in enumerate(product('01', repeat=N)):
        if p[i] == bit:
            indices.append(idx)
            
    return indices

# def permute_matmul() -> torch.Tensor:



if __name__ == '__main__':
    start = time.time()
    indices = find_indices_of_bitstrings_with_zero_at_i(4, 0)
    end = time.time()
    print(indices)
    print(abs(end-start))
    # run_time()