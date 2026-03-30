# AI Employee Vault - Multi-Tier Architecture

## Project Structure

This project is organized into three progressive tiers:

### Bronze Tier - Email-Only Automation
Basic email monitoring, processing, and reply drafting.
- **Location**: `Bronze-Tier/`
- **Status**: Complete ✅
- **Features**: Gmail watcher, email processor, task extraction

### Silver Tier - Multi-Source Automation
Adds WhatsApp and LinkedIn automation.
- **Location**: `Silver-Tier/`
- **Status**: Complete ✅
- **Features**: WhatsApp watcher, LinkedIn poster, multi-source orchestration

### Gold Tier - Automated Email Workflow
Complete automation with email sending and advanced workflows.
- **Location**: `Gold-Tier/` (Active Workspace)
- **Status**: In Development 🚧
- **Features**: Email sender, approval workflow, scheduling

## Quick Start

### For Development (Gold Tier)
```bash
cd Gold-Tier
python run_all_watchers.py
```

### For Testing Bronze Features
```bash
cd Bronze-Tier
python Watchers/gmail_watcher.py
```

### For Testing Silver Features
```bash
cd Silver-Tier
python Watchers/whatsapp_watcher.py
```

## Configuration

Root-level configuration files:
- `.env` - SMTP and API credentials
- `.env.example` - Template for credentials
- `credentials.json` - Gmail API credentials
- `token.json` - Gmail OAuth token
- `pyproject.toml` - Python dependencies

## Installation

```bash
# Install dependencies
uv pip install -e . --system

# Install Playwright (for Silver/Gold)
playwright install chromium
```

## Documentation

Each tier has its own README with specific instructions:
- `Bronze-Tier/README.md`
- `Silver-Tier/README.md`
- `Gold-Tier/README.md`

## Git Workflow

```bash
# Push changes
./push_to_github.sh "Your commit message"
```

## Support

See tier-specific documentation for troubleshooting:
- Bronze: `Bronze-Tier/TROUBLESHOOTING.md`
- Silver: `Silver-Tier/WHATSAPP_TROUBLESHOOTING.md`
- Gold: `Gold-Tier/TEST_EMAIL_SENDER.md`
