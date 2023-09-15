"""A library for saving base64 files in a customisable way."""

import base64
import os

global saveDir
global fileExt
global useBase64

saveDir = "saves/"
fileExt = ""
useBase64 = False

def edit_settings(saveDirectory="", saveFilenameExtention="", autoEncodeBase64=False):
    """Edits the save settings like where to save files and what file name extention they are."""

    global saveDir
    global fileExt
    global useBase64

    if saveDirectory != "":
        if saveDirectory[-1] != "/" or saveDirectory[-1] != "\\":
            saveDirectory = f"{saveDirectory}/"

        saveDir = saveDirectory

    if saveFilenameExtention != "":
        if saveFilenameExtention[0] != ".":
            saveFilenameExtention = f".{saveFilenameExtention}"

        fileExt = saveFilenameExtention

    useBase64 = autoEncodeBase64

def get_saves():
    """Returns a tuple containing strings of all the save file names in the configured directory."""

    return tuple(os.listdir(saveDir))

def create_save(savename: str, initialData=""):
    """Creates a blank new save file, using the configured settings.
    
    The initialData paramater is the data initially (If encoding with
    base64, make sure your initialData is in UTF-8.)
    
    If the save file already exists, this raises a FileExistsError."""

    if not os.path.exists(saveDir):
        os.mkdir(saveDir)
    
    if os.path.exists(f"{saveDir}{savename}{fileExt}"):
        raise FileExistsError("save file already exists")
    
    with open(f"{saveDir}{savename}{fileExt}", "x") as f:
        if useBase64:
            f.write(base64.encodebytes(bytes(initialData, "UTF-8")).decode())
        else:
            f.write(initialData)

def read_save(savename: str):
    """Reads and decodes a save file in the configured directory."""

    with open(f"{saveDir}{savename}{fileExt}", "r") as f:
        if useBase64:
            return base64.decodebytes(bytes(f.read(), "UTF-8")).decode()
        else:
            return f.read()

def write_save(savename: str, data: str):
    """Overwrites a file while respecting configured settings."""

    with open(f"{saveDir}{savename}{fileExt}", "w") as f:
        if useBase64:
            f.write(base64.encodebytes(bytes(data, "UTF-8")).decode())
        else:
            f.write(data)
