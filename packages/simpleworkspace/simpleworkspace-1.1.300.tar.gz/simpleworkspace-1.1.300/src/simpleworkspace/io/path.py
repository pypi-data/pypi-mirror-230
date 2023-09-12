import os as _os

def FindEmptySpot(filepath: str):
    from simpleworkspace.io.file import FileInfo

    fileContainer = FileInfo(filepath)
    TmpPath = filepath
    i = 1
    while _os.path.exists(TmpPath) == True:
        TmpPath = f"{fileContainer.Tail}{fileContainer.Filename}_{i}{fileContainer.FileExtension}"
        i += 1
    return TmpPath

def GetAppdataPath(appName=None, companyName=None):
    """
    Retrieves roaming Appdata folder.\n
    no arguments        -> %appdata%/\n
    appName only        -> %appdata%/appname\n
    appname and company -> %appdata%/appname/companyName\n
    """
    from simpleworkspace.types.os import OperatingSystemEnum
    

    currentOS = OperatingSystemEnum.GetCurrentOS()
    if currentOS == OperatingSystemEnum.Windows:
        pathBuilder = _os.getenv('APPDATA')
    elif currentOS == OperatingSystemEnum.MacOS:
        pathBuilder = _os.path.expanduser('~/Library/Application Support/')
    else:
        pathBuilder = _os.getenv('XDG_DATA_HOME', _os.path.expanduser("~/.local/share"))

    if(companyName is not None):
        pathBuilder = _os.path.join(pathBuilder, companyName)
    if(appName is not None):
        pathBuilder = _os.path.join(pathBuilder, appName)
    return pathBuilder
    
