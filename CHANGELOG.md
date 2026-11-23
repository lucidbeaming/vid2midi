# Changelog

All notable changes to this project are documented here. The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [1.0.0] - 2026-11-23

First tagged release. Note boundaries now fall on the frame where the picture changes (they landed 4 frames early), and the README documents every option.

### Fixed
- Note boundaries landed 4 frames before the change in the picture (133 ms at 30 fps), and the last note ended 4 frames early. Boundaries now use the frame where the change is seen (#17)

### Changed
- README rewritten: install, every option (including `-p/--position`), the note ranges, importing at 120 BPM and how it works (#18)
- Relicensed from GPL-3.0 to MIT; earlier releases keep GPL-3.0 (#15)

[Unreleased]: https://github.com/lucidbeaming/vid2midi/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/lucidbeaming/vid2midi/releases/tag/v1.0.0
