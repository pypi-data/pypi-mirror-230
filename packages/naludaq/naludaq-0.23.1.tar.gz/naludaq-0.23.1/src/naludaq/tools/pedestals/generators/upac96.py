import logging

import numpy as np

from naludaq.controllers import get_board_controller
from naludaq.helpers.exceptions import (
    IterationError,
    OperationCanceledError,
    PedestalsDataCaptureError,
    RegisterNameError,
)

from .udc16 import PedestalsGeneratorUdc16

LOGGER = logging.getLogger("naludaq.pedestals_generator_upac96")


def disable_trigger_monitor_signal(func):
    """Decorator to disable the trigger monitor signal during the execution of a function.

    Args:
        func (function): function to decorate

    Returns:
        function: decorated function
    """

    def wrapper(self, *args, **kwargs):
        try:
            previous = self.board.registers["control_registers"][
                "trigger_monitor_disable"
            ]["value"]
        except KeyError:
            raise RegisterNameError("trigger_monitor_disable")
        bc = get_board_controller(self.board)
        bc.set_trigger_monitoring_disabled(disabled=True)
        try:
            result = func(self, *args, **kwargs)
        finally:
            bc.set_trigger_monitoring_disabled(previous)
        return result

    return wrapper


class PedestalsGeneratorUpac96(PedestalsGeneratorUdc16):
    """Pedestals generator for UPAC96."""

    @disable_trigger_monitor_signal
    def _capture_data_for_pedestals(self) -> list[list[dict]]:
        """Capture raw data for pedestals.

        For UPAC96 it's a bit different. We need to throw away the first window and there's no forced mode,
        so it's random where the window hole shows up in the data. This capture function makes sure that
        regardless of where the hole shows up in each event, we have enough captures for all windows.

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
        get_actual_count = lambda events: np.min(
            self._get_window_counts(events)[self.channels]
        )
        pipeline = (
            self._create_data_pipeline()
            .accumulated()
            .take_while(lambda all: get_actual_count(all) < self._num_captures)
            .unaccumulated()
        )
        try:
            return [pipeline.collect()]
        except OperationCanceledError:
            raise
        except (TimeoutError, IterationError) as e:
            msg = (
                "Failed to capture an event. The board may be unresponsive "
                "or need to be power cycled/reinitialized."
            )
            LOGGER.error("Failed to capture an event!")
            raise PedestalsDataCaptureError(msg) from e

    def _validate_event(self, event):
        """Check if the event has a data field, which means it's parsed"""
        if "data" not in event:
            LOGGER.warning("Got an invalid event")
            return False
        chans_with_data = [i for i, x in enumerate(event.get("data", [])) if len(x) > 0]
        is_superset = set(chans_with_data).issuperset(self._channels)
        if not is_superset:
            LOGGER.warning(
                "Got a parseable event, but the channels are incorrect: %s",
                chans_with_data,
            )
        return is_superset

    def _get_window_counts(self, events: list[dict]) -> np.ndarray:
        """Calculate the number of times each window occurs in the given events.

        Args:
            events (list[dict]): list of validated events.

        Returns:
            np.ndarray: 2D int array with shape (channels, windows) containin
                window counts.
        """
        channels = self.board.channels
        windows = self.board.params["windows"]
        window_hits = np.zeros((channels, windows), dtype=int)

        # Count the number of times each window shows up in the data.
        for event in events:
            for chan, chan_window_labels in enumerate(event["window_labels"]):
                if len(chan_window_labels) == 0:
                    continue
                # skip first window, it's junk.
                window_hits[chan][chan_window_labels[1:-1]] += 1
        return window_hits

    def _store_raw_data(self, blocks: list[list[dict]]):
        num_captures = self._num_captures
        channels = self.board.params.get("channels", 96)
        windows = self.board.params.get("windows", 64)
        samples = self.board.params.get("samples", 64)
        rawdata = self.board.pedestals["rawdata"]
        window_counts = np.zeros((channels, windows), dtype=int)
        for event in blocks[0]:  # only one block for UPAC96
            for chan in range(channels):
                chan_data = event["data"][chan]
                for window_idx, window in enumerate(event["window_labels"][chan]):
                    # first/last windows are junk
                    if window_idx == 0 or window_idx == windows - 1:
                        continue

                    cap = window_counts[chan, window]
                    window_counts[chan, window] += 1
                    if cap >= num_captures:  # skip first few captures
                        continue

                    data = chan_data[window_idx * samples : (window_idx + 1) * samples]
                    rawdata[chan, window, :, cap] = data

        return True
