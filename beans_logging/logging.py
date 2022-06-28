# -*- coding: utf-8 -*-

import os
import sys
import json
import errno
import datetime
import traceback
import logging

import yaml
from loguru import logger
from dotenv import load_dotenv


## Defualt options for logger
_config = {
    'level': 'INFO',
    'use_color': True,
    'use_icon': False,
    'use_backtrace': True,
    'std_format_str': '[<c>{time:YYYY-MM-DD HH:mm:ss.SSS Z}</c> | <level>{lvlname:<5}</level> | <w>{file}</w>:<w>{line}</w>]: <level>{message}</level>',
    'use_log_file': False,
    'file_format_str': '[{time:YYYY-MM-DD HH:mm:ss.SSS Z} | {lvlname:<5} | {file}:{line}]: {message}',
    'rotate_when':
    {
        'at_hour': 0,
        'at_minute': 0,
        'at_second': 0
    },
    'rotate_file_size': 10000000,
    'backup_file_count': 50,
    'file_encoding': 'utf8',
    'all_log_filename': '{app_name}.std.all.log',
    'err_log_filename': '{app_name}.std.err.log',
    'use_log_json': False,
    'use_custom_json': False,
    'json_all_log_filename': '{app_name}.json.all.log',
    'json_err_log_filename': '{app_name}.json.err.log',
    'logs_dir': os.path.join(os.getcwd(), 'logs')
}


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level if it exists
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller from where originated the logged message
        frame, depth = logging.currentframe(), 2
        while frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())


class Rotator:
    def __init__(self, *, size: int, at: datetime.time):
        _now = datetime.datetime.now()
        self._size_limit = size
        self._time_limit = _now.replace(hour=at.hour, minute=at.minute, second=at.second)

        if self._time_limit <= _now:
            # The current time is already past the target time so it would rotate already.
            # Add one day to prevent an immediate rotation.
            self._time_limit += datetime.timedelta(days=1)

    def should_rotate(self, message, file):
        file.seek(0, 2)
        if self._size_limit < (file.tell() + len(message)):
            return True

        if self._time_limit.timestamp() < message.record["time"].timestamp():
            self._time_limit += datetime.timedelta(days=1)
            return True
        return False


## Filter for adding short level name:
def _add_lvlname(record: dict):
    record['lvlname'] = record['level'].name
    if record['level'].name == 'SUCCESS':
        record['lvlname'] = 'OK'
    elif record['level'].name == 'WARNING':
        record['lvlname'] = 'WARN'
    elif record['level'].name == 'CRITICAL':
        record['lvlname'] = 'CRIT'
    return record


## Printing message based on log level to stdout or stderr:
def _std_sink(message):
    if message.record["level"].no < 40:
        sys.stdout.write(message)
    else:
        sys.stderr.write(message)


## Custom json formatter:
def _custom_json_formatter(record: dict):
    _error = None
    if record['exception']:
        _error = {}
        _error_type, _error_value, _error_traceback = record['exception']
        _error['type'] = _error_type.__name__
        _error['value'] = str(_error_value)
        _error['traceback'] = ''.join(traceback.format_tb(_error_traceback))

    _extra = None
    if record['extra'] and (0 < len(record['extra'])):
        _extra = record['extra']

    _json_format = {
        'timestamp': record['time'].strftime('%Y-%m-%dT%H:%M:%S%z'),
        'level': record['level'].name,
        'level_no': record['level'].no,
        'file': record['file'].name,
        'line': record['line'],
        'name': record['name'],
        'process': {
            'name': record['process'].name,
            'id': record['process'].id
        },
        'thread_name': {
            'name': record['thread'].name,
            'id': record['thread'].id
        },
        'message': record['message'],
        'extra': _extra,
        'error': _error,
        'elapsed': str(record['elapsed']),
    }

    record['custom_json'] = json.dumps(_json_format)
    return '{custom_json}\n'



