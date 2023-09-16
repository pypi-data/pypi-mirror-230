import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='pltgui',
    version='0.2',
    author='Dr Jie Zheng',
    author_email='jiezheng@nao.cas.cn',
    description='A GUI with matplotlib, can use on all OS.', # short description
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitee.com/drjiezheng/pltgui',
    packages=['pltgui'],
    license='MIT',
    classifiers=["Development Status :: 5 - Production/Stable",
                 "Intended Audience :: Science/Research",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent",
                 "Programming Language :: Python :: 3.7",
                 "Topic :: Scientific/Engineering :: Physics",
                 "Topic :: Scientific/Engineering :: Astronomy"],
    requires=['numpy', 'matplotlib', ]
)
