"""
pipeline/conv_lstm.py
---------------------
ConvLSTM implementation for keypoint smoothing.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F

class ConvLSTMCell(nn.Module):
    def __init__(self, input_dim, hidden_dim, kernel_size):
        super().__init__()
        self.input_dim = input_dim
        self.hidden_dim = hidden_dim
        self.kernel_size = kernel_size
        self.padding = kernel_size // 2
        
        self.conv = nn.Conv2d(
            in_channels=self.input_dim + self.hidden_dim,
            out_channels=4 * self.hidden_dim,
            kernel_size=self.kernel_size,
            padding=self.padding,
            bias=True
        )

    def forward(self, input_tensor, cur_state):
        if cur_state is None:
            b, _, h, w = input_tensor.size()
            h_cur = torch.zeros(b, self.hidden_dim, h, w, dtype=input_tensor.dtype, device=input_tensor.device)
            c_cur = torch.zeros(b, self.hidden_dim, h, w, dtype=input_tensor.dtype, device=input_tensor.device)
        else:
            h_cur, c_cur = cur_state

        combined = torch.cat([input_tensor, h_cur], dim=1)
        combined_conv = self.conv(combined)
        
        cc_i, cc_f, cc_o, cc_g = torch.split(combined_conv, self.hidden_dim, dim=1)
        i = torch.sigmoid(cc_i)
        f = torch.sigmoid(cc_f)
        o = torch.sigmoid(cc_o)
        g = torch.tanh(cc_g)

        c_next = f * c_cur + i * g
        h_next = o * torch.tanh(c_next)
        
        return h_next, c_next

class KeypointConvLSTM(nn.Module):
    def __init__(self, num_kp, hidden_dim=16, heatmap_size=32):
        super().__init__()
        self.num_kp = num_kp
        self.heatmap_size = heatmap_size
        self.cell = ConvLSTMCell(input_dim=num_kp, hidden_dim=hidden_dim, kernel_size=3)
        self.out_conv = nn.Conv2d(hidden_dim, num_kp, kernel_size=1)
    
    def kp_to_heatmap(self, kp_tensor):
        """
        Converts (B, num_kp, 2) coords in range [-1, 1] to (B, num_kp, H, W).
        """
        b, num_kp, _ = kp_tensor.shape
        H = W = self.heatmap_size
        
        # map [-1, 1] to [0, H-1]
        kp_pixel = (kp_tensor + 1.0) / 2.0 * (H - 1)
        
        y = torch.arange(0, H, device=kp_tensor.device, dtype=kp_tensor.dtype)
        x = torch.arange(0, W, device=kp_tensor.device, dtype=kp_tensor.dtype)
        grid_y, grid_x = torch.meshgrid(y, x, indexing='ij')
        
        grid_x = grid_x.unsqueeze(0).unsqueeze(0) # (1, 1, H, W)
        grid_y = grid_y.unsqueeze(0).unsqueeze(0) # (1, 1, H, W)
        
        kp_x = kp_pixel[..., 0].unsqueeze(-1).unsqueeze(-1) # (B, num_kp, 1, 1)
        kp_y = kp_pixel[..., 1].unsqueeze(-1).unsqueeze(-1) # (B, num_kp, 1, 1)
        
        sigma = 1.0
        heatmap = torch.exp(-((grid_x - kp_x)**2 + (grid_y - kp_y)**2) / (2 * sigma**2))
        return heatmap

    def heatmap_to_kp(self, heatmap):
        """
        Converts (B, num_kp, H, W) to (B, num_kp, 2) coords in range [-1, 1] using soft-argmax.
        """
        b, num_kp, H, W = heatmap.shape
        
        heatmap_spatial = heatmap.view(b, num_kp, -1)
        prob = torch.softmax(heatmap_spatial, dim=-1).view(b, num_kp, H, W)
        
        y = torch.arange(0, H, device=heatmap.device, dtype=heatmap.dtype)
        x = torch.arange(0, W, device=heatmap.device, dtype=heatmap.dtype)
        
        grid_x = x.unsqueeze(0).unsqueeze(0) # (1, 1, W)
        grid_y = y.unsqueeze(0).unsqueeze(0) # (1, 1, H)
        
        # Expectation
        expected_y = (prob.sum(dim=-1) * grid_y).sum(dim=-1) # (B, num_kp)
        expected_x = (prob.sum(dim=-2) * grid_x).sum(dim=-1) # (B, num_kp)
        
        kp_pixel = torch.stack([expected_x, expected_y], dim=-1) # (B, num_kp, 2)
        
        # map [0, H-1] to [-1, 1]
        kp_tensor = kp_pixel / (H - 1) * 2.0 - 1.0
        return kp_tensor

    def forward(self, kp_tensor, state=None):
        """
        kp_tensor: (1, num_kp, 2)
        state: tuple (h, c) or None
        """
        heatmap = self.kp_to_heatmap(kp_tensor)
        h_next, c_next = self.cell(heatmap, state)
        
        smoothed_heatmap = self.out_conv(h_next)
        smoothed_kp = self.heatmap_to_kp(smoothed_heatmap)
        
        return smoothed_kp, (h_next, c_next)

_conv_lstm_model = None

def get_conv_lstm(num_kp, device):
    """
    Singleton accessor for the ConvLSTM model to avoid re-initializing
    it for every frame.
    """
    global _conv_lstm_model
    if _conv_lstm_model is None:
        _conv_lstm_model = KeypointConvLSTM(num_kp=num_kp).to(device)
    return _conv_lstm_model
