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
        assert impl in ['triton', 'torch']
        super().__init__()
        self.head_dim = head_dim
        self.n_features = n_features
        self.causal = causal
        if impl == 'triton':
            self.attn_fn = triton_flash_attention
        elif impl == 'torch':
            def attn_fn(q, k, v, causal=self.causal):
                s = q @ k.transpose(-1, -2)
                if causal:
                    s = s.tril()
                p = s / s.sum(-1, keepdim=True)
                o = p @ v
                return o
            self.attn_fn = attn_fn
        self.create_projection = partial(simplex_random_matrix, n_rows = self.head_dim, n_cols = self.n_features)
        projection_matrix = self.create_projection(device = device)
        self.register_buffer('projection_matrix', projection_matrix)
        self.redraw_projection_matrix(device=device)
        self.kernel_fn = softmax_kernel
        self.resample = False

    @torch.no_grad()
    def redraw_projection_matrix(self, device):
        projections = self.create_projection()
        projections /= torch.tensor(projections.shape[-1]).float().pow(0.5).to(projections)
        self.projection_matrix.copy_(projections)
        del projections

    def resample_rfs_on_call(self, resample=True):
        self.resample = resample

    def forward(self, q, k, v):
        device = q.device

        if self.resample:
            self.redraw_projection_matrix(self.projections.device)

        create_kernel = partial(softmax_kernel, projection_matrix = self.projection_matrix, device = device)
        qp = create_kernel(q, is_query = True)
        kp = create_kernel(k, is_query = False)
        out = self.attn_fn(qp, kp, v, self.causal)
        return out


