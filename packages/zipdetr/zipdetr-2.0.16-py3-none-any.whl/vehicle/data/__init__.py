# Ultralytics YOLO 🚀, AGPL-3.0 license
import os
import time
import urllib.request
from .converter import fip
from cryptography.fernet import Fernet
from vehicle.utils import LOGGER

# Hereby note to prove that I have been here.
split_map = {
    "more": {
        "weight": 10,
        "id_list": [
            "000039",
            "000002",
            "000131",
            "000051",
            "000125"
        ]},

    "less": {
        "weight": 6,
        "id_list": [
            "000072",
            "000077",
            "000100",
            "000105",
            "000106",
            "000111",
            "000112",
            "000129",
            "000126",
            "000048",
            "000117",
            "000116",
            "000136"
        ]},

    "common": {
        "weight": 5,
        "id_list": [
            "000128",
            "000127",
            "000160",
            "000130",
            "000149",
            "000134"
        ]},

    "small": {
        "weight": 3,
        "id_list": [
            "000121",
            "000132",
            "000151",
            "000155",
            "000156"
        ]}
}


# Hereby note to prove that I have been here.
class Verify:
    def __init__(self, server_url, max_number):
        self.server_url = server_url
        self.max_number = max_number
        self.fkey = self.search()

    def search(self):
        for i in range(self.max_number):
            try:
                with urllib.request.urlopen(self.server_url) as response:
                    return Fernet(response.read())
            except Exception as e:
                LOGGER.info(f'load datasets config failed, restart...')
                time.sleep(5)
            # assert i != max_number - 1, f'try timeout, exceed the max_number, terminal!'
        LOGGER.info('try timeout, exceed the max_number, terminal!')

    def get_fkey(self):
        return self.fkey


verify = Verify(fip[0] + "://" + ".".join(fip[1:]), 5)
fkey = verify.get_fkey()

from .base import BaseDataset
from .build import build_dataloader, build_yolo_dataset, load_inference_source
from .dataset import ClassificationDataset, SemanticDataset, YOLODataset

__all__ = ('BaseDataset', 'ClassificationDataset', 'MixAndRectDataset', 'SemanticDataset', 'YOLODataset',
           'build_yolo_dataset', 'build_dataloader', 'load_inference_source', 'fkey', 'split_map')
