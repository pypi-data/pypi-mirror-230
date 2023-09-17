from setuptools import setup, find_packages

setup(
    name='imgbox',
    version='0.3',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'pillow',
    ],
    package_data={
        'imgbox': ['font/*'],
    },
    # other metadata
    author='xxai.art',
    author_email='xxai.art@gmail.com',
    description='用 pillow 画目标检测的框，支持中文（自带字体）',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    url='https://github.com/aier-art/imgbox',
)
