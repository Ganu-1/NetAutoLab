# NetAutoLab

NetAutoLab is a hands-on **Network Automation Learning Platform** designed to help network engineers learn and practice network automation in a real lab environment.

The project focuses on practical automation using **Python, SSH, Netmiko, ArubaOS-CX, configuration backups, snapshots, and restore workflows**.

The goal is to gradually evolve NetAutoLab from a simple network automation lab into a structured platform for learning and practicing real-world network automation.

---

## 🚀 What is NetAutoLab?

NetAutoLab provides a command-line interface called `labdoctor` for common network automation and lab-management tasks.

Current capabilities include:

- Environment diagnostics
- Inventory management
- Device connectivity testing
- SSH connectivity testing
- Network device configuration backup
- Backup snapshot management
- Restore validation
- Restore preview
- Configuration restore
- Automatic pre-restore backups
- ArubaOS-CX device support

---

## 🏗️ Current Architecture

```text
NetAutoLab
│
├── Python Application
├── Device Inventory
├── SSH / Netmiko
├── Provider Architecture
│   └── ArubaOS-CX
├── Backup Engine
│   └── Snapshot Management
├── Restore Engine
│   ├── Validation
│   ├── Preview
│   └── Apply
└── CLI
    └── labdoctor
```

The provider-based architecture allows additional network platforms to be added in the future.

---

## 🛠️ Technology Stack

- **Python**
- **Netmiko**
- **Typer**
- **Rich**
- **PyYAML**
- **Git / GitHub**
- **ArubaOS-CX**
- **SSH**

---

## 📋 Current Features

### Environment Diagnostics

```bash
labdoctor doctor
```

### Device Inventory

```bash
labdoctor inventory
```

### Device Connectivity

```bash
labdoctor ping
```

### SSH Connectivity

```bash
labdoctor ssh test
```

---

## 💾 Configuration Backup

NetAutoLab can collect the running configuration from supported network devices and store it as a timestamped snapshot.

```bash
labdoctor backup
```

Example:

```text
backups/
└── 2026-08-17_14-59-43/
    ├── configs/
    │   └── cx-01.cfg
    └── manifest.json
```

The snapshot contains the device configuration and metadata describing the backup operation.

---

## 🔄 Restore Workflow

NetAutoLab uses a staged restore workflow designed to reduce the risk of accidental configuration changes.

### 1. Validate

Validate that a snapshot can be restored without changing the device.

```bash
labdoctor restore validate 2026-08-17_14-59-43 cx-01
```

Validation checks include:

- Snapshot availability
- Device availability
- Backup status
- Configuration file existence
- Configuration file validity
- Platform compatibility
- SSH connectivity

### 2. Preview

Preview the configuration that would be restored.

```bash
labdoctor restore preview 2026-08-17_14-59-43 cx-01
```

Preview mode **does not modify the device**.

### 3. Apply

Without confirmation, the restore is not applied:

```bash
labdoctor restore apply 2026-08-17_14-59-43 cx-01
```

To actually apply the configuration:

```bash
labdoctor restore apply 2026-08-17_14-59-43 cx-01 --yes
```

Before applying the restore, NetAutoLab automatically creates a **pre-restore backup**.

---

## 🔐 Safety Design

The restore workflow follows multiple safety layers:

```text
Snapshot
   │
   ▼
Validate
   │
   ▼
Preview
   │
   ▼
Explicit --yes
   │
   ▼
Pre-Restore Backup
   │
   ▼
Apply Configuration
```

Validation and preview do not modify the target device.

The actual restore requires explicit confirmation using `--yes`.

A pre-restore backup is created before configuration changes are applied.

---

## 🌐 Current Platform Support

### ArubaOS-CX

Current provider:

```text
aruba_aoscx
```

The current lab has been tested with an ArubaOS-CX virtual switch.

Example device:

```text
Device:   cx-01
Platform: aruba_aoscx
Host:     192.168.211.130
```

---

## 📁 Project Structure

```text
NetAutoLab/
│
├── src/
│   └── netautolab/
│       ├── backup/
│       │   ├── engine.py
│       │   ├── manifest.py
│       │   ├── restore.py
│       │   └── storage.py
│       ├── commands/
│       ├── models/
│       │   └── device.py
│       ├── providers/
│       │   ├── aruba.py
│       │   ├── base.py
│       │   └── registry.py
│       ├── cli.py
│       ├── config.py
│       ├── connectivity.py
│       ├── doctor.py
│       ├── inventory.py
│       └── ssh.py
│
├── backups/
├── inventory/
├── tests/
├── pyproject.toml
└── README.md
```

---

## 🎯 Project Goals

NetAutoLab is being developed as a practical learning project focused on real-world network automation.

Planned areas include:

- Network device facts collection
- Configuration compliance
- Configuration diff
- Multi-device operations
- Additional network platforms
- Automated validation
- Structured logging
- Testing
- Ansible integration
- NetBox integration
- Advanced automation workflows

These capabilities will be introduced incrementally.

---

## 🧪 Lab Environment

The project is currently developed and tested in a virtual network automation lab containing:

- EVE-NG
- VMware
- ArubaOS-CX virtual switch
- Ubuntu
- Python virtual environment
- Netmiko
- NetAutoLab CLI

The environment is intended for learning, experimentation, automation development, and testing.

---

## 🚦 Project Status

**Active Development**

Current milestone:

> **Configuration Backup → Snapshot → Restore Validation → Restore Preview → Restore Apply**

The restore workflow has been successfully tested against the ArubaOS-CX lab device.

---

## 📌 Important Note

NetAutoLab is primarily a **learning and laboratory project**.

Always test automation against a controlled lab environment before using similar workflows in a production network.

Never restore a configuration to a production device without appropriate validation, backups, change control, and recovery procedures.

---

## 👨‍💻 Development

Clone the repository:

```bash
git clone <repository-url>
cd NetAutoLab
```

Create and activate the Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the project:

```bash
pip install -e .
```

Verify the installation:

```bash
labdoctor --help
```

---

## 📄 License

See the repository license for licensing information.

---

## ⭐ Vision

The long-term goal of NetAutoLab is to create a structured, practical environment where network engineers can learn automation by building real capabilities step by step.

Instead of learning automation concepts only theoretically, the project focuses on implementing workflows that resemble real network engineering tasks.

**Learn → Automate → Validate → Improve**
