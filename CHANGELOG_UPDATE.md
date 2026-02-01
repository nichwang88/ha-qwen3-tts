## [1.3.3] - 2026-02-01

### Fixed
- **Critical Import Error**: Fixed `callback` import path from `homeassistant.helpers` to `homeassistant.core`
  - This was causing "ImportError: cannot import name 'callback'" when adding the integration
  - Previous version (1.3.2) had incorrect import path that broke integration setup

### Technical Details
- Changed import statement in `tts.py` line 22:
  - Before: `from homeassistant.helpers import callback`
  - After: `from homeassistant.core import callback`
- This follows the correct Home Assistant API convention

