import torch
from torch import nn

class CompactSpectralGRU(nn.Module):
    def __init__(self, embed_dim, hidden_dim):
        super().__init__()
        self.encoder = nn.Sequential(
            nn.Linear(27, embed_dim),
            nn.ReLU()
        )
        self.gru = nn.GRU(
            input_size=embed_dim,
            hidden_size=hidden_dim,
            num_layers=1,
            batch_first=True
        )
        self.head = nn.Linear(hidden_dim, 1)

    def forward(self, x):
        # x: (B, W, P, F)
        z = self.encoder(x)       # (B,W,P,E)
        z = z.mean(dim=2)         # (B,W,E)
        h, _ = self.gru(z)        # (B,W,H)
        return self.head(h[:, -1]).squeeze(-1)
