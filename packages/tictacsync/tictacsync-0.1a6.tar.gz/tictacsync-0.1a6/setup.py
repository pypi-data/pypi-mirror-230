from setuptools import setup


with open("README.md", "rb") as f:
    long_descr = f.read().decode("utf-8")

long_description = 'CLI for syncing audio video \
	files containing an audio YaLTC sync track.'

setup(
    name = "tictacsync",
    packages = ["tictacsync"],
    package_data={
      'tictacsync': ['tests/data/*'],
    },
    install_requires=[
        'sox>=1.4.1',
        'ffmpeg_python>=0.2.0', 
        'loguru>=0.6.0',
        'matplotlib>=3.7.1',
        'numpy>=1.24.3',
        'rich>=10.12.0',
        'lmfit >= 1.0.2',
        'scipy>=1.10.1',
        'scikit-learn==1.2.2'], 
    python_requires='>=3.7',
    entry_points = {
        "console_scripts": ['tictacsync = tictacsync.entry:main']
        },
    version = '0.1a6',
    description = "command for syncing audio video recordings",
    long_description_content_type='text/markdown',
    long_description = long_descr,
    include_package_data=True,
    zip_safe=False,
    author = "Raymond Lutz",
    author_email = "lutzrayblog@mac.com",
	url ='https://sr.ht/~proflutz/TicTacSync/',
    classifiers=[
          'Development Status :: 2 - Pre-Alpha',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'License :: OSI Approved :: MIT License',
          'Operating System :: MacOS',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: POSIX',
          'Programming Language :: Python :: 3',
          'Topic :: Multimedia :: Sound/Audio',
          'Topic :: Utilities',
          'Topic :: Multimedia :: Sound/Audio :: Capture/Recording',
          'Topic :: Multimedia :: Video :: Non-Linear Editor',
      ], 
    )

