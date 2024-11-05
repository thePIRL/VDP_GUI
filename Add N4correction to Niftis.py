'''
This code can be used to perform N4 bias correction and append to Nifti array
You might have to modify depending on how you store your HPG vent images and
corresponding binary mask arrays. In my case, the vent and masks were originally
stored in 4D Nifti Arrays [rows, columns, slices, dataset] where dataset = 0 is
the raw HPG ventilation images and dataset = 1 is the binary mask array. So the
code as it's written here simply open that Nifti file, calculates N4 corrected
HPG images and appends those to the original Niftis dataset dimension.
1/20/2024, RP Thomen
'''
import nibabel as nib
import numpy as np
import SimpleITK as sitk # ---------------- for N4 Bias Correection
import time
import os

def load_Nifti_file(path):
    activeNifti  = nib.load(path)
    nii_data = activeNifti.get_fdata()
    nii_aff  = activeNifti.affine
    nii_hdr  = activeNifti.header
    return(nii_data,nii_aff,nii_hdr)

def N4_bias_correction(HPvent, mask):
    start_time = time.time()
    print('Performing Bias Correction...')

    # Convert NumPy arrays to SimpleITK images
    image = sitk.GetImageFromArray(HPvent.astype(np.float32))
    mask = sitk.GetImageFromArray(mask.astype(np.float32))

    #Cast to correct format for SimpleITK
    image = sitk.Cast(image, sitk.sitkFloat32)
    mask = sitk.Cast(mask, sitk.sitkUInt8)

    #Run Bias Correction
    corrector = sitk.N4BiasFieldCorrectionImageFilter()
    corrected_image = corrector.Execute(image, mask)
    corrected_HPvent = sitk.GetArrayFromImage(corrected_image)
    print(f'Bias Correction Completed in {np.round(time.time()-start_time,2)} seconds')
    return corrected_HPvent


if __name__ == "__main__":
    nifti_dir = 'C:/PIRL/GUI/Niftis/'
    output_dir = 'C:/PIRL/GUI/N4Niftis/'
    fileList = os.listdir(nifti_dir)
    for k in range(len(fileList)):
        print(f'Opening case {k}/{len(fileList)}: {fileList[k]}')
        nii_data, _, _ = load_Nifti_file(f"{nifti_dir}{fileList[k]}")
        nifti_array = np.zeros((nii_data.shape[0],nii_data.shape[1],nii_data.shape[2],3))
        nifti_array[:,:,:,:2] = nii_data[:,:,:,:2]
        nifti_array[:,:,:,2] = N4_bias_correction(nii_data[:,:,:,0],nii_data[:,:,:,1])
        niImage = nib.Nifti1Image(nifti_array, affine=np.eye(4))
        nib.save(niImage,os.path.join(output_dir,fileList[k]))

