# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog],
and this project adheres to [Semantic Versioning].

## [0.3.1] - 2026-07-24

### Fixed

#### Ngspice class

- Bug where the Ngspice class didnt convert transient statement variables to float

## [0.3.0] - 2026-07-24

### Added

#### Ngspice class
- Set simulation temperature (or temperature sweep) using set_temperature() method

### Fixed
- Code documentation

#### Ngspice class
- Now checks if the DUT netlist path is valid or provided during initialization.
- Library can now be overwritten and swept (PVT).
- Variable/library/temperature setting now returns a dictionary. get_variables() method returns a list of dictionaries.

## [0.2.1] - 2026-07-04

### Fixed

- Reduced required python version from 3.14 to 3.12. The motivation for this is so the package can be used out-of-the-box in [IIC-OSIC-TOOLS](https://github.com/iic-jku/iic-osic-tools)

## [0.2.0] - 2026-07-04

- Initial release after v0.1.0 where the package is fully productive.

<!-- Links -->
[keep a changelog]: https://keepachangelog.com/en/1.0.0/
[semantic versioning]: https://semver.org/spec/v2.0.0.html

<!-- Versions -->
[unreleased]: https://github.com/fhormot/spiceybun/compare/v0.2.1...HEAD
[0.2.1]: https://github.com/fhormot/spiceybun/compare/v0.2.0...v0.2.1
[0.2.0]: https://github.com/fhormot/spiceybun/releases/tag/v0.2.0