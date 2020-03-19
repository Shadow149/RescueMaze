# Changelog
All notable changes and additions Erebus will be documented in this file, excluding the changes from version Orion and before.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

---
## 0.1.1 (Aura) - 19-03-2020
### Added
- Added activities.
- Added children.
- Added relocate button.
- Added new sensors.
- Added win condition screen.

### Changed
- New obsticle generation algorithm. 
- New competition controller look.
- Changed camera settings

### Activities
- New objective in the game where robots can pick up and deposit an activity to its corresponding colour pad. This is the highest scoring task - 5 points for a successful depost.

### Children
- Added children which give more points than adults.
- Changed point density for humans.
  - Adults score 1 point for a sucessfull pick up and an additional 1 point for a deposit.
  - Children score 1 point for a successfull pick up and an additional 2 points for a deposit.

### Sensors
- Added Gryoscopic sensor
- Added Reciever
- Added Emitter
- Added Light sensor
- Added GPS
- Changed camera FOV to 0.9