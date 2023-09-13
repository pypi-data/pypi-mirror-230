#!/usr/bin/env python3
import ast
import asyncio
import json
import os
import pprint
import sys
from abc import ABC, abstractmethod
from signal import SIGTERM
from typing import List, Tuple

import codefast as cf
import fire
import pandas as pd
from codefast.io.osdb import osdb
from codefast.logger import get_logger

from .config import SERVICE_CONFIG
from .state import Config, ProgramState
from .utils import ResetStdFiles

# --------------------------------------------

dbfile = os.path.join(os.path.expanduser('~'), '.knivesout.db')
_db = osdb(dbfile)
logger = get_logger()


def parse_config_from_file(config_file: str) -> Config:
    """Parse config file and return a dictionary of parameters."""
    try:
        js = cf.js(config_file)
        return Config(**js)
    except json.decoder.JSONDecodeError as e:
        logger.warning("json decode error: {}".format(e))
        js = ast.literal_eval(cf.io.reads(config_file))
        return Config(**js)
    except Exception as e:
        logger.warning(e)
        return None


def parse_config_from_string(config_string: str) -> Config:
    """Parse config file and return a dictionary of parameters."""
    import ast
    try:
        js = ast.literal_eval(config_string)
        return Config(**js)
    except Exception as e:
        cf.error({
            'msg': 'parse_config_from_string error',
            'config_string': config_string,
            'error': str(e)
        })
        return None


class ConfigManager(object):

    @staticmethod
    def get_by_program(program: str) -> Config:
        return next((c for c in ConfigManager.load() if c.program == program),
                    None)

    @staticmethod
    def load() -> List[Config]:
        configs = _db.get('configs') or '[]'
        configs = [Config(**c) for c in ast.literal_eval(configs)]
        return list(set(configs))

    @staticmethod
    def add(config: Config):
        configs = ConfigManager.load()
        configs = [c for c in configs if c != config]
        configs.append(config)
        ConfigManager.save(configs)

    @staticmethod
    def _kill_by_pid(pid: int):
        try:
            os.kill(pid, SIGTERM)
        except Exception as e:
            logger.warning(e)

    @staticmethod
    def _kill_by_command(config: Config):
        pids = os.popen(
            f"ps -ef | grep '{config.command}' | grep -v grep | awk '{{print $2}}'"
        ).read().split()
        for pid in pids:
            ConfigManager._kill_by_pid(int(pid))

    @staticmethod
    def delete_by_program_name(name: str):
        configs = ConfigManager.load()
        configs_new = []
        for c in configs:
            if c.program == name:
                ConfigManager._kill_by_command(c)
            else:
                configs_new.append(c)
        print(configs_new)
        ConfigManager.save(configs_new)

    @staticmethod
    def stop_by_program_name(name: str):
        configs = ConfigManager.load()
        configs_new = []
        command = ''
        for c in configs:
            if c.program == name:
                c.next_state = ProgramState.stopped
                c.cur_state = ProgramState.running     # Give control to RunningSwitcher
                c.start_time = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
                command = c.command
            configs_new.append(c)
        ConfigManager.save(configs_new)
        return command

    @staticmethod
    def save(configs: List[Config]):
        configs = list(set(configs))
        configs = [c.dict() for c in configs]
        _db.set('configs', configs)


class AbstractStateSwitcher(ABC):

    def _update_config(self, config: Config):
        ConfigManager.add(config)

    @abstractmethod
    def is_match(self) -> bool:
        ...

    @abstractmethod
    async def _switch(self):
        ...

    async def switch(self, config: Config):
        self.config = config
        if not self.is_match():
            return
        await self._switch()

    async def get_pids(self, config: Config) -> List[str]:
        process = config.command.split()[0]
        pids = os.popen(
            f"ps -ef | grep '{process}' | grep -v grep | awk '{{print $2}}'"
        ).read().split()
        return pids

    def reset_states(self, config: Config, cur_state: str,
                     next_state: str) -> Config:
        config.cur_state = cur_state
        config.next_state = next_state
        return config

    async def is_running(self, config: Config):
        pids = await self.get_pids(config)
        return len(pids) > 0

    async def stop_execute(self, config: Config) -> None:
        pids = await self.get_pids(config)
        logger.info(f"stop running [{config.command}], pids {pids}")

        config = self.reset_states(config, ProgramState.stopped,
                                   ProgramState.stopped)
        self._update_config(config)

        for pid in pids:
            os.system(f"kill -9 {pid}")

    async def restart_execute(self, config: Config):
        """stop and then start program"""
        pids = await self.get_pids(config)
        logger.info(f"restarting [{config.command}], pids {pids}")
        for pid in pids:
            os.system(f"kill -9 {pid}")

        config.cur_state = ProgramState.init
        config.next_state = ProgramState.running
        config.cur_restart = 0
        self._update_config(config)


