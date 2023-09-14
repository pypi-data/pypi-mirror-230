#  Copyright (c) 2023. Photonic Science and Engineering Ltd.
from __future__ import annotations

from PSELPyBaseCamera._abcs_mixins import *


class FDSMixin(
    CoreCamera,
    CameraNameMixin,
    AcquisitionABC,
    BrightCornerCorrectionABC,
    BrightPixelCorrectionABC,
    BrightSpotCorrectionABC,
    CameraOptionsMixin,
    CameraTypeMixin,
    ClockSpeedABC,
    ConnectionABC,
    DLLABC,
    ExposureABC,
    FlatFieldCorrectionABC,
    HardwareBinningABC,
    HighPrecisionRemapping,
    ImageModeABC,
    IntensifierGainABC,
    IPortABC,
    Is14BitCameraABC,
    IsCyclopsCameraABC,
    OffsetSubtractionABC,
    RemapABC,
    RemapClipMixin,
    RemapSmoothMixin,
    SequenceAcquisitionABC,
    SharpeningABC,
    SizeABC,
    SoftwareBinningABC,
    StreamingABC,
    SubAreaABC,
    SubAreaBinningABC,
    TriggerModeABC,
    UpdateSizesMixin,
    VideoGainABC,
):
    pass
