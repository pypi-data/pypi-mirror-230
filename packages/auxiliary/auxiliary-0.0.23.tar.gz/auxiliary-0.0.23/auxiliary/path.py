from path import Path
import os


def turbopath(input_path: str):
    """
    Normalize and convert a given input path to a normalized Path object.

    Args:
        input_path (str): The input path to be processed.

    Returns:
        Path: A Path object representing the normalized absolute path.
    """
    # Normalize the input path by converting it to an absolute path
    # and then normalizing any directory separators
    normalized_path = os.path.normpath(
        os.path.abspath(
            input_path,
        )
    )
    # Create a Path object from the normalized absolute path
    turbo_path = Path(normalized_path)
    return turbo_path


def name_extractor(input_path: str):
    input_path = turbopath(input_path)
    file_name = input_path.name
    parts = file_name.split(".")
    return parts[0]
