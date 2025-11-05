import ants, numpy as np

def ants_build_template(frames_path, out_path):
    # ---------- load & coerce to (X,Y,1,T) ----------
    img = ants.image_read(frames_path)
    arr = img.numpy()
    if arr.ndim == 3:           # (X,Y,T) -> (X,Y,1,T)
        arr = arr[..., np.newaxis, :]
    assert arr.ndim == 4 and arr.shape[2] == 1, f"Expected single-slice time series (Z=1). Got {arr.shape}"
    arr.shape
    dx, dy = img.spacing[:2]

    # ---------- make a list of 2D ANTsImages (one per frame) ----------
    frames_n4_list = [ants.from_numpy(arr[..., 0, t]) for t in range(arr.shape[-1])]

    # ---------- build a rigid template from the N4-corrected frames ----------
    # Prefer Rigid for motion-like alignment (no scaling/shear).
    from ants.registration.build_template import build_template
    template = build_template(image_list=frames_n4_list, type_of_transform="Rigid", write_composite_transform=False, output_dir=None) 

    template = ants.from_numpy(template.numpy()[..., None])

    ants.image_write(template, out_path)   # writes a NIfTI with correct header/spacing

