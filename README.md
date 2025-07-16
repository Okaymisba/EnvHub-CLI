<div align="center">
<img src="https://envhub.net/favicon.ico" alt="EnvHub Logo" width="100">
</div>

# EnvHub CLI

[![License: MPL 2.0](https://img.shields.io/badge/License-MPL%202.0-brightgreen.svg)](https://opensource.org/licenses/MPL-2.0)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

A command-line interface for the EnvHub platform, providing secure environment variable management with encryption and role-based access control.

## Overview

EnvHub is a comprehensive platform for managing environment variables across your development projects. This repository contains the CLI component that works alongside the web interface to provide a seamless experience for managing environment variables securely.

## Features

- 🔒 End-to-End Encryption - Your environment variables are encrypted before they leave your machine
- 👥 Team Collaboration - Securely share environment variables with your team members
- 📱 Cross-Platform - Access your environment variables from anywhere, on any device
- 🛡️ Access Control - Granular permissions for team members and projects
- 📊 Version History - Track changes and roll back to previous versions when needed

## Installation

Install using pip:

```bash
pip install envhub-cli
```

Or if your environment is externally managed:

```bash
pipx install envhub-cli
```

Or install from source:

1. Clone the repository:
```bash
git clone https://github.com/Okaymisba/EnvHub-CLI.git
```

2. Create a virtual environment and activate it:
```bash
python -m venv .venv
source .venv/bin/activate  # On Unix/macOS
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Authentication
```bash
# Login to your account
envhub login

# Logout from your account
envhub logout

# Check current logged-in user
envhub whoami
```

### Project Management
```bash
# Clone a project
envhub clone <project-name>

# Reset current folder
envhub reset

# Pull latest environment variables
envhub pull
```

## Documentation

For detailed documentation, please visit our [Documentation Website](https://envhub.net/docs).

## Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are greatly appreciated.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the Mozilla Public License 2.0 - see the LICENSE file for details.

## Contact

Misbah Sarfraz - [@myLinkedIn](https://www.linkedin.com/in/misbah-sarfaraz-a59854325/) - msbahsarfaraz@gmail.com

Project Link: [https://github.com/okaymisba/envhub](https://github.com/yourusername/envhub)

## Acknowledgments

- [Typer](https://typer.tiangolo.com/) for the amazing CLI framework
- [Supabase](https://supabase.com/) for real-time database integration
- [Python-dotenv](https://github.com/theskumar/python-dotenv) for environment variable management
- [Cryptography](https://cryptography.io/) for secure encryption
- [Hatchling](https://github.com/hatch-python/hatchling) for modern Python packaging
- All the amazing open-source contributors

---
