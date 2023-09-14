# quasar_unred

Quasar Unred is a Python library for determining the E(B-V) value of observed quasar spectra. It can also be used to appropriately deredden these spectra.

## Installation

pip install quasar_unred

qso_template.txt must be downloaded and in working directory for load_template() to work with no argument.
## Usage

A simple demonstration is shown in quasar_unred_demo.ipynb

It is assumed that qso_template.txt and ukfs1037.p0236.final.dat are both downloaded and in your working directory.

## Dependencies

Dependencies for use are numpy, scipy, astropy, and dust_extinction

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.


## License

This project is Copyright (c) John Klawitter and Eilat Glikman and licensed under the terms of the BSD 3-Clause license.
