from logging import Logger
from datetime import datetime, timedelta
from ...utility.linq import LINQ
from ...settingsproviders import SettingsManager_JSON
from ...utility.stopwatch import StopWatch
from time import sleep
import os
from zlib import crc32
from ...utility import module
from ...io import directory
from multiprocessing.pool import ThreadPool
import traceback
from threading import Lock
from typing import Callable
from datetime import datetime
from .model import ITask
from .dependency.croniter import croniter #dependecy needed for cron strings

class TaskSchedulerManager:
    def __init__(self, settingsPath: str, logger: Logger) -> None:
        self.logger = logger
        self._settingsPath = settingsPath
        self._settingsManager = SettingsManager_JSON(self._settingsPath)
        self._settingsManager.LoadSettings()
        self._lock_settingsManager = Lock()
        self._tasks = {} #type: dict[str, ITask]
        '''all registered tasks'''
        self._FLAG_SAVESETTINGS = False
        self._FLAG_RUN = True
        self._config_RunIterationDelay = 1000
        '''delay each schedule check with specified MS'''
        self._config_maxThreads = 6
        '''max threads to use for running tasks'''
        self._threading_activeTasks = set()
        self._lock_threading_activeTasks = Lock()

    class _TaskResult:
        def __init__(self) -> None:
            self.stopwatch = StopWatch()
            self.output = None #type:str
            self.error = None #type:str

        @property
        def ElapsedMS(self):
            return self.stopwatch.GetElapsedMilliseconds(decimalPrecision=2)

    def _RunTaskEvent(self, task: ITask, eventFunc: Callable):
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
            taskResult.error = f"Event {eventName} FAILED[{taskResult.ElapsedMS} MS]: {taskTitle}, Error: {traceback.format_exc()}"
        
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

        activeTaskList = LINQ(self._tasks.values()) \
            .Where(lambda task: task.task_ignore == False) \
            .ToList()

        self._config_maxThreads = min(len(activeTaskList), self._config_maxThreads)
        pool = ThreadPool(processes=self._config_maxThreads)
        

        #skip none overriden ones
        tasksWithStartUp = LINQ(activeTaskList).Where(lambda task: task.On_StartUp.__func__ is not ITask.On_StartUp)
        taskResults = pool.map(self._RunTaskEvent_OnStartUp, tasksWithStartUp)
        #ensure all startup tasks are finished before continuing to onSchedule
        for taskResult in taskResults:
            self._TaskThreadFinished(taskResult)

        tasksWithSchedules = LINQ(activeTaskList) \
            .Where(lambda task: task.task_interval is not None) \
            .ToList()

        while self._FLAG_RUN:
            tasksNeedingScheduleRun = LINQ(tasksWithSchedules) \
                .Where(lambda task: task._task_id not in self._threading_activeTasks) \
                .Where(self._ScheduledTask_ShouldRun)
            
            for task in tasksNeedingScheduleRun:
                pool.apply_async(self._RunTaskEvent_OnSchedule, [task], callback=self._TaskThreadFinished)
            self._SaveSettingsIfNeeded() #save once per full iteration if needed
            sleep(self._config_RunIterationDelay / 1000)

        self._SaveSettingsIfNeeded() #save once per full iteration if needed
        pool.terminate()

    def _SaveSettingsIfNeeded(self):
        '''instead of saving after each small modification, change when modifications are made'''
        if not (self._FLAG_SAVESETTINGS): 
            return

        with self._lock_settingsManager:
            self._settingsManager.SaveSettings()
            self._FLAG_SAVESETTINGS = False
            
    def _ScheduledTask_ShouldRun(self, task: ITask):
        if(datetime.now() > task._task_nextSchedule):
            return True
        return False
    
    def _ScheduledTask_SetNextSchedule(self, task: ITask):
        '''sets the task directly to next scheduled interval'''
        if(isinstance(task.task_interval, str)):
            #use class as a cache to avoid recreating croniter instance, which might be heavy on init parsing
            if not(hasattr(task, '_task_interval_croniter')):
                setattr(task, '_task_interval_croniter', croniter(task.task_interval, ret_type=datetime))
            croniterInstance = getattr(task, '_task_interval_croniter') #type: croniter
            task._task_nextSchedule = croniterInstance.get_next(start_time=datetime.now())
        else:
            task._task_nextSchedule = datetime.now() + timedelta(seconds=task.task_interval.InSeconds())

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
        if(not os.path.isfile(path)):
            raise FileNotFoundError(path)
        
        taskInstances = []
        
        dynamicModuleName = f"{os.path.basename(path)}_{crc32(path.encode())}"
        dynamicModule = module.ImportModuleDynamically(dynamicModuleName, path)
        dynamicModuleInfo = module.ModuleInfo(dynamicModule)
        classes = dynamicModuleInfo.GetDeclaredClasses(ITask, includeChildsOnly=True)
        for className,obj in classes.items():
            taskInstances.append(obj())

        self.LoadTasks(taskInstances)  

        return self

    def LoadTasksFromDirectory(self, path:str, recursive=True):
        '''Scans a directory for all ITask implementing classes and loads them into memory'''

        if(not os.path.isdir(path)):
            raise NotADirectoryError(path)
        
        maxRecursionDepth = None if recursive == True else 1
        taskInstances = []
        pyFiles = directory.List(path, 
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
        TasksWithSchedules = LINQ(self._tasks.values()) \
            .Where(lambda task: task.task_interval is not None)
        
        for task in TasksWithSchedules:
            intervalName = task.task_interval if isinstance(task.task_interval, str) else task.task_interval.InSeconds()
            #if this is a new task, or task interval has changed, then set to trigger them right away
            if(task._task_id not in taskSchedulesSettings) or (taskSchedulesSettings[task._task_id]["interval"] != intervalName):
                taskSchedulesSettings[task._task_id] = {
                    "interval": intervalName,
                    "next": datetime.min.isoformat()
                }
                self._FLAG_SAVESETTINGS = True
            
            task._task_nextSchedule = datetime.fromisoformat(taskSchedulesSettings[task._task_id]["next"])

        self._SaveSettingsIfNeeded()            
        return