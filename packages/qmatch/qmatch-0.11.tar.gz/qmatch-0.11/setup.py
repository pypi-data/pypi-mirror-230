import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='qmatch',
    version='0.11',
    author='Dr Jie Zheng',
    author_email='jiezheng@nao.cas.cn',
    description='Some astronomical matching functions.', # short description
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitee.com/drjiezheng/qmatch',
    packages=['qmatch'],
    license='MIT',
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Science/Research",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python :: 3.7",
                 "Topic :: Scientific/Engineering :: Physics",
                 "Topic :: Scientific/Engineering :: Astronomy"],
    requires=['numpy', 'scipy', ]
)
