"""
(c) ZL-2020.
@author ZhaoLei
@since 2020.10.29 19:55
"""
import os
import sys
import glob
import shutil
from setuptools import find_packages, setup, Command

try:
    import torch
    from torch.utils.cpp_extension import BuildExtension, CUDAExtension, CppExtension
except ModuleNotFoundError:
    from Cython.Distutils import build_ext as BuildExtension
    print('Skip building ext ops due to the absence of torch.')
    os.environ['AIEI'] = '1'


def ext_FAIR():
    EXT_DIR = './aiei/ops/FAIR'
    if not os.path.exists(f'{EXT_DIR}/detectron2'):
        os.makedirs(f'{EXT_DIR}/detectron2')
    sources = [f'{EXT_DIR}/vision.cpp'] + glob.glob(f'{EXT_DIR}/**/*.cpp')  # *.h need be included in MANIFEST.in
    source_cuda = glob.glob(f'{EXT_DIR}/**/*.cu') + glob.glob(f'{EXT_DIR}/*.cu')
    extension = CppExtension
    extra_compile_args = {"cxx": []}
    define_macros = []

    if torch.cuda.is_available() or os.getenv('FORCE_CUDA', '0') == '1':
        extension = CUDAExtension
        sources += source_cuda
        define_macros += [('WITH_CUDA', None)]
        extra_compile_args["nvcc"] = [
            "-DCUDA_HAS_FP16=1",
            "-D__CUDA_NO_HALF_OPERATORS__",
            "-D__CUDA_NO_HALF_CONVERSIONS__",
            "-D__CUDA_NO_HALF2_OPERATORS__",
        ]
        # It's better if pytorch can do this by default.
        CC = os.environ.get('CC', None)
        if CC is not None:
            extra_compile_args['nvcc'].append(f'-ccbin={CC}')
    else:
        extension = CppExtension
        raise NotImplementedError('FAIR CppExtension is not implemented.')
    ext_ops = extension(
        "aiei.ops.FAIR.detectron2._C",  # detectron2/_C.cpython-36m-x86_64-linux-gnu.so
        sources,
        include_dirs=[EXT_DIR],
        define_macros=define_macros,
        extra_compile_args=extra_compile_args,
    )
    return ext_ops


def ext_dcnv2():
    ext_ops = [
        CUDAExtension('aiei.ops.dcnv2.deform_conv_cuda', [
            './aiei/ops/dcnv2/src/deform_conv_cuda.cpp',
            './aiei/ops/dcnv2/src/deform_conv_cuda_kernel.cu',
        ]),
        CUDAExtension('aiei.ops.dcnv2.deform_pool_cuda', [
            './aiei/ops/dcnv2/src/deform_pool_cuda.cpp',
            './aiei/ops/dcnv2/src/deform_pool_cuda_kernel.cu',
        ]),
    ]
    return ext_ops


def ext_nms():
    def make_cuda_ext(name, sources):
        define_macros = []
        if torch.cuda.is_available() or os.getenv('FORCE_CUDA', '0') == '1':
            define_macros += [('WITH_CUDA', None)]
        else:
            raise EnvironmentError('CUDA is required')
        extra_compile_args = {
            'cxx': [], 'nvcc': [
                '-D__CUDA_NO_HALF_OPERATORS__',
                '-D__CUDA_NO_HALF_CONVERSIONS__',
                '-D__CUDA_NO_HALF2_OPERATORS__',
            ]
        }
        return CUDAExtension(name=name, sources=sources, define_macros=define_macros, extra_compile_args=extra_compile_args)

    ext_ops = [
        make_cuda_ext(name='aiei.ops.nms.nms_cpu', sources=['./aiei/ops/nms/src/nms_cpu.cpp']),
        make_cuda_ext(name='aiei.ops.nms.nms_cuda',
        sources=['./aiei/ops/nms/src/nms_cuda.cpp', './aiei/ops/nms/src/nms_kernel.cu']),
    ]
    return ext_ops


def get_extensions():
    extensions = []
    # 'AIEI=0 pip install -v -e .' will build_ext
    if os.getenv('AIEI', '1') == '0':
        # prevent ninja from using too many resources
        os.environ.setdefault('MAX_JOBS', '4')
        extensions.append(ext_FAIR())
        extensions.extend(ext_dcnv2())
        extensions.extend(ext_nms())
    return extensions


def load_requirements(file_name='requirements.txt'):
    with open(f'./requirements/{file_name}', 'r') as file:
        lines = [ln.strip() for ln in file.readlines()]
    reqs = []
    for ln in lines:
        if '#' in ln:  # filer all comments
            ln = ln[:ln.index('#')].strip()
        if ln.startswith('http'):  # skip directly installed dependencies
            continue
        if ln:  # if requirement is not empty
            reqs.append(ln)
    return reqs


def get_info():
    version_file = './aiei/info.py'
    with open(version_file, 'r', encoding='utf-8') as f:
        exec(compile(f.read(), version_file, 'exec'))
    return locals()['INFO']


class UploadCommand(Command):
    user_options = []

    @staticmethod
    def zprint(s):
        print(f'\033[1m{s}\033[0m')  # Prints things in bold.

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        if os.path.exists('./dist'):
            self.zprint('Removing previous builds…')
            shutil.rmtree('./dist')
        self.zprint('Building Source and Wheel (universal) distribution…')
        # os.system(f'{sys.executable} setup.py sdist bdist_wheel --universal')
        os.system(f'{sys.executable} setup.py sdist')  # bdist_wheel -> *.whl
        self.zprint('Uploading the package to PyPI via Twine…')
        os.system('twine upload dist/*')
        sys.exit()


# https://blog.csdn.net/chenfeidi1/article/details/80873979
# python setup.py upload
setup(
    **get_info(),
    zip_safe=False,
    packages=find_packages(exclude=["tests", 'tests/*', 'benchmarks']),
    install_requires=load_requirements(),
    # 'pip install aiei[dev]' or 'pip install -v -e .[dev]' (\[dev\] in zsh)
    extras_require={'dev': load_requirements('develop.txt')},
    ext_modules=get_extensions(),
    cmdclass={'build_ext': BuildExtension, 'upload': UploadCommand},
    classifiers=[
        # Full list: https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ],
    # include_package_data=True,
    scripts=['tools/aiei']
)
