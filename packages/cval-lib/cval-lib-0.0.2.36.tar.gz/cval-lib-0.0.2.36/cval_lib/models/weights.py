from __future__ import annotations

from typing import Optional

from pydantic import BaseModel

from typing import List


class WeightsConfigModel(BaseModel):
    """
    :param weights_id: weights ID to be used in active learning
    :param retrain_model: perform a model retrain
    :param weights_version: Weights Version to be used in the operation
    """
    weights_id: str
    retrain_model: bool = False
    weights_version: Optional[str]


class Version(BaseModel):
    """
    :param ID: internal id of version
    :param timestamp: UNIX timestamp creation time
    :param ver: version
    :param task_id: id of task
    """
    ID: str
    timestamp: float
    ver: str
    task_id: str


class WeightsOfModel(BaseModel):
    ID: str
    model: str


class WeightsBase(BaseModel):
    """
    :param weights_of_model: internal id of version
    :param versions: list of versions
    """
    weights_of_model: WeightsOfModel
    versions: List[Version]
