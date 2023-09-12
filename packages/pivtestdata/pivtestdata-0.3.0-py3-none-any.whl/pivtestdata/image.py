import pathlib
from dataclasses import dataclass
from typing import Tuple


def load_img(img_filepath: pathlib.Path):
    """
    loads b16 or other file format
    """
    img_filepath = pathlib.Path(img_filepath)
    if img_filepath.suffix in ('b16', '.b16'):
        try:
            import pco
        except ImportError:
            raise ImportError('Package "pco_tools" missing. you need to install it to load b16 files')
        im_ = pco.load(str(img_filepath))
    else:
        try:
            from cv2 import imread as cv2_imread
        except ImportError:
            raise ImportError('Package "cv2" missing. you need to install it to load b16 files')
        im_ = cv2_imread(str(img_filepath), -1)
    return im_


@dataclass
class PIVImageMetaData:
    """PIV image meta data"""

    # camera characteristics:
    pixel_size_mu: Tuple[float, float] = None  # e.g. (6.7, 6.7); units is micrometer
    sensor_size_mm: Tuple[float, float] = None  #
    dynamic_range_bits: int = None  # e.g. 12; units is bits
    quantum_efficiency: float = None  # e.g. 0.4 for 40%
    full_well_capacity: int = None  # e.g. 25000 e
    readout_noise: int = None  # e.g. 7 e

    field_of_view_m: Tuple[float, float] = None  # e.g. (0.001, 0.001); units is meter

    lens_focal_length_mm: float = None  # e.g. 50; units is millimeter
    lens_f_number: float = None  # e.g. 1.4
