from setuptools import setup

version_ns = {}
with open('sfmta/_version.py', 'r') as version_file:
    exec(version_file.read(), {}, version_ns)

setup(name='sfmta',
      version=version_ns['__version__'],
      description='Python library for shuttle analysis',
      long_description=open('README.md').read(),
      author='',
      author_email='',
      url='',
      install_requires=['pandas>=0.20.0', 'ipyleflet>=0.4.0', 
                        'ipywidgets>=7.0.1'],
      extras_require={
      },
      packages=[
          'application',
          'sql_queries',
      ],
      package_data={},
      classifiers=[
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Programming Language :: Python :: 3.5',
      ])

