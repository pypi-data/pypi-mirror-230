from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, validator

from cval_lib.models.weights import WeightsConfigModel


class ClassificationTest(BaseModel):
    """
    :param weights_of_model to be used in active learning or evaluation
    :param model: type of the model. Currently, supports: b0, resnet50, mobilenet
    :param use_pretrain_model : Whether to use a pre-trained model or not
    :param use_backbone_freezing: Whether to use backbone freezing in the training process
    """
    weights_of_model: Optional[WeightsConfigModel]
    model: str
    use_pretrain_model: bool = True
    use_backbone_freezing: bool = False

    @validator('model')
    def validate_model(cls, value):
        allowed = ['b0', 'resnet50', 'mobilenet']
        if value not in allowed:
            raise ValueError(f"Invalid name: {value}. Allowed models are: {', '.join(allowed)}")
        return value


class ClassificationSampling(BaseModel):
    """
    :param weights_of_model to be used in active learning or evaluation
    :param num_samples: absolute number of samples to select
    :param batch_unlabeled: the limit of unlabeled samples that can be processed during selection
    :param model: type of the model. Currently, supports: b0, resnet50, mobilenet
    :param use_pretrain_model : Whether to use a pre-trained model or not
    :param use_backbone_freezing: Whether to use backbone freezing in the training process
    """
    num_samples: int
    weights_of_model: Optional[WeightsConfigModel]
    batch_unlabeled: int
    model: str
    selection_strategy: str
    use_pretrain_model: bool = True
    use_backbone_freezing: bool = False

    @validator('selection_strategy')
    def validate_selection_strategy(cls, value):
        allowed = ['margin', 'least', 'ratio', 'entropy', 'vae', 'mixture']
        if value not in allowed:
            raise ValueError(f"Invalid name: {value}. Allowed selection strategies are: {', '.join(allowed)}")
        return value
