# README
`./lib/segcor.py` generates the file `merges(time).txt` which can be applied to the uncorrected image with `apply_corrections.py` to generate a corrected segmented image.

## SegCor
Located at: `./lib/segcor.py`

Usage: `segcor.py [segmented_image_for_correction] [base_image_for_comparison]`

#### Commands

| Key                | Command                | Notes                                       |
| ------------------ | ---------------------- | ------------------------------------------- |
| up / scroll up     | Zoom In                |                                             |
| down / scroll down | Zoom Out               |                                             |
| left               | Previous Image         |                                             |
| right              | Next Image             |                                             |
| h                  | Move Left              |                                             |
| j                  | Move Up                |                                             |
| k                  | Move Down              |                                             |
| l                  | Move Right             |                                             |
| 1                  | Select Cell 1          | Cell under mouse pointer                    |
| 2                  | Select Cell 2 and merge| Cell under mouse pointer                    |
| b                  | Set cell to background | Change cell under mouse pointer to black    |
| s                  | Save an RGB image      | RGB values denotes cell ID                  |

## SegCor2
Located at: `./lib/segcor2.py`

Usage: `segcor2.py [segmented_image_for_correction] [base_image_for_comparison]`

#### Commands
| Key                | Command                | Notes                                       |
| ------------------ | ---------------------- | ------------------------------------------- |
| y                  | Accept suggested merge |                                             |
| n                  | Reject suggested merge |                                             |

## Apply Corrections
Located at: `./lib/apply_corrections.py` 

Usage: `python apply_corrections.py [image_to_be_corrected] [corrections_file]`

