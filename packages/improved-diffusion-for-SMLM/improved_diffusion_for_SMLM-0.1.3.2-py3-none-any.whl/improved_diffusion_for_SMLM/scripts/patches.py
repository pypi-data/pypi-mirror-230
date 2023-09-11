import torch
import numpy as np
from PIL import Image
from nd2reader import ND2Reader
from pathlib import Path, PosixPath
import torchvision.transforms as transforms
import torchvision


def crop_to_patches(image, top, left, patch_height, patch_width, overlap):
    # overlap in precentage, for exmaple: 0.8 / 0.5
    overlap_range_width = int(patch_width * overlap)
    overlap_range_height = int(patch_height * overlap)
    patches_list = []
    cur_left = left

    range_x = 1 + (image.shape[1] - patch_height - (((image.shape[1] - patch_height)) % (patch_height - overlap_range_height))) // (patch_height-overlap_range_height)
    range_y = 1 + (image.shape[2] - patch_width - (((image.shape[2] - patch_width)) % (patch_width - overlap_range_width))) // (patch_width-overlap_range_width)

    for i in range(int(range_x)):
        for j in range(int(range_y)):
            if cur_left + overlap_range_width <= image.shape[2] and top + overlap_range_height <= image.shape[1]:
                patches_list.append(torchvision.transforms.functional.crop(image, top, cur_left, patch_height, patch_width))
                cur_left += (patch_width - overlap_range_width)
        top += (patch_height - overlap_range_height)
        cur_left = left

    return patches_list

def augmentation(img,n_rotation):
    '''
    the function creates augmentation of the same image: flipped L-R, and rotations.
    for each orientation (original + flipped) the function rotate by n_rotation.
    for example: if n_rotation = 6, 6 image will be created: 0 deg, 60 deg, 120 deg, 180 deg, 240 deg, 300 deg.
    :param img: pytorch tensor
    :param n_rotation: int
    :return: img_augmentations: pytorch tensor of tensors, each tensor is a new image
    '''
    flipped = img.fliplr()
    orientations = [img, flipped]
    img_augmentations = torch.zeros((n_rotation*2, img.shape[1], img.shape[2]))
    angle = 360/n_rotation
    for i, cur_img in enumerate(orientations):
        for j in range(n_rotation):
            cur_angle = j*angle
            rotated_img = transforms.functional.rotate(cur_img, interpolation=transforms.InterpolationMode.BILINEAR, angle= cur_angle)
            img_augmentations[(i*n_rotation) +j, :,:] = rotated_img

    return img_augmentations

def create_patches_for_type(images_folder_path, patch_size, overlap, crop_start, n_rotations=2):
    '''
    The function get a folder with images, divides each image to patches, and take each patch and creates augmentations.
    :param images_folder: folder path as string
    :return: patches_all: tensor of patches tensors.
    '''
    patches_all = torch.tensor([])
    orig_images = []
    images_folder = PosixPath(images_folder_path)
    top, left = crop_start
    patch_height, patch_width = patch_size

    for image in images_folder.iterdir():
        if image.is_file():
            image_path = image.__fspath__()
            if "nd2" in image.suffix:
                nd = ND2Reader(image_path)
                img_arr = nd.get_frame(0)
                tensor_img = torch.tensor(np.array([np.int16(img_arr)]))
            else:
                try:
                    img = Image.open(image_path)
                except:
                    print("error - this file is not an image: ", image_path)
                    continue
                convert_tensor = transforms.ToTensor()
                tensor_img = convert_tensor(img)
                if torch.max(tensor_img) == 1:
                    tensor_img = tensor_img*255
            patches = crop_to_patches(tensor_img, top, left, patch_height, patch_width, overlap) #maia's function
            for patch in patches:
                augmentations = augmentation(patch, n_rotations) # 2 - only non-interpolation augmentation
                patches_all = torch.cat((patches_all, augmentations))
            orig_images += ([image_path] * (len(patches)*4)) # 4 - number of augmentations

    return patches_all, orig_images


