from pydantic import BaseModel
from typing import List, Optional
import pandas as pd
import sys


class ProgramState(object):
    init = 'init'
    running = 'running'
    restart = 'restart'
    stopped = 'stopped'
    error = 'error'
    deleted = 'deleted'


class Config(BaseModel):
    program: str
    directory: str
    command: str
    stdout_file: Optional[str] = '/tmp/stdout.txt'
    stderr_file: Optional[str] = '/tmp/stderr.txt'
    max_restart: Optional[int] = 3
    cur_restart: Optional[int] = 0
    cur_state: Optional[str] = ''
    next_state: Optional[str] = ''
    start_time: Optional[str] = pd.Timestamp.now().strftime(
        '%Y-%m-%d %H:%M:%S')
    restart_period: Optional[int] = sys.maxsize

    def __str__(self):
        return str(self.dict())

    def __eq__(self, other):
        return self.program == other.program

    def __hash__(self):
        return hash(self.program)
