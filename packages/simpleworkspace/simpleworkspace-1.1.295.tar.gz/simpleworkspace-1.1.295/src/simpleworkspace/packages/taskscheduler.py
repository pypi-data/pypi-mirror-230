from logging import Logger as _Logger
from abc import ABC as _ABC
from datetime import datetime as _datetime, timedelta as _timedelta
from ..types.time import TimeSpan as _TimeSpan
from ..utility.linq import LINQ as _LINQ
from ..settingsproviders import SettingsManager_JSON as _SettingsManager_JSON
from ..utility.stopwatch import StopWatch as _StopWatch
from time import sleep as _sleep
import os as _os
from zlib import crc32 as _crc32
from ..utility import module as _module
from ..io import directory as _directory
from multiprocessing.pool import ThreadPool as _ThreadPool
import traceback as _traceback
from threading import Lock as _Lock
from typing import Callable as _Callable

class ITask(_ABC):
    '''
    Tasks needs to implement this interface to be loaded into task scheduler

    properties and methods for Derived classes:
        * task_interval
        * task_ignore
        * task_description
        * On_StartUp
        * On_Schedule 
    '''
    task_interval = None  # type: _TimeSpan
    '''Runs On_Schedule event per specified interval, example: TimeSpan(minute=2), would run the task once ever 2 minutes'''
    task_ignore = False
    '''Can ignore a task from triggering'''
    task_description = None
    '''A human friendly description that is logged alongside each action of this task'''
    _task_id = None #type: str
    '''An unique identifier for this task, is used to store persistant task states and for lookups'''

    def __init__(self) -> None:
        self._task_id = self.__class__.__module__ + "." + self.__class__.__name__
        self._task_nextSchedule = _datetime.min

    def On_StartUp(self) -> str|None:
        '''runs once per start of taskscheduler'''
        pass

    def On_Schedule(self) -> str|None:
        '''runs once per specified interval'''
        pass


