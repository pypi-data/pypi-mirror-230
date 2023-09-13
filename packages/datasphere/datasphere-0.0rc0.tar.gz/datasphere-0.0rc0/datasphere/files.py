import logging
from pathlib import Path
from typing import Dict, List

import requests
import tempfile

from lzy.py_env.py_env_provider import PyEnv
from lzy.utils.files import zip_path

from datasphere.config import VariablePath, local_module_prefix
from yandexproto.jobs_pb2 import StorageFile

logger = logging.getLogger(__name__)


def prepare_local_modules(py_env: PyEnv, tmpdir: str) -> List[VariablePath]:
    result = []
    for i, module in enumerate(py_env.local_modules_path):
        logger.debug('zip local module `%s`', module)
        with tempfile.NamedTemporaryFile('rb', dir=tmpdir, delete=False) as ar:
            zip_path(module, ar)

            # Path does not matter for local module since it will be unzipped to correct location, also, lzy
            # determines local module path as absolute path in general case, so we give it utility var value.
            path = VariablePath(ar.name, var=f'{local_module_prefix}_{i}')
            path.get_file(ar)

            result.append(path)

    return result


def upload_files(files: List[StorageFile], sha256_to_display_path: Dict[str, str]):
    # Maybe add debug log about already uploaded files.
    logger.info('uploading %d files', len(files))
    for f in files:
        with open(f.file.desc.path, 'rb') as fd:
            display_path = sha256_to_display_path.get(f.file.sha256, f.file.desc.path)
            logger.info('uploading file `%s`', display_path)
            if not f.url:
                continue
            resp = requests.put(f.url, data=fd)
            resp.raise_for_status()


def download_files(files: List[StorageFile]):
    logger.info('downloading %d files', len(files))
    for f in files:
        logger.info('downloading file `%s`', f.file.desc.path)
        resp = requests.get(f.url)
        resp.raise_for_status()
        path = Path(f.file.desc.path)
        if not path.parent.exists():
            # Create dirs containing output file.
            path.parent.mkdir(parents=True)
        with path.open('wb') as fd:
            for chunk in resp.iter_content(chunk_size=1 << 24):  # 16Mb chunk
                fd.write(chunk)
