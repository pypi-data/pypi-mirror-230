import pathlib
import re
import shutil
import warnings
import zipfile
from typing import Tuple

import appdirs
import requests
from tqdm import tqdm

from .image import PIVImageMetaData

user_dir = pathlib.Path(appdirs.user_data_dir('pivtestdata'))

# IMG_EXTENSIONS = ('.tif', '.tiff', '.b16')
IMG_FILE_PATTERN = r'^(?!.*mask).*\.(tif|tiff|b16|bmp)$'
MASK_FILE_PATTERN = r'^(.*mask).*\.(tif|tiff|b16|bmp)$'


class WebZip:
    """Web resource as zip file"""

    def __init__(self, url: str, name=None,
                 img_file_pattern: str = IMG_FILE_PATTERN,
                 mask_file_pattern: str = MASK_FILE_PATTERN):
        self.url = url
        self.img_file_pattern = img_file_pattern
        self.mask_file_pattern = mask_file_pattern

        if name is None:
            self.name = pathlib.Path(self.url).stem
        else:
            self.name = name

        self._all_files = None
        self._meta = PIVImageMetaData()

    def __repr__(self):
        return f'{self.__class__.__name__}(name={self.name}, nimg={self.n_images}, url={self.url})'

    @property
    def file_size(self):
        """Return file size in bytes"""
        r = requests.get(self.url, stream=True)
        return int(r.headers.get("content-length", 0))

    @property
    def image_dir(self) -> pathlib.Path:
        """Return target folder"""
        return user_dir / self.name

    def exists(self):
        """Check if the target folder exists"""
        return self.image_dir.exists()

    @property
    def n_images(self):
        """Return number of images"""
        return len(self.image_filenames)

    def download(self, force: bool = False):
        """download to user dir or specified target folder.
        If force is True, download even if the target folder exists.
        """

        if self.exists() and force:
            shutil.rmtree(self.image_dir)

        if self.exists() and not force and self.n_images > 1:
            return self.image_dir

        if not self.exists():
            self.image_dir.mkdir(parents=True)

        zip_filename = self.image_dir / 'file.zip'
        try:
            r = requests.get(self.url, stream=True)
            total_size = int(r.headers.get("content-length", 0))
            with open(zip_filename, "wb") as file, tqdm(total=total_size, unit='B', unit_scale=True,
                                                        desc=self.name) as progress_bar:
                for data in r.iter_content(chunk_size=1024):
                    # Write the data to the file
                    file.write(data)
                    progress_bar.update(len(data))

            with zipfile.ZipFile(zip_filename) as z:
                z.extractall(self.image_dir)
            zip_filename.unlink()
        except Exception as e:
            print(f'could not download {self.name} from {self.url}: {e}')

        return self.image_dir

    @property
    def all_files(self):
        """return all files in the dataset"""
        if not self.exists():
            raise ValueError('download the dataset first')
        return sorted(pathlib.Path(self.image_dir).glob('*.*'))

    @property
    def image_filenames(self):
        """return all image filenames in the dataset"""
        return sorted([f for f in self.all_files if re.match(self.img_file_pattern, f.name, re.IGNORECASE)])

    @property
    def mask_filename(self):
        """return the mask filename in the dataset"""
        return sorted([f for f in self.all_files if re.match(self.mask_file_pattern, f.name, re.IGNORECASE)])

    mask_filenames = mask_filename  # alias

    @property
    def readme(self) -> str:
        """Return the content of the readme file as string"""
        if self.image_dir is None:
            raise ValueError('download the dataset first')
        # guess the readme file: use regex for this on file names:
        all_files = pathlib.Path(self.image_dir).glob('*.*')
        readme_file_candidates = [f for f in all_files if re.match(r'readme', f.name, re.IGNORECASE)]
        readme = readme_file_candidates[0]
        if len(readme_file_candidates) > 1:
            warnings.warn(f'found multiple readme files. Will use {readme}. Others are: {readme_file_candidates}',
                          UserWarning)
        return readme.read_text()

    @property
    def meta(self) -> PIVImageMetaData:
        return self._meta

    @property
    def A(self):
        """Return image A interface class"""
        return self.image_filenames[::2]

    @property
    def B(self):
        """Return image B interface class"""
        return self.image_filenames[1::2]

    @property
    def AB(self) -> Tuple[pathlib.Path, pathlib.Path]:
        """Return image AB interface class"""
        return self.image_filenames[::2], self.image_filenames[1::2]
