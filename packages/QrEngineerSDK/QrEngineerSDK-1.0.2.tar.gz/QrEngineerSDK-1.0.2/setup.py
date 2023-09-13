from setuptools import setup, find_packages

classifiers = [
  'Topic :: Scientific/Engineering',
  'Topic :: Software Development',
  'Development Status :: 5 - Production/Stable',
  'License :: Freely Distributable',
  'License :: Other/Proprietary License',
  'Programming Language :: Python :: 3',
  'Operating System :: OS Independent',
  'Intended Audience :: Developers',
  'Intended Audience :: Education',
  'Intended Audience :: Information Technology'
]

setup(
  name='QrEngineerSDK',
  version='1.0.2',
  description='QApps QrEngineer Python SDK',
  long_description=open('README.md').read(),
  long_description_content_type = 'text/markdown',
  url='https://core.quantumpath.app/qappsrengineer/',
  author='QuantumPath',
  classifiers=classifiers,
  keywords='quantum, quantumpath, qSOA, sdk, quantum applications, quantum software, qapps, qrengineer, transpilation',
  packages=find_packages(exclude=["test"]),
  install_requires=['QuantumPathQSOAPySDK','matplotlib']
)