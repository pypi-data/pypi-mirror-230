from distutils.core import setup
setup(
  name = 'process-twarc',         
  packages = ['process_twarc'],   
  version = '0.15.5',
  license='MIT',
  description = 'Tools for tranforming raw data from Twarc2 to structured data for Masked Language Modeling.',   # Give a short description about your library
  author = 'Jordan Wolfgang Klein',
  author_email = 'jordan.klein.21@um.edu.mt',
  url = 'https://github.com/user/Lone-Wolfgang',
  keywords = ['Twitter', 'Deduplication', "Tokenization", "Language Modeling"],
  install_requires=[            
          'pyarrow',
          'transformers',
          'pandas',
          'datasets'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',      
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',  
    'Programming Language :: Python :: 3.9',      
    'Programming Language :: Python :: 3.10'
  ],
)