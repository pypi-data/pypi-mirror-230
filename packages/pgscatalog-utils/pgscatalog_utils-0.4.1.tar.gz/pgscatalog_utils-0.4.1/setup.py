# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pgscatalog_utils',
 'pgscatalog_utils.aggregate',
 'pgscatalog_utils.ancestry',
 'pgscatalog_utils.download',
 'pgscatalog_utils.match',
 'pgscatalog_utils.relabel',
 'pgscatalog_utils.samplesheet',
 'pgscatalog_utils.scorefile',
 'pgscatalog_utils.validate',
 'pgscatalog_utils.validate.formatted',
 'pgscatalog_utils.validate.harmonized_position']

package_data = \
{'': ['*']}

install_requires = \
['jq>=1.2.2,<2.0.0',
 'numpy>=1.23.3,<2.0.0',
 'pandas-schema>=0.3.6,<0.4.0',
 'pandas>=1.4.3,<2.0.0',
 'pgzip>=0.3.2,<0.4.0',
 'polars>=0.15.0,<0.16.0',
 'pyliftover>=0.4,<0.5',
 'requests>=2.28.1,<3.0.0',
 'scikit-learn>=1.2.1,<2.0.0',
 'zstandard>=0.18.0,<0.19.0']

entry_points = \
{'console_scripts': ['aggregate_scores = '
                     'pgscatalog_utils.aggregate.aggregate_scores:aggregate_scores',
                     'ancestry_analysis = '
                     'pgscatalog_utils.ancestry.ancestry_analysis:ancestry_analysis',
                     'combine_matches = '
                     'pgscatalog_utils.match.combine_matches:combine_matches',
                     'combine_scorefiles = '
                     'pgscatalog_utils.scorefile.combine_scorefiles:combine_scorefiles',
                     'download_scorefiles = '
                     'pgscatalog_utils.download.download_scorefile:download_scorefile',
                     'match_variants = '
                     'pgscatalog_utils.match.match_variants:match_variants',
                     'relabel_ids = '
                     'pgscatalog_utils.relabel.relabel_ids:relabel_ids',
                     'samplesheet_to_json = '
                     'pgscatalog_utils.samplesheet.check:check_samplesheet',
                     'validate_scorefiles = '
                     'pgscatalog_utils.validate.validate_scorefile:validate_scorefile']}

setup_kwargs = {
    'name': 'pgscatalog-utils',
    'version': '0.4.1',
    'description': 'Utilities for working with PGS Catalog API and scoring files',
    'long_description': "# PGS Catalog utilities\n\n[![CI](https://github.com/PGScatalog/pgscatalog_utils/actions/workflows/main.yml/badge.svg)](https://github.com/PGScatalog/pgscatalog_utils/actions/workflows/main.yml)\n[![DOI](https://zenodo.org/badge/513521373.svg)](https://zenodo.org/badge/latestdoi/513521373)\n\nThis repository is a collection of useful tools for downloading and working with scoring files from the\nPGS Catalog. This is mostly used internally by the PGS Catalog Calculator ([`PGScatalog/pgsc_calc`](https://github.com/PGScatalog/pgsc_calc)); however, other users may find some of these tools helpful.\n\n## Overview\n\n* `download_scorefiles`: Download scoring files by PGS ID (accession) in genome builds GRCh37 or GRCh38\n* `combine_scorefile`: Combine multiple scoring files into a single scoring file\nin 'long' format\n* `match_variants`: Match target variants (bim or pvar files) against the output\nof `combine_scorefile` to produce scoring files for plink 2\n* `ancestry_analysis` : use genetic PCA loadings to compare samples to population reference panels, and report PGS adjusted for these axes of genetic ancestry. The PCs will likely have been generated with [FRAPOSA (pgs catalog version)](https://github.com/PGScatalog/fraposa_pgsc)\n* `validate_scorefiles`: Check/validate that the scoring files and harmonized scoring files match the PGS Catalog scoring file formats.\n\n## Installation\n\n```\n$ pip install pgscatalog-utils\n```\n\n## Quickstart\n\n```\n$ download_scorefiles -i PGS000922 PGS001229 -o . -b GRCh37\n$ combine_scorefiles -s PGS*.txt.gz -o combined.txt \n$ match_variants -s combined.txt -t <example.pvar> --min_overlap 0.75 --outdir .\n$ validate_scorefiles -t formatted --dir <scoringfiles_directory> --log_dir <logs_directory>\n```\n\nMore details are available using the `--help` parameter.\n\n## Install from source\n\nRequirements:\n\n- python 3.10\n- [poetry](https://python-poetry.org)\n\n```\n$ git clone https://github.com/PGScatalog/pgscatalog_utils.git\n$ cd pgscatalog_utils\n$ poetry install\n$ poetry build\n$ pip install --user dist/*.whl \n```\n\n## Credits\n\nThe `pgscatalog_utils` package is developed as part of the **Polygenic Score (PGS) Catalog** \n([www.PGSCatalog.org](https://www.PGSCatalog.org)) project, a collaboration between the \nUniversity of Cambridge’s Department of Public Health and Primary Care (Michael Inouye, Samuel Lambert, Laurent Gil) \nand the European Bioinformatics Institute (Helen Parkinson, Aoife McMahon, Ben Wingfield, Laura Harris).\n\nA manuscript describing the tool and larger PGS Catalog Calculator pipeline \n[(`PGSCatalog/pgsc_calc`)](https://github.com/PGScatalog/pgsc_calc) is in preparation. In the meantime \nif you use these tools we ask you to cite the repo(s) and the paper describing the PGS Catalog resource:\n\n- >PGS Catalog utilities _(in development)_. PGS Catalog\n  Team. [https://github.com/PGScatalog/pgscatalog_utils](https://github.com/PGScatalog/pgscatalog_utils)\n- >PGS Catalog Calculator _(in development)_. PGS Catalog\n  Team. [https://github.com/PGScatalog/pgsc_calc](https://github.com/PGScatalog/pgsc_calc)\n- >Lambert _et al._ (2021) The Polygenic Score Catalog as an open database for\nreproducibility and systematic evaluation.  Nature Genetics. 53:420–425\ndoi:[10.1038/s41588-021-00783-5](https://doi.org/10.1038/s41588-021-00783-5).\n\nThis work has received funding from EMBL-EBI core funds, the Baker Institute, the University of Cambridge, \nHealth Data Research UK (HDRUK), and the European Union's Horizon 2020 research and innovation programme \nunder grant agreement No 101016775 INTERVENE.\n",
    'author': 'Benjamin Wingfield',
    'author_email': 'bwingfield@ebi.ac.uk',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/PGScatalog/pgscatalog_utils',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.10,<4.0',
}


setup(**setup_kwargs)
