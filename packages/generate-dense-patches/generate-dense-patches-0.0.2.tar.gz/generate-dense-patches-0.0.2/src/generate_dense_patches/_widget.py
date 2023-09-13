"""
This module is an example of a barebones QWidget plugin for napari

It implements the Widget specification.
see: https://napari.org/stable/plugins/guides.html?#widgets

Replace code below according to your needs.
"""
from typing import TYPE_CHECKING

from magicgui import magic_factory
import numpy as np
import scipy.ndimage as ndi
import tifffile as tif
import os
from tqdm import tqdm

if TYPE_CHECKING:
    import napari




@magic_factory
def generate_2d_patches_widget(point_layer: "napari.layers.Points", image_volume: "napari.layers.Image", mask_volume: "napari.layers.Labels", 
                               step_size: int, rotation_theta: int, patch_size: int, rotate_around_point: bool, save_directory: str, rotate_x: bool, rotate_y: bool, rotate_z: bool):
    """
    Generates a 2D patches widget from a given point layer, image volume, and mask volume.

    Args:
        point_layer (napari.layers.Points): The point layer containing the coordinates of the patches. If None, the center of the image will be used as the coordinates.
        image_volume (napari.layers.Image): The image volume from which to extract the patches.
        mask_volume (napari.layers.Labels): The mask volume corresponding to the image volume. If None, only the images will be saved.
        step_size (int): The step size for extracting the patches.
        rotation_theta (int): The rotation angle for each patch.
        save_directory (str): The directory where the patches will be saved.
        patch_size (int): The size of each patch.
        rotate_x (bool): Whether to rotate the patches along the x-axis.
        rotate_y (bool): Whether to rotate the patches along the y-axis.
        rotate_z (bool): Whether to rotate the patches along the z-axis.

    Raises:
        ValueError: If the save directory is not specified, the image volume is not selected, the mask volume is not selected, the rotation theta is invalid, the step size is invalid, or the patch size is invalid.

    Returns:
        None
    """
    
    keep_point_as_centroid = rotate_around_point
    
    #create save directory if it doesn't exist
    if save_directory == '':
        raise ValueError("No save directory specified!")

    if image_volume is None:
        raise ValueError("No image volume selected!")
    
    if step_size > patch_size:
        raise ValueError("Step size must be less than patch size")
            
    if rotation_theta > 180 or rotation_theta <= 0:
        raise ValueError("Rotation theta must be greater than 0 and less than 180")
    if step_size == 0:
        raise ValueError("Step size must be greater than 0")
    if patch_size == 0:
        raise ValueError("Patch size must be greater than 0")
    
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)
        
    if not os.path.exists(os.path.join(save_directory, 'images')):
        os.makedirs(os.path.join(save_directory, 'images'))

        
    if mask_volume is None:
        MASK = False
        print("No mask volume selected. Only saving images")
    else:
        MASK = True
        if not os.path.exists(os.path.join(save_directory, 'masks')):
            os.makedirs(os.path.join(save_directory, 'masks'))

    image_vol = image_volume.data
    im_shape = image_vol.shape
    
    if MASK:
        mask_vol = mask_volume.data
        mask_shape = mask_vol.shape
    else:
        mask_vol = None
        mask_shape = None
        
    if point_layer is None:
        print("No points layer selected! Using center of image as coordinates")
        
        z = im_shape[0]//2
        y = im_shape[1]//2
        x = im_shape[2]//2
        coordinates = (z,y,x)
        keep_point_as_centroid = False
    
    else:
        coordinates = point_layer.data
        z,y,x = coordinates[0]
        z = int(z)
        y = int(y)
        x = int(x)
        coordinates = (z,y,x)


    fname = image_volume.source.path
    fname = os.path.basename(fname)

    #print("coordinates: ", z,y,x, "im_shape: ", im_shape, "mask_shape: ", mask_shape, "fname: ", fname)

    cropped_image_volume, cropped_mask_volume = get_cropped_volume(image_vol, mask_vol, coordinates, patch_size, keep_point_as_centroid)
    
    angles = np.arange(0, 180, rotation_theta)
    
    #create a progress bar
    rotint = 0
    if rotate_x and rotate_y and rotate_z:
        rotint = 3
    elif rotate_x and rotate_y:
        rotint = 2
    elif rotate_x and rotate_z:
        rotint = 2
    elif rotate_y and rotate_z:
        rotint = 2
    elif rotate_x or rotate_y or rotate_z:
        rotint = 1
    else:
        raise ValueError("No rotation axes selected!")
    
    pbar = tqdm(total=len(angles)*rotint)

    
    print("Processing image: ", fname)
    
    
    patch = 1
    
    if rotate_z:
        axes = 'z'
        for angle in angles:
            #print("Processing angle: ", angle)
            rotated_image = custom_rotate_3d(cropped_image_volume, angle, axes)
            
            if MASK:
                rotated_mask = custom_rotate_3d(cropped_mask_volume, angle, axes)
            
            for j in range(0, rotated_image.shape[0], step_size):
                modified_fname = fname + f'_z_{z}' + f'_y_{y}' + f'_x_{x}' + f'_r{axes}_{angle}' + f'_slice_{j}' + f'_patch_{patch:05d}' + '.tif'
                tif.imwrite(os.path.join(save_directory, 'images', modified_fname), rotated_image[j])
                if MASK:
                    tif.imwrite(os.path.join(save_directory, 'masks', modified_fname), rotated_mask[j])
                #print("Saved image: ", modified_fname)
                fname = fname.split('.')[0]
                
                patch += 1
            pbar.update(1)
    
    if rotate_y:
        axes = 'y'
        
        for angle in angles:
            
            if angle > 0:
                
                #print("Processing angle: ", angle)
                rotated_image = custom_rotate_3d(cropped_image_volume, angle, axes)
                if MASK:
                    rotated_mask = custom_rotate_3d(cropped_mask_volume, angle, axes)                
                for j in range(0, rotated_image.shape[0], step_size):
                    modified_fname = fname + f'_z_{z}' + f'_y_{y}' + f'_x_{x}' + f'_r{axes}_{angle}' + f'_slice_{j}' + f'_patch_{patch:05d}' + '.tif'
                    tif.imwrite(os.path.join(save_directory, 'images', modified_fname), rotated_image[j])
                    if MASK:
                        tif.imwrite(os.path.join(save_directory, 'masks', modified_fname), rotated_mask[j])
                    fname = fname.split('.')[0]
                    patch += 1
        
            pbar.update(1)
    
    if rotate_x:        
        axes = 'x'
        
        for angle in angles:
            
            if angle > 0:

                #print("Processing angle: ", angle)
                rotated_image = custom_rotate_3d(cropped_image_volume, angle, axes)
                if MASK:
                    rotated_mask = custom_rotate_3d(cropped_mask_volume, angle, axes)                
                for j in range(0, rotated_image.shape[0], step_size):
                    modified_fname = fname + f'_z_{z}' + f'_y_{y}' + f'_x_{x}' + f'_r{axes}_{angle}' + f'_slice_{j}' + f'_patch_{patch:05d}' + '.tif'
                    tif.imwrite(os.path.join(save_directory, 'images', modified_fname), rotated_image[j])
                    if MASK:
                        tif.imwrite(os.path.join(save_directory, 'masks', modified_fname), rotated_mask[j])
                    fname = fname.split('.')[0]
            
                    patch += 1
            pbar.update(1)
                    
    return
    


