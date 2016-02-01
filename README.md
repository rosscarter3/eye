# Eye

`/lib/eye.py` A simple command line image viewer, written in SDL.

# SegCor
`/lib/segcor.py` generates the file `merges(time).txt` which can be applied to the uncorrected image with `apply_corrections.py` to generate a corrected segmented image.

# Apply Corrections
`/lib/apply_corrections.py`

# Keyboard Commands

| Key  | Command                | Notes                                                     |
| ---- | ---------------------- | --------------------------------------------------------- |
| up   | Zoom In                |                                                           |
| down | Zoom Out               |                                                           |
| left | Previous Image         |                                                           |
| right| Next Image             |                                                           |
| h    | Move Left              |                                                           |
| j    | Move Up                |                                                           |
| k    | Move Down              |                                                           |
| l    | Move Right             |                                                           |
| 1    | Select Cell 1          | (segcor only) Cell under mouse pointer                    |
| 2    | Select Cell 2          | (segcor only) Cell under mouse pointer                    |
| m    | Merge cells 1 and 2    | (segcor only) Changes colour of cell 2 to colour of cell 1|
| b    | Set cell to background | (segcor only) Change cell under mouse pointer to black    |