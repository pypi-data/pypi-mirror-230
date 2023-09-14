# -*- coding: utf-8 -*-

name = 'brainpylib-cu11x'

all_names = [
  'brainpylib',
  'brainpylib-cu11x',
  'brainpylib-cu12x',
]

all_names.remove(name)

try:
  # require users to uninstall previous brainpylib releases.
  import pkg_resources

  installed_packages = pkg_resources.working_set
  for i in installed_packages:
    if i.key in all_names:
      raise SystemError('Please uninstall the existing version of brainpylib '
                        f'package "{i.key}={i.version}" '
                        f'(located in {i.location}) first. \n'
                        'Because brainpylib, brainpylib-cu11x and brainpylib-cu12x are not compatible, '
                        'if you have multiple versions of brainpylib installed, '
                        'please uninstall all of them and reinstall the one you need. \n'
                        f'>>> pip uninstall {i.key}')
except ModuleNotFoundError:
  pass

__version__ = "0.1.10.post2"


# IMPORTANT, must import first
from . import _register_custom_calls, _check

del _check, _register_custom_calls
