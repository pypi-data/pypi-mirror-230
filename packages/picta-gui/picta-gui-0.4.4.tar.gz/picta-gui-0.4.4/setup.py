from setuptools import setup
#4.4 is an experimental build to test import statements from different modules
setup(
    name='picta-gui',
    version='0.4.4',
    install_requires=[
        'opencv-python',
        'psd_tools',
        'tensorflow==2.13.0',
        'Pillow',
        'rawpy'
    ],
    author='Andrew Hanigan',
    author_email='andrew.hanigan@intelligent-it.com',
    description='Simple GUI for use with identifying turtle plastrons',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',
)