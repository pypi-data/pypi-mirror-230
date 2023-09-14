# Copy from https://github.com/open-mmlab/mmdetection/
# Modified by Lei Zhao

import os
import torch
from setuptools import setup
from torch.utils.cpp_extension import BuildExtension, CUDAExtension


def make_cuda_ext(name, sources):
    define_macros = []

    if torch.cuda.is_available() or os.getenv('FORCE_CUDA', '0') == '1':
        define_macros += [('WITH_CUDA', None)]
    else:
        raise EnvironmentError('CUDA is required to compile MMDetection!')

    return CUDAExtension(
        name=name,
        sources=sources,
        define_macros=define_macros,
        extra_compile_args={
            'cxx': [],
            'nvcc': [
                '-D__CUDA_NO_HALF_OPERATORS__',
                '-D__CUDA_NO_HALF_CONVERSIONS__',
                '-D__CUDA_NO_HALF2_OPERATORS__',
            ]
        })


setup(
    name='nms',
    ext_modules=[
        make_cuda_ext(
            name='nms_cpu',
            sources=['src/nms_cpu.cpp']),
        make_cuda_ext(
            name='nms_cuda',
            sources=['src/nms_cuda.cpp', 'src/nms_kernel.cu']),
    ],
    cmdclass={'build_ext': BuildExtension}
)
