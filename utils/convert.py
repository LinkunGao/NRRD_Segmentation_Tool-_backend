import numpy as np
import json
import SimpleITK as sitk
import os
from .tools import get_file_path

def convert_to_nii_sigel_channel(patient_id):
    nii_image = convert_json_data(patient_id)
    nii_path = get_file_path(patient_id, "nii")
    # Save the image as a NIfTI file
    sitk.WriteImage(nii_image, nii_path)
    print("convert successfully!")


def convert_to_nrrd_sigel_channel(folder):
    nrrd_image = convert_json_data(folder)
    nrrd_path = os.path.join(folder, "mask.nrrd")
    # Save the image as a NRRD file
    sitk.WriteImage(nrrd_image, nrrd_path)
    print("convert successfully!")

def convert_json_data(patient_id):

    print("start converting...")

    nrrd_path = get_file_path(patient_id, "nrrd")
    mask_path = get_file_path(patient_id, "json")

    nrrd_image = sitk.ReadImage(nrrd_path)
    headerKeys = nrrd_image.GetMetaDataKeys()

    with open(mask_path) as user_file:
        file_contents = user_file.read()
        parsed_json = json.loads(file_contents)
    images = []
    width = parsed_json[0]["width"]
    height = parsed_json[0]["height"]
    depth = len(parsed_json)
    for i in range(len(parsed_json)):
        data = parsed_json[i]["data"]
        if len(data)==0:
            data = [0]*width*height*4
        images.append(data)

    try:
        pixels = np.array(images).reshape((depth, height, width, 4))

        # Take the average of the RGB values and use the Alpha value as the transparency
        merged_pixels = np.mean(pixels[:, :, :, :3], axis=3)

        new_image = sitk.GetImageFromArray(merged_pixels)

        spacing = parsed_json[0]["voxelSpacing"]
        origin = parsed_json[0]["spaceOrigin"]
        new_image.SetSpacing(spacing)
        new_image.SetOrigin(origin)

        for key in headerKeys:
            new_image.SetMetaData(key, nrrd_image.GetMetaData(key))
        return new_image

    except Exception as e:
        print("An error occurred: ", e)
        import traceback
        print(traceback.format_exc())

def convert_to_nii_full_channels(patient_id):

    print("start converting...")
    mask_path = get_file_path(patient_id, "json")

    with open(mask_path) as user_file:
        file_contents = user_file.read()
        parsed_json = json.loads(file_contents)
    images = []
    width = parsed_json[0]["width"]
    height = parsed_json[0]["height"]
    for i in range(len(parsed_json)):
        data = parsed_json[i]["data"]
        if len(data)==0:
            data = [0]*width*height*4
        images.append(data)

    spacing = parsed_json[0]["voxelSpacing"]
    origin = parsed_json[0]["spaceOrigin"]
    try:
        rgba_pixels = np.array(images, dtype=np.uint8)  # Convert pixel data to a numpy array of uint8 type
        rgba_pixels = rgba_pixels.reshape((-1, 4))  # Reshape the pixel data to have 4 columns

        rgb_pixels = rgba_pixels[:, :-1]

        rgb_image = np.array(rgb_pixels, dtype=np.float32).reshape((len(parsed_json), height, width, 3))

        # Convert the RGB image to a grayscale image
        red_channel = sitk.VectorIndexSelectionCast(sitk.GetImageFromArray(rgb_image), 0)
        green_channel = sitk.VectorIndexSelectionCast(sitk.GetImageFromArray(rgb_image), 1)
        blue_channel = sitk.VectorIndexSelectionCast(sitk.GetImageFromArray(rgb_image), 2)
        nii = sitk.Compose(red_channel, green_channel, blue_channel)

        nii.SetSpacing(spacing)
        nii.SetOrigin(origin)

        nii_path = get_file_path(patient_id, "nii")
        # Save the image as a NIfTI file
        sitk.WriteImage(nii, nii_path)
        print("convert successfully!")

    except Exception as e:
        print("An error occurred: ", e)
        import traceback
        print(traceback.format_exc())
