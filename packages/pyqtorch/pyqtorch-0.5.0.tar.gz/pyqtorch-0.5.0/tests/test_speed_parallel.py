# import time
# import pyqtorch.modules as pyq
# from pyqtorch.modules.utils import _apply_parallel
# # from pyqtorch.core.utils import _apply_parallel
# import torch



# N_QUBITS = 16
# def hea(n_qubits:int, depth:int) -> list:
#     for d in range(depth):
#         rxgates = [pyq.RX([i], N_QUBITS) for i in range(N_QUBITS)]
#         rygates = [pyq.RY([i], N_QUBITS) for i in range(N_QUBITS)]
#         rzgates = [pyq.RZ([i], N_QUBITS) for i in range(N_QUBITS)]

# circ = pyq.QuantumCircuit(N_QUBITS, rxgates+rygates+rzgates)

# thetas = torch.rand(1)
# state = pyq.zero_state(N_QUBITS)


# def circ_fwd(state) -> torch.Tensor:
#     return circ(state, thetas)


# def parallel_(state) -> torch.Tensor:
#     state = _apply_parallel(state, thetas, rxgates, N_QUBITS)
#     state = _apply_parallel(state, thetas, rygates, N_QUBITS)
#     state = _apply_parallel(state, thetas, rzgates, N_QUBITS)
#     return state


# def timeit(func):
#     def wrapper(*args, **kwargs):
#         start_time = time.time()
#         result = func(*args, **kwargs)
#         end_time = time.time()
#         print(f"{func.__name__} took {end_time - start_time} seconds to run.")
#         return result
#     return wrapper


# @timeit
# def time_fn():
#     circ_fwd(state)


# if __name__ == "__main__":
#     time_fn()
