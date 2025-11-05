import ants
import sys
import os
import imageio.v3 as iio
import numpy as np
import tifffile as tiff
from pathlib import Path
import re


def tiff_folder_to_multipage(
    folder: str,
    out_path: str = "stack.tif",
    pattern: str = "*.tif*",
    dtype=np.uint16,
    flipping = 'lr',
    xy_spacing_mm: tuple[float, float] | None = None,  # (sx, sy) mm/px
    z_spacing_mm: float | None = None,                 # metadata only
    compression: str | None = "zlib",                  # None, "zlib", "lzma", "jpegxl" (if supported), etc.
    bigtiff: bool | None = None,                       # auto if None; set True for >4GB
    imagej: bool = True,                               # ImageJ-compatible stack
):
    """
    Stack 2D TIFFs (Y,X) into a multi-page TIFF stack (P,Y,X).
    Returns (out_path, (P, Y, X)).
    """
    files = [filename for filename in os.listdir(folder) if '.tiff' in filename]
    if not files:
        raise FileNotFoundError(f"No TIFFs matching '{pattern}' in {folder}")
    
    def flip_frame(frame, flip = flipping):
        if flip == 'ud':
            return np.flipud(frame)
        if flip == 'lr':
            return np.fliplr(frame)
        if flip == 'udlr':
            return np.fliplr(np.flipud(frame))
        return frame

    # Read first slice for shape & dtype
    first = tiff.imread(str(folder+'/'+files[0]))
    first = flip_frame(first, flip=flipping)
    if first.ndim != 2:
        raise ValueError(f"Expected 2D TIFFs; got shape {first.shape} for {files[0].name}")
    H, W = map(int, first.shape)

    # Pre-allocate stack
    P = len(files)
    stack = np.empty((P, H, W), dtype=dtype)

    for k, p in enumerate(files):
        arr = tiff.imread(str(folder+'/'+p))
        arr = flip_frame(arr, flip=flipping)
        if arr.shape != (H, W):
            raise ValueError(f"Inconsistent shape: {p.name} has {arr.shape}, expected {(H, W)}")
        stack[k] = arr.astype(dtype, copy=False)

    # Resolution tags (optional): store pixels-per-centimeter if spacings provided
    # TIFF stores resolution as pixels per resolution unit (INCH or CENTIMETER).
    # We’ll use CENTIMETER so px/cm = 10 / (mm/px).
    resolution = None
    resolutionunit = None
    if xy_spacing_mm is not None:
        sx_mm, sy_mm = map(float, xy_spacing_mm)
        if sx_mm > 0 and sy_mm > 0:
            x_ppcm = 10.0 / sx_mm
            y_ppcm = 10.0 / sy_mm
            resolution = (x_ppcm, y_ppcm)
            resolutionunit = "CENTIMETER"

    # ImageJ metadata for z-spacing (ImageJ reads this as voxel depth)
    metadata = {}
    if imagej and (z_spacing_mm is not None):
        metadata["spacing"] = float(z_spacing_mm)
        metadata["unit"] = "mm"

    # Decide BigTIFF automatically if not specified
    if bigtiff is None:
        est_bytes = stack.nbytes
        bigtiff = est_bytes >= (4 * 1024**3)  # ~4GB

    os.makedirs('/'.join(out_path.split('/')[:-1]), exist_ok=True)
    tiff.imwrite(
        out_path,
        stack,
        imagej=imagej,
        compression=compression,
        bigtiff=bigtiff,
        resolution=resolution,
        resolutionunit=resolutionunit,
        metadata=metadata or None,
    )
    return out_path, stack.shape



def load_tif_as_4dnii(path, out_path, MAX_D = 300, increment = 10):
    arr = iio.imread(path)  # could be [H,W], [H,W,C], or [P,H,W]
    # If color, convert to grayscale
    if arr.ndim == 3 and arr.shape[-1] in (3,4):
        arr = arr[..., :3].mean(axis=-1)
    # If multi-page, make 4D (H,W,1,P); subsample to reduce frames
    if arr.ndim == 3 and arr.shape[0] > 1 and arr.shape[-1] not in (3,4):
        arr = arr.transpose(1,2,0)  # (H,W,P)
        arr = arr[..., np.newaxis, :] # (H,W,1,P)
        D = min(MAX_D, arr.shape[-1])
        arr = np.stack([arr[...,i] for i in range(0, D*increment, increment)], axis=-1)  # subsample every N (default = 10) frames
    else: print('Please check the input image shape. Is it a multi-page tif?')
    frames = ants.from_numpy(arr.squeeze().astype(np.float32))
    ants.image_write(frames, out_path)
    # returns the 4D ants TS frames [H, W, 1, T]
    return ants.from_numpy(arr.astype(np.float32))