class CommandTask(ITask):
    '''Premade task for running a simple command'''
    def __init__(self, interval:_TimeSpan, command:str|list[str]) -> None:
        from hashlib import md5
        import shlex

        super().__init__()

        self.task_interval = interval
        if isinstance(command, str):
            command = shlex.split(command)
        self.command = command
        commandStringRepresentation = ' '.join(command)
        self.task_description = commandStringRepresentation
        self._task_id = md5(commandStringRepresentation.encode()).hexdigest()[:16]

    
    def On_Schedule(self):
        import subprocess
        result = subprocess.run(self.command, text=True, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        
        message = ""
        if(result.returncode != 0): #something went bad
            stderr = result.stderr if result.stderr is not None else ""
            message += f"STDERR[{result.returncode}]: {stderr};"
        
        if(result.stdout):
            message += f"STDOUT: {result.stdout.rstrip()};"

        return message

class TaskSchedulerManager:
    def __init__(self, settingsPath: str, logger: _Logger) -> None:
        self.logger = logger
        self._settingsPath = settingsPath
        self._settingsManager = _SettingsManager_JSON(self._settingsPath)
        self._settingsManager.LoadSettings()
        self._lock_settingsManager = _Lock()
        self._tasks = {} #type: dict[str, ITask]
        '''all registered tasks'''
        self._FLAG_SAVESETTINGS = False
        self._FLAG_RUN = True
        self._config_RunIterationDelay = 1
        self._config_maxThreads = 6
        '''max threads to use for running tasks'''
        self._threading_activeTasks = set()
        self._lock_threading_activeTasks = _Lock()

    class _TaskResult:
        def __init__(self) -> None:
            self.stopwatch = _StopWatch()
            self.output = None #type:str
            self.error = None #type:str

        @property
        def ElapsedMS(self):
            return self.stopwatch.GetElapsedMilliseconds(decimalPrecision=2)

    def _RunTaskEvent(self, task: ITask, eventFunc: _Callable):
        with self._lock_threading_activeTasks:
            self._threading_activeTasks.add(task._task_id)

        eventName = eventFunc.__name__
        taskResult = self._TaskResult()
        taskResult.stopwatch.Start()

        taskTitle = task._task_id if not task.task_description else f'{task._task_id}({task.task_description})'
        try:
            output = eventFunc()
            taskResult.output = f"Event {eventName}[{taskResult.ElapsedMS} MS]: {taskTitle}"
            if(output):
                taskResult.output += f", Output: {output}"
        except Exception as e:
            taskResult.error = f"Event {eventName} FAILED[{taskResult.ElapsedMS} MS]: {taskTitle}, Error: {_traceback.format_exc()}"
        
        with self._lock_threading_activeTasks:
            self._threading_activeTasks.remove(task._task_id)
        return taskResult
    
        
    def _RunTaskEvent_OnStartUp(self, task: ITask):
        return self._RunTaskEvent(task, task.On_StartUp)
    
    def _RunTaskEvent_OnSchedule(self, task: ITask):
        results = self._RunTaskEvent(task, task.On_Schedule)
        self._ScheduledTask_SetNextSchedule(task)
        return results

    def _TaskThreadFinished(self, taskResult: _TaskResult):
        if(taskResult.error):
            self.logger.error(taskResult.error)
        else:
            self.logger.info(taskResult.output)
        return

    def Run(self):
        self._InitializeTasks()
        self.logger.info(f"Event Start")

        activeTaskList = _LINQ(self._tasks.values()) \
            .Where(lambda task: task.task_ignore == False) \
            .ToList()

        self._config_maxThreads = min(len(activeTaskList), self._config_maxThreads)
        pool = _ThreadPool(processes=self._config_maxThreads)
        

        #skip none overriden ones
        tasksWithStartUp = _LINQ(activeTaskList).Where(lambda task: task.On_StartUp.__func__ is not ITask.On_StartUp)
        taskResults = pool.map(self._RunTaskEvent_OnStartUp, tasksWithStartUp)
        #ensure all startup tasks are finished before continuing to onSchedule
        for taskResult in taskResults:
            self._TaskThreadFinished(taskResult)

        tasksWithSchedules = _LINQ(activeTaskList) \
            .Where(lambda task: task.task_interval is not None) \
            .ToList()

        while self._FLAG_RUN:
            tasksNeedingScheduleRun = _LINQ(tasksWithSchedules) \
                .Where(lambda task: task._task_id not in self._threading_activeTasks) \
                .Where(self._ScheduledTask_ShouldRun)
            
            for task in tasksNeedingScheduleRun:
                pool.apply_async(self._RunTaskEvent_OnSchedule, [task], callback=self._TaskThreadFinished)
            self.SaveSettingsIfNeeded() #save once per full iteration if needed
            _sleep(self._config_RunIterationDelay)
            
        pool.terminate()

    def SaveSettingsIfNeeded(self):
        '''instead of saving after each small modification, change when modifications are made'''
        if not (self._FLAG_SAVESETTINGS): 
            return

        with self._lock_settingsManager:
            self._settingsManager.SaveSettings()
            self._FLAG_SAVESETTINGS = False
            
    def _ScheduledTask_ShouldRun(self, task: ITask):
        if(_datetime.now() > task._task_nextSchedule):
            return True
        return False
    
    def _ScheduledTask_SetNextSchedule(self, task: ITask):
        '''sets the task directly to next scheduled interval'''
        task._task_nextSchedule = _datetime.now() + _timedelta(seconds=task.task_interval.InSeconds())
        with self._lock_settingsManager:
            self._settingsManager.Settings["TaskSchedules"][task._task_id]["next"] = task._task_nextSchedule.isoformat()
            self._FLAG_SAVESETTINGS = True
        return

    def LoadTasks(self, tasks: list[ITask]):
        '''Load list of ITasks into memory'''
        for task in tasks:
            if not isinstance(task, ITask):
                raise TypeError(f"Task must be of type ITask, got {type(task)}")
            self._tasks[task._task_id] = task
        return self

    def LoadTasksFromFile(self, path:str):
        '''Scans a file for all ITask implementing classes and loads them into memory'''
        if(not _os.path.isfile(path)):
            raise FileNotFoundError(path)
        
        taskInstances = []
        
        dynamicModuleName = f"{_os.path.basename(path)}_{_crc32(path.encode())}"
        dynamicModule = _module.ImportModuleDynamically(dynamicModuleName, path)
        dynamicModuleInfo = _module.ModuleInfo(dynamicModule)
        classes = dynamicModuleInfo.GetDeclaredClasses(ITask, includeChildsOnly=True)
        for className,obj in classes.items():
            taskInstances.append(obj())

        self.LoadTasks(taskInstances)  

        return self

    def LoadTasksFromDirectory(self, path:str, recursive=True):
        '''Scans a directory for all ITask implementing classes and loads them into memory'''

        if(not _os.path.isdir(path)):
            raise NotADirectoryError(path)
        
        maxRecursionDepth = None if recursive == True else 1
        taskInstances = []
        pyFiles = _directory.List(path, 
                             includeDirs=False, 
                             includeFilter='/\.py$/i',
                             maxRecursionDepth=maxRecursionDepth)
        for filepath in pyFiles:
            self.LoadTasksFromFile(filepath)

        return self

    def _InitializeTasks(self):
        if("TaskSchedules" not in self._settingsManager.Settings):
            self._settingsManager.Settings["TaskSchedules"] = {}
            self._FLAG_SAVESETTINGS = True
            

        taskSchedulesSettings = self._settingsManager.Settings["TaskSchedules"]

        #clear invalid/old settings
        for key in list(taskSchedulesSettings.keys()):
            if(key not in self._tasks): #this includes ignored tasks aswell, since we dont want to reset it's schedule when its temporarily ignored
                del taskSchedulesSettings[key]
                self._FLAG_SAVESETTINGS = True

        #register tasks with schedules
        TasksWithSchedules = _LINQ(self._tasks.values()) \
            .Where(lambda task: task.task_interval is not None)
        
        for task in TasksWithSchedules:
            #if this is a new task, or task interval has changed, then set to trigger them right away
            if(task._task_id not in taskSchedulesSettings) or (taskSchedulesSettings[task._task_id]["interval"] != task.task_interval.InSeconds()):
                taskSchedulesSettings[task._task_id] = {
                    "interval": task.task_interval.InSeconds(),
                    "next": _datetime.min.isoformat()
                }
                self._FLAG_SAVESETTINGS = True
            
            task._task_nextSchedule = _datetime.fromisoformat(taskSchedulesSettings[task._task_id]["next"])

        self.SaveSettingsIfNeeded()            
        return