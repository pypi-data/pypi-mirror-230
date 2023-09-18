from setuptools import setup
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='video_images_creator',
    version='0.1.46',
    description= "Create videos from images using the 'video_images_creator' package.",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='',
    author='Nikhil Sharma',
    author_email='nikhilsharma972@gmail.com',
    license='BSD 2-clause',
    packages=['video_images_creator'],
    package_dir={"": "src"},
    package_data={"video_images_creator": ["*.ttf", "video-music.wav",'*.jpg','*.jpeg','*.png']},
    install_requires=['opencv-python', 'numpy', 'pillow'],
    classifiers=[
        'Development Status :: 1 - Planning',
    ],
)


