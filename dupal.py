from dupal_client import DuPalClient
from pal import PalBase


class DuPalBase:
    def __init__(self, pal: PalBase):
        self.pal = pal

    def set_inputs(self, inputs: int) -> int:
        raise NotImplementedError

    def clock(self) -> int:
        raise NotImplementedError


class DuPalBoard(DuPalBase):
    def __init__(self, pal: PalBase, port: str, delay: float = 0.01):
        super().__init__(pal)
        self._client = DuPalClient(port=port, delay=delay)
        self._client.init_board()
        self._client.control_led(1, 1)  # currently we only support 20-pin PALs

    def set_inputs(self, inputs: int) -> int:
        self._client.write_status(self.pal.map_inputs(inputs))
        self.pal.set_inputs(inputs)
        try:
            self.pal.set_register_inputs(None)  # set to "unknown"
        except NotImplementedError:
            pass
        return self.read_outputs()

    def read_outputs(self) -> int:
        outputs = self._client.read_status()
        self.pal.set_outputs(outputs)
        # assert outputs == self.pal.outputs_as_byte
        return self.pal.outputs_as_byte

    def clock(self) -> int:
        inputs = self.pal.inputs_as_byte
        self._client.write_status(
            self.pal.map_inputs(inputs, clock_bit=True)
        )  # with clock bit
        self._client.write_status(
            self.pal.map_inputs(inputs, clock_bit=False)
        )  # no clock bit
        outputs = self.read_outputs()
        self.pal.set_register_inputs(outputs)
        return outputs
