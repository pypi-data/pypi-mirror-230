# -*- coding: utf-8 -*-


import jax

__all__ = [
  'transform_brainpy_array',
  'import_gpu_ops',
]


try:
  from brainpylib import gpu_ops
except ImportError:
  gpu_ops = None


def transform_brainpy_array(array):
  if hasattr(array, 'is_brainpy_array'):
    if array.is_brainpy_array:
      return array.value
  return array


def import_gpu_ops(err=None):
  if err is not None:
    if gpu_ops is None:
      raise err
  return gpu_ops

