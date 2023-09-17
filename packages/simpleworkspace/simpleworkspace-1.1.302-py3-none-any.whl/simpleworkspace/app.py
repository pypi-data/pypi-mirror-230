class App():
    @classmethod
    def Setup(cls, appName:str, appCompany:str=None, appID:str=None):
        '''
        :param appID: 
            supply an id(such as a random guid) to be able to uniquely identify this app, 
            if not supplied appname+appcompany will be used as id
        '''

        import os
        import simpleworkspace.io.directory
        import simpleworkspace.io.path
        from simpleworkspace.logproviders import RotatingFileLogger
        from simpleworkspace.settingsproviders import SettingsManager_JSON
        from hashlib import md5
        
        if(appName is None or appName == ''):
            raise ValueError("appname cannot be left empty")
        
        cls.appName = appName
        cls.appCompany = appCompany

        if(appID is None):
            appID = appName
            if(appCompany is not None):
                appID += cls.appCompany
        
        cls.appID = md5((appID).encode()).hexdigest()[:16]
    
        cls.path_AppData = simpleworkspace.io.path.GetAppdataPath(appName, appCompany)
        ''''C:\\Users\\username\\AppData\\Roaming\\AppCompany\\AppName'''
        cls.path_AppData_Storage = os.path.join(cls.path_AppData, "storage")
        '''windows example: 'C:\\Users\\username\\AppData\\Roaming\\AppCompany\\AppName\\Storage'''
        simpleworkspace.io.directory.Create(cls.path_AppData_Storage) # creates parent folders aswell
        
        cls._path_LogFile = os.path.join(cls.path_AppData, "app.log")
        cls.logger = RotatingFileLogger.GetLogger(cls._path_LogFile, registerGlobalUnhandledExceptions=True)

        cls.settingsManager = SettingsManager_JSON(os.path.join(cls.path_AppData, "config.json"))
        cls.settingsManager.LoadSettings()


    @classmethod
    def PreventMultipleInstances(cls):
        cls.__EnsureInitialized()

        import os
        import tempfile
        
        lock_file_path = os.path.join(tempfile.gettempdir(), f"py_{cls.appID}.lock")
        try:
            if(os.path.exists(lock_file_path)):
                os.remove(lock_file_path)
            cls.__mutexlock_fh = open(lock_file_path, "w")
        except OSError as ex:
            if(ex.errno == 13):
                exit("Another instance is already running... exiting()")
            raise  #something unexpected went bad, let the exception rise upwards 


    @classmethod
    def __EnsureInitialized(cls):
        if not hasattr(cls, "appID"):
            raise ValueError("Incorrect Usage, Call App.Setup() first.")
        