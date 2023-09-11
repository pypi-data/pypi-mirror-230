from setuptools import setup

setup(
    py_modules=['src'],
    entry_points={
        'flake8.extension': [
            'PBP1 = src.flake8_pbp:ProduceBetterPythonPlugin',
        ],
    },
)