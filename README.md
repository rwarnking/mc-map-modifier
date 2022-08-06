# mc-map-modifier

[<img alt="Unit tests" src="https://img.shields.io/github/workflow/status/rwarnking/mc-map-modifier/Compile%20Evaluation%20Sheet?label=Build&logo=github&style=for-the-badge" height="23">](https://github.com/rwarnking/mc-map-modifier/actions/workflows/pytests.yml)
[<img alt="Linting status of master" src="https://img.shields.io/github/workflow/status/rwarnking/mc-map-modifier/Lint%20Code%20Base?label=Linter&style=for-the-badge" height="23">](https://github.com/marketplace/actions/super-linter)
[<img alt="Version" src="https://img.shields.io/github/v/release/rwarnking/mc-map-modifier?style=for-the-badge" height="23">](https://github.com/rwarnking/mc-map-modifier/releases/latest)
[<img alt="Licence" src="https://img.shields.io/github/license/rwarnking/mc-map-modifier?style=for-the-badge" height="23">](https://github.com/rwarnking/mc-map-modifier/blob/main/LICENSE)

## Description

## Table of Contents

- [mc-map-modifier](#mc-map-modifier)
  - [Table of Contents](#table-of-contents)
  - [List of Features](#list-of-features)
  - [Installation](#installation)
    - [Dependencies](#dependencies)
  - [Usage](#usage)
    - [GUI](#gui)
    - [Supported Versions](#supported-versions)
  - [Contributing](#contributing)
  - [Credits](#credits)
  - [License](#license)

## List of Features
This tool has five different functions which can be used to alter the Minecraft
region files (`.mca`).

The selectable functions are:

- [x] Fill air pockets
  - tested values: 1
- [x] Fill block pockets inside the water
  - tested values: 1, 2, 3
- [x] Replace solid areas
  - tested values: 0, 1, 2, 3, 4
  - recommended value: 2
- [ ] Fill a cave at a given position
- [ ] Dig a railway tunnel between a start- and an endpoint

Take a look into the [wiki](https://github.com/rwarnking/mc-map-modifier/wiki) for more information about the features and for implementation details.

<p float="left">
  <p>
  The left image shows an example of a .mca file where a lot of holes were generated.
  The right image shows the same spot but after applying the algorithm with size 1.

  As can be seen most of the holes where removed, only those of bigger size are still present.
  </p>
  <img src="docs/images/ex1_airp_before.png" alt="Air pockets before" width="45%" />
  <img src="docs/images/ex1_airp_after.png" alt="Air pockets after" width="45%" />
</p>

## Installation

Download this repository or install directly from GitHub
```bash
pip install git+https://github.com/rwarnking/mc-map-modifier.git
```

### Dependencies

This project uses python. One of the tested versions is python 3.9.

Use either
```bash
pip install -r requirements.txt
```
to install all dependencies.

Or use Anaconda for your python environment and create a new environment with
```bash
conda env create --file mc-env.txt
```
afterwards activate the environment (`conda activate mc`) and start the application.

The main dependency is the anvil tool found here:
[anvil-parser](https://github.com/matcool/anvil-parser)

Further dependencies are mostly computer vision libraries for image processing:
- [numpy](https://numpy.org)
- [scipy](https://www.scipy.org)
- [scikit-image](https://scikit-image.org)
- [matplotlib](https://matplotlib.org)

## Usage

### GUI

The GUI gives you options for selecting the directories for input, output and replacement.
Furthermore options are available to enable the different functions and the size of the
modified area.
Progress-bars are given for continuous observation of the progress.

![GUI](/docs/images/gui.png)

### Supported Versions

Inputfiles up to version 1.16 should be processable.

## Contributing

We encourage you to contribute to this project, in form of bug reports, feature requests or code additions. Although it is likely that your contribution will not be implemented.

Please check out the [contribution](docs/CONTRIBUTING.md) guide for guidelines about how to proceed as well as a style guide.

## Credits
Up until now there are no further contributors other than the repository creator.

## License
This project is licensed under the [MIT License](LICENSE).

