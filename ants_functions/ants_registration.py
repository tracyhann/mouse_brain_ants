#ANTS registration

import ants
import sys
import os
import imageio.v3 as iio
import numpy as np
import nibabel as nib
import tifffile as tiff

def ants_registrate(moving_path, tpl_moving_path, tpl_ref_path, method = 'Rigid', save_register_tx_dir = None, save_reg_path = None):
    # flipping = 'ud' = up-down; 'lr' = 'left-right'; None or else = no flipping
    moving = ants.image_read(moving_path)
    mtpl = ants.image_read(tpl_moving_path)
    rtpl = ants.image_read(tpl_ref_path)
    
    reg = ants.registration(fixed=rtpl, moving=mtpl, type_of_transform=method, outprefix=save_register_tx_dir) # or Rigid, SyN

    _, _, sz = moving.numpy().shape
    out_np = np.zeros((rtpl.shape[0], rtpl.shape[1], sz), dtype=np.float32)
    for z in range(sz):
        sl_arr = np.expand_dims(moving.numpy()[:, :, z], axis=2)
        sl = ants.from_numpy(sl_arr.astype(np.float32))
        warped2d = ants.apply_transforms(
                fixed=rtpl,
                moving=sl,
                transformlist=reg['fwdtransforms'],
                interpolator='linear',
            )
        warped2d = ants.from_numpy(
            warped2d.numpy(),
            spacing=rtpl.spacing,
        )
        out_np[:, :, z] = warped2d.numpy().squeeze()
    out_img = ants.from_numpy(out_np)
    if save_reg_path:
        ants.image_write(out_img, save_reg_path)
    
    return out_img




def apply_registration(tif_path, tx_dict, method='Rigid', save_dir=None):
    frames = tiff.imread(tif_path)
    i = 0
    for arr in frames:
        img = ants.from_numpy(np.expand_dims(arr, axis=2).astype(np.float32))
        for key, tx in tx_dict.items():
            if key == 'mc':
                tpl = ants.from_numpy(ants.image_read(tx_dict[key]['tpl_path']).numpy().squeeze())
                img = ants.from_numpy(img.numpy().squeeze())
                img = ants.apply_transforms(fixed=tpl, moving=img, transformlist=tx_dict[key]['tx_list'], interpolator="linear")
                img = ants.from_numpy(np.expand_dims(img.numpy(), axis=2).astype(np.float32))
            else:
                tpl = ants.image_read(tx_dict[key]['tpl_path'])
                img = ants.apply_transforms(fixed=tpl, moving=img, transformlist=tx_dict[key]['tx_list'], interpolator="linear")
        img = img.numpy().squeeze().astype(np.uint16)
        tiff.imwrite(os.path.join(save_dir, f'frame_{i}.tiff'), img)
        i += 1

