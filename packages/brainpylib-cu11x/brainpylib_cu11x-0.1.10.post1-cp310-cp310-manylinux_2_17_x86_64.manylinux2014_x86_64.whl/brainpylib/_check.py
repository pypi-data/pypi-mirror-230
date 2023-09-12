# -*- coding: utf-8 -*-


jaxlib_minimal_version = '0.4.1'

brainpy_minimal_version = '2.4.4.post3'


jax_install_msg = '''

1. If you are using Windows with Python=3.8, install jaxlib through

   >>> pip install jaxlib -f https://whls.blob.core.windows.net/unstable/index.html

2. If you are using Windows (with Python>3.8), macOS, or Linux platform, install jaxlib through

   >>> pip install jaxlib

3. If you are using Linux + CUDA platform, install jaxlib through

   >>> pip install jaxlib -f https://storage.googleapis.com/jax-releases/jax_cuda_releases.html

Note that the versions of "jax" and "jaxlib" should be consistent, like "jax=0.3.14" and "jaxlib=0.3.14".  

For more detail installation instructions, please see https://brainpy.readthedocs.io/en/latest/quickstart/installation.html#dependency-2-jax 

'''

try:
    import jaxlib
    if jaxlib.__version__ < jaxlib_minimal_version:
        raise RuntimeError(f'brainpylib needs jaxlib >= {jaxlib_minimal_version}, please upgrade it. '
                           + jax_install_msg)
except (ModuleNotFoundError, ImportError):
    raise ModuleNotFoundError(f'brainpylib needs jaxlib >= {jaxlib_minimal_version}, please install it. '
                              + jax_install_msg)

try:
    import brainpy as bp
    if bp.__version__ < brainpy_minimal_version:
        raise RuntimeError(f'brainpylib needs brainpy >= {brainpy_minimal_version}, please upgrade it. ')
except ModuleNotFoundError as e:
    pass






