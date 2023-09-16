from setuptools import setup

setup(
  name='pokemon_stats',
  packages=['pokemon_stats'],
  version='0.1',
  license='MIT',
  description='Librería para proyecto final sobre stats de Pokémon',
  author='Angela Chica',
  author_email='angelachicaortega@gmail.com',
  url='https://github.com/angelachica/pokemon_stats_package',
  download_url='https://github.com/angelachica/pokemon_stats_package/archive/0.1.tar.gz',
  keywords=['pokemon', 'stats', 'grupo'],
  install_requires=[
    'pandas',
    'sqlalchemy',
    'requests',
  ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)