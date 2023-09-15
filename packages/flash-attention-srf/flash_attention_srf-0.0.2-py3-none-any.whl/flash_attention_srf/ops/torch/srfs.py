import math
import torch
from scipy.linalg import hadamard

@torch.no_grad()
def orthogonal_matrix_chunk_hadamard(d, device=None):
    """
    Generate an orthogonal matrix chunk using Hadamard transformation.
    
    Args:
    - d (int): Dimension of the matrix.
    - device (torch.device, optional): The desired device of returned tensor. Default: None.

    Returns:
    - torch.Tensor: Orthogonal matrix of shape (d, d).
    """
    # Generate 3 Hadamard matrices
    h1, h2, h3 = [torch.tensor(hadamard(d), device=device) for _ in range(3)]
    
    # Generate 3 diagonal matrices with random signs
    d1, d2, d3 = [torch.diag(torch.sign(torch.rand(d, device=device) - 0.5)).to(h1) for _ in range(3)]
    
    # Compute the orthogonal matrix by multiplying the Hadamard and diagonal matrices
    m = torch.matmul(torch.matmul(h3, d3), torch.matmul(torch.matmul(h2, d2), torch.matmul(h1, d1)))
    
    # Normalize the matrix
    m = m / m[0].pow(2).sum().sqrt()
    return m

@torch.no_grad()
def compute_simplex_dir(d, device=None):
    """
    Compute the simplex directions given the dimensionality of the random features.
    
    Args:
    - d (int): Dimension of the random features.
    - device (torch.device, optional): The desired device of returned tensor. Default: None.

    Returns:
    - torch.Tensor: Simplex directions matrix of shape (d, d).
    """
    # Compute the projection directions
    simp_dir = (torch.diag(torch.ones(d)) / math.sqrt(2) -
                torch.ones((d, d)) * (1 / ((d-1) * math.sqrt(2))) * (1 + 1 / math.sqrt(d)))
    
    simp_dir[d-1, :] = 1 / math.sqrt(2 * d) * torch.ones((d))
    simp_dir[:, d-1] = 0
    
    # Normalize the simplex direction matrix
    simp_dir = simp_dir / math.sqrt(torch.sum(simp_dir[1, :]**2))
    
    # Randomize the simplex directions
    rand_sim = torch.matmul(torch.diag(torch.distributions.chi2.Chi2(torch.ones(d) * d).sample().sqrt()), simp_dir)
    rand_sim = rand_sim.to(device)
    
    return rand_sim

@torch.no_grad()
def simplex_random_matrix(n_rows, n_cols, device=None):
    """
    Generate a random matrix with blocks of simplex directions.
    
    Args:
    - n_rows (int): Number of rows for the matrix.
    - n_cols (int): Number of columns for the matrix.
    - device (torch.device, optional): The desired device of returned tensor. Default: None.

    Returns:
    - torch.Tensor: Random matrix of shape (n_rows, n_cols).
    """
    n_full_blocks = int(n_rows / n_cols)
    block_list = []

    # Compute full blocks
    for _ in range(n_full_blocks):
        q = orthogonal_matrix_chunk_hadamard(n_cols, device=device)
        q = torch.matmul(compute_simplex_dir(n_cols, device=device), q)
        block_list.append(q)

    # Compute any remaining rows for the matrix
    remaining_rows = n_rows - n_full_blocks * n_cols
    if remaining_rows > 0:
        q = orthogonal_matrix_chunk_hadamard(n_cols, device=device)
        q = torch.matmul(compute_simplex_dir(n_cols, device=device), q)
        block_list.append(q[:remaining_rows])

    # Concatenate all blocks to form the final matrix
    final_matrix = torch.cat(block_list)
    
    return final_matrix

