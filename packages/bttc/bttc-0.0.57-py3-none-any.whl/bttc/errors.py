"""BTTC related errors."""


class Error(Exception):
  """A base class for errors related to BTTC."""


class AdbExecutionError(Error):
  """Failed in adb execution."""

  def __init__(
      self, return_code: int, error_msg: str, guiding_msg: str | None = None):
    guiding_msg = f'>>> {guiding_msg} <<<\n' if guiding_msg else ''
    message = f'''{guiding_msg}
    Failed in adb execution with return code={return_code}:
    {error_msg}'''
    super().__init__(message)


class AdbUnknownOutputError(Error):
  """Failed in searching/parsing adb output."""

  def __init__(self, output: str):
    super().__init__(
        f'Adb with unexpected output: {output}')


class UnknownWiFiStatusError(Error):
  """Unknown WiFi status error."""

  def __init__(self, adb_output: str):
    super().__init__(
        f'Unknown WiFi status from adb output={adb_output}')
