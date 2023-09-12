from .inference_dataset import InferenceDataset
from torch.utils.data import DataLoader
import torch
from torch import nn
import json

sample_config = {
    # mean and std for normalization
    "mean": (0.45211223, 0.27139644, 0.19264949),
    "std": (0.31418097, 0.21088019, 0.16059452),
    # Image Size
    "size_x": 716,
    "size_y": 716,
    # how to wrangle axes of the image before putting them in the network
    "axes": [2,1,0],
    "batchsize": 16,
    "num_workers": 1, # always 1 for Windows systems
    # maybe add sigmoid after prediction?
    "activation": nn.Sigmoid(),
    "labels": ['appendix',  'blood',  'diverticule',  'grasper',  'ileocaecalvalve',  'ileum',  'low_quality',  'nbi',  'needle',  'outside',  'polyp',  'snare',  'water_jet',  'wound']
}

class Classifier():
    def __init__(self, model=None, config=sample_config, verbose = False):
        self.config = config
        self.model = model
        self.verbose = verbose

    def pipe(self, paths, crops, verbose = None):
        if verbose is None:
            verbose = self.verbose

        dataset = InferenceDataset(paths, crops, self.config)
        if verbose:
            print("Dataset created")

        dl = DataLoader(
            dataset=dataset,
            batch_size=self.config["batchsize"],
            num_workers=self.config["batchsize"],
            shuffle = False,
            pin_memory=True
        )
        if verbose:
            print("Dataloader created")

        predictions = []

        with torch.inference_mode():
            if self.verbose:
                print("Starting inference")
            for i,batch in enumerate(dl):
                prediction = self.model(batch.cuda())
                prediction = self.config["activation"](prediction).cpu().tolist()#.numpy().tolist()
                predictions += prediction
                if self.verbose and i==0:
                    print("First batch done")

        return predictions

    def __call__(self, image, crop=None):
        return self.pipe([image], [crop])

    def readable(self, predictions):
        return {label: prediction for label, prediction in zip(self.config["labels"], predictions)}
    
    def get_prediction_dict(self, predictions, paths):
        json_dict = {
            "labels": self.config["labels"],
            "paths": paths,
            "predictions": predictions
        }
        
        return json_dict
    
    def get_prediction_json(self, predictions, paths, json_target_path: str = None):
        if not json_target_path:
            json_target_path = "predictions.json"

        json_dict = self.get_prediction_dict(predictions, paths)

        with open(json_target_path, 'w') as f:
            json.dump(json_dict, f)
        
        if self.verbose:
            print(f"Saved predictions to {json_target_path}")

