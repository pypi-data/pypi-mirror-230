import argparse
import logging
from pathlib import Path
import tempfile
from typing import Optional

from datasphere.client import Client
from datasphere.config import parse_config
from datasphere.files import prepare_local_modules
from datasphere.logs import configure_logging
from datasphere.pyenv import get_auto_py_env
from datasphere.utils import format_jobs_table

logger = logging.getLogger(__name__)


def execute(oauth_token: Optional[str], args):
    cfg = parse_config(Path(args.config))

    py_env = None
    if cfg.python_script:
        # If user didn't specify manual Python environment in config, we take Python interpreter version the same as
        # interpreter running this CLI program.
        py_env = get_auto_py_env(cfg.python_script)
        logger.debug('explored python env: %s', py_env)

    with tempfile.TemporaryDirectory(prefix='datasphere_') as tmpdir:
        logger.debug('using tmp dir `%s` to prepare local files', tmpdir)

        if py_env:
            local_modules = [f.get_file() for f in prepare_local_modules(py_env, tmpdir)]
            # Preserve original local modules paths (before archiving).
            sha256_to_display_path = {f.sha256: p for f, p in zip(local_modules, py_env.local_modules_path)}
        else:
            local_modules = []
            sha256_to_display_path = {}

        job_params = cfg.get_job_params(py_env, local_modules)

        client = Client(oauth_token)

        job_id = client.create(job_params, cfg, args.project_id, sha256_to_display_path)
        op = client.execute(job_id)
        logger.debug('operation `%s` performs job', op.id)

    client.wait_for_completion(job_id, op)


def attach(oauth_token: Optional[str], args):
    client = Client(oauth_token)
    op = client.execute(args.job_id)  # TODO: handle case of completed job, display DS job link with results.
    client.wait_for_completion(args.job_id, op)


def ls(oauth_token: Optional[str], args):
    client = Client(oauth_token)
    jobs = client.list(args.project_id)
    print(format_jobs_table(jobs))


def get(oauth_token: Optional[str], args):
    client = Client(oauth_token)
    job = client.get(args.job_id)
    print(format_jobs_table([job]))


def delete(oauth_token: Optional[str], args):
    client = Client(oauth_token)
    client.delete(args.job_id)
    logger.info('job deleted')


def build_arg_parser() -> argparse.ArgumentParser:
    parser_datasphere = argparse.ArgumentParser(prog='datasphere')
    parser_datasphere.add_argument(
        '-t', '--oauth-token', required=False,
        help='YC OAuth token, see https://cloud.yandex.com/docs/iam/concepts/authorization/oauth-token'
    )
    parser_datasphere.add_argument(
        '-l', '--log-level', required=False, default='DEBUG',
        choices=[logging.getLevelName(level) for level in (logging.ERROR, logging.WARN, logging.INFO, logging.DEBUG)],
        help='Log levels',
    )
    subparsers_datasphere = parser_datasphere.add_subparsers(required=True)

    parser_project = subparsers_datasphere.add_parser('project')
    subparsers_project = parser_project.add_subparsers(required=True)

    parser_job = subparsers_project.add_parser('job')
    subparsers_job = parser_job.add_subparsers(required=True)

    def add_project_id_argument(parser):
        parser.add_argument('-p', '--project-id', required=True, help='DataSphere project ID')

    def add_job_id_argument(parser):
        parser.add_argument('-j', '--job-id', required=True, help='Job ID')

    parser_execute = subparsers_job.add_parser('execute', help='Execute job')
    add_project_id_argument(parser_execute)
    parser_execute.add_argument('-c', '--config', required=True, help='Config file')
    parser_execute.set_defaults(func=execute)

    parser_attach = subparsers_job.add_parser('attach', help='Attach to the job execution')
    add_job_id_argument(parser_attach)
    parser_attach.set_defaults(func=attach)

    parser_list = subparsers_job.add_parser('list', help='List jobs')
    add_project_id_argument(parser_list)
    parser_list.set_defaults(func=ls)

    parser_get = subparsers_job.add_parser('get', help='Get job')
    add_job_id_argument(parser_get)
    parser_get.set_defaults(func=get)

    parser_delete = subparsers_job.add_parser('delete', help='Delete job')
    add_job_id_argument(parser_delete)
    parser_delete.set_defaults(func=delete)

    return parser_datasphere


def main():
    arg_parser = build_arg_parser()

    args = arg_parser.parse_args()

    configure_logging(args.log_level)

    oauth_token: Optional[str] = args.oauth_token

    args.func(oauth_token, args)


if __name__ == '__main__':
    main()
