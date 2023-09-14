from tifffile import imread, imwrite


def read_tiff(tiff_path: str):
    data = imread(tiff_path)
    return data


def write_tiff(
    numpy_array,
    output_tiff_path: str,
    transpose: bool = True,
):
    if transpose == True:
        numpy_array = numpy_array.T

    imwrite(output_tiff_path, numpy_array)