class InitSwitcher(AbstractStateSwitcher):

    def is_match(self):
        return self.config.cur_state == ProgramState.init and self.config.next_state == ProgramState.running

    async def _switch(self):
        await self.start_execute(self.config)

    def check_log_file_permission(self, config: Config):
        if not os.path.exists(config.stdout_file):
            return True

        if not os.path.exists(config.stderr_file):
            return True

        if not os.access(config.stdout_file, os.W_OK):
            cf.error(f"stdout_file {config.stdout_file} is not writable")
            return False

        if not os.access(config.stderr_file, os.W_OK):
            cf.error(f"stderr_file {config.stderr_file} is not writable")
            return False
        return True

    def to_error_state(self, config: Config):
        config.cur_state = ProgramState.error
        config.next_state = ProgramState.error
        self._update_config(config)

    def to_running_state(self, config: Config):
        config.cur_state = ProgramState.running
        self._update_config(config)

    async def start_execute(self, config: Config):
        if config.cur_restart >= config.max_restart:
            cf.error(
                f"restart [{config.command}] reached retry limit {config.max_restart}"
            )
            self.config.cur_state = ProgramState.error
            self.config.next_state = ProgramState.error
            self._update_config(self.config)

        else:
            logger.info(f'start config: {config}')
            if not self.check_log_file_permission(config):
                self.to_error_state(config)
                return
            else:
                self.to_running_state(config)

            cmd = f"{config.command} 1>> {config.stdout_file} 2>> {config.stderr_file}"
            logger.info(f"Start running [{config.command}]")
            is_running = await self.is_running(config)

            if is_running:
                logger.info({'msg': 'already running', 'config': config})
            else:
                self.config.start_time = pd.Timestamp.now().strftime(
                    '%Y-%m-%d %H:%M:%S')
                self._update_config(self.config)

                os.chdir(config.directory)
                proc = await asyncio.create_subprocess_shell(
                    cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE)
                stdout, stderr = await proc.communicate()

                # Failed to start or been terminated
                msg = {
                    'stdout': stdout,
                    'stderr': stderr,
                    'return code': proc.returncode
                }
                logger.info(msg)
                if int(proc.returncode) not in (0, ):
                    msg = (
                        f"[{config.command}] is either terminated or failed to start, "
                        "return code: {proc.returncode}")
                    logger.warning(msg)

                config = ConfigManager.get_by_program(config.program)
                config.cur_restart += 1
                self._update_config(config)


class RunningSwitcher(AbstractStateSwitcher):

    def is_match(self):
        return self.config.cur_state == ProgramState.running

    def running_time(self) -> float:
        uptime = pd.Timestamp.now() - pd.Timestamp(self.config.start_time)
        return uptime.total_seconds()

    async def restart_by_period(self, config: Config):
        if self.running_time() > config.restart_period:
            await self.restart_execute(config)

    async def running_execute_helper(self, config: Config):
        is_running = await self.is_running(config)
        if not is_running:     # program maybe dead and stuck on running state
            self.config.cur_state = ProgramState.init
            self.config.next_state = ProgramState.running
            self._update_config(config)
        await self.restart_by_period(config)

    async def _switch(self):
        stratergies = {
            ProgramState.stopped: self.stop_execute,
            ProgramState.restart: self.restart_execute,
            ProgramState.running: self.running_execute_helper,
        }
        await stratergies[self.config.next_state](self.config)


class StopSwitcher(AbstractStateSwitcher):

    def is_match(self) -> bool:
        return self.config.cur_state == ProgramState.stopped

    def restart(self, config: Config) -> None:
        config.cur_state = ProgramState.init
        config.next_state = ProgramState.running
        self._update_config(config)

    def delete(self, config: Config) -> None:
        self.stop_execute(config)

    async def _switch(self):
        if self.config.next_state in (ProgramState.init, ProgramState.running):
            self.restart(self.config)


class Context(object):
    SWITCHERS = [RunningSwitcher(), InitSwitcher(), StopSwitcher()]

    @staticmethod
    async def run():
        configs = ConfigManager.load()
        for config in configs:
            for switcher in Context.SWITCHERS:
                asyncio.create_task(switcher.switch(config))


# ------------------------------------------------


def is_root() -> bool:
    return os.geteuid() == 0


def create_service() -> bool:
    path = '/etc/systemd/system' if is_root() else '~/.config/systemd/user'
    service_path = os.path.expanduser(path)
    if not os.path.exists(service_path):
        os.makedirs(service_path)
    service_file = os.path.join(service_path, 'knivesout.service')
    which_knivesout = cf.shell('which knivesout')
    config = SERVICE_CONFIG.format(which_knivesout)
    cf.io.write(config, service_file)
    cf.info('create service file: {}'.format(service_file))
    return True


def update_service() -> bool:
    user = '' if is_root() else '--user'
    cf.shell(f'systemctl {user} daemon-reload')
    cf.shell(f'systemctl {user} enable knivesout.service')
    cf.shell(f'systemctl {user} restart knivesout.service')
    cf.info('service restarted')
    cf.info(f'check status by `systemctl {user} status knivesout.service`')
    return True


async def _loop():
    reset_std = ResetStdFiles()
    while True:
        await asyncio.sleep(1)
        await Context.run()
        await reset_std.run()


