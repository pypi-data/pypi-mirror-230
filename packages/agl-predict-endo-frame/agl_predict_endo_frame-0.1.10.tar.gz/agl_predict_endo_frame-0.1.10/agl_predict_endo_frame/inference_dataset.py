from torch.utils.data import Dataset
import cv2
import torch
import numpy as np
import warnings
from .preprocess import Cropper
from PIL import Image
import albumentations as A

class InferenceDataset(Dataset):
    def __init__(self, paths, crops, config):
        self.paths = paths
        self.crops = crops
        self.cropper = Cropper()
        self.config = config

        self.img_transforms = A.Compose([
            A.Normalize(
                mean=self.config["mean"],
                std=self.config["std"],
            max_pixel_value=255)
        ])
        

    def __len__(self):
        return len(self.paths)

    def __getitem__(self, idx):
        image = cv2.imread(self.paths[idx])
                
        crop = self.crops[idx]

        cropped = self.cropper(
            image, 
            crop, 
            scale=[
                self.config["size_x"],
                self.config["size_y"]
            ]    
        )
        
        img = self.img_transforms(image=cropped)["image"]
        img = torch.tensor(img, dtype = torch.float32)
        img = img.permute(self.config["axes"])

        return img
