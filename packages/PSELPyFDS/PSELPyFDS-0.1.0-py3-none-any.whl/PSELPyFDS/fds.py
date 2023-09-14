#  Copyright (c) 2023. Photonic Science and Engineering Ltd.
from __future__ import annotations

import ctypes as ct
import logging
import traceback
from _ctypes import FreeLibrary
from _ctypes import LoadLibrary
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Union

import numpy as np
from PSELPyBaseCamera.helper import *
from PSELPyBaseCamera.image_modes import ImageMode
from PSELPyBaseCamera.logging_tools import log_this_function
from PSELPyBaseCamera.options import OptionSetterResult

from ._fds_mixin import FDSMixin

_logger = logging.getLogger(__name__)

PointerType = Any


class FDS(FDSMixin):
    def __init__(self, _current_working_directory: Union[str, Path], name: str = "FDS"):
        """Create FDS camera.

        Args:
            _current_working_directory: path to camera folder
            name: camera name
        """
        # Path to camera folder
        self._current_working_directory = Path(_current_working_directory)

        self._name = name  # Camera name
        self._camera_directory = self._current_working_directory / self._name
        res, dll_path = get_dll_path(self._camera_directory)

        if not res and isinstance(dll_path, int):
            raise ValueError(dll_path)  # dll_path is a count of dll files present
        self._dll_path = dll_path

        self._is_closed = True

    @log_this_function(_logger)
    def __del__(self):
        msg = ""
        if not self._is_closed:
            if hasattr(self, "dll") and self.dll is not None:
                try:
                    _logger.warning("Attempting self.close in __del__")
                    res = self.close()
                    if not res:
                        msg = f"__del__ failed to close camera {self.name}"
                except OSError:
                    msg = f"__del__ failed with exception: {traceback.format_exc()}"

            if msg != "":
                _logger.error(msg)

    @log_this_function(_logger)
    def reset_options(self) -> None:
        self._is_cyclops_camera = False
        self._is_14_bit_camera = False
        self._is_iport = False
        self.fusion = False

        self.sub_area = (0, 1367, 0, 1039)
        self.software_binning = (1, 1)
        self.hardware_binning = (1, 1)

        self._mode = ImageMode.I16
        self._byte_depth = 2

        # Manage Calibration Files
        # Flat Field
        self._calibration_files_flat_field_use_user_file = False
        self._calibration_files_flat_field_user_file_image_file = None
        self._calibration_files_flat_field_user_file_pedestal = 100
        self._calibration_files_flat_field_user_file_scale_factor = 1
        self._calibration_files_flat_field_save_flat_average = 10

        # Remapping
        self.remapping = False
        self._smooth = False
        self._clip = True
        self._remap_x = 0
        self._remap_y = 0
        self._remap_rotation = 0
        self._remap_sub_width = 0
        self._remap_sub_height = 0
        self._remap_angular = 0

        # Auto Level
        self._auto_level = False

        self._camera_options = [
            {
                "name": f"{self.name} settings",
                "type": "group",
                "children": [
                    {
                        "name": "exposure",
                        "title": "Exposure",
                        "type": "float",
                        "value": 0.1,
                        "dec": True,
                        "step": 1,
                        "minStep": 1.0e-6,
                        "siPrefix": True,
                        "suffix": "S",
                        "limits": (1.0e-3, 1e6),
                        "decimals": 10,
                    },
                    {
                        "name": "PostCorrections",
                        "type": "group",
                        "children": sorted(
                            [
                                {
                                    "name": "flat_field",
                                    "title": "Flat Field",
                                    "type": "bool",
                                    "value": False,
                                },
                                {
                                    "name": "offset",
                                    "title": "Offset",
                                    "type": "bool",
                                    "value": False,
                                },
                                {
                                    "name": "sharpening",
                                    "title": "Sharpening",
                                    "type": "bool",
                                    "value": False,
                                },
                                {
                                    "name": "bright_corner",
                                    "title": "Bright Corner",
                                    "type": "bool",
                                    "value": False,
                                },
                                {
                                    "name": "bright_pixel",
                                    "title": "Bright Pixel",
                                    "type": "bool",
                                    "value": False,
                                },
                                {
                                    "name": "bright_spot",
                                    "title": "Bright Spot",
                                    "type": "bool",
                                    "value": False,
                                },
                            ],
                            key=lambda x: str(x["name"]),
                        ),
                    },
                    {
                        "name": "Manage Calibration Files",
                        "type": "group",
                        "children": [
                            {
                                "name": "Flat Field",
                                "type": "group",
                                "children": [
                                    {
                                        "name": (
                                            "calibration_files_flat_field_use_user_file"
                                        ),
                                        "title": "User file",
                                        "type": "bool",
                                        "value": self._calibration_files_flat_field_use_user_file,
                                        "children": [
                                            {
                                                "name": "calibration_files_flat_field_user_file_image_file",
                                                "title": "Image File",
                                                "type": "file",
                                                "fileMode": "ExistingFile",
                                                "directory": str(
                                                    self._camera_directory
                                                ),
                                                "value": self._calibration_files_flat_field_user_file_image_file,
                                            },
                                            {
                                                "name": "calibration_files_flat_field_user_file_pedestal",
                                                "title": "Pedestal",
                                                "type": "int",
                                                "value": self._calibration_files_flat_field_user_file_pedestal,
                                                "limits": (0, 100_000),
                                            },
                                            {
                                                "name": "calibration_files_flat_field_user_file_scale_factor",
                                                "title": "Scale Factor",
                                                "type": "int",
                                                "value": self._calibration_files_flat_field_user_file_scale_factor,
                                                "limits": (1, 1_000_000),
                                            },
                                        ],
                                    },
                                    {
                                        "name": "calibration_files_flat_field_save",
                                        "title": "save",
                                        "type": "action",
                                        "children": [
                                            {
                                                "name": "calibration_files_flat_field_save_flat_average",
                                                "title": "Flat Average",
                                                "type": "int",
                                                "value": self._calibration_files_flat_field_save_flat_average,
                                                "limits": (1, 256),
                                            }
                                        ],
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "name": "Camera Mode",
                        "type": "group",
                        "children": [
                            {
                                "name": "clock_speed_mode",
                                "title": "Clock Speed Mode",
                                "type": "list",
                                "limits": ["12.5MHz", "25MHz"],
                                "value": "12.5MHz",
                            },
                            {
                                "name": "trigger_mode",
                                "title": "Trigger Mode",
                                "type": "list",
                                "limits": [
                                    "FreeRunning",
                                    "Software",
                                    "Hardware_Falling",
                                    "Hardware_Rising",
                                ],
                                "value": "FreeRunning",
                            },
                        ],
                    },
                    {
                        "name": "Fusion",
                        "type": "group",
                        "children": [
                            {
                                "name": "enable_fusion",
                                "title": "Enable Fusion",
                                "type": "bool",
                                "value": False,
                            },
                            {
                                "name": "fusion_noise_average",
                                "title": "Fusion Noise Average",
                                "type": "int",
                                "value": 0,
                                "limits": (0, 16),
                            },
                        ],
                    },
                    {
                        "name": "Gains",
                        "type": "group",
                        "children": [
                            {
                                "name": "intensifier_gain",
                                "title": "Intensifier Gain",
                                "type": "int",
                                "value": 1,
                                "limits": (1, 100),
                            },
                            {
                                "name": "video_gain",
                                "title": "Video Gain",
                                "type": "int",
                                "value": 1,
                                "limits": (1, 100),
                            },
                        ],
                    },
                    {
                        "name": "Binning",
                        "type": "group",
                        "children": [
                            {
                                "name": "hardware_binning",
                                "title": "Hardware Binning",
                                "type": "binning",
                                "value": (1, 1),
                            },
                            {
                                "name": "software_binning",
                                "title": "Software Binning",
                                "type": "binning",
                                "value": (1, 1),
                            },
                            {
                                "name": "bin2mode",
                                "title": "Bin 2 mode",
                                "type": "bool",
                                "value": False,
                            },
                        ],
                    },
                    {
                        "name": "enable_remapping",
                        "title": "Remapping",
                        "type": "bool",
                        "value": False,
                        "children": [
                            {
                                "name": "remapping_smooth",
                                "title": "Smooth",
                                "type": "bool",
                                "value": False,
                            },
                            {
                                "name": "remapping_clip",
                                "title": "Clip",
                                "type": "bool",
                                "value": False,
                            },
                            {
                                "name": "HPM",
                                "type": "group",
                                "children": [
                                    {
                                        "name": "HPM_x",
                                        "title": "HPM x",
                                        "type": "int",
                                        "value": 0,
                                        "limits": (-10000, 10000),
                                    },
                                    {
                                        "name": "HPM_y",
                                        "title": "HPM y",
                                        "type": "int",
                                        "value": 0,
                                        "limits": (-10000, 10000),
                                    },
                                    {
                                        "name": "HPM_rotation",
                                        "title": "HPM rotation",
                                        "type": "int",
                                        "value": 0,
                                        "limits": (-10000, 10000),
                                    },
                                    {
                                        "name": "HPM_sub_width",
                                        "title": "HPM sub width",
                                        "type": "int",
                                        "value": 0,
                                        "limits": (0, 10000),
                                    },
                                    {
                                        "name": "HPM_sub_height",
                                        "title": "HPM sub height",
                                        "type": "int",
                                        "value": 0,
                                        "limits": (0, 10000),
                                    },
                                    {
                                        "name": "HPM_angular",
                                        "title": "HPM angular",
                                        "type": "bool",
                                        "value": False,
                                    },
                                ],
                            },
                        ],
                    },
                    {
                        "name": "Flouresence",
                        "type": "group",
                        "children": [
                            {
                                "name": "flouresence_exposure_start_delay",
                                "title": "ExposureStartDelay",
                                "type": "int",
                                "value": 0,
                                "limits": (0, 1_000_000_000),
                            },
                            {
                                "name": "flouresence_trigger_out_high_time",
                                "title": "TriggerOutHighTime",
                                "type": "int",
                                "value": 0,
                                "limits": (0, 1_000_000_000),
                            },
                        ],
                    },
                    {
                        "name": "Sub Area",
                        "type": "group",
                        "children": [
                            {
                                "name": "sub_area",
                                "title": "(L, R, T, B)",
                                "type": "subarea",
                                "value": (0, 1367, 0, 1039),
                            },
                        ],
                    },
                    {
                        "name": "Auto Level",
                        "type": "group",
                        "children": [
                            {
                                "name": "auto_level",
                                "title": "Auto Level",
                                "type": "bool",
                                "value": self._auto_level,
                            }
                        ],
                    },
                    {
                        "name": "Miscellaneous",
                        "type": "group",
                        "children": [
                            {
                                "name": "reset_camera",
                                "title": "Reset Camera",
                                "type": "action",
                            }
                        ],
                    },
                    # {"name": "", "type": "", "value": ""},  # Template
                ],  # children
            }
        ]

        self._set_camera_option_routing_dict = {
            "bright_corner": self.enable_bright_corner_correction,
            "bright_pixel": self.enable_bright_pixel_correction,
            "bright_spot": self.enable_bright_spot_correction,
            "clock_speed_mode": self.set_clock_speed,
            "enable_remapping": self.enable_remapping,
            "exposure": self.set_exposure,
            "flat_field": self.enable_flat_field_correction,
            "hardware_binning": self.set_hardware_binning,
            "HPM_angular": self.set_HPM_angular,
            "HPM_rotation": self.set_HPM_rotation,
            "HPM_sub_height": self.set_HPM_sub_height,
            "HPM_sub_width": self.set_HPM_sub_width,
            "HPM_x": self.set_HPM_x,
            "HPM_y": self.set_HPM_y,
            "intensifier_gain": self.set_intensifier_gain,
            "offset": self.enable_offset_subtraction,
            "remapping_clip": self.enable_clip,
            "remapping_smooth": self.enable_smooth,
            "reset_camera": self.reset_camera,
            "sharpening": self.enable_sharpening,
            "software_binning": self.set_software_binning,
            "sub_area": self.set_sub_area,
            "trigger_mode": self.set_trigger_mode,
            "video_gain": self.set_video_gain,
        }

        self._get_camera_option_routing_dict = {"sub_area": self.get_sub_area}

    @log_this_function(_logger)
    def load_cam_dll(self) -> None:
        # ct.cdll.LoadLibrary()  # Can this be used?
        _logger.info(self.dll_path)
        self._lib_handle = LoadLibrary(str(self.dll_path))
        # ct.cdll.LoadLibrary()
        self.dll = ct.CDLL(self.dll_path.name, handle=self._lib_handle)
        self.init_functions()

    @log_this_function(_logger)
    def unload_cam_dll(self) -> True:
        del self.dll
        self.dll = None
        FreeLibrary(self._lib_handle)
        return True

    # fmt: off
    @log_this_function(_logger)
    def init_functions(self) -> None:
        self.dll.PSL_VHR_abort_snap.argtypes = []
        self.dll.PSL_VHR_abort_snap.restype = ct.c_bool
        self.dll.PSL_VHR_apply_post_snap_processing.argtypes = [c_char_p]
        self.dll.PSL_VHR_apply_post_snap_processing.restype = ct.c_bool
        self.dll.PSL_VHR_Close.argtypes = []
        self.dll.PSL_VHR_Close.restype = ct.c_bool
        self.dll.PSL_VHR_enable_auto_gain_control.argtypes = [ct.c_bool]
        self.dll.PSL_VHR_enable_auto_gain_control.restype = ct.c_bool
        self.dll.PSL_VHR_enable_bright_corner_subtraction.argtypes = [ct.c_bool]
        self.dll.PSL_VHR_enable_bright_corner_subtraction.restype = ct.c_bool
        self.dll.PSL_VHR_enable_bright_pixel_correction.argtypes = [ct.c_bool]
        self.dll.PSL_VHR_enable_bright_pixel_correction.restype = ct.c_bool
        self.dll.PSL_VHR_enable_flat_field_correction.argtypes = [ct.c_bool]
        self.dll.PSL_VHR_enable_flat_field_correction.restype = ct.c_bool
        self.dll.PSL_VHR_enable_image_streaming.argtypes = [ct.c_bool]
        self.dll.PSL_VHR_enable_image_streaming.restype = None
        self.dll.PSL_VHR_enable_offset_subtraction.argtypes = [ct.c_bool]
        self.dll.PSL_VHR_enable_offset_subtraction.restype = ct.c_bool
        self.dll.PSL_VHR_enable_sharpening.argtypes = [ct.c_bool]
        self.dll.PSL_VHR_enable_sharpening.restype = None
        self.dll.PSL_VHR_Fusion_snap.argtypes = [ct.c_ushort]
        self.dll.PSL_VHR_Fusion_snap.restype = ct.c_bool
        self.dll.PSL_VHR_Fusion_snap_for_14_bit_cameras.argtypes = [ct.c_ushort]
        self.dll.PSL_VHR_Fusion_snap_for_14_bit_cameras.restype = c_ulong_p
        self.dll.PSL_VHR_generate_high_precision_working_map.argtypes = []
        self.dll.PSL_VHR_generate_high_precision_working_map.restype = ct.c_bool
        self.dll.PSL_VHR_get_auto_gain_control_status.argtypes = []
        self.dll.PSL_VHR_get_auto_gain_control_status.restype = ct.c_bool
        self.dll.PSL_VHR_get_exposure_start_delay.argtypes = []
        self.dll.PSL_VHR_get_exposure_start_delay.restype = ct.c_int
        self.dll.PSL_VHR_get_height.argtypes = []
        self.dll.PSL_VHR_get_height.restype = ct.c_long
        self.dll.PSL_VHR_get_high_precision_remapped_image_dimensions.argtypes = [c_int_p, c_int_p]
        self.dll.PSL_VHR_get_high_precision_remapped_image_dimensions.restype = None
        self.dll.PSL_VHR_get_image_pointer.argtypes = []
        self.dll.PSL_VHR_get_image_pointer.restype = c_char_p
        self.dll.PSL_VHR_get_maximum_height.argtypes = []
        self.dll.PSL_VHR_get_maximum_height.restype = ct.c_long
        self.dll.PSL_VHR_get_maximum_width.argtypes = []
        self.dll.PSL_VHR_get_maximum_width.restype = ct.c_long
        self.dll.PSL_VHR_Get_snap_status.argtypes = []
        self.dll.PSL_VHR_Get_snap_status.restype = ct.c_bool
        self.dll.PSL_VHR_get_trigger_out_high_time.argtypes = []
        self.dll.PSL_VHR_get_trigger_out_high_time.restype = ct.c_int
        self.dll.PSL_VHR_get_width.argtypes = []
        self.dll.PSL_VHR_get_width.restype = ct.c_long
        self.dll.PSL_VHR_Is_14bit_camera.argtypes = []
        self.dll.PSL_VHR_Is_14bit_camera.restype = ct.c_bool
        self.dll.PSL_VHR_Is_Cyclops_camera.argtypes = []
        self.dll.PSL_VHR_Is_Cyclops_camera.restype = ct.c_bool
        self.dll.PSL_VHR_Open.argtypes = [ct.c_char_p]
        self.dll.PSL_VHR_Open.restype = ct.c_bool
        self.dll.PSL_VHR_open_map.argtypes = [ct.c_char_p]
        self.dll.PSL_VHR_open_map.restype = ct.c_bool
        self.dll.PSL_VHR_perform_high_precision_remap.argtypes = [c_char_p, ct.c_bool]
        self.dll.PSL_VHR_perform_high_precision_remap.restype = c_char_p
        self.dll.PSL_VHR_remap_14bit_fusion_image.argtypes = [c_ulong_p, c_int_p, c_int_p, ct.c_bool, ct.c_bool]
        self.dll.PSL_VHR_remap_14bit_fusion_image.restype = c_ulong_p
        self.dll.PSL_VHR_remap_image.argtypes = [c_char_p, c_int_p, c_int_p, ct.c_bool, ct.c_bool]
        self.dll.PSL_VHR_remap_image.restype = c_char_p
        self.dll.PSL_VHR_reset_camera.argtypes = []
        self.dll.PSL_VHR_reset_camera.restype = None
        self.dll.PSL_VHR_select_IPORT_device.argtypes = [ct.c_char_p, ct.c_char_p]
        self.dll.PSL_VHR_select_IPORT_device.restype = None
        self.dll.PSL_VHR_set_exposure.argtypes = [ct.c_ulong]
        self.dll.PSL_VHR_set_exposure.restype = ct.c_bool
        self.dll.PSL_VHR_set_exposure_start_delay.argtypes = [ct.c_int]
        self.dll.PSL_VHR_set_exposure_start_delay.restype = ct.c_bool
        self.dll.PSL_VHR_set_intensifier_gain.argtypes = [ct.c_ulong]
        self.dll.PSL_VHR_set_intensifier_gain.restype = ct.c_bool
        self.dll.PSL_VHR_set_speed.argtypes = [ct.c_int]
        self.dll.PSL_VHR_set_speed.restype = ct.c_bool
        self.dll.PSL_VHR_set_sub_area_coordinates.argtypes = [ct.c_long, ct.c_long, ct.c_long, ct.c_long, ct.c_long, ct.c_long]
        self.dll.PSL_VHR_set_sub_area_coordinates.restype = ct.c_bool
        self.dll.PSL_VHR_set_trigger_mode.argtypes = [ct.c_int]
        self.dll.PSL_VHR_set_trigger_mode.restype = ct.c_bool
        self.dll.PSL_VHR_set_trigger_out_high_time.argtypes = [ct.c_int]
        self.dll.PSL_VHR_set_trigger_out_high_time.restype = ct.c_bool
        self.dll.PSL_VHR_set_video_gain.argtypes = [ct.c_ulong]
        self.dll.PSL_VHR_set_video_gain.restype = ct.c_bool
        self.dll.PSL_VHR_Snap_and_return.argtypes = []
        self.dll.PSL_VHR_Snap_and_return.restype = ct.c_bool
    # fmt: on

    def reset_camera(self, _=None) -> OptionSetterResult:
        # self.dll.PSL_VHR_reset_camera()
        return OptionSetterResult.COMPLETED

    def _set_is_cyclops_camera(self) -> None:
        self._is_cyclops_camera = self.dll.PSL_VHR_Is_Cyclops_camera()

    def _set_is_14_bit_camera(self) -> None:
        self._is_14_bit_camera = self.dll.PSL_VHR_Is_14bit_camera()

    """Camera options"""

    def image_mode(self) -> ImageMode:
        """Return the image mode of the camera.

        Returns:
            camera's image mode
        """
        return self._mode

    # def get_camera_options(self) -> list[dict]:
    #     return self._camera_options

    # def get_camera_option_names(self) -> list[str]:
    #     """Get a list of all settable camera option names that can be used in
    #     conjunction with :py:meth:`PSELPyFDS.FDS.set_camera_option_value`.
    #
    #     Returns:
    #         list of settable camera option names
    #     """
    #     return list(self._set_camera_option_routing_dict.keys())

    # def get_camera_option_value(self, name) -> OptionType:
    #     if name in self._get_camera_option_routing_dict:
    #         return self._get_camera_option_routing_dict[name]()
    #     else:
    #         _logger.error(f"Option does not have a get method: {name}")
    #         raise ValueError(f"Option does not have a get method: {name}")

    # @log_this_function(_logger)
    # def set_camera_option_value(
    #     self,
    #     option_name: str,
    #     option_value: OptionType,
    #     update_value_callback: Callable[[OptionType], bool],
    # ) -> bool:
    #     """Set the value of a camera option.
    #
    #     Args:
    #         option_name: Name of the option.
    #         option_value: Value to set this option to.
    #         update_value_callback: Function callback to set the named options value at
    #             the source of this call.
    #     Returns:
    #         Boolean indicating success or failure in setting option in the camera
    #         driver.
    #     Raises:
    #         SettingCameraOptionValueError: if setting the option in the camera fails.
    #     """
    #     if option_name not in self._set_camera_option_routing_dict:
    #         raise KeyError(f"{option_name} not in dict. Setting with {option_value}")
    #
    #     _logger.info(f"Setting option {option_name} with value {option_value}")
    #
    #     setter = self._set_camera_option_routing_dict[option_name]
    #
    #     if isinstance(option_value, tuple):
    #         result = setter(*option_value)
    #     else:
    #         result = setter(option_value)
    #
    #     _logger.info(f"Setting option {option_name} result={result}")
    #
    #     if result is OptionSetterResult.COMPLETED:
    #         # if result:
    #         return True
    #     elif result is OptionSetterResult.FAILED:
    #         # if not result:
    #         _logger.log(
    #             logging.ERROR,
    #             f"set_camera_option_value for {self.name} failed to set"
    #             f" {option_name} to {option_value}",
    #         )
    #         # TODO: This should try and read the value the driver has back out so that
    #         #  it can be reflected in the GUI
    #         raise SettingCameraOptionValueError(option_name, option_value, self.name)
    #     elif result is OptionSetterResult.CHECK:
    #         new_value = self.get_camera_option_value(option_name)
    #         _logger.log(
    #             logging.INFO,
    #             f"The driver returned a different value ({new_value}) to the one"
    #             f" requested by the user ({option_value}). Callback triggered to"
    #             " reflect this change",
    #         )
    #         _logger.info(update_value_callback)
    #         _logger.info(type(update_value_callback))
    #         res = update_value_callback(new_value)
    #         _logger.info(f"Callback result {res}")
    #         return res
    #     else:
    #         raise ValueError(
    #             f"Invalid result when setting option {option_name} to {option_value},"
    #             f" recieved {result}."
    #         )

    """Properties"""

    @property
    def is_cyclops_camera(self) -> bool:
        """Is this camera a cyclops camera.

        Returns:
            boolean indicating if this camea is a cyclops camera
        """
        return self._is_cyclops_camera

    @property
    def is_14_bit_camera(self) -> bool:
        """Is this camera a (noncolour) 14 bit camera.

        If it is a 14 bit camera the cyclops post processing will be used, without the
        colour processing section.

        Returns:
            boolean indicating if this camea is a 14 bit camera
        """
        return self._is_14_bit_camera

    @property
    def is_iport(self) -> bool:
        """Is this camera using IPORT hardware.

        Returns:
            boolean indicating if this camera is using IPORT hardware
        """
        return self._is_iport

    @property
    def name(self) -> str:
        """Name of the camera.

        Returns:
            name of the camera
        """
        return self._name

    @property
    def size(self) -> tuple[int, int]:
        """Size of image currently set in the driver.

        Returns:
            size of images (x, y)
        """
        Nx = self.dll.PSL_VHR_get_width()
        Ny = self.dll.PSL_VHR_get_height()
        return Nx, Ny

    @property
    def size_max(self) -> tuple[int, int]:
        """Maximum size image the sensor can output.

        Returns:
            maximum size of an image (x, y)
        """
        Nx = self.dll.PSL_VHR_get_maximum_width()
        Ny = self.dll.PSL_VHR_get_maximum_height()
        return Nx, Ny

    @property
    def dll_path(self) -> Path:
        """Path to camera dll.

        Returns:
            Path to camera dll
        """
        return self._dll_path

    def select_iport_device(self) -> bool:
        """For systems using IPORT hardware read the MAC address and IP address from
        IPConf.dat.

        If one or other of these is not specified we are not using IPORT.

        This function should be called before :py:meth:`PSELPyFDS.FDS.open`.

        Use is_iport property to test if we are using IPORT hardware after this
        function has been called.

        Returns:
            True if MAC address and IP address are set, or if we are not using IPORT,
            and False if IPConf.dat is not present
        """
        path = self._current_working_directory / self.name / "IPConf.dat"
        if not path.exists():
            self._is_iport = False
            return False

        self._mac_address = ""
        self._ip_address = ""
        self._is_iport = True

        with path.open(mode="r") as file:
            lines = file.readlines()

        for line in lines:
            option, _, value = line.strip().partition("=")
            if option == "MAC":
                self._mac_address = value
            elif option == "IP":
                self._ip_address = value

        if self._mac_address == "" or self._ip_address == "":
            self.dll.PSL_VHR_select_IPORT_device(b"", b"")
        else:
            self.dll.PSL_VHR_select_IPORT_device(
                bytes(self._mac_address, "utf-8"),
                bytes(f"[{self._ip_address}]", "utf-8"),
            )

        return True

    """Camera Standard functions"""

    @log_this_function(_logger)
    def open(self) -> bool:
        """Open and initialise the system (framegrabber and camera).

        This function should be called only once and after
        :py:meth:`PSELPyFDS.FDS.select_iport_device`

        Returns:
            boolean indicating success
        """
        _logger.info("Loading cam dll")
        self.load_cam_dll()
        self.reset_options()

        path = self._current_working_directory / self.name / "PSL_camera_files"

        self.select_iport_device()

        _logger.info("Opening camera")
        if not self.dll.PSL_VHR_Open(str(path).encode()):
            _logger.log(logging.ERROR, f"Failed to open {self.name} camera.")
            return False
        self._is_closed = False

        self._set_is_cyclops_camera()
        self._set_is_14_bit_camera()

        _logger.log(logging.INFO, f"is_cyclops_camera={self.is_cyclops_camera}")
        _logger.log(logging.INFO, f"is_14_bit_camera={self.is_14_bit_camera}")
        _logger.log(logging.INFO, f"is_iport={self.is_iport}")

        if not has_high_performance_mapping(self._current_working_directory, self.name):
            # Hide HPM options if we do not have HPM
            self.use_hpm_remap = False
            self._camera_options = FDS._disable_camera_option(
                self._camera_options, "enable_remapping", "HPM"
            )
        else:
            self.use_hpm_remap = True

        _has_bin = has_binning(self._current_working_directory, self.name)
        # If we do not have binning hide hardware and software binning option
        if not _has_bin:
            self._camera_options = FDS._disable_camera_option(
                self._camera_options, "Binning", "hardware_binning"
            )
            self._camera_options = FDS._disable_camera_option(
                self._camera_options, "Binning", "software_binning"
            )
        # bin2mode requires both binning and HPM to be enabled.
        if not (_has_bin and self.use_hpm_remap):
            self._camera_options = FDS._disable_camera_option(
                self._camera_options, "Binning", "bin2mode"
            )

        # If we do not have an intensifier we remove intensifier gain
        if not has_intensifier(self._current_working_directory, self.name):
            self._camera_options = FDS._disable_camera_option(
                self._camera_options, "Gains", "intensifier_gain"
            )

        # If we were unable to open a map file we remove all remapping
        if self.open_map() is not OptionSetterResult.COMPLETED:
            # without a map file cannot use HPM even if we have it
            self.use_hpm_remap = False
            self._camera_options = FDS._disable_camera_option(
                self._camera_options, "enable_remapping"
            )
            _logger.warning("Failed to open map file, remapping unavailable.")

        # Generate initial map if we have HPM available
        if (
            self.use_hpm_remap
            and self.generate_HPM_working_map() is not OptionSetterResult.COMPLETED
        ):
            _logger.error("Initial map generation failed.")

        self.rotate = has_rotate(self._current_working_directory, self.name)
        self.set_exposure(10, "Millisec")
        self.update_size()
        return True

    @log_this_function(_logger)
    def close(self) -> bool:
        """Close connection to FDS camera.

        This function should be called as the last action of the camera.

        Returns:
            boolean indicating if the closure was successful or not
        """
        res_close = self.dll.PSL_VHR_Close()
        res_unload = self.unload_cam_dll()
        self._is_closed = res_close and res_unload
        return self._is_closed

    def set_sub_area_and_binning(
        self, left: int, right: int, top: int, bottom: int, xbin: int, ybin: int
    ) -> OptionSetterResult:
        """Set both the sub area and the binning together in the driver.

        Args:
            left: left edge of the sub area rectangle
            right: right edge of the sub area rectangle
            top: top edge of the sub area rectangle
            bottom: bottom edge of the sub area rectangle
            xbin: binning level in x direction
            ybin: binning level in y direction
        Returns:
            success or failure
        """
        self.sub_area = (left, right, top, bottom)
        self.hardware_binning = (xbin, ybin)

        rep = self.dll.PSL_VHR_set_sub_area_coordinates(
            left, right, top, bottom, xbin, ybin
        )
        self.update_size()
        return _map_result_to_enum(rep)

    def set_sub_area(
        self, left: int, right: int, top: int, bottom: int
    ) -> OptionSetterResult:
        """Set the sub area in the driver. Binning used is whatever the camera
        instance currenly stores.

        Args:
            left: left edge of the sub area rectangle
            right: right edge of the sub area rectangle
            top: top edge of the sub area rectangle
            bottom: bottom edge of the sub area rectangle
        Returns:
            success or failure
        """
        self.sub_area = (left, right, top, bottom)
        xbin, ybin = self.hardware_binning

        rep = self.dll.PSL_VHR_set_sub_area_coordinates(
            left, right, top, bottom, xbin, ybin
        )

        self.update_size()

        changed = False
        if hasattr(self.dll, "PSL_VHR_get_actual_sub_area_coordinates"):
            l, r, t, b = ct.c_int(0), ct.c_int(0), ct.c_int(0), ct.c_int(0)
            self.dll.PSL_VHR_get_actual_sub_area_coordinates(
                ct.byref(l), ct.byref(r), ct.byref(t), ct.byref(b)
            )
            if self.sub_area != (l.value, r.value, t.value, b.value):
                changed = True
                _logger.info(
                    f"Driver modified sub area: {self.sub_area} =>"
                    f" {(l.value, r.value, t.value, b.value)}"
                )
                self.sub_area = l.value, r.value, t.value, b.value
        if rep:
            if changed:
                return OptionSetterResult.CHECK
            else:
                return OptionSetterResult.COMPLETED
        else:
            return OptionSetterResult.FAILED

    def get_sub_area(self) -> tuple[int, int, int, int]:
        """Return the current subarea set in the camera.

        Returns:
            current subarea (L, R, T, B)
        """
        return self.sub_area

    def set_hardware_binning(self, xbin: int, ybin: int) -> OptionSetterResult:
        """Set on chip hardware binning. Subarea used is whatever the camera instance
        currenly stores.

        Args:
            xbin: binning level in x direction
            ybin: binning level in y direction
        Returns:
            success or failure
        """
        self.hardware_binning = (xbin, ybin)
        left, right, top, bottom = self.sub_area

        rep = self.dll.PSL_VHR_set_sub_area_coordinates(
            left, right, top, bottom, xbin, ybin
        )
        self.update_size()
        return _map_result_to_enum(rep)

    def set_software_binning(self, xbin: int, ybin: int) -> OptionSetterResult:
        """Set software binning in the driver.

        This is performed once the image has been captures so is applied after any
        subarea or hardware binning.

        Args:
            xbin: binning level in x direction
            ybin: binning level in y direction
        Returns:
            success or failure
        """
        self.software_binning = (xbin, ybin)
        return OptionSetterResult.COMPLETED

    def set_exposure(self, expo: float, unit: str = "Second") -> OptionSetterResult:
        """Set the exposure time of the sensor.

        Suported units: ``"Millisec"`` and ``"Second"``

        Args:
             expo: exposure time to use, in given unit
             unit: time unit of the exposure value
        Returns:
            success or failure
        """
        if unit == "Millisec":
            return _map_result_to_enum(self.dll.PSL_VHR_set_exposure(int(expo)))
        elif unit == "Second":
            return _map_result_to_enum(self.dll.PSL_VHR_set_exposure(int(expo * 1000)))
        else:
            return OptionSetterResult.FAILED

    def set_trigger_mode(self, trigger_mode: str) -> OptionSetterResult:
        """Set camera trigger mode.

        Available options:
            * ``FreeRunning``
            * ``Software``
            * ``Hardware_Falling``
            * ``Hardware_Rising``
            * ``Pipeline_Master``
            * ``Pipeline_Slave``
            * ``Dual_Software``
            * ``Dual_Hardware``
            * ``Master_FreeRunning``
            * ``Master_Software``
            * ``Master_Falling``
            * ``Master_Rising``
            * ``High_Gate_Hardware``
            * ``Low_Gate_Hardware``
            * ``High_Gate_Soft``
            * ``Low_Gate_Soft``
            * ``Gen_Soft``
            * ``Gen_Rising``
            * ``Gen_Falling``

        Args:
            trigger_mode: trigger mode
        Returns:
            success or failure
        """
        mapping = {
            "FreeRunning": 0,
            "Software": 1,
            "Hardware_Falling": 2,
            "Hardware_Rising": 6,
            "Pipeline_Master": 16,
            "Pipeline_Slave": 18,
            "Dual_Software": 129,
            "Dual_Hardware": 130,
            "Master_FreeRunning": 64,
            "Master_Software": 65,
            "Master_Falling": 66,
            "Master_Rising": 70,
            "High_Gate_Hardware": 14,
            "Low_Gate_Hardware": 10,
            "High_Gate_Soft": 15,
            "Low_Gate_Soft": 11,
            "Gen_Soft": 257,
            "Gen_Rising": 258,
            "Gen_Falling": 262,
        }
        if trigger_mode in mapping:
            return _map_result_to_enum(
                self.dll.PSL_VHR_set_trigger_mode(mapping[trigger_mode])
            )
        else:
            _logger.log(
                logging.ERROR,
                f"{self.name} - set_trigger - Trigger mode not valid {trigger_mode}",
            )
            return OptionSetterResult.FAILED

    def set_intensifier_gain(self, gain: int) -> OptionSetterResult:
        """Set value for intensifier gain.

        Args:
            gain: value to set
        Returns:
            success or failure
        """
        return _map_result_to_enum(self.dll.PSL_VHR_set_intensifier_gain(gain))

    def set_video_gain(self, gain) -> OptionSetterResult:
        """Set value for video gain.

        Args:
            gain: value to set
        Returns:
            success or failure
        """
        return _map_result_to_enum(self.dll.PSL_VHR_set_video_gain(gain))

    def set_clock_speed(self, mode: str) -> OptionSetterResult:
        """set camera's clock speep.

        Available options:
            * ``15.5MHz``
            * ``25MHz``

        Args:
            mode: clock speed
        Returns:
            success or failure
        """
        if mode == "12.5MHz":
            return _map_result_to_enum(self.dll.PSL_VHR_set_speed(0))
        elif mode == "25MHz":
            return _map_result_to_enum(self.dll.PSL_VHR_set_speed(1))
        else:
            return OptionSetterResult.FAILED

    """Image Acquisition"""

    def snap(self) -> bool:
        """Acquire an image. This function will block for the duration of the exposure
        time.

        Type of acquisition performed depends on if the camera is
        fusion or not, and if it is, whether it is 14 bit. Regardles of this the image
        can be read out with :py:meth:`PSELPyFDS.FDS.get_image_pointer`,
        :py:meth:`PSELPyFDS.FDS.get_image` or :py:meth:`PSELPyFDS.FDS.get_raw_image`.

        .. note:: this function must be used when doing fusion acquisitions.

        Returns:
            acquisition success or failure
        """
        self.state = 1
        self.abort_flag = False
        if self.fusion:
            if self.is_14_bit_camera:
                self._fusion14bit_buff = (
                    self.dll.PSL_VHR_Fusion_snap_for_14_bit_cameras(
                        self._noise_reduction_factor
                    )
                )
                rep = True
            else:
                rep = self.dll.PSL_VHR_Fusion_snap(self._noise_reduction_factor)
        else:
            rep = self.dll.PSL_VHR_Snap_and_return()
            while not self.abort_flag:
                if self.dll.PSL_VHR_Get_snap_status():
                    break
                # time.sleep(0.000_002)

        self.state = 0
        return rep

    def snap_and_return(self) -> bool:
        """Acquire an image. This function will not block for the duration of an
        exposure.

        .. warning:: this function does not support fusion acquisitions.

        Returns:
            snap success or failure
        """
        self.abort_flag = False

        rep = self.dll.PSL_VHR_Snap_and_return()
        return rep

    def abort_snap(self) -> bool:
        """Abort the snap.

        This will end the wait loop if the image is acquiring.

        Returns:
            result of abort
        """
        self.abort_flag = True
        return self.dll.PSL_VHR_abort_snap()

    def get_status(self) -> bool:
        """Get the status of the current snap request. If ``True`` the image
        has finished acquiring and can now be read out using
        :py:meth:`PSELPyFDS.FDS.get_image_pointer`, :py:meth:`PSELPyFDS.FDS.get_image` or
        :py:meth:`PSELPyFDS.FDS.get_raw_image`..

        Returns:
            current snap status
        """
        return self.dll.PSL_VHR_Get_snap_status()

    def get_image_pointer(self) -> PointerType:
        """Return a pointer to the current image buffer. This function is used for both
        fusion and standard acquistioned images.

        To get the image as a processed numpy array pass the pointer to
        :py:meth:`PSELPyFDS.FDS.get_image`, or for a raw, unprocessed, image use
        :py:meth:`PSELPyFDS.FDS.get_raw_image`.

        Returns:
            image buffer with current image.
        """
        if self.fusion and self.is_14_bit_camera:
            return self._fusion14bit_buff
        else:
            image_pointer = self.dll.PSL_VHR_get_image_pointer()

            (Nx, Ny) = self.size
            ct.memmove(self.safe_buffer, image_pointer, Nx * Ny * self._byte_depth)
            return self.safe_buffer

    def get_image(
        self,
        image_pointer: Optional[PointerType] = None,
        tsize: Optional[tuple[int, int]] = None,
    ) -> tuple[tuple[int, int], np.ndarray]:
        """Return the image size and a numpy array of the image data.

        This function will apply post snap processing corrections (those that are
        enabled), remapping (if enabled), software binning (if set) and a 180 degree
        rotation (if enabled).

        Args:
            image_pointer: optional pointer to the image to process, if unspecified
                get_image_pointer is used to get the pointer
            tsize: optional size of image to use, if unspecified the current camera
                size is used.
        Returns:
            image size (x, y), image data
        """
        if tsize is None:
            (Nx, Ny) = self.size
        else:
            (Nx, Ny) = tsize

        if image_pointer is None:
            image_pointer = self.get_image_pointer()

        if not self.fusion:
            pp_res = self.dll.PSL_VHR_apply_post_snap_processing(image_pointer)
            if not pp_res:
                _logger.log(
                    logging.ERROR,
                    f"{__name__} - get_image - post snap processing failed",
                )

        # remapping must be performed before software binning
        if self.remapping:
            (Nx, Ny), image_pointer = self.remap(image_pointer, Nx, Ny)

        if self.software_binning != (1, 1):
            Nx, Ny = self.software_bin_image(image_pointer, Nx, Ny)

        data = image_pointer_to_numpy_array(
            image_pointer, (Nx, Ny), self.image_mode(), depth=self._byte_depth
        )
        if self.rotate:
            data = np.flipud(np.fliplr(data))  # TODO: Make this a rotate, faster?
        return (Nx, Ny), data

    def get_raw_image(
        self, image_pointer: Optional[PointerType] = None
    ) -> tuple[tuple[int, int], np.ndarray]:
        """Return the image size and a numpy array of the image data.

        This function will not apply any corrections or other operations on the image.

        Args:
            image_pointer: optional pointer to the image to process, if unspecified
                get_image_pointer is used to get the pointer
        Returns:
            image size, image data

        """
        if image_pointer is None:
            image_pointer = self.get_image_pointer()

        data = image_pointer_to_numpy_array(
            image_pointer, self.size, self.image_mode(), depth=self._byte_depth
        )
        return self.size, data

    def enable_streaming(self, enable: bool) -> OptionSetterResult:
        """Enable the cameras image streaming mode.

        This should ONLY be switched on with caution on versions of the camera dll
        built with PLEORA'S VISION SDK.
        This should ALWAYS be switched on for versions of the camera dll built with
        PLEORA'S EBUS SDK (GEV).

        Args:
            enable or disable image streaming
        Returns:
            True
        """
        self.dll.PSL_VHR_enable_image_streaming(enable)
        return OptionSetterResult.COMPLETED

    def allocate_sequence_buffer(self, image_count: int) -> bool:
        """Allocate a sequence buffer of ``image_count`` images to use when acquiring
        an image sequence.

        Returns:
            success or failure
        """
        Nx, Ny = self.size

        self.safe_sequence = []

        buffer_size = Nx * Ny * self._byte_depth
        for i in range(image_count):
            buffer = ct.c_ushort * buffer_size
            self.safe_sequence.append(buffer())

        self.safe_sequence_idx = 0
        self.safe_sequence_id_max = image_count
        self.safe_sequence_buffer_size = buffer_size
        return True

    def transfer_image_pointer(self) -> ct.Array[ct.c_ushort]:
        """Copy image data into previously allocated sequence buffer.

        Returns:
            ct.Array containing image data.

        Raises:
             BufferError: If the image buffer has been exhausted
        """
        if self.safe_sequence_idx >= self.safe_sequence_id_max:
            raise BufferError("Safe sequence buffer exhausted")

        # Get pointer to acquired image
        image_pointer = self.dll.PSL_VHR_get_image_pointer()

        # get pointer to next available buffer in sequence buffer
        safe = self.safe_sequence[self.safe_sequence_idx]

        # move data into buffer
        ct.memmove(safe, image_pointer, self.safe_sequence_buffer_size)
        self.safe_sequence_idx += 1

        return safe

    def free_sequence_buffer(self) -> bool:
        """Clean up and free image sequence buffer.

        Returns:
            success or failure
        """
        # print("Free sequence buffer")
        self.safe_sequence = []
        self.safe_sequence_idx = -1
        self.safe_sequence_id_max = -1
        self.safe_sequence_buffer_size = -1
        return True

    """Camera correction functions"""

    def software_bin_image(
        self, image_pointer: PointerType, Nx: int, Ny: int
    ) -> tuple[int, int]:
        """Apply software binning to image referenced by ``image_pointer`` with size
        ``(Nx, Ny)``. Binned image remains in original pointer location.

        Args:
            image_pointer: pointer to image to software bin
            Nx: width of input image
            Ny: height of input image

        Returns:
            size of binned image (width, height)
        """
        newX = ct.c_int(Nx)
        newY = ct.c_int(Ny)

        xbin, ybin = self.software_binning

        self.dll.PSL_VHR_software_bin_image(
            image_pointer, ct.byref(newX), ct.byref(newY), xbin, ybin
        )

        return newX.value, newY.value

    def enable_offset_subtraction(self, enable: bool) -> OptionSetterResult:
        """Enable offset correction.

        Args:
            enable: Enable/ disable offset correction
        Returns:
            instance of OptionSetterResult indicating success status
        """
        return _map_result_to_enum(self.dll.PSL_VHR_enable_offset_subtraction(enable))

    def enable_bright_pixel_correction(self, enable: bool) -> OptionSetterResult:
        """Enable bright pixel correction.

        Args:
            enable: Enable/ disable bright pixel correction
        Returns:
            instance of OptionSetterResult indicating success status
        """
        return _map_result_to_enum(
            self.dll.PSL_VHR_enable_bright_pixel_correction(enable)
        )

    def enable_bright_corner_correction(self, enable: bool) -> OptionSetterResult:
        """Enable bright corner correction.

        Args:
            enable: Enable/ disable bright corner correction
        Returns:
            instance of OptionSetterResult indicating success status
        """
        return _map_result_to_enum(
            self.dll.PSL_VHR_enable_bright_corner_subtraction(enable)
        )

    def enable_bright_spot_correction(self, enable: bool) -> OptionSetterResult:
        """Enable bright spot correction.

        Args:
            enable: Enable/ disable bright spot correction
        Returns:
            instance of OptionSetterResult indicating success status
        """
        self.dll.PSL_VHR_enable_spotred(enable)
        return OptionSetterResult.COMPLETED

    def enable_flat_field_correction(self, enable: bool) -> OptionSetterResult:
        """Enable flat field correction.

        Args:
            enable: Enable/ disable flat field correction
        Returns:
            instance of OptionSetterResult indicating success status
        """
        return _map_result_to_enum(
            self.dll.PSL_VHR_enable_flat_field_correction(enable)
        )

    def enable_sharpening(self, enable: bool) -> OptionSetterResult:
        """Enable sharpening.

        Args:
            enable: Enable/ disable sharpening
        Returns:
            instance of OptionSetterResult indicating success status
        """
        self.dll.PSL_VHR_enable_sharpening(enable)
        return OptionSetterResult.COMPLETED

    """Remapping"""

    def open_map(self, file_name: str = "distortion.map") -> OptionSetterResult:
        """Open the map file.

        The map file must be in the camera folder

        Args:
            file_name: name of map file
        Returns:
            Success or failure
        """
        return _map_result_to_enum(self.dll.PSL_VHR_open_map(bytes(file_name, "utf-8")))

    def remap(
        self, image_pointer: PointerType, Nx: int, Ny: int
    ) -> tuple[tuple[int, int], PointerType]:
        """Perform remapping on an image provided in the pointer.

        Supports High Performance remapping, remapping 14-bit fusion images and
        standard remapping. Which is used is determied by camera properties and user
        settings.

        Args:
            image_pointer: the image pointer
            Nx: image width
            Ny: image height

        Returns:
            Tuple of image size and image pointer
        """
        if self.use_hpm_remap:
            w, h = self.get_HPM_remap_size()
            imp = self.high_precision_remap(image_pointer)
            return (w, h), imp
        elif self.is_14_bit_camera and self.fusion:
            newX = ct.c_int(Nx)
            newY = ct.c_int(Ny)
            imp = self.dll.PSL_VHR_remap_14bit_fusion_image(
                image_pointer, ct.byref(newX), ct.byref(newY), self._smooth, self._clip
            )
            return (newX.value, newY.value), imp
        else:
            newX = ct.c_int(Nx)
            newY = ct.c_int(Ny)
            imp = self.dll.PSL_VHR_remap_image(
                image_pointer, ct.byref(newX), ct.byref(newY), self._smooth, self._clip
            )
            return (newX.value, newY.value), imp

    def set_remap_parameters(self) -> OptionSetterResult:
        """Set remap parameters in driver.

        .. important:: Remap parameters are NOT written to the
            driver until this function is called.

        Function sets the following remap parameters: ``HPM_x``, ``HPM_y``,
        ``HPM_rotation``, ``HPM_sub_width``, ``HPM_sub_height``, ``HPM_angular``.

        .. warning:: This function should not generally be called directly as it is
            called in :py:meth:`PSELPyFDS.FDS.generate_working_map`.

        Returns:
            instance of OptionSetterResult indicating success status
        """
        # If we do not have HPM-ing we cannot set the parameters
        if not self.use_hpm_remap:
            return OptionSetterResult.FAILED
        self.dll.PSL_VHR_configure_high_precision_mapping(
            self._remap_x,
            self._remap_y,
            self._remap_rotation,
            self._remap_sub_width,
            self._remap_sub_height,
            self._remap_angular,
        )
        return OptionSetterResult.COMPLETED

    def set_HPM_x(self, value: int) -> OptionSetterResult:
        """Set High Performance Mapping x parameter.

        .. note:: To use the High Performance Mapping functions a map file should
            already have been loaded.

        Returns:
            instance of OptionSetterResult indicating success status
        """
        # If we do not have HPM-ing we cannot set the parameters
        if not self.use_hpm_remap:
            return OptionSetterResult.FAILED

        self._remap_x = int(value)
        return self.generate_HPM_working_map()

    def set_HPM_y(self, value: int) -> OptionSetterResult:
        """Set High Performance Mapping y parameter.

        .. note:: To use the High Performance Mapping functions a map file should
            already have been loaded.

        Returns:
            instance of OptionSetterResult indicating success status
        """
        # If we do not have HPM-ing we cannot set the parameters
        if not self.use_hpm_remap:
            return OptionSetterResult.FAILED

        self._remap_y = int(value)
        return self.generate_HPM_working_map()

    def set_HPM_rotation(self, value: int) -> OptionSetterResult:
        """Set High Performance Mapping rotation parameter.

        .. note:: To use the High Performance Mapping functions a map file should
            already have been loaded.

        Returns:
            instance of OptionSetterResult indicating success status
        """
        # If we do not have HPM-ing we cannot set the parameters
        if not self.use_hpm_remap:
            return OptionSetterResult.FAILED

        self._remap_rotation = int(value)
        return self.generate_HPM_working_map()

    def set_HPM_sub_width(self, value: int) -> OptionSetterResult:
        """Set High Performance Mapping sub width parameter.

        .. note:: To use the High Performance Mapping functions a map file should
            already have been loaded.

        Returns:
            instance of OptionSetterResult indicating success status
        """
        # If we do not have HPM-ing we cannot set the parameters
        if not self.use_hpm_remap:
            return OptionSetterResult.FAILED

        self._remap_sub_width = int(value)
        return self.generate_HPM_working_map()

    def set_HPM_sub_height(self, value: int) -> OptionSetterResult:
        """Set High Performance Mapping sub height parameter.

        .. note:: To use the High Performance Mapping functions a map file should
            already have been loaded.

        Returns:
            instance of OptionSetterResult indicating success status
        """
        # If we do not have HPM-ing we cannot set the parameters
        if not self.use_hpm_remap:
            return OptionSetterResult.FAILED

        self._remap_sub_height = int(value)
        return self.generate_HPM_working_map()

    def set_HPM_angular(self, enable: bool) -> OptionSetterResult:
        """Set High Performance Mapping angular parameter.

        .. note:: To use the High Performance Mapping functions a map file should
            already have been loaded.

        Returns:
            instance of OptionSetterResult indicating success status
        """
        # If we do not have HPM-ing we cannot set the parameters
        if not self.use_hpm_remap:
            return OptionSetterResult.FAILED

        self._remap_angular = bool(enable)
        return self.generate_HPM_working_map()

    def generate_HPM_working_map(self) -> OptionSetterResult:
        """Generate High Precision Mapping working map.

        Sets all remap parameters and generates new working map based on those values.

        Returns:
            instance of OptionSetterResult indicating success status
        """
        # If we do not have HPM-ing we cannot set the parameters
        if not self.use_hpm_remap:
            _logger.error("generate_working_map: HPM unavailable")
            return OptionSetterResult.FAILED

        # set remap parameters to values currently stored in camera
        if self.set_remap_parameters() is not OptionSetterResult.COMPLETED:
            _logger.error("generate_working_map: unable to set remap parameters")
            return OptionSetterResult.FAILED

        # Generate the HMP map
        res = self.dll.PSL_VHR_generate_high_precision_working_map()
        if not res:
            _logger.error(
                "generate_working_map: Failed"
                " PSL_VHR_generate_high_precision_working_map"
            )
            return OptionSetterResult.FAILED

        return _map_result_to_enum(res)

    def get_HPM_remap_size(self) -> tuple[int, int]:
        """Get the dimentions of the dimensions of the image after high performance
        remapping has been performed.

        Returns:
            remapped image width, remapped image height
        """
        w = ct.c_int(0)
        h = ct.c_int(0)
        self.dll.PSL_VHR_get_high_precision_remapped_image_dimensions(
            ct.byref(w), ct.byref(h)
        )
        return w.value, h.value

    def high_precision_remap(self, image_pointer: PointerType) -> PointerType:
        """Perform high precision remmapping on the image.

        Returns:
            Pointer to remppaed image
        """
        return self.dll.PSL_VHR_perform_high_precision_remap(
            image_pointer, self._smooth
        )

    def enable_smooth(self, enable: bool) -> OptionSetterResult:
        """Enable/ disable image smoothing during remapping.

        Args:
            enable: Enable/ disable image smoothing
        Returns:
            True
        """
        self._smooth = enable
        return OptionSetterResult.COMPLETED

    def enable_clip(self, enable: bool) -> OptionSetterResult:
        """Enable clip.

        Args:
            enable: Enable/ disable clip
        Returns:
            instance of OptionSetterResult indicating success status
        """
        self._clip = enable
        return OptionSetterResult.COMPLETED

    def enable_remapping(self, enable: bool) -> OptionSetterResult:
        """Enable remapping.

        Args:
            enable: Enable/ disable remapping
        Returns:
            instance of OptionSetterResult indicating success status
        """
        self.remapping = enable
        return OptionSetterResult.COMPLETED
