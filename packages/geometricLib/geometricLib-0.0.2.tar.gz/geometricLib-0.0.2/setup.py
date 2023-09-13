from setuptools import setup, find_packages


def readme():
  with open('README.md', 'r') as f:
    return f.read()


setup(
  name='geometricLib',
  version='0.0.2',
  author='blank1xs',
  author_email='oignatevich@gmail.com',
  description='calculates the area of a circle by radius and a triangle by three sides',
  long_description=readme(),
  long_description_content_type='text/markdown',
  url='https://github.com/uhiintezz/geometricLib',
  packages=['geometricLib'],
  project_urls={
    'GitHub': 'https://github.com/uhiintezz'
  },
  python_requires='>=3.6'
)