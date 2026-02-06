# Telegram Key Finder & Uploader

This tool scans specified Telegram groups and channels for VPN configuration strings (vless, vmess, ss, etc.), extracts them, and uploads the consolidated list to Google Drive. I used it to automate the gathering of free configs to be able to access informations at any times in highly restrictive Network Firewall environments.


## Features
- **Telegram Scanning**: Monitors "Network" folder dialogs and specified channels.
- **Auto-Extraction**: regex-based extraction of valid VPN config links.
- **Google Drive Upload**: Authenticates with Google and uploads/updates a text file with the configs.
- **Secure Config**: Uses `.env` for all credentials.

## Prerequisites
- Python 3.8+
- A Telegram API ID and Hash (from [my.telegram.org](https://my.telegram.org))
- A Google Cloud Project with Drive API enabled and OAuth 2.0 Client ID (download `client_secrets.json`).

## Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/SapaAtayev/key-finder.git
   cd key-finder
   ```

2. **Run Setup Script**
   This will create the virtual environment, install dependencies, and help you create the `.env` file.
   ```bash
   chmod +x setup.sh launch.sh
   ./setup.sh
   ```

3. **Google Auth**
   Place your `client_secrets.json` file in the project root.

## Usage

Run the main script:
```bash
./launch.sh
```

On the first run, you will be prompted to:
1. Log in to Telegram (phone number + code).
2. Authenticate with Google (browser link + copy-paste code).

Subsequent runs will use the saved session and token files.

## Configuration

Edit `.env` to change settings:
- `MONITOR_USER_LIST`: Comma-separated list of extra channels/groups to scan.
- `FORWARD_CHANNEL_ID`: ID of a channel to forward found messages to.
- `GDRIVE_FOLDER_IDS`: Specific Drive folder(s) to upload the file to.

## Project Structure
- `main.py`: Main logic, Telegram client, and orchestration.
- `extract_configs.py`: Config extraction regex and Google Drive upload logic.
- `launch.sh`: Entry point for running the bot.
- `setup.sh`: Installation helper.
