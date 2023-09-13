import nibabel as nib
import numpy as np


def write_nifti(
    input_array: np.ndarray,
    output_nifti_path: str,
    reference_nifti_path: str = None,
):
    """
    Write a NIfTI file from a NumPy array.

    Parameters:
    input_array (np.ndarray): The NumPy array containing the data to be written.
    output_nifti_path (str): The path where the output NIfTI file will be saved.
    reference_nifti_path (str, optional): Path to a reference NIfTI file for header and affine information.

    Returns:
    None
    """
    if reference_nifti_path:
        reference = nib.load(reference_nifti_path)
        the_nifti = nib.Nifti1Image(
            dataobj=input_array,
            affine=reference.affine,
            header=reference.header,
        )
    else:
        the_nifti = nib.Nifti1Image(dataobj=input_array, affine=np.eye(4))

    nib.save(the_nifti, output_nifti_path)


def read_nifti(
    input_nifti_path: str,
    maintain_dtype: bool = True,
) -> np.ndarray:
    """
    Read a NIfTI file and return its data as a NumPy array.

    Args:
        input_nifti_path (str): Path to the input NIfTI file.
        maintain_dtype (bool, optional): If True, maintain the data type of the NIfTI data.
                                         If False, allow data type conversion to float. Default is True.

    Returns:
        numpy.ndarray: NIfTI data as a NumPy array.
    """
    the_nifti = nib.load(input_nifti_path)
    nifti_data = the_nifti.get_fdata()

    if maintain_dtype:
        # Get the data type from the NIfTI header
        data_type = the_nifti.header.get_data_dtype()
        # Convert data type if necessary
        nifti_data = nifti_data.astype(data_type, copy=False)

    return nifti_data
