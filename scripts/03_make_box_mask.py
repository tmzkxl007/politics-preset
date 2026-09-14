# -*- coding: utf-8 -*-
"""
Step 3 (run once, reusable across all videos): generate the rounded-corner
alpha mask PNG used to composite every screenshot/meme into the rounded video box.

Geometry here MUST match BOX_W/BOX_H used in 05_render.py.
"""
from PIL import Image, ImageDraw
import os

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W, H, R = 1004, 1143, 80  # box width, box height, corner radius (px) -- confirmed spec, don't change per-story

mask = Image.new("L", (W, H), 0)
d = ImageDraw.Draw(mask)
d.rounded_rectangle([0, 0, W - 1, H - 1], radius=R, fill=255)

out_path = os.path.join(BASE, "assets", "box_mask.png")
mask.save(out_path)
print("saved mask", mask.size, "->", out_path)
