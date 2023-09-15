from setuptools import setup, find_packages


def read_file(path_to_file):
    with open(path_to_file, 'r') as f:
        return f.read()


setup(name='sonic_arabic',
      version='0.2.3',
      author='i.karpenko',
      author_email='volgakarp@gmail.com',
      description='анализ арабской речи',
      long_description=read_file('README.md'),
      long_description_content_type='text/markdown',
      url='https://git.id-network.ru/data-science/sc_ar',
      packages=find_packages(),
      install_requires=read_file('sonic_arabic/requirements.txt').splitlines(),
      classifiers=['Programming Language :: Python :: 3.9'],
      python_requires='>=3.9')
