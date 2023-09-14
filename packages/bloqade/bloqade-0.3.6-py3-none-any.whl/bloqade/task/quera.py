from bloqade.submission.mock import MockBackend
from bloqade.task.base import Geometry
from bloqade.task.base import RemoteTask

from bloqade.submission.base import ValidationError
from bloqade.submission.ir.task_results import QuEraTaskResults, QuEraTaskStatusCode
from bloqade.submission.ir.task_specification import QuEraTaskSpecification
from bloqade.submission.ir.parallel import ParallelDecoder
from bloqade.submission.quera import QuEraBackend

from typing import Dict, Optional, Union
from bloqade.builder.base import ParamType
from dataclasses import dataclass
import warnings


@dataclass
class QuEraTask(RemoteTask):
    task_id: Optional[str]
    backend: Union[QuEraBackend, MockBackend]
    task_ir: QuEraTaskSpecification
    metadata: Dict[str, ParamType]
    parallel_decoder: ParallelDecoder
    task_result_ir: Optional[QuEraTaskResults] = None

    def submit(self, force: bool = False) -> "QuEraTask":
        if not force:
            if self.task_id is not None:
                raise ValueError(
                    "the task is already submitted with %s" % (self.task_id)
                )

        self.task_id = self.backend.submit_task(self.task_ir)

        self.task_result_ir = QuEraTaskResults(task_status=QuEraTaskStatusCode.Enqueued)

        return self

    def validate(self) -> str:
        try:
            self.backend.validate_task(self.task_ir)
        except ValidationError as e:
            return str(e)

        return ""

    def fetch(self) -> "QuEraTask":
        # non-blocking, pull only when its completed
        if self.task_id is None:
            raise ValueError("Task ID not found.")

        status = self.status()
        if status == QuEraTaskStatusCode.Completed:
            self.task_result_ir = self.backend.task_results(self.task_id)
        else:
            self.task_result_ir = QuEraTaskResults(task_status=status)

        return self

    def pull(self) -> "QuEraTask":
        # blocking, force pulling, even its completed
        if self.task_id is None:
            raise ValueError("Task ID not found.")

        self.task_result_ir = self.backend.task_results(self.task_id)

        return self

    def result(self) -> QuEraTaskResults:
        # blocking, caching

        if self.task_result_ir is None:
            pass
        else:
            if (
                self.task_id is not None
                and self.task_result_ir.task_status != QuEraTaskStatusCode.Completed
            ):
                self.pull()

        return self.task_result_ir

    def status(self) -> QuEraTaskStatusCode:
        if self.task_id is None:
            return QuEraTaskStatusCode.Unaccepted

        return self.backend.task_status(self.task_id)

    def cancel(self) -> None:
        if self.task_id is None:
            warnings.warn("Cannot cancel task, missing task id.")
            return

        self.backend.cancel_task(self.task_id)

    @property
    def nshots(self):
        return self.task_ir.nshots

    def _geometry(self) -> Geometry:
        return Geometry(
            sites=self.task_ir.lattice.sites,
            filling=self.task_ir.lattice.filling,
            parallel_decoder=self.parallel_decoder,
        )

    def _result_exists(self) -> bool:
        if self.task_id is None:
            return False

        if self.task_result_ir is None:
            return False
        else:
            if self.task_result_ir.task_status in [
                QuEraTaskStatusCode.Completed,
                QuEraTaskStatusCode.Partial,
            ]:
                return True
            else:
                return False

    # def submit_no_task_id(self) -> "HardwareTaskShotResults":
    #    return HardwareTaskShotResults(hardware_task=self)


# class QuEraBatch(Batch, JSONInterface):
#    #futures: List[QuEraTask]
#    pass
