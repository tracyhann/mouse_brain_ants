import ants
import sys
import os
import imageio.v3 as iio
import numpy as np
import nibabel as nib
import matplotlib.pyplot as plt
import tifffile as tiff

def ants_n4_bias_correction_nii(frames_path, out_path):
    img = nib.load(frames_path)
    data = img.get_fdata()
    dx, dy, dz = img.header.get_zooms()[:3]

    # --- 2D ANTs image ---
    img3d = ants.from_numpy(data, spacing=(dx, dy, dz))

    # quick mask (ignore obvious background); tweak threshold as needed
    # Using intensity percentile for robustness:
    thr = np.percentile(data[data>0], 10) if np.any(data>0) else np.percentile(data, 10)
    mask3d = ants.threshold_image(img3d, thr, img3d.max())  # binary mask

    n4 = ants.n4_bias_field_correction(img3d, mask=mask3d, return_bias_field = False, verbose = False)
    n4arr = ants.from_numpy(n4.numpy().astype(np.float32))

    ants.image_write(n4arr, out_path)


def plot_image_means(antsimg, slice_to_show=20):
    plt.figure(figsize=(12,6))
    plt.subplot(1,3,1)
    imgmeans = antsimg.mean(axis=(0,1,2))
    plt.plot(imgmeans)
    plt.ylabel('total image mean')
    plt.subplot(1,3,2)
    plt.imshow(
        antsimg[:,:,slice_to_show, np.argmin(imgmeans)],
        cmap='gray')
    plt.title('signal from lowest mean timepoint')
    plt.subplot(1,3,3)
    plt.imshow(
        antsimg[:,:,slice_to_show, np.argmax(imgmeans)],
        cmap='gray')
    plt.title('signal from highest mean timepoint')



