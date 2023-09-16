# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
# Copyright 2018-2023 OpenMMLab. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ---------------------------------------------------------

"""MMtracking multi-object tracking model wrapper class."""


import numpy as np
import os
import shutil
import torch

from mmcv import Config
from pathlib import Path
from torch import nn, Tensor
from torch.nn.utils.rnn import pad_sequence
from typing import Dict, List, Union, Any, Tuple, OrderedDict

from azureml.acft.common_components import get_logger_app, ModelSelectorDefaults
from azureml.acft.image.components.finetune.common.mlflow.common_utils import get_current_device
from azureml.acft.image.components.finetune.mmtracking.common.constants import (
    MmTrackingDatasetLiterals,
)
from azureml.acft.image.components.finetune.mmdetection.object_detection.model_wrapper import (
    ObjectDetectionModelWrapper,
)
from azureml.acft.image.components.model_selector.constants import ImageModelSelectorConstants

logger = get_logger_app(__name__)


class MultiObjectTrackingModelWrapper(ObjectDetectionModelWrapper):
    """Wrapper class over multi-object tracking model of MMTracking framework."""

    def __init__(
        self,
        mm_multi_object_tracking_model: nn.Module,
        config: Config,
        model_name_or_path: str,
        task_type: str,
        num_labels: int,
        box_score_threshold: int,
        iou_threshold: int,
        meta_file_path: str,
    ):
        """Wrapper class over multi_object_tracking model of MMTracking.
        :param mm_multi_object_tracking_model: MM multi_object_tracking model
        :type mm_multi_object_tracking_model: nn.Module
        :param config: MM Detection model configuration
        :type config: MMCV Config
        :param model_name_or_path: model name or path
        :type model_name_or_path: str
        :param task_type: Task type either of Object Detection or Instance Segmentation
        :type task_type: str
        :param num_labels: Number of ground truth classes in the dataset
        :type num_labels: int
        :param box_score_threshold: Threshold for bounding box score
        :type box_score_threshold: float
        :param iou_threshold: Threshold for IoU(intersection over union)
        :type iou_threshold: float
        :param meta_file_path: path to meta file
        :type meta_file_path: str
        """
        super().__init__(
            mm_multi_object_tracking_model,
            config,
            model_name_or_path,
            task_type,
            num_labels,
            box_score_threshold,
            iou_threshold,
            meta_file_path
        )
        self.test_mode = False

    def forward(self, **data) -> Union[Dict[str, Any], Tuple[Tensor, Tuple]]:
        """
        Model forward pass for training and validation mode
        :param data: Input data to model
        :type data: Dict
        :return: A dictionary of loss components in training mode OR Tuple of dictionary of predicted and ground
        labels in validation mode
        :rtype: Dict[str, Any] in training mode; Tuple[Tensor, Dict[str, Tensor]] in validation mode;

        Note: Input data dictionary consist of
            img: Tensor of shape (N, C, H, W) encoding input images.
            img_metas: list of image info dict where each dict has: 'img_shape', 'scale_factor', 'flip',
             and may also contain 'filename', 'ori_shape', 'pad_shape', and 'img_norm_cfg'. For details on the values
             of these keys see `mmdet/datasets/pipelines/formatting.py:Collect`.
            gt_bboxes - list of tensor, ground truth bboxes for each image with shape (num_gts, 4)
                            in [tl_x, tl_y, br_x, br_y] format.
            gt_labels - List of tensor, class indices corresponding to each box
            gt_crowds - List of "is crowds" (boolean) to each box
            gt_masks - List of masks (type BitmapMasks) for each image if task is instance_segmentation
        """
        # removing dummy_labels for forward calls
        dummy_labels = data.pop(MmTrackingDatasetLiterals.DUMMY_LABELS, None)
        if self.model.training:
            # GT_CROWDS is not required for training
            data.pop(MmTrackingDatasetLiterals.GT_CROWDS)
            return self.model.detector.train_step(data, optimizer=None)
        img = data.pop(MmTrackingDatasetLiterals.IMG)
        img = [i.unsqueeze(0).to(get_current_device()) for i in img]
        img_metas = data.pop(MmTrackingDatasetLiterals.IMG_METAS)
        gt_bboxes = data.pop(MmTrackingDatasetLiterals.GT_BBOXES)
        gt_labels = data.pop(MmTrackingDatasetLiterals.GT_LABELS)
        gt_crowds = data.pop(MmTrackingDatasetLiterals.GT_CROWDS)

        is_video_data = img_metas[0][MmTrackingDatasetLiterals.IS_VIDEO_DATA]

        if not is_video_data:
            batch_predictions = self.model.detector(
                img=img, img_metas=[img_metas], return_loss=False
            )
            dummy_loss = torch.asarray([]).to(get_current_device())
            dummy_labels = torch.asarray([]).to(get_current_device())

            predictions: dict = self._organize_predictions_for_evaluation(batch_predictions)
            gts, img_meta_infos = self._organize_ground_truths_for_evaluation(
                gt_bboxes, gt_labels, gt_crowds)
            self.metrics_computer.update_states(y_test=gts, image_meta_info=img_meta_infos, y_pred=predictions)

            return dummy_loss, dummy_labels
        else:
            # inference with video input
            # track_predictions = self.model(
            #     img=[img], img_metas=[img_metas], return_loss=False, rescale=True)
            # output: dict = self._organize_track_predictions_for_trainer(
            #     track_predictions, img_metas)

            dummy_loss = torch.asarray([]).to(get_current_device())
            dummy_labels = torch.asarray([]).to(get_current_device())

            return dummy_loss, dummy_labels  # output
