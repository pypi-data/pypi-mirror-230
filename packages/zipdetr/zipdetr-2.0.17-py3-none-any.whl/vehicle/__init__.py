# Ultralytics YOLO 🚀, AGPL-3.0 license

# Hereby note to prove that I have been here.
# __version__ = '8.0.158'
__version__ = '2.0.17'

from vehicle.hub import start
from vehicle.models import RTDETR, SAM, YOLO
from vehicle.models.fastsam import FastSAM
from vehicle.models.nas import NAS
from vehicle.utils import SETTINGS as settings
from vehicle.utils.checks import check_yolo as checks
from vehicle.utils.downloads import download

__all__ = '__version__', 'YOLO', 'NAS', 'SAM', 'FastSAM', 'RTDETR', 'checks', 'download', 'start', 'settings'  # allow simpler import
