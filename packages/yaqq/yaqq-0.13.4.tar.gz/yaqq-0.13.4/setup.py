# Copyright © 2023 Quantum Intelligence Research Group
#
# Distributed under terms of the GNU Affero General Public License.

from setuptools import setup

from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='yaqq',
    version='0.13.4',
    install_requires=["numpy >= 1.23.5", "qiskit >= 0.43.3", "astropy >= 5.3.1", "matplotlib >= 3.7.2", "scipy >= 1.11.1", "tqdm >= 4.65.0", "qutip >= 4.7.2", "scikit-learn >= 1.3.0", "weylchamber >= 0.4.0"],
    long_description=long_description,
    long_description_content_type='text/markdown'
)