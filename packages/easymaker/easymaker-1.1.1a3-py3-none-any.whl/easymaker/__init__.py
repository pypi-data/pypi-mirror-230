from easymaker import initializer

from easymaker.log import logger

from easymaker.experiment import experiment

from easymaker.training import training

from easymaker.training import hyperparameter_tuning

from easymaker.training import model

from easymaker.endpoint import endpoint

from easymaker.common import constants

from easymaker.common import exceptions

from easymaker.common import utils

from easymaker.storage import objectstorage

import importlib_metadata

__version__ = importlib_metadata.version("easymaker")

easymaker_config = initializer.global_config

init = easymaker_config.init

logger = logger.Logger

Experiment = experiment.Experiment

Training = training.Training

HyperparameterTuning = hyperparameter_tuning.HyperparameterTuning

Model = model.Model

Endpoint = endpoint.Endpoint

download = objectstorage.download

upload = objectstorage.upload

ObjectStorage = objectstorage.ObjectStorage

TENSORFLOW = 'TENSORFLOW'
PYTORCH = 'PYTORCH'

HYPERPARAMETER_TYPE_CODE = constants.HYPERPARAMETER_TYPE_CODE
OBJECTIVE_TYPE_CODE = constants.OBJECTIVE_TYPE_CODE
TUNING_STRATEGY = constants.TUNING_STRATEGY
EARLY_STOPPING_ALGORITHM = constants.EARLY_STOPPING_ALGORITHM

__all__ = (
    "init",
    "Training",
)
