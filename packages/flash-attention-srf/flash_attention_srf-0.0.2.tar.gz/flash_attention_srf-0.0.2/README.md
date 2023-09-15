# flash-attention-srf
An implementation of sequence-parallel Flash Attention, sans softmax, with SRFs.\
Makes [ERPTRI](https://erptri.com) go brrrrr.

```python
import torch
from ops.torch.attention import Attention

B, H, L, D = 2, 4, 2 ** 10, 128
fast_attention = Attention(D, causal = True, device='cuda')

q, k, v = [torch.randn(B, H, L, D, dtype=torch.float16).cuda().requires_grad_() for i in range(3)]
output = fast_attention(q, k, v)

```
