import logging
import os
from importlib.metadata import version, PackageNotFoundError
from pathlib import Path

import glog
import tomlkit

try:
  __version__ = version('ascend-io-cli')
except PackageNotFoundError:
  try:
    with open(os.path.join(Path(__file__).parent.parent, 'pyproject.toml')) as pyproject:
      file_contents = pyproject.read()
      __version__ = tomlkit.parse(file_contents)['tool']['poetry']['version']
  except:
    __version__ = 'unknown version'

# align log levels to warn
glog.setLevel(logging.WARN)
logging.getLogger().setLevel(logging.WARN)