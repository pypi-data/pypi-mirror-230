from distutils.core import setup
setup(
  name = 'MIGNON',         
  packages = ['MIGNON'],   
  version = '1.0.0',     
  license='gpl-2.0',       
  description = 'MIGNON (Multiplexed Imaging auGmeNtatiONs) is a tool to generate data augmentations of multiplexed images. Given an IMC array and a mask array, augmentations can be generated. Possible augmentations that can be selected are Shift, Rotate, Merge, Expand, and Shrink. Users can select the probability to apply each augmentation and the desired number of augmentations to generate. The output includes original cell expressions and augmented cell expressions.',   # Give a short description about your library
  author = 'Kevin Sun, Jett Lee, Kieran Campbell',                   
  author_email = 'kierancampbell@lunenfeld.ca',      
  url = 'https://github.com/camlab-bioml/MIGNON',    
  keywords = ['Data Augmentation', 'Multiplexed Imaging'],  
  install_requires=[            
          'numpy',
          'scikit-image',
          'scipy',
          'anndata',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)