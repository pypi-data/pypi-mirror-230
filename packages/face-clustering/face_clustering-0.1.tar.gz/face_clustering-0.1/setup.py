from setuptools import setup, find_packages

setup(
    name='face_clustering',
    version='0.1',
    author='Aryan Sharma',
    author_email='aryansharma2909@gmail.com',
    description='The pipeline uses state-of-the-art computer vision techniques, including face detection, feature extraction, and clustering algorithms. The face detection module can detect faces under different lighting conditions and poses, while the feature extraction module extracts high-dimensional feature vectors that capture the unique characteristics of each face.',
    packages=find_packages(),
    install_requires=[
        'opencv-python',        # OpenCV
        'dlib',                 # dlib face detection
        'pandas',               # Data manipulation
        'scikit-learn',         # Machine learning tools
        'tqdm',                 # Progress bar
        'face-recognition',     # Face recognition
    ],
)
