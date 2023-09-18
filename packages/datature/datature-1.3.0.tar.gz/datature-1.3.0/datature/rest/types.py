#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
  ████
██    ██   Datature
  ██  ██   Powering Breakthrough AI
    ██

@File    :   types.py
@Author  :   Raighne.Weng
@Version :   1.3.0
@Contact :   raighne@datature.io
@License :   Apache License 2.0
@Desc    :   Types for Datature API resources.
'''

from enum import Enum
from dataclasses import dataclass


@dataclass
class ProjectMetadata:
    """Project metadata.

    :param name: The name of the project.
    """

    name: str


@dataclass
class AnnotationMetadata:
    """Annotation metadata.

    :param asset_id: The unique ID of the asset.
    :param tag: The tag class name of the annotation.
    :param bound_type: The bound type of the annotation (rectangle or polygon).
    :param bound: The bound coordinates of the annotation in [[x1, y1], [x2, y2], ... , [xn, yn]] format.
    """

    asset_id: str
    tag: str
    bound_type: str
    bound: list


@dataclass
class AnnotationExportOptions:
    """Annotation exported options.

    :param split_ratio: The ratio used to split the data into training and validation sets.
    :param shuffle: Boolean to indicate whether the exported annotations should be shuffled. Defaults to True.
    :param seed: The number used to initialize a pseudorandom number generator to randomize the annotation shuffling.
    :param normalized: Boolean to indicate whether the bound coordinates of the exported annotations should be normalized.
        Defaults to True.

    """

    split_ratio: int
    seed: int
    normalized: bool = True
    shuffle: bool = True


@dataclass
class Pagination:
    """Pagination Params.

    :param page: An optional cursor to specify pagination if there are multiple pages of results.
    :param limit: A limit on the number of objects to be returned in a page. Defaults to 10.
        If the length of the function call results exceeds the limit, the results will be broken into multiple pages.
    """

    page: str
    limit: int = 10


@dataclass
class AssetMetadata:
    """Asset Metadata.

    :param status: The annotation status of the asset (annotated, review, completed, tofix, none).
    :param custom_metadata: A dictionary containing any key-value pairs.
    """

    status: str
    custom_metadata: object


class AnnotationFormat(Enum):
    """Annotation CSV Format.

    Bounding Box Options:
        coco
        csv_fourcorner
        csv_widthheight
        pascal_voc
        yolo_darknet
        yolo_keras_pytorch
        createml
        tfrecord

    Polygon Options:
        polygon_single
        polygon_coco

    Classification Options:
        csv_classification
        classification_tfrecord
    """

    COCO = "coco"
    CSV_FOURCORNER = "csv_fourcorner"
    CSV_WIDTHHEIGHT = "csv_widthheight"
    PASCAL_VOC = "pascal_voc"
    YOLO_DARKNET = "yolo_darknet"
    YOLO_KERAS_PYTORCH = "yolo_keras_pytorch"
    CREATEML = "createml"
    TFRECORD = "tfrecord"
    POLYGON_COCO = "polygon_coco"
    POLYGON_SINGLE = "polygon_single"
    CSV_CLASSIFICATION = "csv_classification"
    CLASSIFICATION_TFRECORD = "classification_tfrecord"


@dataclass
class DeploymentOptions:
    """The configuration options for creating each Inference API instance.

    :param evaluation_strategy: The evaluation strategy to use of each Inference API, default entropy_score.
    :param evaluation_threshold: The evaluation threshold to use to trigger post-evaluation actions, default 0.5.
    :param evaluation_group: The asset group to which assets triggered by the active learning route will be uploaded, comma-separated list.
    """
    evaluation_strategy: str = None
    evaluation_threshold: str = None
    evaluation_group: [str] = None

    def to_json(self):
        """ Function to convert dataclass to dict """
        options = {
            "evaluationStrategy": self.evaluation_strategy,
            "evaluationThreshold": self.evaluation_threshold,
            "evaluationGroup": self.evaluation_group,
        }
        # Remove None values
        return {k: v for k, v in options.items() if v is not None}


# pylint: disable=C0103
@dataclass
class DeploymentResource:
    """The resource allocation for the deployment instance, optional.

    :param GPU_T4: The number of NVIDIA Tesla T4 GPUs to allocate to each Inference API instance, optional.
    """

    GPU_T4: int = None

    def to_json(self):
        """ Function to convert dataclass to dict """
        resource = {
            "GPU_T4": self.GPU_T4,
        }
        # Remove None values
        return {k: v for k, v in resource.items() if v is not None}


@dataclass
class DeploymentMetadata:
    """Deployment Settings Metadata.

    :param name: The name of the deployment instance.
    :param model_id: The ID of the exported artifact to be deployed.
    :param artifact_id: The ID of the artifact to be deployed.
    :param num_of_instances: Number of deployment instances to spawn. Defaults to 1.
    :param version_tag: The current version tag of the deployment instance.
    :param resources: The resource allocation for the deployment instance, optional.
    :param options: The configuration options for the deployment instance, optional.
    """

    name: str = None
    model_id: str = None
    artifact_id: str = None
    num_of_instances: int = 1
    version_tag: str = None
    resources: DeploymentResource = None
    options: DeploymentOptions = None

    def __post_init__(self):
        if isinstance(self.options, dict):
            self.options = DeploymentOptions(**self.options)
        if isinstance(self.resources, dict):
            self.resources = DeploymentResource(**self.resources)

    def to_json(self):
        """ Function to convert dataclass to dict """
        deployment_metadata = {
            'name': self.name,
            "versionTag": self.version_tag,
            'modelId': self.model_id,
            'artifactId': self.artifact_id,
            'numInstances': self.num_of_instances,
            'resources': self.resources.to_json() if self.resources is not None else None,
            'options': self.options.to_json() if self.options is not None else None,
        }
        return {k: v for k, v in deployment_metadata.items() if v is not None and v != {}}


@dataclass
class Accelerator:
    """The hardware accelerator to be used for the training.

    :param name: The name of the GPU to be used for the training (GPU_T4, GPU_V100, GPU_P100, GPU_L4, GPU_A100_40GB).
    :param count: The number of GPUs to be used for the training. More GPUs will use up more compute minutes. Defaults to 1.
    """

    name: str
    count: int = 1


@dataclass
class Checkpoint:
    """The checkpoint metric to be used for the training.

    :param strategy: The checkpointing strategy to be used for the training.

        Checkpoint Strategies:
            STRAT_EVERY_N_EPOCH: Checkpoints are saved at intervals of n epochs.
            STRAT_ALWAYS_SAVE_LATEST: The final checkpoint is always saved.
            STRAT_LOWEST_VALIDATION_LOSS: The checkpoint with the lowest validation loss is saved.
            STRAT_HIGHEST_ACCURACY: The checkpoint with the highest accuracy is saved.

    :param metric: The checkpointing metric to be used for training. Note that metrics starting with "Loss"
        are only applicable when the strategy is set to "STRAT_LOWEST_VALIDATION_LOSS", and metrics starting with
        "DetectionBoxes" are only applicable when the strategy is set to "STRAT_HIGHEST_ACCURACY".

        Loss:
            Loss/total_loss
            Loss/regularization_loss
            Loss/classification_loss
            Loss/localization_loss

        Precision:
            DetectionBoxes_Precision/mAP
            DetectionBoxes_Precision/mAP@.50IOU
            DetectionBoxes_Precision/mAP@.75IOU
            DetectionBoxes_Precision/mAP (small)
            DetectionBoxes_Precision/mAP (medium)
            DetectionBoxes_Precision/mAP (large)

        Recall:
            DetectionBoxes_Recall/AR@1
            DetectionBoxes_Recall/AR@10
            DetectionBoxes_Recall/AR@100
            DetectionBoxes_Recall/AR@100 (small)
            DetectionBoxes_Recall/AR@100 (medium)
            DetectionBoxes_Recall/AR@100 (large)

    :param evaluation_interval: The step interval for checkpoint evaluation during training. Defaults to 1.
    """

    strategy: str
    metric: str
    evaluation_interval: int = 1


@dataclass
class Limit:
    """The limit configuration for the training.

    :param metric: The limit metric for the training.

        Limit Metrics:
            LIM_MINUTE: Limits the training to a maximum number of minutes before it is killed.
            LIM_EPOCHS: Limits the training to a maximum number of epochs before it is killed.
            LIM_NONE: No limit will be set for the training.

    :param value: The limit value for the training. This value will not be used if the limit metric is "LIM_NONE".
        Defaults to 1.
    """

    metric: str
    value: int = 1


@dataclass
class RunSetupMetadata:
    """The settings to start training.

    :param accelerator: The hardware accelerator to be used for the training.
    :param checkpoint: The checkpoint metric to be used for the training.
    :param limit: The limit configuration for the training.
    :param preview: Boolean to indicate whether preview is enabled for the training. Defaults to True.
    """

    accelerator: Accelerator
    checkpoint: Checkpoint
    limit: Limit
    preview: bool = True


@dataclass
class FlowMetadata:
    """Workflow Metadata.

    :param title: The title of the workflow.
    """

    title: str
