# services/backup_service.py

import os
import datetime
import requests
import dropbox

APP_KEY = "73utd2tnk4zkete"
APP_SECRET = "ce94goh0jy5szye"
REFRESH_TOKEN = "nvRhkiuOOjQAAAAAAAAAAYzFEdFvN2MQ6KMGoDe2Pq179abzz-ypLGB0LdQd9nFY"

DB_FILE = "crm_database.db"
BACKUP_FOLDER = "/crm_backups"


def get_access_token():
    url = "https://api.dropboxapi.com/oauth2/token"

    data = {
        "grant_type": "refresh_token",
        "refresh_token": REFRESH_TOKEN
    }

    auth = (APP_KEY, APP_SECRET)

    response = requests.post(url, data=data, auth=auth)
    token_data = response.json()

    if "access_token" not in token_data:
        raise Exception(f"Dropbox Auth Error: {token_data}")

    return token_data["access_token"]


def get_dbx():
    access_token = get_access_token()
    return dropbox.Dropbox(access_token)


# ========================
# BACKUP
# ========================
def backup_database():

    if not os.path.exists(DB_FILE):
        return "DB not found"

    dbx = get_dbx()

    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")

    backup_name = f"crm_backup_{timestamp}.db"
    dropbox_path = f"{BACKUP_FOLDER}/{backup_name}"

    with open(DB_FILE, "rb") as f:
        dbx.files_upload(
            f.read(),
            dropbox_path,
            mode=dropbox.files.WriteMode.overwrite
        )

    cleanup_old_backups(dbx)

    return backup_name


# ========================
# CLEANUP (keep last 10)
# ========================
def cleanup_old_backups(dbx, keep=10):

    files = dbx.files_list_folder(BACKUP_FOLDER).entries

    files = [f for f in files if isinstance(f, dropbox.files.FileMetadata)]

    if len(files) <= keep:
        return

    files.sort(key=lambda x: x.client_modified)

    for old_file in files[:-keep]:
        dbx.files_delete_v2(old_file.path_lower)


# ========================
# LIST BACKUPS
# ========================
def list_backups():

    dbx = get_dbx()

    files = dbx.files_list_folder(BACKUP_FOLDER).entries

    backups = [
        f.name for f in files
        if isinstance(f, dropbox.files.FileMetadata)
    ]

    backups.sort(reverse=True)

    return backups


# ========================
# RESTORE BACKUP
# ========================
def restore_backup(filename):

    dbx = get_dbx()

    dropbox_path = f"{BACKUP_FOLDER}/{filename}"

    metadata, res = dbx.files_download(dropbox_path)

    with open(DB_FILE, "wb") as f:
        f.write(res.content)

    return "Restored successfully"
    
# ========================
# GET BACKUP DETAILS
# ========================
def get_backup_details():

    dbx = get_dbx()

    files = dbx.files_list_folder(BACKUP_FOLDER).entries

    backups = [
        f for f in files
        if isinstance(f, dropbox.files.FileMetadata)
    ]

    backups.sort(key=lambda x: x.client_modified, reverse=True)

    return backups


# ========================
# DOWNLOAD BACKUP
# ========================
def download_backup(filename):

    dbx = get_dbx()

    path = f"{BACKUP_FOLDER}/{filename}"

    metadata, res = dbx.files_download(path)

    return res.content
    
def get_last_backup_time():
    dbx = get_dbx()

    files = dbx.files_list_folder(BACKUP_FOLDER).entries

    backups = [
        f for f in files
        if isinstance(f, dropbox.files.FileMetadata)
    ]

    if not backups:
        return None

    backups.sort(key=lambda x: x.client_modified, reverse=True)

    return backups[0].client_modified.replace(tzinfo=None)