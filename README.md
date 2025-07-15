# EnvHub CLI

A command-line interface tool for managing environment variables with encryption and role-based access control.

## Features

- Secure environment variable management
- Role-based access control (owner, user, admin)
- Project-based environment variable organization
- Encryption of sensitive data
- CLI interface with Typer for user-friendly interaction

## Installation

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

## Commands

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
```

### Environment Variables
```bash
# Add a new environment variable
envhub add

# Pull environment variables from remote
envhub pull

# List all environment variables
envhub list

# Execute command with decrypted environment
envhub decrypt [command]
```

## Security Features

- All environment variables are encrypted
- Role-based access control for different levels of access
- Secure password management
- Project isolation for environment variables

## Usage Examples

```bash
# Add a new environment variable
envhub add

# Execute a command with decrypted environment
envhub decrypt "python app.py"

# List all environment variables
envhub list
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