def knivesout():
    # run forver with systemctl service
    asyncio.run(_loop())


def knivesd():
    create_service()
    update_service()


# ------------------------------------------------


def uptime(c: Config) -> str:
    uptime = pd.Timestamp.now() - pd.Timestamp(c.start_time)
    seconds = uptime.total_seconds()
    return cf.fp.readable_time(seconds)


def format_str(data: List[Tuple]) -> str:
    return ' | '.join([f'{d[1]:<{d[0]}}' for d in data])


class KnivesCli(object):
    """Terminal cli powered by fire."""

    def _check_daemon_status(self) -> None:
        """Check daemon status."""
        logger.info('Checking daemon status...')
        status = cf.shell('systemctl status knivesd')
        if not 'active (running)' in status:
            logger.warning('knivesd is not running')

    def _identify_config(self, proc_or_file: str) -> Config:
        """Find config by proc or file name

        Args:
            proc_or_file (str): proc or file name

        Returns:
            _type_: Config
        """

        configs = ConfigManager.load()
        config = None
        for c in configs:
            if c.program == proc_or_file:
                config = c
                break
        file_exist = os.path.exists(proc_or_file) and os.path.isfile(
            proc_or_file)

        if file_exist:
            c_file = parse_config_from_file(proc_or_file)
            config = None
            for c in configs:
                if c.program == c_file.program:
                    config = c
                    break
            # Tasks with same program name is forbidden
            if config:
                logger.info(f"Program [{config.program}] already exists")
            config = c_file

        if not config:
            logger.warning(f"Program [{proc_or_file}] not found")
            sys.exit(1)
        return config

    def init(self, name: str, command: str, directory: str = None):
        """Init a program, usage: knives init --name=xxx --command=xxx --directory=xxx

        Args:
            name (str): program name
            command (str): command to run
            directory (str, optional): directory to run. Defaults to None.
        """
        c = {
            'program': name,
            'command': command,
            'directory': directory or cf.shell('pwd')
        }
        filepath = '/data/knivesd/{}.json'.format(name)
        try:
            cf.js.write(c, filepath)
        except FileNotFoundError:
            filepath = os.path.join(os.getcwd(), '{}.json'.format(name))
            cf.js.write(c, filepath)
        self.start(filepath)

    def start(self, proc_or_file: str):
        """Start a program."""
        config = self._identify_config(proc_or_file)

        if config:
            config.cur_state = ProgramState.init
            config.next_state = ProgramState.running
            previous_config = ConfigManager.load()
            for pc in previous_config:
                if pc == config:
                    config.start_time = pc.start_time
                    break
            config.cur_restart = 0
            ConfigManager.add(config)
            logger.info(f"[{config.command}] started")
        else:
            logger.info(f"config not found: {proc_or_file}")

    def stop(self, proc_or_file: str):
        """Stop a program."""
        config = self._identify_config(proc_or_file)
        program = ConfigManager.stop_by_program_name(config.program)
        logger.info(f"[{program}] stopped")

    def restart(self, proc: str):
        """Restart a program."""
        config = self._identify_config(proc)
        config.cur_state = ProgramState.running
        config.next_state = ProgramState.restart
        ConfigManager.add(config)
        logger.info(f"[{config.program}] restarted")

    def list_configs(self, proc: str = None) -> List[Config]:
        config_list = []
        for c in ConfigManager.load():
            if proc is None or c.program == proc:
                config_list.append(c)
        config_list.sort(key=lambda c: (c.cur_state, c.program))
        return config_list

    def format_configs(self, configs: List[Config]) -> str:
        """ To display configs in a table
        """
        colors = {
            ProgramState.running: cf.fp.green,
            ProgramState.error: cf.fp.red,
            ProgramState.stopped: cf.fp.cyan,
            ProgramState.init: cf.fp.cyan
        }
        headers = [(7, 'state'), (17, 'proc_alias'), (15, 'uptime'),
                   (30, 'command')]
        texts = [format_str(headers), '-' * 66]
        for c in configs:
            cur_state = c.cur_state
            color_func = colors.get(cur_state, cf.fp.cyan)
            state = color_func(cur_state.upper())
            command_str = c.command[:50] + '...' if len(
                c.command) > 50 else c.command
            state_list = [(7, state), (17, c.program), (15, uptime(c)),
                          (30, command_str)]
            texts.append(format_str(state_list))
        return '\n'.join(texts)

    def status(self, proc: str = None):
        """Show status of a program."""
        configs = self.list_configs(proc)
        configs_str = self.format_configs(configs)
        print(configs_str)

    def st(self, proc: str = None):
        """Alias of status"""
        self.status(proc)

    def delete(self, proc: str):
        """Delete a program."""
        ConfigManager.delete_by_program_name(proc)
        logger.info(f"[{proc}] deleted")

    def configs(self, proc: str = None):
        """Show configs of a program."""
        configs = self.list_configs(proc)
        for config in configs:
            pprint.pprint(config.dict())

    def cs(self, proc: str = None):
        """Show configs of a program."""
        self.configs(proc)


def knivescli():
    fire.Fire(KnivesCli)