def custom_rotate_3d(image_vol, angle, axis):
    """
    Rotates a 3D image volume around a specified axis by a given angle.

    Parameters:
    - image_vol: The 3D image volume to be rotated.
    - angle: The angle (in degrees) by which to rotate the image volume.
    - axis: The axis around which to rotate the image volume. Must be one of: 'x', 'y', or 'z'.

    Returns:
    - The rotated 3D image volume.

    Raises:
    - ValueError: If an invalid axis is specified.
    """

    if axis == 'x':
        return ndi.rotate(image_vol, angle, axes=(1, 2), reshape=False, order=0)
    elif axis == 'y':
        return ndi.rotate(image_vol, angle, axes=(0, 2), reshape=False, order=0)
    elif axis == 'z':
        return ndi.rotate(image_vol, angle, axes=(0, 1), reshape=False, order=0)
    else:
        raise ValueError("Invalid axis specified. Must be one of: 'x', 'y', or 'z'.")

def min_max(coord, patch_size, im_size, keep_point_as_centroid):
    
    if keep_point_as_centroid:
        coordinate_min = coord - patch_size//2
        coordinate_max = coord + patch_size//2
        
        if coordinate_min < 0:
            coordinate_min = 0
            print("Warning: Patch size at coordinates chosen is larger than image dimensions. Image will be padded with zeros and will result in many empty patches generated.")
        if coordinate_max > im_size:
            coordinate_max = im_size
            print("Warning: Patch size at coordinates chosen is larger than image dimensions. Image will be padded with zeros and will result in many empty patches generated.")

            
    else:            
        coordinate_min = coord - patch_size//2
        coordinate_max = coord + patch_size//2
        
        if coordinate_min < 0:
            coordinate_min = 0
            coordinate_max = patch_size
        
        if coordinate_max > im_size:
            coordinate_max = im_size
            coordinate_min = im_size - patch_size
    
    return coordinate_min, coordinate_max


