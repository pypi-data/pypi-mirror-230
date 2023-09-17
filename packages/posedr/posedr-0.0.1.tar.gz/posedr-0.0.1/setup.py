from setuptools import setup
import setuptools


with open("README.md","r") as fh:
    long_description = fh.read()

setup(
    name='posedr',
    version='0.0.1',
    description='Pose Detection By mediapipe and cv2',
    author='Karthikeyan',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(),
    keywords=['Human pose estimation','Body tracking','Image processing'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    py_modules=['posedr'],
    package_dir={'':'src'},
    install_requires=[
        'opencv-python',
        'mediapipe'
    ]
    # entry_points={
    #     'console_scripts': [
    #         'pose_detection=pose_detection.__main__:run_pose_detection'
    #     ]
    # },
)

