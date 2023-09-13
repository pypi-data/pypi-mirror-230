"""Defines a utility class for automatically detecting the device to use.

This function just goes through a list of devices in order of priority and
finds whichever one is available. To disable some device, you can set the
associated environment variable, for example:

.. code-block:: bash

    export DISABLE_METAL=1
    export DISABLE_GPU=1
"""

import logging

from ml.utils.device.base import base_device
from ml.utils.device.cpu import cpu_device
from ml.utils.device.gpu import gpu_device
from ml.utils.device.metal import metal_device
from ml.utils.logging import DEBUGALL

logger: logging.Logger = logging.getLogger(__name__)

# These devices are ordered by priority, so an earlier device in the list
# is preferred to a later device in the list.
ALL_DEVICES: list[type[base_device]] = [
    metal_device,
    gpu_device,
    cpu_device,
]


def detect_device() -> base_device:
    for device_type in ALL_DEVICES:
        if device_type.has_device():
            device = device_type()
            logger.log(DEBUGALL, "Device: [%s]", device._get_device())
            return device
    raise RuntimeError("Could not automatically detect the device to use")
