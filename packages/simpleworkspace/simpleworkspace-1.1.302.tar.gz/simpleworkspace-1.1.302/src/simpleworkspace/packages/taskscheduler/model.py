from abc import ABC
from datetime import datetime
from ...types.time import TimeSpan

class ITask(ABC):
    '''
    Tasks needs to implement this interface to be loaded into task scheduler

    properties and methods for Derived classes:
        * task_interval
        * task_ignore
        * task_description
        * On_StartUp
        * On_Schedule 
    '''
    task_interval = None  # type: TimeSpan|str
    '''
    Runs On_Schedule event per specified interval, takes either TimeSpan or TimeSchedule
        example 1: TimeSpan(minute=2), would run the task once ever 2 minutes
        example 2: a cron string "* * * * *" would run the task every minute
    '''
    task_ignore = False
    '''Can ignore a task from triggering'''
    task_description = None
    '''A human friendly description that is logged alongside each action of this task'''
    _task_id = None #type: str
    '''An unique identifier for this task, is used to store persistant task states and for lookups'''

    def __init__(self) -> None:
        self._task_id = self.__class__.__module__ + "." + self.__class__.__name__
        self._task_nextSchedule = datetime.min

    def On_StartUp(self) -> str|None:
        '''runs once per start of taskscheduler'''
        pass

    def On_Schedule(self) -> str|None:
        '''runs once per specified interval'''
        pass

class CommandTask(ITask):
    '''Premade task for running a simple command'''
    def __init__(self, interval:TimeSpan|str, command:str|list[str]) -> None:
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
