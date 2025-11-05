import ants, numpy as np

def zscore2d(a):
    a = a.astype(np.float32)
    m, s = a.mean(), a.std() + 1e-6
    return (a - m) / s

def mc_2d_ants_stable(frames_path, ref_img_path, mask=None,
                      transform="Translation",
                      shrink=(6,4,2,1), sigmas=(3,2,1,0), 
                      save_mc_tx_dir = None, save_mc_nii_path = None):
    frames = ants.image_read(frames_path)
    ref_img = ants.image_read(ref_img_path)
    frames_hwt = frames.numpy().astype(np.float32)
    H,W,T = frames_hwt.shape
    # robust reference (median) + light smoothing for stability
    #mask_img = ants.from_numpy(mask.astype(np.uint8)) if mask is not None else None

    aligned = np.empty_like(frames_hwt, dtype=np.float32)
    prev_tx = None

    ref_img = ants.from_numpy(ref_img.numpy().squeeze().astype(np.float32))

    for t in range(T):
        mov_img   = ants.from_numpy(frames_hwt[..., t].astype(np.float32))

        reg = ants.registration(
            fixed=ref_img,
            moving=mov_img,
            type_of_transform=transform,
            #mask=mask_img,
            initial_transform=prev_tx,   # temporal continuity
            shrink_factors=shrink,
            smoothing_sigmas=sigmas,
            write_composite_transform=False,
            verbose=False,
            outprefix=save_mc_tx_dir
        )
        # apply to RAW frame (not the proxy)
        warped = ants.apply_transforms(
            fixed=ref_img, moving=mov_img,
            transformlist=reg["fwdtransforms"],
            interpolator="linear"
        )
        aligned[..., t] = warped.numpy()
        prev_tx = reg["fwdtransforms"]  # warm-start next frame
        if not save_mc_nii_path == None:
            ants.image_write(ants.from_numpy(aligned.astype(np.float32)), save_mc_nii_path)

    return aligned



