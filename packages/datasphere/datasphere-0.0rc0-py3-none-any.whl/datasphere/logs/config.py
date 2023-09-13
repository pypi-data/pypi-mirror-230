import logging.config
from pathlib import Path
from string import Template
import yaml

PROGRAM_STDOUT_LOGGER = 'program_stdout'
PROGRAM_STDERR_LOGGER = 'program_stderr'

program_stdout, program_stderr = logging.getLogger(PROGRAM_STDOUT_LOGGER), logging.getLogger(PROGRAM_STDERR_LOGGER)


def configure_logging(level: str):
    cfg_path = Path(__file__).with_name('logging.yaml')
    cfg_str_tpl = Template(cfg_path.read_text())
    cfg_str = cfg_str_tpl.substitute({
        'LOG_LEVEL': level,
        'PROGRAM_STDOUT_LOGGER': PROGRAM_STDOUT_LOGGER,
        'PROGRAM_STDERR_LOGGER': PROGRAM_STDERR_LOGGER,
    })
    cfg = yaml.safe_load(cfg_str)
    logging.config.dictConfig(cfg)
