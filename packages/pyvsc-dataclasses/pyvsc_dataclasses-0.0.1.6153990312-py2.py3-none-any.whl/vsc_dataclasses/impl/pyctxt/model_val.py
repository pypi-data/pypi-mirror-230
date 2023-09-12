
import vsc_dataclasses.impl.context as ctxt_api

class ModelVal(ctxt_api.ModelVal):

    def __init__(self):
        self._bits = 0
        self._val = 0

    def bits(self) -> int:
        return self._bits

    def setBits(self, bits : int) ->int:
        self._bits = bits

    def val_u(self) -> int:
        return self._val

    def val_i(self) -> int:
        return self._val

    def set_val_i(self, v : int, bits : int=-1):
        print("TODO: set_val_i -- mask value")
        self._val = v

    def set_val_u(self, v : int, bits : int=-1):
        print("TODO: set_val_u -- mask value")
        self._val = v