def _init():
    global _config

    ## Loading environment variables from .env file, if it's exits:
    _env_filename = '.env'
    _env_file_path = os.path.join(os.getcwd(), _env_filename)
    if os.path.isfile(_env_file_path):
        load_dotenv(dotenv_path=_env_file_path, override=True)

    ## Loading config from file, if it's exits:
    _configs_dir = os.path.join(os.getcwd(), 'configs')
    _yaml_config_file_path = os.path.join(_configs_dir, 'logger.yaml')
    if not os.path.isfile(_yaml_config_file_path):
        _yaml_config_file_path = os.path.join(_configs_dir, 'logger.yml')
    _json_config_file_path = os.path.join(_configs_dir, 'logger.json')

    if os.path.isfile(_yaml_config_file_path):
        try:
            with open(_yaml_config_file_path, 'r', encoding='utf8') as _yaml_config_file:
                _config = yaml.safe_load(_yaml_config_file)['logger']
        except Exception:
            logger.exception(f"Failed to load '{_yaml_config_file_path}' yaml config file.")
            exit(2)
    elif os.path.isfile(_json_config_file_path):
        try:
            with open(_json_config_file_path, 'r', encoding='utf8') as _json_config_file:
                _config = json.load(_json_config_file)['logger']
        except Exception:
            logger.exception(f"Failed to load '{_json_config_file_path}' json config file.")
            exit(2)

    if not 'level' in _config:
        _config['level'] = 'INFO'
    _config['is_debug'] = False
    _config['use_diagnose'] = False

    ## Checking environment for DEBUG option:
    _ENV = str(os.getenv('ENV')).strip().lower()
    _DEBUG = str(os.getenv('DEBUG')).strip().lower()
    if (_DEBUG == 'true') or ((_ENV == 'development') and ((_DEBUG == 'none') or (_DEBUG == ''))):
        _config['is_debug'] = True
        os.environ['DEBUG'] = 'true'

    if _config['is_debug'] and (_config['level'] != 'TRACE'):
        _config['level'] = 'DEBUG'

    if (_config['level'] == 'DEBUG') or (_config['level'] == 'TRACE'):
        _config['use_diagnose'] = True

    if _config['use_icon']:
        _config['std_format_str'] = _config['std_format_str'].replace('lvlname:<5', 'level.icon:<4')

    # if _USE_COLOR:
    #     ## Checking terminal could support xterm colors:
    #     _TERM = str(os.getenv('TERM'))
    #     if (_TERM != 'xterm') and (_TERM != 'xterm-16color') and (_TERM != 'xterm-88color') and (_TERM != 'xterm-256color'):
    #         _USE_COLOR = False

    ## Initializing std stream log handler:
    logger.remove()
    logger.add(_std_sink,
                level=_config['level'],
                format=_config['std_format_str'],
                colorize=_config['use_color'],
                filter=_add_lvlname,
                backtrace=_config['use_backtrace'],
                diagnose=_config['use_diagnose'])

    ## Checking log file handlers enabled or not:
    if _config['use_log_file'] or _config['use_log_json']:
        ## Setting 'APP_NAME':
        if (not os.getenv('APP_NAME')) or (not os.getenv('APP_NAME').strip()):
            _base_filename = os.path.splitext(os.path.basename(sys.argv[0]))[0]
            os.environ['APP_NAME'] = _base_filename.strip().replace(' ', '_').lower()
            logger.debug(f"Not found 'APP_NAME' environment variable, changed app name to '{os.getenv('APP_NAME')}'.")

        _APP_NAME = os.getenv('APP_NAME').strip().replace(' ', '_').lower()

        ## Checking and creating 'logs_dir':
        if os.getenv('PY_LOGS_DIR') and os.getenv('PY_LOGS_DIR').strip():
            _LOGS_DIR = os.getenv('PY_LOGS_DIR').strip()
        else:
            if ('logs_dir' in _config) and _config['logs_dir'].strip():
                _LOGS_DIR = _config['logs_dir'].strip()
            else:
                _LOGS_DIR = os.path.join(os.getcwd(), 'logs')
                logger.debug(f"Not found 'PY_LOGS_DIR' environment variable or not found 'logs_dir' config, changed to '{_LOGS_DIR}' local directory.")
            os.environ['PY_LOGS_DIR'] = _LOGS_DIR

        if not os.path.isdir(_LOGS_DIR):
            logger.warning(f"'{_LOGS_DIR}' directory doesn't exist!")
            try:
                os.makedirs(_LOGS_DIR)
            except Exception as err:
                if err.errno == errno.EEXIST:
                    logger.info(f"'{_LOGS_DIR}' directory already exists.")
                else:
                    logger.exception(f"Failed to create '{_LOGS_DIR}' directory.")
                    exit(2)
            logger.success(f"Successfully created '{_LOGS_DIR}' directory!")

        ## Setting up log file handlers:
        _rotate_when = datetime.time(_config['rotate_when']['at_hour'], _config['rotate_when']['at_minute'], _config['rotate_when']['at_second'])
        if _config['use_log_file']:
            ## Initializing log file handler:
            _out_rotator = Rotator(size=_config['rotate_file_size'], at=_rotate_when)
            _log_file_path = os.path.join(_LOGS_DIR, _config['all_log_filename'].format(app_name=_APP_NAME))
            logger.add(_log_file_path,
                        level=_config['level'],
                        format=_config['file_format_str'],
                        rotation=_out_rotator.should_rotate,
                        retention=_config['backup_file_count'],
                        encoding=_config['file_encoding'],
                        enqueue=True,
                        backtrace=_config['use_backtrace'],
                        diagnose=_config['use_diagnose'])

            ## Initializing error log file handler:
            _err_rotator = Rotator(size=_config['rotate_file_size'], at=_rotate_when)
            _log_file_path = os.path.join(_LOGS_DIR, _config['err_log_filename'].format(app_name=_APP_NAME))
            logger.add(_log_file_path,
                        level='WARNING',
                        format=_config['file_format_str'],
                        rotation=_err_rotator.should_rotate,
                        retention=_config['backup_file_count'],
                        encoding=_config['file_encoding'],
                        enqueue=True,
                        backtrace=_config['use_backtrace'],
                        diagnose=_config['use_diagnose'])

        if _config['use_log_json']:
            _json_out_rotator = Rotator(size=_config['rotate_file_size'], at=_rotate_when)
            _json_err_rotator = Rotator(size=_config['rotate_file_size'], at=_rotate_when)

            if _config['use_custom_json']:
                ## Initializing json log file handler:
                _log_file_path = os.path.join(_LOGS_DIR, _config['json_all_log_filename'].format(app_name=_APP_NAME))
                logger.add(_log_file_path,
                            level=_config['level'],
                            format=_custom_json_formatter,
                            rotation=_json_out_rotator.should_rotate,
                            retention=_config['backup_file_count'],
                            encoding=_config['file_encoding'],
                            enqueue=True,
                            backtrace=_config['use_backtrace'],
                            diagnose=_config['use_diagnose'])

                ## Initializing json error log file handler:
                _log_file_path = os.path.join(_LOGS_DIR, _config['json_err_log_filename'].format(app_name=_APP_NAME))
                logger.add(_log_file_path,
                            level='WARNING',
                            format=_custom_json_formatter,
                            rotation=_json_err_rotator.should_rotate,
                            retention=_config['backup_file_count'],
                            encoding=_config['file_encoding'],
                            enqueue=True,
                            backtrace=_config['use_backtrace'],
                            diagnose=_config['use_diagnose'])
            else:
                ## Initializing json log file handler:
                _log_file_path = os.path.join(_LOGS_DIR, _config['json_all_log_filename'].format(app_name=_APP_NAME))
                logger.add(_log_file_path,
                            level=_config['level'],
                            format='',
                            serialize=True,
                            rotation=_json_out_rotator.should_rotate,
                            retention=_config['backup_file_count'],
                            encoding=_config['file_encoding'],
                            enqueue=True,
                            backtrace=_config['use_backtrace'],
                            diagnose=_config['use_diagnose'])

                ## Initializing json error log file handler:
                _log_file_path = os.path.join(_LOGS_DIR, _config['json_err_log_filename'].format(app_name=_APP_NAME))
                logger.add(_log_file_path,
                            level='WARNING',
                            format='',
                            serialize=True,
                            rotation=_json_err_rotator.should_rotate,
                            retention=_config['backup_file_count'],
                            encoding=_config['file_encoding'],
                            enqueue=True,
                            backtrace=_config['use_backtrace'],
                            diagnose=_config['use_diagnose'])

        logging.basicConfig(handlers=[InterceptHandler()], level=0)

_init()
