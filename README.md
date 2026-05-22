# Make_pytom_boundary_mask
For making a mask that can be used to exclude pytom particle coordinates during extraction which are too close to the edge of the tomogram.


To use:

`python3 -m venv pytom_mask_env
source pytom_mask_env/bin/activate
pip install numpy mrcfile`


And then run `python3 make_pytom_boundary_mask.py $YOUR_$TOMOGRAM.mrc --margin-angstrom 500` 

I recommend setting --margin-angstrom to at least the diameter of your particle, if not a little bit bigger.
