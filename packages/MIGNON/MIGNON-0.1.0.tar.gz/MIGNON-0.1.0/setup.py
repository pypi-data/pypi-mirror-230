from distutils.core import setup
setup(
  name = 'MIGNON',         # How you named your package folder (MyLib)
  packages = ['MIGNON'],   # Chose the same as "name"
  version = '0.1.0',      # Start with a small number and increase it with every change you make
  license='gpl-2.0',        # Chose a license from here: https://help.github.com/articles/licensing-a-repository
  description = 'MIGNON (Multiplexed Imaging auGmeNtatiONs) is a tool to generate data augmentations of multiplexed images. Given an IMC tiff file and a mask tiff file, augmentations can be generated. Possible augmentations that can be selected are Shift, Rotate, Merge, Expand, and Shrink. Users can select the probability to apply each augmentation and the desired number of augmentations to generate. The output includes original cell expressions and augmented cell expressions.',   # Give a short description about your library
  author = 'Kevin Sun, Jett Lee, Kieran Campbell',                   # Type in your name
  author_email = 'kierancampbell@lunenfeld.ca',      # Type in your E-Mail
  url = 'https://github.com/camlab-bioml/MIGNON',   # Provide either the link to your github or to your website
  download_url = 'https://github.com/camlab-bioml/MIGNON/archive/refs/tags/v0.0.1.tar.gz',    # I explain this later on
  keywords = ['Data Augmentation', 'Multiplexed Imaging'],   # Keywords that define your package best
  install_requires=[            # I get to this in a second
          'numpy',
          'skimage',
          'scipy',
          'random',
          'anndata',
      ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Bio-Informatics",
    ],
)