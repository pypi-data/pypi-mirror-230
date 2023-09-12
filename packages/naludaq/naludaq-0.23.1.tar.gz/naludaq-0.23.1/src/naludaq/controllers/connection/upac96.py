from logging import getLogger

from naludaq.controllers.board import get_board_controller

from . import ConnectionController

LOGGER = getLogger("naludaq.connection_controller_upac96")
UART_LIKE = ["uart", "ftdi", "d2xx"]
USB_TYPES = ["ft60x", "d3xx"]


class Upac96ConnectionController(ConnectionController):
    """Connection controller for UPAC96.

    UPAC96 boards have different, mutually exclusive paths for UART/FTDI and USB3.
    This connection controller attempts to set the correct FIFO on the board
    for the board's connection type.
    """

    def _get_sync_response(self) -> int:
        """Tries to read the identifier register."""
        self._try_switch_output_fifo()
        return super()._get_sync_response()

    def _try_switch_output_fifo(self):
        """Tries to switch the output FIFO on the board according to the
        board connection type.

        This will always work for switching from UART/FTDI to USB3, but may or
        may not work for UART/FTDI depending on whether the baud rate is matched.

        Raises:
            NotImplementedError: if the connection type is invalid.
        """
        conn_type = self.board.connection_info.get("type", None)
        if conn_type in UART_LIKE:
            get_board_controller(self.board).enable_uart()
        elif conn_type in USB_TYPES:
            get_board_controller(self.board).enable_usb()
        else:
            raise NotImplementedError(
                f"Invalid connection type for UPAC96: {conn_type}"
            )

    def _configure_non_ethernet(self):
        super()._configure_non_ethernet()
        self._try_switch_output_fifo()
