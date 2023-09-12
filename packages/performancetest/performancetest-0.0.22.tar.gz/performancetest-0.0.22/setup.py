# # _*_ coding: utf-8 _*_
from setuptools import setup, find_packages

setup(
    name='performancetest',
    version='0.0.22',
    url='https://github.com/1033866383/perf-orange-cat',
    author='bozhou.fan',
    author_email='15525730080@163.com',
    description='Android, IOS app_performance',
    packages=find_packages(),
    install_requires=[
        "psutil==5.9.5", "airtest==1.3.0.1", "fastapi==0.103.1", "tidevice==0.11.1", "func-timeout==4.3.5", "sqlalchemy==2.0.20", "sqlalchemy-serializer==1.4.1", "uvicorn==0.23.2"
    ],
    include_package_data=True,  # 这里添加 include_package_data 参数
    package_data={
        'performancetest': ['web/test_result/*']
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
    ],
)
