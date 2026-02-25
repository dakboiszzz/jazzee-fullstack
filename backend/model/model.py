

import torch
import torch.nn as nn
# We just need the generator model arch because Discriminator is only used in the training phase

# -----BUILDING THE GENERATOR------

# This is different from the pix2pix model
# 1. Filter 3x3, stride 2, padding_mode = 'reflect'
# 2. InstanceNorm, not BatchNorm
# 3. Use ReLU 
class GBlock(nn.Module):
    def __init__(self,in_channels, out_channels, down = True, stride = 2, use_act = True):
        super().__init__()
        layers = []
        if down:
            layers.append(nn.Conv2d(in_channels, out_channels, 3, stride, 1, bias = False,  padding_mode='reflect'))
        else: 
            layers.append(nn.ConvTranspose2d(in_channels, out_channels, 3, stride, 1, bias = False, output_padding= 1))
        layers.extend([
            nn.InstanceNorm2d(out_channels),
            nn.ReLU(inplace = True) if use_act else nn.Identity(),
        ])
        self.block = nn.Sequential(*layers)
    def forward(self,x):
        return self.block(x)
class ResBlock(nn.Module):
    def __init__(self,in_channels):
        super().__init__()
        self.model = nn.Sequential(
            # Kinda subtle here, like I need to use a convBlock rather than a conv layer
            # And the second layer I need to remove the activation 
            GBlock(in_channels,in_channels, stride = 1),
            GBlock(in_channels,in_channels, stride = 1, use_act = False),
        )
    def forward(self,x):
        return x + self.model(x)
        
class Generator(nn.Module):
    def __init__(self, in_feat = 1, feat = 64,num_res = 9):
        super().__init__()
        # c7s1-64,d128,d256,R256,R256,R256,R256,R256,R256,u128,u64,c7s1-3
        # c7s1-k: Conv2d 7x7 k filter, stride 1 + InstanceNorm + ReLU
        # dk: Conv2d 3x3 k filter, stride 2 + InstanceNorm, ReLU
        # Rk: ResBlock
        # uk: ConvTranspose2d 3x3 k filter, stride 2 + InstanceNorm + ReLU
        self.initial_layer = nn.Sequential(
            nn.Conv2d(in_feat,feat, 7, 1, 3, padding_mode = 'reflect', bias = False), # Need to change the padding to 3 to preserve the original img
            nn.InstanceNorm2d(feat),
            nn.ReLU(inplace = True),
        )
        self.down = nn.Sequential(
            GBlock(feat, feat * 2),
            GBlock(feat * 2, feat * 4),
        )
        self.res = nn.Sequential(
            *[ResBlock(feat * 4) for _ in range(num_res)]
        )
        self.up = nn.Sequential(
            GBlock(feat * 4, feat * 2, down = False),
            GBlock(feat * 2, feat, down = False),
        )
        self.last_layer = nn.Sequential(
            nn.Conv2d(feat,1, 7, 1, 3, padding_mode = 'reflect', bias = False),
            nn.Tanh(),
        )
    def forward(self,x):
        out = self.initial_layer(x)
        out = self.down(out)
        out = self.res(out)
        out = self.up(out)
        return self.last_layer(out)
        
        
