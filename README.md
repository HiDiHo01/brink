[![hacs_badge](https://img.shields.io/badge/HACS-Default-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

[![GitHub Release](https://img.shields.io/github/release/samuolis/brink.svg?style=for-the-badge&color=blue)](https://github.com/samuolis/brink/releases) 

![Project Maintenance](https://img.shields.io/badge/maintainer-Lukas%20Samuolis-blue.svg?style=for-the-badge)

# Brink-Home Ventilation

Custom component for Home Assistant. This component is designed to integrate the [Brink-Home](https://www.brink-home.com/) systems with [ebus Brink Emodule](https://www.brinkclimatesystems.nl/documenten/brink-home-emodule-imodule-614491.pdf).

<img width="503" alt="Screenshot 2023-05-08 at 21 14 39" src="https://user-images.githubusercontent.com/28056781/236899814-e903fbb0-e007-4938-aa2c-0e04e91fbb36.png">
<img width="334" height="435" alt="Screenshot 2026-03-07 at 09 29 06" src="https://github.com/user-attachments/assets/004c04e2-3e04-4fe3-9018-50ddf42deb65" />
<img width="334" height="256" alt="Screenshot 2026-03-07 at 09 29 13" src="https://github.com/user-attachments/assets/96976cb0-62a6-4eb7-9a10-9946d89ef2a3" />
<img width="335" height="288" alt="Screenshot 2026-03-07 at 09 29 19" src="https://github.com/user-attachments/assets/d6b4304f-c55b-4167-ad88-e42cfa1800a0" />

## Installation

Requires Home Assistant **2026.7.0 or newer**. This minimum provides the
`UnitOfRatio` API used by the CO₂ entities.

You have two options for installation:

### HACS

- Go to the [HACS](https://hacs.xyz) panel
- Go to integrations 
- Search for 'Brink-Home ventilations'
- Click \'Download this repository with HACS'.

### Manually

- Copy "brink_home" folder to the "/config/custom_components" folder.
- Restart HA server.

## Translations

English, Dutch, and German translations are included. This update uses lowercase
keys for enum states, select options, and fan presets. Review the
[translation migration guide](docs/translation-migration.md) before updating
automations or scripts that use the previous English values.

If different device options normalize to the same key, that ambiguous choice is
omitted and cannot be written. Other unambiguous options remain available.

## Alert diagnostics

The active-alert sensor uses Brink's valid summary count when supplied. If that
optional count is missing or invalid, it counts the complete fetched list of
active, unarchived alerts for its own system. An empty successful result is `0`;
a failed or incomplete refresh remains unavailable until a successful update.

## Development and maintenance

GitHub Actions runs Python 3.14 tests against Home Assistant 2026.7.0 and
2026.10.3, scoped Ruff lint/format checks, HACS validation, and hassfest. The checks
run for pull requests to `master`, pushes to `master`, weekly, or manually from
the [Actions page](https://github.com/HiDiHo01/brink/actions). See `AGENTS.md` for
the exact commands and validation scope.

- [Repository policy](AI_POLICY.md)
- [Contributor instructions, architecture, and checks](AGENTS.md)
- [Localization guide](LOCALIZATION.md)
- [Home Assistant engineering requirements](home-assistant.md)

### WORKING ON:
- Brink Renovent 180
- Brink Renovent 300
- Brink Renovent 400 Plus
- Brink Flair 300
- Brink Flair 325
- Please tell me, it should work with all Brink ventilation systems
