"""General utilities used in Phone testing."""
import logging
import os
import re
from functools import partial

from bttc import bt_utils
from bttc.utils import key_events_handler
from bttc.utils import typing_utils
from mobly.controllers import android_device
from mobly.controllers.android_device_lib import adb
from mobly.controllers.android_device_lib.services import sl4a_service

import shlex
from typing import TypeAlias, Union


BINDING_KEYWORD = 'gm'
ANDROID_DEVICE: TypeAlias = android_device.AndroidDevice


class GModule:
  """General module to hold extended functions define in this module."""

  def __init__(self, ad: ANDROID_DEVICE):
    self._ad: ANDROID_DEVICE = ad
    self.dumpsys = partial(dumpsys, self._ad)
    self.get_call_state = partial(get_call_state, self._ad)
    self.push_file = partial(push_file, self._ad)
    self.shell = bt_utils.safe_adb_shell(ad)

  @property
  def call_state(self) -> str:
    return self.get_call_state()

  @property
  def sim_operator(self):
    return get_sim_operator(self._ad)


def bind(
    ad: Union[ANDROID_DEVICE, str],
    init_mbs: bool = False, init_sl4a: bool = False) -> ANDROID_DEVICE:
  """Binds the input device with functions defined in current module.

  Sample Usage:
  ```python
  >>> from bttc import general_utils
  >>> ad = general_utils.bind('07311JECB08252', init_mbs=True, init_sl4a=True)
  >>> ad.gm.sim_operator
  'Chunghwa Telecom'
  >>> ad.gm.call_state
  'IDLE'
  ```
  """
  device = None
  if isinstance(ad, str):
    device = android_device.create([{'serial': ad}])[0]
  else:
    device = ad

  setattr(device, BINDING_KEYWORD, GModule(device))
  device.ke = key_events_handler.KeyEventHandler(device)

  if init_mbs:
    device.load_snippet(
        'mbs',
        'com.google.android.mobly.snippet.bundled')

  if init_sl4a and not device.services.has_service_by_name('sl4a'):
    device.services.register('sl4a', sl4a_service.Sl4aService)

  return device


def get_call_state(device: typing_utils.AdbDevice) -> str:
  """Gets call state from dumpsys telecom log.

  For this function to work, we expect below log snippet from given log content:

  Call state is IDLE:
  ```
  mCallAudioManager:
    All calls:
    Active dialing, or connecting calls:
    Ringing calls:
    Holding calls:
    Foreground call:
    null
  ```

  Call state is ACTIVE if there is a single call:
  ```
  mCallAudioManager:
    All calls:
      TC@1
    Active dialing, or connecting calls:
      TC@1
    Ringing calls:
    Holding calls:
    Foreground call:
    [Call id=TC@1, state=ACTIVE, ...
  ```

  Call state is RINGING if there is two calls:
  ```
  mCallAudioManager:
    All calls:
      TC@1
      TC@2
    Active dialing, or connecting calls:
      TC@1
    Ringing calls:
      TC@2
    Holding calls:
    Foreground call:
    [Call id=TC@1, state=ACTIVE, ...
  ```

  Args:
    device: Adb like device.

  Returns:
    Call state of the device.

  Raises:
    adb.Error: If the output of adb commout is not expected.
  """
  output = dumpsys(device, 'telecom', 'mCallAudioManager', '-A11')
  pattern = r'(Ringing) calls:\n\s+TC@\d|Call id=.+state=(\w+)|null'
  match = re.search(pattern, output)
  if match is None:
    raise adb.Error('Failed to execute command for dumpsys telecom')

  return (match.group(1) or match.group(2) or 'IDLE').upper()


def get_sim_operator(ad: ANDROID_DEVICE) -> str:
  """Gets SIM operator.

  Args:
    ad: Android phone device object.

  Returns:
    SIM Operator or empty string if no SIM card.
  """
  return ad.adb.getprop('gsm.operator.alpha').split(',')[0]


def dumpsys(ad: typing_utils.AdbDevice,
            service: str,
            keyword: str,
            grep_argument: str = '') -> str:
  """Searches dumpsys log by grep argument and keyword.

  Args:
    ad: Adb like object.
    service: Service name such as "bluetooth_manager".
    keyword: Keyword for search.
    grep_argument: Grep argument for search.

  Returns:
    String of dumpsys that contain keyword.

  Raises:
    UnicodeDecodeError: Fails to conduct the default decoding.
  """
  return ad.adb.shell(
      shlex.split('dumpsys {} | grep {} "{}"'.format(
          shlex.quote(service), grep_argument, shlex.quote(keyword)))).decode()


def push_file(
    ad: typing_utils.AdbDevice, src_file_path: str, dst_file_path: str,
    push_timeout_sec: int = 300,
    overwrite_existing: bool = True) -> bool:
  """Pushes file from host file system into given phone.

  Args:
    ad: Adb like object.
    src_file_path: Source file path from host.
    dst_file_path: Destination file path in Phone `ad`.
    push_timeout_sec: How long to wait for the push to finish in seconds.
    overwrite_existing: True to allow overwriting; False to skip push if
        the destination file exist.

  Returns:
    True iff file is pushed successfully.
  """
  src_file_path = os.path.expanduser(src_file_path)

  if not os.path.isfile(src_file_path):
    logging.warning('Source file %s does not exist!', src_file_path)
    return False

  if not overwrite_existing and ad.adb.path_exists(dst_file_path):
    logging.debug(
        "Skip pushing {} to {} as it already exists on device".format(
            src_file_path, dst_file_path))
    return True

  out = ad.adb.push(
      [src_file_path, dst_file_path],
      timeout=push_timeout_sec).decode().rstrip()
  if 'error' in out:
    logging.warning(
        'Failed to copy %s to %s: %s', src_file_path, dst_file_path, out)
    return False

  return True
