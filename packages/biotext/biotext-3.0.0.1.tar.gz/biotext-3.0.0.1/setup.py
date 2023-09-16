from setuptools import setup, find_packages

setup(name='biotext',
      version='3.0.0.1',
      author='Diogo de J. S. Machado',
      author_email='diogomachado.bioinfo@gmail.com',
      description='The biotext library offers resources for natural language processing based on bioinformatics tools',
      packages=find_packages(),
      long_description_content_type='text/markdown',
      long_description=open('README.md').read(),
      zip_safe=False,
      install_requires=['numpy', 'pandas', 'biopython', 'nltk', 'sweep', 'scipy', 'unidecode'],
      license = 'BSD-3-Clause',
      url='https://github.com/diogomachado-bioinfo/biotext',
      )
