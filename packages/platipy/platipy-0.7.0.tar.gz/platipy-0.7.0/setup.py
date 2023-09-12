# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['platipy',
 'platipy.backend',
 'platipy.backend.sample',
 'platipy.cli',
 'platipy.dicom',
 'platipy.dicom.communication',
 'platipy.dicom.download',
 'platipy.dicom.io',
 'platipy.dicom.tests',
 'platipy.imaging',
 'platipy.imaging.dose',
 'platipy.imaging.generation',
 'platipy.imaging.label',
 'platipy.imaging.projects',
 'platipy.imaging.projects.bronchus',
 'platipy.imaging.projects.cardiac',
 'platipy.imaging.projects.multiatlas',
 'platipy.imaging.projects.nnunet',
 'platipy.imaging.registration',
 'platipy.imaging.tests',
 'platipy.imaging.utils',
 'platipy.imaging.visualisation',
 'platipy.imaging.visualisation.tests']

package_data = \
{'': ['*'],
 'platipy.backend': ['static/css/*',
                     'static/feather/*',
                     'static/feather/icons/*',
                     'static/js/*',
                     'static/pages/*',
                     'templates/*']}

install_requires = \
['SimpleITK>=2.0.2,<3.0.0',
 'click>=8.0.3,<9.0.0',
 'matplotlib>=3.2.2,<4.0.0',
 'pandas>=2.0.3,<3.0.0',
 'pydicom>=2.1.2,<3.0.0',
 'pynetdicom>=2.0.2,<3.0.0',
 'requests>=2.25.1,<3.0.0',
 'rt-utils>=1.1.4,<2.0.0',
 'scikit-image>=0.18.1']

extras_require = \
{'backend': ['Flask>=2.1.0,<3.0.0',
             'Flask-RESTful>=0.3.8',
             'Flask-SQLAlchemy>=2.4.4,<3.0.0',
             'celery>=5.2.3,<6.0.0',
             'redis>=3.5.3,<5.0.0',
             'psutil>=5.8.0,<6.0.0',
             'gunicorn>=20.0.4,<21.0.0',
             'Jinja2>=3.1,<4.0',
             'pymedphys>=0.38.0'],
 'cardiac': ['vtk>=9.1.0,<10.0.0', 'nnunet>=1.7.0,<2.0.0'],
 'nnunet': ['nnunet>=1.7.0,<2.0.0']}

entry_points = \
{'console_scripts': ['platipy = platipy.cli.run:platipy_cli']}

setup_kwargs = {
    'name': 'platipy',
    'version': '0.7.0',
    'description': 'Processing Library and Analysis Toolkit for Medical Imaging in Python',
    'long_description': '# PlatiPy\n\n[![DOI](https://joss.theoj.org/papers/10.21105/joss.05374/status.svg)](https://doi.org/10.21105/joss.05374)\n\n## Processing Library and Analysis Toolkit for Medical Imaging in Python\n\nPlatiPy is a library of **amazing** tools for image processing and analysis - designed specifically\nfor medical imaging!\n\nCheck out the [PlatiPy documentation](https://pyplati.github.io/platipy/) for more info.\n\nThis project was motivated by the need for a simple way to use, visualise, process, and analyse\nmedical images. Many of the tools and algorithms are designed in the context of radiation therapy,\nalthough they are more widely applicable to other fields that use 2D, 3D, or 4D imaging.\n\nPlatiPy is written in Python, and uses SimpleITK, VTK, and standard Python libraries. Jupyter\nnotebooks are provided where possible, mainly for guidance on getting started with using the tools.\nWe welcome feedback and contributions from the community (yes, you!) and you can find more\ninformation about contributing [here](https://pyplati.github.io/platipy/contributing.html).\n\n## What can I do with **platipy**?\n\nA lot! A good place to start is by looking in the\n[examples directory](https://github.com/pyplati/platipy/tree/master/examples).\n\nSome examples of what PlatiPy can do:\n\n- DICOM organising and converting:\n  - Bulk convert from multiple series and studies with a single function\n  - Convert DICOM-RT structure and dose files to NIfTI images\n  - Create DICOM-RT structure files from binary masks e.g. from automatic contouring algorithms\n- Image registration\n  - Register images and transform labels with a few lines of code\n  - Linear transformations: rigid, affine, similarity\n  - Non-linear deformable transformations: demons, b-splines\n  - Multiple metrics for optimisation\n- Atlas-based segmentation\n  - A suite of tools that can be used out-of-the-box\n  - Includes advanced algorithms for\n      [iterative atlas selection](https://doi.org/10.1088/1361-6560/ab652a/) and\n      [vessel splining](https://doi.org/10.1088/1361-6560/abcb1d/)\n- Synthetic deformation field generation\n  - Simulate anatomically realistic shifts, expansions, and bending\n  - Compare DIR results from clinical systems\n- Basic tools for image processing and analysis\n  - Computing label similarity metrics: DSC, mean distance to agreement, Hausdorff distance, and more\n  - Cropping images to a region of interest\n  - Rotate images and generate maximum/mean intensity projections (beams eye view modelling)\n\nA major part of this package is **visualisation**, and some examples are shown below!\n\n#### Visualise some contours\n\n``` python\nfrom platipy.imaging import ImageVisualiser\n\nvis = ImageVisualiser(image)\nvis.add_contour(contours)\nfig = vis.show()\n```\n\n![Figure 1](assets/figure_1.png)\n\n#### Register some images\n\n```python\nfrom platipy.imaging.registration.linear import linear_registration\n\nimage_2_registered, tfm = linear_registration(\nimage_1,\nimage_2\n)\n\nvis = ImageVisualiser(image_1)\nvis.add_comparison_overlay(image_2_registered)\nfig = vis.show()\n```\n\n![Figure 2](assets/figure_2.png)\n\n#### Calculate deformation vector fields\n\n```python\nfrom platipy.imaging.registration.deformable import fast_symmetric_forces_demons_registration\n\nimage_2_deformed, tfm_dir, dvf = fast_symmetric_forces_demons_registration(\nimage_1,\nimage_2_registered\n)\n\nvis = ImageVisualiser(image_2_deformed, axis="z")\nvis.add_vector_overlay(\n    dvf,\n    subsample=12,\n    arrow_scale=1,\n    arrow_width=2,\n    colormap=plt.cm.magma,\n    name="DVF magnitude [mm]",\n    color_function="magnitude"\n)\nfig = vis.show()\n```\n\n![Figure 3](assets/figure_3.png)\n\n## Getting started\n\nThere aren\'t many requirements, just an installed Python interpreter (3.7 or greater). PlatiPy can\nbe installed with **pip**:\n\n```bash\npip install platipy\n```\n\nThe base installation of platipy does not include some large libraries needed for various\ncomponents of platipy. The following extras are available to install to run specific platipy tools:\n\n```bash\npip install platipy[cardiac]\npip install platipy[nnunet]\npip install platipy[backend]\n```\n\n## Authors\n\n- **Phillip Chlap** - [phillip.chlap@unsw.edu.au](phillip.chlap@unsw.edu.au)\n- **Robert Finnegan** - [robert.finnegan@sydney.edu.au](robert.finnegan@sydney.edu.au)\n',
    'author': 'Phillip Chlap & Robert Finnegan',
    'author_email': 'None',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'None',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.8.0,<4.0.0',
}


setup(**setup_kwargs)
