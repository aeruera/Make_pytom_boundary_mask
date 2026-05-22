#!/usr/bin/env python3

import argparse
from pathlib import Path

import mrcfile
import numpy as np


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Create a binary tomogram mask for PyTom extraction. "
            "The interior is 1 and the boundary margin is 0, preventing "
            "candidate extraction near tomogram edges."
        )
    )

    parser.add_argument(
        "tomogram",
        help="Input tomogram in MRC format."
    )

    parser.add_argument(
        "-o", "--output",
        default=None,
        help="Output mask filename. Default: <tomogram_stem>_boundary_mask.mrc"
    )

    parser.add_argument(
        "--margin-px",
        type=int,
        default=None,
        help="Boundary margin to exclude, in pixels."
    )

    parser.add_argument(
        "--margin-angstrom",
        type=float,
        default=None,
        help="Boundary margin to exclude, in Angstrom. Pixel size is read from the tomogram header."
    )

    args = parser.parse_args()

    if (args.margin_px is None) == (args.margin_angstrom is None):
        parser.error("Provide exactly one of --margin-px or --margin-angstrom.")

    tomo_path = Path(args.tomogram)

    if args.output is None:
        output_path = tomo_path.with_name(f"{tomo_path.stem}_boundary_mask.mrc")
    else:
        output_path = Path(args.output)

    with mrcfile.open(tomo_path, permissive=True) as mrc:
        shape = mrc.data.shape  # MRC array order: z, y, x
        voxel_size = float(mrc.voxel_size.x)

    if args.margin_angstrom is not None:
        if voxel_size <= 0:
            raise ValueError(
                "The tomogram header does not contain a valid voxel size. "
                "Use --margin-px instead."
            )
        margin = int(np.ceil(args.margin_angstrom / voxel_size))
    else:
        margin = args.margin_px

    if margin <= 0:
        raise ValueError("Margin must be greater than zero.")

    if any(2 * margin >= dim for dim in shape):
        raise ValueError(
            f"Margin of {margin} px is too large for tomogram dimensions {shape}."
        )

    mask = np.ones(shape, dtype=np.float32)

    # Exclude boundaries in z, y, and x.
    mask[:margin, :, :] = 0
    mask[-margin:, :, :] = 0

    mask[:, :margin, :] = 0
    mask[:, -margin:, :] = 0

    mask[:, :, :margin] = 0
    mask[:, :, -margin:] = 0

    with mrcfile.new(output_path, overwrite=True) as out:
        out.set_data(mask)
        out.voxel_size = voxel_size
        out.update_header_stats()

    print(f"Tomogram dimensions (z, y, x): {shape}")
    print(f"Voxel size: {voxel_size:.3f} Å/px")
    print(f"Excluded boundary margin: {margin} px ({margin * voxel_size:.1f} Å)")
    print(f"Wrote mask: {output_path}")


if __name__ == "__main__":
    main()
