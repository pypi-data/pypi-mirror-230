import logging
from threading import Thread
from time import sleep
from typing import Dict, List, Optional, Tuple

from yandexproto.jobs_pb2 import JobParameters, Job
from yandexproto.project_job_service_pb2 import (
    CreateProjectJobRequest, CreateProjectJobResponse,
    ExecuteProjectJobRequest, ExecuteProjectJobResponse,
    ReadStdLogsRequest, StdLog,
    ListProjectJobRequest, GetProjectJobRequest, DeleteProjectJobRequest,
)
from yandexproto.project_job_service_pb2_grpc import ProjectJobServiceStub
from yandexproto.operation_pb2 import Operation
from yandexproto.operation_service_pb2 import GetOperationRequest, CancelOperationRequest
from yandexproto.operation_service_pb2_grpc import OperationServiceStub

from datasphere.auth import get_md, get_channel
from datasphere.config import Config
from datasphere.files import download_files, upload_files
from datasphere.logs import program_stdout, program_stderr
from datasphere.utils import query_yes_no


logger = logging.getLogger(__name__)

operation_check_interval_seconds = 5
log_read_interval_seconds = 5


class Client:
    cfg: Config
    md: List[Tuple[str, str]]

    stub: ProjectJobServiceStub
    op_stub: OperationServiceStub

    def __init__(self, oauth_token: Optional[str] = None):
        self.md = get_md(oauth_token)
        channel = get_channel()
        self.stub = ProjectJobServiceStub(channel)
        self.op_stub = OperationServiceStub(channel)

    def create(
            self,
            job_params: JobParameters,
            cfg: Config,
            project_id: str,
            sha256_to_display_path: Dict[str, str],
    ) -> str:
        logger.debug('receiving presigned urls to upload files from server')
        op = self.stub.Create(
            CreateProjectJobRequest(
                project_id=project_id,
                job_parameters=job_params,
                config=cfg.content,
                name=cfg.name,
                desc=cfg.desc,
            ),
            metadata=self.md,
        )
        op = self._poll_operation(op)
        resp = CreateProjectJobResponse()
        op.response.Unpack(resp)
        upload_files(list(resp.upload_files), sha256_to_display_path)
        logger.info('created job `%s` for your program', resp.job_id)
        return resp.job_id

    def execute(self, job_id: str) -> Operation:
        logger.debug('requesting program execution')
        return self.stub.Execute(ExecuteProjectJobRequest(job_id=job_id), metadata=self.md)

    def list(self, project_id: str) -> List[Job]:
        page_token = None
        jobs = []
        while True:
            resp = self.stub.List(
                ListProjectJobRequest(project_id=project_id, page_size=50, page_token=page_token),
                metadata=self.md,
            )
            jobs += resp.jobs
            page_token = resp.page_token
            if not page_token or len(resp.jobs) == 0:
                break
        return jobs

    def get(self, job_id: str) -> Job:
        resp = self.stub.Get(GetProjectJobRequest(job_id=job_id), metadata=self.md)
        return resp.job

    def delete(self, job_id: str):
        self.stub.Delete(DeleteProjectJobRequest(job_id=job_id), metadata=self.md)

    def wait_for_completion(self, job_id: str, op: Operation):
        Thread(target=self.print_std_logs, args=[job_id], daemon=True).start()
        try:
            op = self._poll_operation(op)
            resp = ExecuteProjectJobResponse()
            op.response.Unpack(resp)
            download_files(list(resp.output_files))
            if resp.result.return_code != 0:
                raise ProgramError(resp.result.return_code)
            else:
                logger.info('job completed successfully')
                return
        except KeyboardInterrupt:
            if query_yes_no('cancel job?', default=False):
                logger.info('cancelling job...')
                self.op_stub.Cancel(CancelOperationRequest(operation_id=op.id), metadata=self.md)
                logger.info('job is canceled')
                return
            else:
                logger.info('resuming job...')

    # Wait until operation is done, if it's error in operation, raise it as in case of usual gRPC call.
    def _poll_operation(self, op: Operation) -> Operation:
        while True:
            if not op.done:
                logger.debug('waiting for operation...')
                sleep(operation_check_interval_seconds)
            else:
                if op.HasField('error'):
                    raise OperationError(op)
                else:
                    # We are ready to unpack response.
                    return op
            op = self.op_stub.Get(GetOperationRequest(operation_id=op.id), metadata=self.md)

    def print_std_logs(self, job_id: str, offset: int = 0):
        # Server has two possible ways to return streaming response with logs:
        # 1) Stream will end only after job finish.
        # 2) Stream can end at any moment, and we have to make several requests remembering last offset.
        #
        # We don't know which way server will use, so we support both ways. Because of 1), we can read logs only
        # in separate thread. Because of 2), we remember offset and make requests in infinite loop, which will
        # terminate with daemon thread termination.
        #
        # In case of attach to executing job, we send offset = -1 to indicate that we want to get logs from current
        # moment at time.
        #
        # Opened questions:
        # - Logs read will end after downloading results (CLI process finish), some final logs may be lost.

        while True:
            for resp in self.stub.ReadStdLogs(ReadStdLogsRequest(job_id=job_id, offset=offset), metadata=self.md):
                for log in resp.logs:
                    try:
                        log_str = log.content.decode('utf8')
                    except UnicodeError:
                        log_str = f'[non-unicode sequence] {log.content}'

                    program_logger = {
                        StdLog.Type.OUT: program_stdout,
                        StdLog.Type.ERR: program_stderr,
                    }.get(log.type)

                    if program_logger is not None:
                        program_logger.info(log_str)
                offset = resp.offset
            sleep(log_read_interval_seconds)


# Exception to display traceback about operation errors in similar way as usual RPC error (grpc.RpcError).
class OperationError(Exception):
    def __init__(self, op: Operation):
        self.op = op

    def __str__(self):
        status = self.op.error
        return f'Operation returned error:\n\tstatus={status.code}\n\tdetails={status.message}'

    def __repr__(self):
        return str(type(self))


class ProgramError(Exception):
    def __init__(self, return_code: int):
        self.return_code = return_code

    def __str__(self):
        return f'Program returned code {self.return_code}'

    def __repr__(self):
        return str(type(self))
