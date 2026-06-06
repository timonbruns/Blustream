# Blustream MFP62 – Home Assistant Integration

Home Assistant integration for the **Blustream MFP62** (6 inputs, 2 outputs,
multi-format presentation switch).

## Installation

1. Copy the `blustream` folder into `config/custom_components/`, so that
   `config/custom_components/blustream/__init__.py` exists.
2. **Restart** Home Assistant (not just "reload integration", since the
   Python files have changed).
3. Go to *Settings → Devices & Services → Add Integration* and select
   "Blustream".

## Setup

The wizard asks, in this order:

1. **Which Blustream product?** – currently only "Blustream MFP62".
2. **Connection** – IP address, port (default 23), name.
3. **Name the inputs** – pre-filled with HDMI 1/2/3, DisplayPort, USB-C, VGA.
4. **Name the outputs** – Output 1 / Output 2.

The number of inputs/outputs is no longer asked – it is derived from the
device model.

## Entities created

| Type         | Function                                   | Command             |
|--------------|--------------------------------------------|---------------------|
| media_player | Source, volume, mute, power                | `OUT 01 FR yy`, `VOL`, `MUTE`, `PON/POFF` |
| switch       | Output 1 on/off                            | `OUT 01 ON/OFF`     |
| switch       | Output 2 on/off                            | `OUT 02 ON/OFF`     |
| switch       | Auto switching                             | `OUT AUTO ON/OFF`   |
| switch       | Microphone mute                            | `MIC MUTE ON/OFF`   |
| number       | Microphone volume                          | `MIC VOL xx`        |
| select       | Microphone mix                             | `MIC MIX mm`        |
| select       | Output resolution                          | `OUT RES rr`        |
| button (x6)  | Direct source selection                    | `OUT 01 FR yy`      |

> Note: Both HDMI outputs of the MFP62 always show the **same** source
> (mirrored). Only the **on/off** state of the two outputs can be switched
> independently.

## Status polling

The integration queries the `STATUS` command every **5 minutes** to pick up
external changes (e.g. made via the web GUI). When you switch from within
Home Assistant, the display updates immediately – the polling is only a
safety net.

The interval can be changed in `const.py` via `DEFAULT_SCAN_INTERVAL`
(value in seconds).

## Fine-tuning the STATUS parser (optional)

The exact output format of the `STATUS` command is not publicly documented.
The included parser (`coordinator.py`) is therefore deliberately cautious: it
only adopts values it can clearly recognize and leaves everything else at the
last value that was set.

If you want to read the real status optimally:

1. Enable debug logging in `configuration.yaml`:

   ```yaml
   logger:
     default: warning
     logs:
       custom_components.blustream: debug
   ```

2. Restart Home Assistant and wait ~5 minutes (or reload the integration).
3. In the log, look for the line with the raw `STATUS` response
   (`Antwort auf 'STATUS' ...`).
4. Share that output and the regular expressions in the parser can be tuned
   precisely to the MFP62's format.

## Command format

All commands are sent in the documented format, with spaces and a trailing
carriage return (e.g. `OUT 01 FR 02`). If a single command does not respond,
the command strings are kept centrally in `media_player.py`, `switch.py`,
`select.py`, `number.py` and `button.py` and are easy to adjust.
