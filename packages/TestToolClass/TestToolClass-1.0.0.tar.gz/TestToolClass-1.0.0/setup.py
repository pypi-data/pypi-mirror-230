from setuptools import setup

setup(
    name='TestToolClass',
    version='1.0.0',
    description='测试工具',
    author='毛鹏',
    author_email='729164035@qq.com',
    packages=['src'],
    install_requires=[
        'jsonpath~=0.82.2',
        'cachetools~=5.3.1',
        'Faker~=19.6.0',
        'diskcache~=5.6.3',
        'setuptools~=60.2.0',
    ],
)
"""
 1. pip install build twine
 2. python setup.py sdist bdist_wheel
 3. python -m twine upload dist/*

"""
