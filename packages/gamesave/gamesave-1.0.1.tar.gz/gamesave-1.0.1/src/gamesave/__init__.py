"""A library for saving base64 files in a customisable way."""

import base64
import os

global saveDir
global fileExt
global useBase64
global fileEncodec

saveDir = "saves/"
fileExt = ""
useBase64 = False
fileEncodec = "UTF-8"

def edit_settings(saveDirectory="saves/", saveFilenameExtention="", autoEncodeBase64=False,
                fileCodec="UTF-8"):
    
    """Edits the save settings like where to save files and what file name extention they are."""

    global saveDir
    global fileExt
    global useBase64
    global fileEncodec

    if saveDirectory[-1] != "/":
        saveDirectory = f"{saveDir}/"
    
    if len(saveFilenameExtention) > 0 and saveFilenameExtention[0] != ".":
        saveFilenameExtention = f".{saveFilenameExtention}"

    saveDir = saveDirectory
    fileExt = saveFilenameExtention
    useBase64 = autoEncodeBase64
    fileEncodec = fileCodec

def get_saves():
    """Returns a tuple containing strings of all the save file names in the configured directory."""

    return tuple(os.listdir(saveDir))

def create_save(savename: str, initialData=""):
    """Creates a blank new save file, using the configured settings.
    
    The initialData paramater writes data into the new save file.
    
    If the save file already exists, this raises a FileExistsError."""

    if not os.path.exists(saveDir):
        os.mkdir(saveDir)
    
    if os.path.exists(f"{saveDir}{savename}{fileExt}"):
        raise FileExistsError("save file already exists")

    with open(f"{saveDir}{savename}{fileExt}", "x", encoding=fileEncodec) as f:
        if useBase64:
            f.write(base64.encodebytes(bytes(initialData, fileEncodec)).decode())
        else:
            f.write(initialData)

def read_save(savename: str):
    """Reads and decodes a save file in the configured directory."""

    with open(f"{saveDir}{savename}{fileExt}", "r", encoding=fileEncodec) as f:
        if useBase64:
            return base64.decodebytes(bytes(f.read(), fileEncodec)).decode()
        else:
            return f.read()

def write_save(savename: str, data: str):
    """Overwrites a file while respecting configured settings."""

    with open(f"{saveDir}{savename}{fileExt}", "w", encoding=fileEncodec) as f:
        if useBase64:
            f.write(base64.encodebytes(bytes(data, fileEncodec)).decode())
        else:
            f.write(data)