def get_cropped_volume(image_volume, mask_volume, coordinates, patch_size, keep_point_as_centroid=True):
    """
    Gets a cropped image volume from an image volume and a mask volume.
    
    Parameters:
    - image_volume: The input image volume.
    - mask_volume: The mask volume.
    - coordinates: The coordinates of the patch within the image volume.
    - patch_size: The size of the patch.
    
    Returns:
    - cropped_image_volume: The cropped image volume.
    - cropped_mask_volume: The cropped mask volume.
    
    Raises:
    - ValueError: If the patch size is larger than one or more of the image dimensions.
    """
    patch_dims = (patch_size, patch_size, patch_size)
    z,y,x = coordinates
    im_size = image_volume.shape
    
    if mask_volume is None:
        MASK = False
    else:
        MASK = True
    
    #if patch_size is > than image size, throw error
    if patch_size > im_size[0] or patch_size > im_size[1] or patch_size > im_size[2]:
        raise ValueError("Patch size is larger than one or more of image dimensions")
    
    #get min and max coordinates for each dimension
    z_min, z_max = min_max(z, patch_size, im_size[0],keep_point_as_centroid)
    y_min, y_max = min_max(y, patch_size, im_size[1],keep_point_as_centroid)
    x_min, x_max = min_max(x, patch_size, im_size[2],keep_point_as_centroid)
        
    #crop image volume
    cropped_image_volume = image_volume[z_min:z_max, y_min:y_max, x_min:x_max]
    
    if keep_point_as_centroid:
        #pad image volume to fit (patchsize,patchsize,patchsize) dimensions
        if cropped_image_volume.shape[0] < patch_size:
            cropped_image_volume = np.pad(cropped_image_volume, ((0, patch_size - cropped_image_volume.shape[0]), (0, 0), (0, 0)), 'constant', constant_values=0)
        if cropped_image_volume.shape[1] < patch_size:
            cropped_image_volume = np.pad(cropped_image_volume, ((0, 0), (0, patch_size - cropped_image_volume.shape[1]), (0, 0)), 'constant', constant_values=0)
        if cropped_image_volume.shape[2] < patch_size:
            cropped_image_volume = np.pad(cropped_image_volume, ((0, 0), (0, 0), (0, patch_size - cropped_image_volume.shape[2])), 'constant', constant_values=0)
            
        print(cropped_image_volume.shape)
        
        assert cropped_image_volume.shape == patch_dims, "Cropped image volume is not the correct dimensions!"
            
    
    if MASK:
        cropped_mask_volume = mask_volume[z_min:z_max, y_min:y_max, x_min:x_max]

        if keep_point_as_centroid:
            if cropped_mask_volume.shape[0] < patch_size:
                cropped_mask_volume = np.pad(cropped_mask_volume, ((0, patch_size - cropped_mask_volume.shape[0]), (0, 0), (0, 0)), 'constant', constant_values=0)
            if cropped_mask_volume.shape[1] < patch_size:
                cropped_mask_volume = np.pad(cropped_mask_volume, ((0, 0), (0, patch_size - cropped_mask_volume.shape[1]), (0, 0)), 'constant', constant_values=0)
            if cropped_mask_volume.shape[2] < patch_size:
                cropped_mask_volume = np.pad(cropped_mask_volume, ((0, 0), (0, 0), (0, patch_size - cropped_mask_volume.shape[2])), 'constant', constant_values=0)
                        
            assert cropped_mask_volume.shape == patch_dims, "Cropped mask volume is not the correct dimensions!"
            assert cropped_image_volume.shape == cropped_mask_volume.shape, "Cropped image and mask volumes are not the same dimensions!"
    else:
        cropped_mask_volume = None
        
    return cropped_image_volume, cropped_mask_volume