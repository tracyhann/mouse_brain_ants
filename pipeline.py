import ants
import sys
import os
import imageio.v3 as iio
import numpy as np
import tifffile as tiff
from pathlib import Path
import re

from ants_functions.utils import tiff_folder_to_multipage, load_tif_as_4dnii
from ants_functions.ants_n4 import ants_n4_bias_correction_nii
from ants_functions.ants_mc import mc_2d_ants_stable
from ants_functions.ants_build_tpl import ants_build_template
from ants_functions.ants_registration import ants_registrate, apply_registration




mouse = 'M2'
# Moving camera folder; contains T x frame.tiff (single-page tiff files)
moving_camera_folder_path = 'Data/20251001/M2/M2_470'
# Path to the reference camera (Orca) data stack; frames.tif (multi-page tif file)
reference_frames_path = 'Data/20251001/M2/M2_565/frames.tif'
date = '20251001'
data_root = 'Data'
moving_filename = 'MOVING_FRAMES'
ref_filename = 'REFERENCE_FRAMES'

out_dir = os.path.join(data_root, date, mouse, 'registration_output')
out_tx_dir = os.path.join(out_dir, 'registration_tx')
os.makedirs(out_dir, exist_ok=True)
os.makedirs(out_tx_dir, exist_ok=True)


# STEP 1: Define moving and reference camera. Convert both to 4D Nifti

moving_frames_out_path = os.path.join(out_dir, moving_filename+'.tif')
nii_moving_frames_out_path = os.path.join(out_dir, moving_filename+'.nii.gz')

tiff_folder_to_multipage(moving_camera_folder_path, flipping='lr', out_path=moving_frames_out_path)
mov_stack = load_tif_as_4dnii(moving_frames_out_path, out_path=nii_moving_frames_out_path, MAX_D=300, increment=10)

nii_ref_frames_out_path = os.path.join(out_dir, ref_filename+'.nii.gz')
ref_stack = load_tif_as_4dnii(reference_frames_path, out_path=nii_ref_frames_out_path, MAX_D=300, increment=10)


# STEP 2: N4 correction for both

n4_moving_out_path = os.path.join(out_dir, moving_filename+'_N4.nii.gz')
ants_n4_bias_correction_nii(nii_moving_frames_out_path, n4_moving_out_path)

n4_ref_out_path = os.path.join(out_dir, ref_filename+'_N4.nii.gz')
ants_n4_bias_correction_nii(nii_ref_frames_out_path, n4_ref_out_path)


# STEP 3: Build 1 template for each camera

tpl_moving_out_path = os.path.join(out_dir, moving_filename+'_TPL.nii.gz')
ants_build_template(nii_moving_frames_out_path, tpl_moving_out_path)

tpl_ref_out_path = os.path.join(out_dir, ref_filename+'_TPL.nii.gz')
ants_build_template(nii_ref_frames_out_path, tpl_ref_out_path)

# STEP 4: Motion correction for each camera's time series stack
# This function registers the time series of camera A, TS_A, to the template developed for camera A, TPL_A

mc_moving_out_path = os.path.join(out_dir, moving_filename+'_MC.nii.gz')
mc_moving_tx_dir = os.path.join(out_tx_dir, moving_filename+'_MC_')
mc_mov_arr = mc_2d_ants_stable(n4_moving_out_path, tpl_moving_out_path, transform='Rigid', save_mc_tx_dir=mc_moving_tx_dir, save_mc_nii_path = mc_moving_out_path)

mc_ref_out_path = os.path.join(out_dir, ref_filename+'_MC.nii.gz')
mc_ref_tx_dir = os.path.join(out_tx_dir, ref_filename+'_MC_')
mc_ref_arr = mc_2d_ants_stable(n4_ref_out_path, tpl_ref_out_path, transform='Rigid', save_mc_tx_dir=mc_ref_tx_dir, save_mc_nii_path = mc_ref_out_path)



# STEP 5: Register moving frame template to reference camera frame template, and save the transformation

reg_moving_out_path = os.path.join(out_dir, moving_filename+'_REGISTERED.nii.gz')
reg_tx_out_dir = os.path.join(out_tx_dir, 'CROSS_CAM_REG_')
registered = ants_registrate(mc_moving_out_path, tpl_moving_out_path, tpl_ref_out_path, 
                             method='Rigid', save_register_tx_dir=reg_tx_out_dir, save_reg_path=reg_moving_out_path)


# STEP 6: Apply the transformation to every frame

mov_registered_dir = os.path.join(out_dir, 'MOVING_REGISTERED')
ref_registered_dir = os.path.join(out_dir, 'REF_REGISTERED')

os.makedirs(mov_registered_dir, exist_ok=True)
os.makedirs(ref_registered_dir, exist_ok=True)

mov_tx_dict = {'mc':{'tpl_path':tpl_moving_out_path, 'tx_list':[mc_moving_tx_dir+'0GenericAffine.mat']},
               'reg_to_ref':{'tpl_path':tpl_ref_out_path, 'tx_list':[reg_tx_out_dir+'0GenericAffine.mat']}}

ref_tx_dict = {'mc':{'tpl_path':tpl_ref_out_path, 'tx_list':[mc_ref_tx_dir+'0GenericAffine.mat']}}


apply_registration(moving_frames_out_path, tx_dict=mov_tx_dict, save_dir=mov_registered_dir)
apply_registration(reference_frames_path, tx_dict=ref_tx_dict, save_dir=ref_registered_dir)


# Summary
# Reports
# Plots

