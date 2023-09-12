import logging

from naludaq.helpers import FancyIterator
from naludaq.helpers.exceptions import (
    IterationError,
    OperationCanceledError,
    PedestalsDataCaptureError,
)

from .default import PedestalsGenerator

LOGGER = logging.getLogger("naludaq.pedestals_generator_udc16")


class PedestalsGeneratorUdc16(PedestalsGenerator):
    """Pedestals generator for UDC16."""

    def _capture_data_for_pedestals(self) -> list[list[dict]]:
        """Capture raw data for pedestals.

        Returns:
            list[list[dict]]: list of data for blocks. Warmup events
                are removed from the output.

        Raises:
            PedestalsDataCaptureError: if pedestals failed to generate.
            OperationCanceledError: if pedestals generation was cancelled.
        """
        LOGGER.debug(
            "Capturing pedestals for %s. channels=%s",
            self.board.model,
            self._channels,
        )
        n_events = self._num_captures + self._num_warmup_events
        try:
            events = self._create_data_pipeline().take(n_events).collect()
        except OperationCanceledError:
            raise
        except (TimeoutError, IterationError) as e:
            msg = (
                "Failed to capture enough events. The board may be unresponsive "
                "and need to be power cycled/reinitialized."
            )
            raise PedestalsDataCaptureError(msg) from e
        return [events]

    def _create_validation_stage(self, pipeline: FancyIterator) -> FancyIterator:
        return pipeline.filter(self._validate_event, exclusion_limit=10)

    def _validate_event(self, event: dict) -> bool:
        """Validate an event.

        The expected_window_labels argument is ignored for UDC16,
        since if it's parsed then it's probably valid.
        """
        return "data" in event

    def _backup_settings(self) -> dict:
        return {}

    def _create_progress_update_stage(self, pipeline: FancyIterator) -> FancyIterator:
        total_events = self._num_warmup_events + self._num_captures
        min_progress = 20
        max_progress = 80

        def inner(x):
            idx = x[0]
            percent = min_progress + (max_progress - min_progress) * idx / total_events
            msg = f"Capturing event {idx + 1}/{total_events}"
            self._update_progress(percent, msg)

        return pipeline.enumerate().for_each(inner).unenumerate()
