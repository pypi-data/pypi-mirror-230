import os

from setuptools import find_packages, setup

base_path = os.path.abspath(os.path.dirname(__file__))

requirements = []
with open("requirements.txt") as f:
    requirements = f.read().splitlines()

readme = ""
with open("README.md") as f:
    readme = f.read()

setup(
    name="LineAuthGPT",
    author="line_defult",
    url="https://github.com/linechengchen/LineAuthGPT",
    project_urls={
        "Documentation": "https://github.com/linechengchen/LineAuthGPT/blob/main/README.md",
        "Issue tracker": "https://github.com/linechengchen/LineAuthGPT/issues",
        "Changelog": "https://github.com/linechengchen/LineAuthGPT/blob/main/CHANGELOG.md",
    },
    version="0.0.2",
    packages=["LineAuthGPT", "LineAuthGPT/internal"],
    # py_modules=["LineAuthGPT"],
    license="GPL-3.0 license",
    description="An unofficial Python wrapper for OpenAI's ChatGPT API",
    long_description=readme,
    long_description_content_type="text/markdown",
    include_package_data=True,
    package_data={
        'LineAuthGPT': ['internal/chromedriver.exe'],
    },
    install_requires=requirements,
    python_requires=">=3.8.0",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Intended Audience :: Developers",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
        "Typing :: Typed",
    ],
)
