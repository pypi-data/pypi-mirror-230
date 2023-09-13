# pyright: reportShadowedImports=false
import subprocess
from pathlib import Path
from typing import *

import setuptools

PACKAGE = "soboro"
CURRENT_DIR = Path(__file__).resolve().parent

with open(CURRENT_DIR / "README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()


def read_requirements(path: Union[str, Path]):
    with open(path, "r") as fh:
        return {line.strip() for line in fh.readlines() if not line.startswith("#")}


__VERSION__ = "0.0.4"

requirements = list(read_requirements(CURRENT_DIR / "requirements.txt"))
extras_require = {"all": set()}


packages = setuptools.find_packages()
sub_packages = []
for sub_requirement in (CURRENT_DIR / PACKAGE).rglob("requirements.txt"):
    sub_package = sub_requirement.parent.relative_to(CURRENT_DIR)
    sub_requirements = read_requirements(sub_requirement)
    extras_require[sub_package.name] = sub_requirements
    extras_require["all"].update(sub_requirements)

extras_require = {key: list(val) for key, val in extras_require.items()}
entry_points = {"console_scripts": (f"{PACKAGE} = {PACKAGE}.__main__:main",)}

try:
    subprocess.check_output(["which", "nvidia-smi"])
except subprocess.CalledProcessError:
    pass
else:
    num_gpus = str(subprocess.check_output(["nvidia-smi", "-L"])).count('UUID')
    if num_gpus:
        requirements.remove("onnxruntime")
        requirements.append("onnxruntime-gpu")
        for values in extras_require.values():
            if "onnxruntime" in values:
                values.remove("onnxruntime")
                values.append("onnxruntime-gpu")

setuptools.setup(
    name=PACKAGE,
    packages=packages,
    version=__VERSION__,
    author="datnh21",
    author_email="v.datnh21@vinai.io",
    description=PACKAGE,
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points=entry_points,
    install_requires=requirements,
    extras_require=extras_require,
)
