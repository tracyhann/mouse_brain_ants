# Data structure

. {root_dir} Data
├── {date} 20251001
    └── {mouse} M2
        ├── M2_470
        |   ├── *_0.tiff # Single-page, (H, W) per timepoint
        |   ├── *_1.tiff
        |   ├── ...
        └── M2_565
            └── frames.tif # Multi-page, (T, H, W) where T = timepoints


# Output data directory structure

. {root_dir} Data
├── {date} 20251001
    └── {mouse} M2
    |   ├── M2_470
    |   |   ├── frame_0.tiff # Single-page, (H, W) per timepoint
    |   |   ├── frame_1.tiff
    |   |   ├── ...
    |   └── M2_565
    |       └── frames.tif # Multi-page, (T, H, W) where T = timepoints
    └── registration_output # Pipeline dumps all intermediate and output files here
        ├── MOVING_REGISTERED # Motion-corrected (within-camera) and co-registered to the reference camera's template (cross-camera)
        |   ├── frame_0.tiff # Single-page, (H, W) per timepoint
        |   ├── frame_1.tiff
        |   ├── ...
        ├── REF_REGISTERED # Motion-corrected to reference camera's template (within-camera)
        |   ├── frame_0.tiff # Single-page, (H, W) per timepoint
        |   ├── frame_1.tiff
        |   ├── ...
        ├── REFERENCE_FRAMES_MC.nii.gz # Motion-corrected reference camera's sampled stack (within-camera)
        ├── REFERENCE_FRAMES_N4.nii.gz # N4-corrected reference camera's sampled stack (within-camera)
        ├── REFERENCE_FRAMES_TPL.nii.gz # Template derived from reference camera's sampled stack (within-camera)
        ├── REFERENCE_FRAMES.nii.gz # Reference camera's sampled stack (within-camera)
        ├── MOVING_FRAMES_MC.nii.gz # Motion-corrected moving camera's sampled stack (within-camera)
        ├── MOVING_FRAMES_N4.nii.gz
        ├── MOVING_FRAMES_REGISTERED.nii.gz # Moving camera's sampled stack registered to reference camera's template (cross-camera), post within-camera steps
        ├── MOVING_FRAMES_TPL.nii.gz
        ├── MOVING_FRAMES.nii.gz
        ├── MOVING_FRAMES.tif # Moving camera's multi-page stack (T, H, W), all frames
        └── registration_tx # Saved registration functions (affine transformations)
            ├── CROSS_CAM_REG_0GenericAffine.mat 
            ├── MOVING_FRAMES_MC_0GenericAffine.mat # Moving stack within-camera motion-correction
            └── REFERENCE_FRAMES_MC_0GenericAffine.mat 


