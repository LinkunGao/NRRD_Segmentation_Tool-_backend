import numpy as np
import json
import SimpleITK as sitk
import os


def convert_to_nii(folder):

    print("start converting...")
    print(folder)
    mask_path = os.path.join(folder, "mask.json")

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

        nii_path = os.path.join(folder, "output.nii")
        # Save the image as a NIfTI file
        sitk.WriteImage(nii, nii_path)
        print("convert successfully!")

    except Exception as e:
        print("An error occurred: ", e)
        import traceback
        print(traceback.format_exc())
