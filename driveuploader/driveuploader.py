#!/usr/bin/env python3.5
#####################################
#    LAST UPDATED     14 DEC 2017   #
#####################################
"""
Once a month, zips a folder and uploads it to Google Drive
"""
import os
import datetime
from zipfile import ZipFile
from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth
from pushbullet import PushBullet


def push(title: str, body: str=None) -> None:
    """
    Push a message to iPhone
    :param title: Title of the message to push
    :param body: Body of the message to push

    """
    with open('/Users/Alex/Documents/Python3/driveuploader/pushbullet_token.txt') as files:
        token = files.read().strip()
    pb = PushBullet(token)
    pb.push_note('{}'.format(title), '{}'.format(body), device=pb.get_device('iPhone'))


def harddrives_connected(path: str) -> bool:
    """
    Determine if the hard drives are connected to determine if the backup can take place
    :param path: Path to the source folder to zip
    :return: bool
    """
    if os.path.exists(path):
        return True
    else:
        push('Goolge Drive Photos backup could not happen', 'Plug in the hard drives!')
        return False


def zip_folder(folder: str, path: str, zipfilename: str) -> bool:
    """
    Zip the Photos folder on /Volumes/MAC2/Photos/
    :param folder: Path of the folder you want to backup
    :param path: Path where you want to backup the zip
    :param zipfilename: Name of the zipped file
    :return: None
    """
    if os.path.exists(folder) and os.path.exists(path):
        os.chdir(path)

        # create the ZIP file
        print('Creating {}...'.format(zipfilename))

        backupzip = ZipFile(zipfilename, 'w', allowZip64=True)

        for foldername, __, filenames in os.walk(folder):
            # Add the current folder to the ZIP file.
            backupzip.write(foldername)
            # Add all the files in this folder to the ZIP file.
            for filename in filenames:
                if not filename.startswith('.DS'):
                    backupzip.write(os.path.join(foldername, filename))

        backupzip.close()
        abspath = os.path.abspath(__file__)
        dname = os.path.dirname(abspath)
        os.chdir(dname)
        return True
    else:
        return False


def manage_google_drive(path: str, zipfilename: str, parent_folder_id: str) -> bool:
    """
    Delete the old Photos file and upload the new one
    :param path: Path to ZIP file
    :param zipfilename: Name of the zipped file
    :param parent_folder_id: Folder ID of the parent folder to upload the file
    :return: bool of whether the file has been uploaded
    """
    # Authenticate!
    gauth = GoogleAuth()

    drive = GoogleDrive(gauth)

    # Figure out which file needs to be deleted
    old_filename = 'Photos {0:%b %Y}.zip'.format(datetime.datetime.now() - datetime.timedelta(days=25))

    upload_file = drive.CreateFile({'title': zipfilename,
                                   'parents': [{u'id': parent_folder_id}]})
    upload_file.SetContentFile(path)
    upload_file.Upload()

    file_list = drive.ListFile({'q': "'0B2jADZue7Al4dy0ydVVkay1TMDg' in parents and trashed=false"}).GetList()
    for file1 in file_list:
        if file1['title'] == old_filename:
            file1.Delete()
            return True
    return False


def main() -> None:
    """
    Runs the script. Returns nothing
    :return: None
    """
    source = '/Volumes/MAC2/Photos/'
    destination = '/Users/Alex/Desktop/'
    if harddrives_connected(source):
        name = 'Photos {0:%b %Y}.zip'.format(datetime.datetime.now())
        zip_folder(source, destination, name)
        parent_id = '0B2jADZue7Al4dy0ydVVkay1TMDg'
        manage_google_drive(os.path.join(destination, name), name, parent_id)
        os.unlink(os.path.join(destination, name))


if __name__ == '__main__':
    main()
