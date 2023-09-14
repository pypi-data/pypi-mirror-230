from tifffile import imread, imwrite
import os

from auxiliary.path import turbopath


def read_tiff(tiff_path: str):
    data = imread(tiff_path)
    return data


def write_tiff(
    numpy_array,
    output_tiff_path: str,
    transpose: bool = True,
    create_parent_directory: bool = False,
):
    if transpose == True:
        numpy_array = numpy_array.T

    if create_parent_directory == True:
        output_tiff_path = turbopath(output_tiff_path)
        parent_dir = output_tiff_path.parent
        os.makedirs(parent_dir, exist_ok=True)
    imwrite(output_tiff_path, numpy_array)
