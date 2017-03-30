from setuptools import setup

setup(
    name='MediaInfo',
    version='0.0.6',

    description='A Python wrapper around the ffprobe or mediainfo command line utility',
    long_description=open('README.rst').read(),
    url='https://github.com/laodifang/MediaInfo',
    author='Ren Peng',
    author_email='ithink.ren@gmail.com',
    license='MIT',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',

        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3 :: Only',
    ],
    keywords='Python ffmpeg ffprobe mediainfo',

    packages=['tests'],
    py_modules=['MediaInfo'],
    test_suite='tests',
)
