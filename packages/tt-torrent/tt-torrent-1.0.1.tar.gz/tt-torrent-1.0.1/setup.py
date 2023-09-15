"""The python wrapper for tt-torrent API package setup."""
import shutup
from pathlib import Path
from setuptools import find_packages, setup

shutup.please()

this_dir = Path(__file__).parent

requirements = []
requirements_path = this_dir / "requirements.txt"
if requirements_path.is_file():
    with open(requirements_path, "r", encoding="utf-8") as requirements_file:
        requirements = requirements_file.read().splitlines()

# -----------------------------------------------------------------------------

setup(
    name="tt-torrent",
    version="1.0.1",
    author="Santiago Ramirez",
    author_email="santiirepair@gmail.com",
    description="😈 Daemon to manage torrents through tt-torrent website.",
    entry_points={"console_scripts": ["tt-torrent = cli.__main__:main"]},
    packages=find_packages(),
    install_requires=requirements,
    include_package_data=True,
    python_requires=">=3.10",
)
