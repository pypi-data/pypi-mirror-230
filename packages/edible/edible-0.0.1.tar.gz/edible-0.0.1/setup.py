from setuptools import setup

setup(
    name='edible',
    version='0.0.1',    
    description='Editing LLMs',
    url='https://github.com/thartvigsen/grace',
    author='Thomas Hartvigsen',
    author_email='tomh@mit.edu',
    license='BSD 2-clause',
    packages=['src'],
    install_requires=['torch',                     
                      'numpy',
                      #'tokenizers==0.6.0',
                      'transformers==4.16.2',
                      'pandas',                     
                      ],
    classifiers=[
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: BSD License',  
        'Programming Language :: Python :: 3.8',
    ],
)
