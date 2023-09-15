# ClipDetect

<!-- [![codecov](https://codecov.io/gh/roedoejet/clipdetect/branch/master/graph/badge.svg)](https://codecov.io/gh/roedoejet/clipdetect) -->
[![Build Status](https://github.com/roedoejet/clipdetect/actions/workflows/tests.yaml/badge.svg)](https://github.com/roedoejet/clipdetect/actions)
[![PyPI package](https://img.shields.io/pypi/v/clipdetect.svg)](https://pypi.org/project/clipdetect/)
[![license](https://img.shields.io/badge/Licence-MIT-green)](LICENSE)
[![standard-readme compliant](https://img.shields.io/badge/readme%20style-standard-brightgreen.svg?style=flat-square)](https://github.com/roedoejet/clipdetect)

> Detect clipping in your wav files

## Table of Contents
- [ClipDetect](#clipdetect)
  - [Table of Contents](#table-of-contents)
  - [Background](#background)
  - [Install](#install)
  - [Usage](#usage)
  - [Maintainers](#maintainers)
  - [Contributing](#contributing)
  - [How to Cite](#citation)
  - [License](#license)

## Background

This library is for detecting clipping in audio even if the audio has been normalized (ie does not actually produce the maximum possible value given the bit depth). I implemented this library from the pseudocode in [this paper](https://www.sciencedirect.com/science/article/pii/S0167639321000832) - please cite them if you use this.

## Install

To use this package just run `pip install clipdetect` or `poetry add clipdetect` if you use poetry.

## Usage

To detect a single file:

    clipdetect path/to/file.wav

To detect all wav files in a folder:

    clipdetect path/to/folder


Results for a folder will be written to csv format.


### Export to TextGrid

The following will export a [Praat TextGrid](https://www.fon.hum.uva.nl/praat/) of the clipping sections

    clipdetect path/to/file.wav --textgrid

You can also do it for a whole folder:

    clipdetect path/to/folder --textgrid


## Maintainers

[@roedoejet](https://github.com/roedoejet).


## Contributing

Feel free to dive in! [Open an issue](https://github.com/roedoejet/clipdetect/issues/new) or submit PRs.

This repo follows the [Contributor Covenant](http://contributor-covenant.org/version/1/3/0/) Code of Conduct.

Have a look at [Contributing.md](Contributing.md) for help using our standardized formatting conventions and pre-commit hooks.

## Citation

If you use this work in a project of yours and write about it, please feel free to link to this repo but also cite the authors of the algorithm using the following:

Hansen, John H. L., Allen Stauffer, and Wei Xia. “Nonlinear Waveform Distortion: Assessment and Detection of Clipping on Speech Data and Systems.” Speech Communication 134 (2021): 20–31. https://doi.org/10.1016/j.specom.2021.07.007.


Or in BibTeX:

```
@article{HANSEN202120,
title = {Nonlinear waveform distortion: Assessment and detection of clipping on speech data and systems},
journal = {Speech Communication},
volume = {134},
pages = {20-31},
year = {2021},
issn = {0167-6393},
doi = {https://doi.org/10.1016/j.specom.2021.07.007},
url = {https://www.sciencedirect.com/science/article/pii/S0167639321000832},
author = {John H.L. Hansen and Allen Stauffer and Wei Xia},
keywords = {Audio clipping, Speech quality assessment, Non-linear distortion, Speaker recognition},
abstract = {Speech, speaker, and language systems have traditionally relied on carefully collected speech material for training acoustic models. There is an enormous amount of freely accessible audio content. A major challenge, however, is that such data is not professionally recorded, and therefore may contain a wide diversity of background noise, nonlinear distortions, or other unknown environmental or technology-based contamination or mismatch. There is a crucial need for automatic analysis to screen such unknown datasets before acoustic model development training, or to perform input audio purity screening prior to classification. In this study, we propose a waveform based clipping detection algorithm for naturalistic audio streams and examine the impact of clipping at different severities on speech quality measurements and automatic speaker recognition systems. We use the TIMIT and NIST SRE08 corpora as case studies. The results show, as expected, that clipping introduces a nonlinear distortion into clean speech data, which reduces speech quality and performance for speaker recognition. We also investigate what degree of clipping can be present to sustain effective speech system performance. The proposed detection system, which will be released, could contribute to massive new audio collections for speech and language technology development (e.g. Google Audioset (Gemmeke et al., 2017), CRSS-UTDallas Apollo Fearless-Steps (Yu et al., 2014) (19,000 h naturalistic audio from NASA Apollo missions)).}
}
```

## License

MIT. See [LICENSE](LICENSE) for the Copyright and license statements.
