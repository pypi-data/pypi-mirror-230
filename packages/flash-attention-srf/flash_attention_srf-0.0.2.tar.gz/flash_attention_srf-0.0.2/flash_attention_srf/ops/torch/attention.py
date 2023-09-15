import math
from functools import partial
import torch
from ..triton.flash_attn import attention as triton_flash_attention
from ..torch.srfs import simplex_random_matrix
from ..torch.kernels import softmax_kernel

class Attention(torch.nn.Module):
    def __init__(self, head_dim, n_features = None, causal = True, impl = 'triton', device = 'cpu'):
        if n_features is None:
            n_features = int(round(2 ** math.log2(head_dim)))
        assert n_features == int(round(2 ** math.log2(n_features)))
        assert impl in ['triton']
        super().__init__()
        self.head_dim = head_dim
        self.n_features = n_features
        self.causal = causal
        if impl == 'triton':
            self.attn_fn = triton_flash_attention
        self.create_projection = partial(simplex_random_matrix, n_rows = self.head_dim, n_cols = self.n_features)
        projection_matrix = self.create_projection()
        self.register_buffer('projection_matrix', projection_matrix)
        self.kernel_fn = softmax_kernel

    @torch.no_grad()
    def redraw_projection_matrix(self, device):
        projections = self.create_projection(device = device)
        self.projection_matrix.copy_(projections)
        del projections

    def forward(self, q, k, v):
        device = q.device

        create_kernel = partial(softmax_kernel, projection_matrix = self.projection_matrix, device = device)
        q = create_kernel(q, is_query = True)
        k = create_kernel(k, is_query = False)

        out = self.attn_fn(q, k, v, self.causal)
        return out


