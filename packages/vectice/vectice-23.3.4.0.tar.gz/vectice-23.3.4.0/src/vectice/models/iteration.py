from __future__ import annotations

import logging
from contextlib import suppress
from textwrap import dedent
from typing import TYPE_CHECKING, ClassVar

from rich.table import Table

from vectice.api.http_error_handlers import NoStepsInPhaseError, VecticeException
from vectice.api.json.iteration import (
    IterationInput,
    IterationStatus,
)
from vectice.utils.common_utils import _check_read_only, _get_step_type, _temp_print
from vectice.utils.logging_utils import get_iteration_status

if TYPE_CHECKING:
    from vectice import Connection
    from vectice.api import Client
    from vectice.models import Phase, Project, Step, Workspace
    from vectice.models.model import Model

_logger = logging.getLogger(__name__)


class Iteration:
    """Represent a Vectice iteration.

    Iterations reflect the model development and test cycles completed
    by data scientists until a fully functional algorithm is ready for
    deployment.  Each iteration contains the sequence of steps defined
    at the Phase and acts as a guardrail for data scientists to
    provide their updates.

    Typical usage example:

    ```python
    my_iteration = my_phase.create_iteration()

    my_iteration.step_cleaning = my_dataset
    # you can append assets of the same types (datasets/models) with +=
    my_iteration.step_cleaning += my_other_dataset

    my_iteration.step_model = my_model
    my_iteration.step_model += my_other_model
    ```

    If steps are added to a phase after iterations have been created
    and completed, these steps won't appear in these iterations.

    ```tree
    iteration 1
        step 1
        step 2
        step 3
    ```

    NOTE: **Phases and Steps Definitions are created in the Vectice App,
    Iterations are created from the Vectice Python API.**

    To create a new iteration:

    ```python
    my_iteration = my_phase.create_iteration()
    ```
    """

    __slots__: ClassVar[list[str]] = [
        "_id",
        "_index",
        "_phase",
        "_status",
        "_client",
        "_model",
        "_current_step",
        "_steps",
        "__dict__",
    ]

    def __init__(
        self,
        id: str,
        index: int,
        phase: Phase,
        status: IterationStatus = IterationStatus.NotStarted,
    ):
        self.__dict__ = {}
        self._id = id
        self._index = index
        self._phase = phase
        self._status = status
        self._client: Client = self._phase._client
        self._model: Model | None = None
        self._current_step: Step | None = None
        self._steps = self._populate_steps()

    def __repr__(self):
        steps = self._client.list_steps(self.id).total
        return f"Iteration (index={self._index}, status={self._status}, No. of steps={steps})"

    def __eq__(self, other: object):
        if not isinstance(other, Iteration):
            return NotImplemented
        return self.id == other.id

    def _populate_steps(self):
        with suppress(NoStepsInPhaseError):
            step_output = self._client.list_steps(self.id, True).list
            steps = [_get_step_type(step_output=item, iteration=self) for item in step_output]
            check = {step.slug: step for step in steps}
            return check
        return {}

    def __getattr__(self, item):
        if item in self.__dict__:
            return self.__dict__[item]
        if item in super().__getattribute__("_steps"):
            step_item = self._steps[item]
            step = self._client.get_step_by_name(step_item.name, self.id)
            return _get_step_type(step_output=step, iteration=self)
        raise AttributeError(f"The attribute '{item}' does not exist.")

    def __setattr__(self, attr_name, attr_value):
        if hasattr(self, "_steps") and attr_name in super().__getattribute__("_steps"):
            if self._status in {IterationStatus.Abandoned, IterationStatus.Completed}:
                raise VecticeException(f"The Iteration is {self.status} and is read-only!")
            self._steps[attr_name] = self._steps[attr_name]._step_factory_and_update(value=attr_value)
        elif hasattr(self, "__dict__") and attr_name not in self.__slots__:
            raise AttributeError(f"The attribute '{attr_name}' does not exist.")
        else:
            super().__setattr__(attr_name, attr_value)

    @property
    def id(self) -> str:
        """The iteration's identifier.

        Returns:
            The iteration's identifier.
        """
        return self._id

    @id.setter
    def id(self, iteration_id: str):
        """Set the iteration's identifier.

        Parameters:
            iteration_id: The identifier.
        """
        _check_read_only(self)
        self._id = iteration_id

    @property
    def index(self) -> int:
        """The iteration's index.

        Returns:
            The iteration's index.
        """
        return self._index

    @property
    def status(self) -> str:
        """The iteration's status.

        Returns:
            The iteration's status.
        """
        return get_iteration_status(self._status)

    @property
    def completed(self) -> bool:
        """Whether this iteration is completed.

        Returns:
            Whether the iteration is completed.
        """
        return self._status is IterationStatus.Completed

    @property
    def properties(self) -> dict:
        """The iteration's identifier and index.

        Returns:
            A dictionary containing the `id` and `index` items.
        """
        return {"id": self.id, "index": self.index}

    def list_steps(self) -> None:
        """Prints a list of steps belonging to the iteration in a tabular format, limited to the first 10 steps. A link is provided to view the remaining steps.

        Returns:
            None
        """
        steps_output = self._client.list_steps(self.id, populate=False)

        rich_table = Table(expand=True, show_edge=False)

        rich_table.add_column("Shortcut", justify="left", no_wrap=True, min_width=5, max_width=20)
        rich_table.add_column("Registered items (count)", justify="left", no_wrap=True, min_width=5, max_width=15)
        rich_table.add_column("Description", justify="left", no_wrap=True, min_width=5, max_width=35)

        for step in steps_output.list:
            rich_table.add_row(step.slug, str(step.artifacts_count), step.description)
        description = f"""There are {steps_output.total} steps in Iteration '{self.index!r}' and a maximum of 10 steps are displayed in the table below:"""
        tips = dedent(
            """
        To access a specific step, use the step shortcut \033[1iiteration\033[0m.step_my_step_name
        The step reference is referred to as shortcut"""
        ).lstrip()
        link = dedent(
            f"""
        For quick access to the list of steps in the Vectice web app, visit:
        {self._client.auth._API_BASE_URL}/browse/iteration/{self.id}"""
        ).lstrip()

        _temp_print(description)
        _temp_print(table=rich_table)
        _temp_print(tips)
        _temp_print(link)

    def cancel(self) -> None:
        """Cancel the iteration by abandoning all unfinished steps."""
        iteration_input = IterationInput(status=IterationStatus.Abandoned.name)
        self._client.update_iteration(self.id, iteration_input)
        self._status = IterationStatus.Abandoned
        _logger.info(f"Iteration with index {self.index} cancelled.")

    def complete(self) -> None:
        """Mark the iteration as completed."""
        if self._status is IterationStatus.Abandoned:
            raise VecticeException("The iteration is cancelled and cannot be completed.")
        iteration_input = IterationInput(status=IterationStatus.Completed.name)
        self._client.update_iteration(self.id, iteration_input)
        self._status = IterationStatus.Completed
        logging_output = dedent(
            f"""
                        Iteration with index {self.index} completed.

                        For quick access to the Iteration in the Vectice web app, visit:
                        {self._client.auth._API_BASE_URL}/browse/iteration/{self.id}"""
        ).lstrip()
        _logger.info(logging_output)

    def delete(self) -> None:
        """Permanently deletes the iteration."""
        self._client.delete_iteration(self.id)
        _logger.info(f"Iteration with index {self.index} was deleted.")

    @property
    def connection(self) -> Connection:
        """The connection to which this iteration belongs.

        Returns:
            The connection to which this iteration belongs.
        """
        return self._phase.connection

    @property
    def workspace(self) -> Workspace:
        """The workspace to which this iteration belongs.

        Returns:
            The workspace to which this iteration belongs.
        """
        return self._phase.workspace

    @property
    def project(self) -> Project:
        """The project to which this iteration belongs.

        Returns:
            The project to which this iteration belongs.
        """
        return self._phase.project

    @property
    def phase(self) -> Phase:
        """The phase to which this iteration belongs.

        Returns:
            The phase to which this iteration belongs.
        """
        return self._phase
