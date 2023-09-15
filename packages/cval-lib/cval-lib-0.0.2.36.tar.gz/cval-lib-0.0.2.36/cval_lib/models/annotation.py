from __future__ import annotations

from typing import List
from typing import Optional

from pydantic import BaseModel


class Label(BaseModel):
    """
    :param img_external_id: img\'s external dataset_id
    :param img_label: img\'s label
    """
    img_external_id: str
    img_label: int


class Annotation(BaseModel):
    segmentation: List
    area: float
    iscrowd: int
    image_id: int
    bbox: List[float]
    category_id: int
    id: int


class Image(BaseModel):
    license: int
    file_name: str
    coco_url: str
    height: int
    width: int
    date_captured: str
    flickr_url: str
    id: int


class Category(BaseModel):
    supercategory: str
    id: int
    name: str


class Info(BaseModel):
    description: str
    url: str
    version: str
    year: int
    contributor: str
    date_created: str


class License(BaseModel):
    url: str
    id: int
    name: str


class DetectionAnnotationCOCO(BaseModel):
    """
    cocodataset annotation model
    https://haobin-tan.netlify.app/ai/computer-vision/object-detection/coco-dataset-format/
    """
    annotations: List[Annotation]
    images: List[Image]
    categories: List[Category]
    info: Info
    licenses: List[License]


class ClassificationLabels(BaseModel):
    train_labels: Optional[List[Label]]
    val_labels: Optional[List[Label]]
    test_labels: Optional[List[Label]]


class LabelsResponse(BaseModel):
    """
    :param dataset_id: id of the dataset
    :param labels_quantity: number of labels
    """
    dataset_id: str
    labels_quantity: int
    labels: List[Label]
