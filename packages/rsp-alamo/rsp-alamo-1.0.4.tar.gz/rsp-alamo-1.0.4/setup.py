from distutils.core import setup
from setuptools import find_packages

with open("README.md", "r") as f:
    long_description = f.read()
setup(name='rsp-alamo',
      version='1.0.4',
      description='Python extension for processing random string',
      long_description=long_description,
      long_description_content_type='text/markdown',
      author='alamo',
      author_email='453638071@qq.com',
      url='https://gitee.com/alamoliuyang/rsp',
      install_requires=['transformers==4.33.1'],
      license='MIT License',
      packages=find_packages(),
      platforms=["all"],
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Natural Language :: Chinese (Simplified)',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.8',
          'Topic :: Software Development :: Libraries'
      ],
      include_package_data=True,
      zip_safe=False,
      )
