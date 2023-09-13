from setuptools import setup, find_packages


setup(
    name='quasar_unred',
    version='0.6',
    license='BSD3',
    author="John Klawitter",
    author_email='jackklawitter@gmail.com',
    packages=find_packages('quasar_unred'),
    package_dir={'': 'quasar_unred'},
    url='https://github.com/jackklawitter/quasar_unred',
    download_url='https://github.com/jackklawitter/quasar_unred/archive/refs/tags/v0.6.tar.gz',
    keywords='Red Quasars',
    install_requires=[
          'numpy', 'scipy', 'astropy', 'dust_extinction', 'matplotlib'
      ],

)
