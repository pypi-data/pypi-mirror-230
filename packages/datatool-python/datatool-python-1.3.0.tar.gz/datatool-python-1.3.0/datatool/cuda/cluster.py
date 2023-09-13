"""
There is an implementation of a clusterization algorithm on CUDA.
"""

import math
import warnings

import numpy as np

try:
    import pycuda.autoinit
    import pycuda.driver as cuda
    from pycuda import gpuarray
    from pycuda.compiler import SourceModule
except ImportError:
    warnings.warn("Pycuda is not installed")
else:
    from .base import get_cuda_struct


def clusterize(items, code):
    """
    The function clusterizes the given items on GPU using 'edge' defined
    in the code. 'items' must by a numpy array. Struct data types are allowed.

    Example:

        items = np.array(
            [('text', i, 0) for i in range(11)],
            dtype=np.dtype(
                [('key', 'S4'), ('x', np.uint8), ('y', np.uint16)],
                align=True
            )
        )

        code = '''
        __device__ int edge(const Item* item1, const Item* item2) {
            return (item1->x == 2 * item2->x) || (item2->x == 2 * item1->x);
        }
        '''

        clusters = clusterize(items, code)

        print(clusters)  # [0 1 1 3 1 5 3 7 1 9]
    """
    # Build Item type code
    item_type = get_cuda_struct(items.dtype)

    # Compile kernel
    kernel = _get_cluster_pass_kernel(item_type, code)

    # Size of items
    size = len(items)

    # Prepare cluster array
    cluster_arr = np.arange(size, dtype=np.uint32)
    cluster_arr_gpu = gpuarray.to_gpu(cluster_arr)

    # Pass items to GPU
    items_gpu = cuda.mem_alloc(items.nbytes)
    cuda.memcpy_htod(items_gpu, items)

    # Clusterization loop
    cluster_sum_prev = None
    while True:
        # Run kernel
        kernel(
            np.uint32(size),
            items_gpu,
            cluster_arr_gpu,
            block=(1, 1024, 1),
            grid=(size, math.ceil(size / 1024))
        )
        # Calculate sum of clusters
        cluster_sum = gpuarray.sum(cluster_arr_gpu, dtype=np.uint64).get()

        # Leave the loop if the sum does not change
        if cluster_sum == cluster_sum_prev:
            break

        # Save the sum to cluster_sum_prev
        cluster_sum_prev = cluster_sum

    # Return clusters of the given items
    return cluster_arr_gpu.get()


def _get_cluster_pass_kernel(item_type, code):
    data = {'item_type': item_type, 'code': code}
    source = """
        typedef unsigned int uint;
        typedef unsigned short ushort;
        typedef %(item_type)s Item;

        %(code)s

        __global__ void cluster_pass(
                    uint size,
                    const Item* items_arr,
                    uint* cluster_arr
                ) {
            uint i = threadIdx.x + blockIdx.x * blockDim.x;
            uint j = threadIdx.y + blockIdx.y * blockDim.y;

            if ((i < size) && (j < i)) {
                int has_edge = edge(items_arr + i, items_arr + j);

                if (has_edge) {
                    if (cluster_arr[i] != cluster_arr[j]) {
                        uint m = min(cluster_arr[i], cluster_arr[j]);
                        atomicMin(cluster_arr + i, m);
                        atomicMin(cluster_arr + j, m);
                    }
                }
            }
        }
    """ % data
    return SourceModule(source).get_function("cluster_pass")
