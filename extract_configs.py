import os
import re
import base64
import io
import logging
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from google.auth.exceptions import RefreshError

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Constants
SCOPES = ['https://www.googleapis.com/auth/drive.file']
DRIVE_FILENAME = 'vpn_config.txt'

def authenticate_google(client_secrets_file='client_secrets.json', token_file='token.json'):
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                logger.warning("Token expired and refresh failed. Re-authenticating...")
                if os.path.exists(token_file):
                    os.remove(token_file)
                creds = None
        
        if not creds:
            if not os.path.exists(client_secrets_file):
                logger.error(f"Client secrets file '{client_secrets_file}' not found.")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            
            # Using run_local_server which is standard for desktop apps
            # Note: This requires a browser. For headless, we might need a different flow or copy-paste token.
            try:
                creds = flow.run_local_server(port=0)
            except Exception as e:
                logger.error(f"Failed to run local server auth: {e}")
                return None

        with open(token_file, 'w') as token:
            token.write(creds.to_json())
            
    return creds

def extract_links(file_path):
    if not os.path.exists(file_path):
        logger.warning(f"Source file '{file_path}' does not exist.")
        return []

    valid_links = []
    regex = r'(?:vless|vmess|ss|trojan|hysteria|tuic)://\S+'
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
        matches = re.findall(regex, content, re.IGNORECASE)
        
        for link in matches:
            clean_link = link.rstrip(").],!?'\";:> ")
            clean_link = clean_link.split('<')[0] 
            
            if len(clean_link) > 15:
                valid_links.append(clean_link)
    
    return list(set(valid_links))

def update_drive_file(service, links, folder_ids=None):
    content_string = "\n".join(links)
    
    # If folder_ids are provided, we should probably upload to those folders.
    # The original script just searched globally. Let's respect the user's intent to upload to specific folders if possible.
    # However, for simplicity/legacy compatibility, we'll search for the file first.
    
    query = f"name = '{DRIVE_FILENAME}' and trashed = false"
    # If we want to restrict to a folder: f"'{folder_id}' in parents and name = ..."
    
    results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
    items = results.get('files', [])

    media = MediaIoBaseUpload(io.BytesIO(content_string.encode('utf-8')), mimetype='text/plain', resumable=True)

    if not items:
        # Create new file
        file_metadata = {'name': DRIVE_FILENAME}
        if folder_ids:
            # Add to the first folder in the list for now
            file_metadata['parents'] = [folder_ids[0]]
            
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        logger.info(f"Created new file on Drive (ID: {file.get('id')})")
    else:
        # Update existing file(s)
        # We update ALL found files with that name to keep them in sync? Or just the first?
        # Let's update the first one found.
        file_id = items[0]['id']
        service.files().update(fileId=file_id, media_body=media).execute()
        logger.info(f"Updated existing file on Drive (ID: {file_id})")

def run_extraction(source_file='extracted_codes.txt', client_secrets='client_secrets.json', folder_ids=None):
    logger.info("--- Starting Extraction ---")
    links = extract_links(source_file)
    logger.info(f"Found {len(links)} unique links.")
    
    if links:
        logger.info("--- Authenticating with Google ---")
        creds = authenticate_google(client_secrets_file=client_secrets)
        if not creds:
            logger.error("Authentication failed. Aborting upload.")
            return

        service = build('drive', 'v3', credentials=creds)
        
        logger.info(f"--- Uploading to {DRIVE_FILENAME} ---")
        update_drive_file(service, links, folder_ids)
        logger.info("Done!")
    else:
        logger.info("No links found to upload.")

if __name__ == '__main__':
    # When run directly, use defaults or env vars
    from dotenv import load_dotenv
    load_dotenv()
    
    secrets_file = os.getenv('GOOGLE_CLIENT_SECRETS_FILE', 'client_secrets.json')
    folders = os.getenv('GDRIVE_FOLDER_IDS', '').split(',')
    folders = [f.strip() for f in folders if f.strip()]
    
    run_extraction(client_secrets=secrets_file, folder_ids=folders)
