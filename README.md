[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

# Satel Integra 2026 — Home Assistant integration (fork by sjauquet)

Fork of [alessioburgassi/ha_satel_integra_ext](https://github.com/alessioburgassi/ha_satel_integra_ext), itself based on [wasilukm/alt_ha_satel_integra](https://github.com/wasilukm/alt_ha_satel_integra).

---

## What this fork adds

- **UI configuration** — no `configuration.yaml` editing needed
- **Auto-discovery** — zones, partitions and outputs are discovered automatically from the panel at first setup and cached for instant restarts
- **ETHM-1 support** — polling mode (100 ms) for the original module; ETHM-1 Plus uses push/event mode
- **Device grouping** — all entities appear under a single HA device "Satel Integra 2026"
- **YAML backward compatibility** — `configuration.yaml` setup still works if preferred

---

## Supported entity types

| Type | Description |
|------|-------------|
| `alarm_control_panel` | One per partition — arm/disarm |
| `binary_sensor` | Zones (violated, alarm, tamper, mask, bypass...) and outputs |
| `switch` | Switchable/programmable outputs (YAML config only) |

> **Tested hardware:** ETHM-1 Plus only. ETHM-1 (original polling mode) is included from the upstream codebase but has **not been tested** — use at your own risk.
| `sensor` | Temperature sensors (if configured) |

---

## Installation via HACS

1. In HACS, go to **Integrations** → menu → **Custom repositories**
2. Add `https://github.com/sjauquet/ha_satel_integra_ext` as type **Integration**
3. Install **Satel Integra 2026**
4. Restart Home Assistant
5. Go to **Settings → Devices & Services → Add Integration** → search "Satel Integra"
6. Fill in the connection form (module type, IP, port, optional alarm code)

The integration connects, validates the connection, discovers all zones/partitions/outputs, and creates the entities automatically. **Discovery runs at first setup only** — subsequent restarts load from cached data instantly.

> **Note:** The alarm code is only required to control switchable/programmable outputs.

---

## Manual installation

1. Copy `custom_components/satel_integra` to your HA `config/custom_components/` folder
2. Restart Home Assistant
3. Add via the UI (Settings → Devices & Services → Add Integration)

---

## Re-discovery

If the panel configuration changes (new zones added, etc.), delete the integration entry in the UI and re-add it. Discovery runs automatically on first setup.

---

## YAML configuration (backward compatible)

The original YAML configuration is still supported. Add a `satel_integra:` section to `configuration.yaml`:

```yaml
satel_integra:
  host: 192.168.1.200
  port: 7094
  code: 1234
  # Optional: integration key for AES encryption (ETHM-1 Plus only)
  integration_key: ""
  partitions:
    01:
      name: "Home"
      arm_home_mode: 2
    02:
      name: "Garden"
  zones:
    01:
      name: "Living room"
      type: "motion"
      mask: "yes"
    02:
      name: "Front door"
      type: "opening"
    06:
      name: "Smoke detector"
      type: "smoke"
  outputs:
    35:
      name: "Siren"
  switchable_outputs:
    235:
      name: "Kitchen"
    237:
      name: "Oven"
  expander:
    0:
      name: "Expander bus 1 #0"
      battery: "yes"
  trouble:
    7:
      name: "Battery fault"
    8:
      name: "AC fault"
  keypad:
    0:
      name: "Keypad 0"
```

### YAML configuration variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `host` | yes | — | IP address or hostname of the ETHM module |
| `port` | no | 7094 | TCP port |
| `code` | no | — | Alarm code (needed for switchable outputs) |
| `integration_key` | no | — | AES encryption key (ETHM-1 Plus only) |
| `partitions` | no | auto | Map of partition IDs → `name`, `arm_home_mode` (1/2/3) |
| `zones` | no | auto | Map of zone IDs → `name`, `type`, `mask` |
| `outputs` | no | auto | Map of output IDs → `name` |
| `switchable_outputs` | no | — | Map of programmable output IDs → `name` |
| `expander` | no | — | Map of expander IDs → `name`, `battery` |
| `trouble` | no | — | Map of trouble IDs → `name` |
| `keypad` | no | — | Map of keypad IDs → `name` |

---

## Troubleshooting

- **No entities created**: check HA logs for `Discovery complete: X zones, Y partitions, Z outputs`. If all zeros, the ETHM module may not be responding to device name queries.
- **Partitions missing**: check logs for `Partition X (type=0x00) query result:` lines.
- **Cannot connect**: verify IP address, port (default 7094), and that the ETHM module is reachable from HA.
- **"17 bytes read" warning in logs**: harmless artifact from the ETHM module on connection — can be ignored.

---

## Python library

This integration uses the `satel_integra2` library: [sjauquet/satel_integra2](https://github.com/sjauquet/satel_integra2)
