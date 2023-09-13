from setuptools import setup, find_packages
import os
import shutil

target_directory = 'SG1AB'

setup(
    name=target_directory,
    version='1.0.1.2',
    description='nnfw_api binding',
    long_description='you can use nnfw_api by python',
    url='https://github.com/Samsung/ONE/tree/master/runtime',
    author='Your Name',
    author_email='your@email.com',
    license='Samsung',
    packages=[target_directory],
    package_data={target_directory: ['nnfw_api_pybind.cpython-38-x86_64-linux-gnu.so', 'libnnfw-dev.so', 'libonert_core.so', 'libbackend_cpu.so', 'nnfw_api_pybind.cpython-38-arm-linux-gnueabihf.so','nnfw_api_pybind.cpython-38-aarch64-linux-gnueabihf.so']},
    install_requires=[
        # 필요한 의존성 패키지를 여기에 추가
    ],
)

