
import vsc_dataclasses.impl.context as ctxt_api
from .model_val import ModelVal
from .type_field import TypeField



class TypeFieldPhy(ctxt_api.TypeFieldPhy, TypeField):

    def __init__(self, name, dtype, attr, init):
        TypeField.__init__(self, name, dtype, attr)
        self._init = ModelVal()
        if init is not None:
            self._init.setBits(init.bits())
            self._init.set_val_u(init.val_u())

    def getInit(self) -> 'ModelVal':
        return self._init
    
    def accept(self, v):
        v.visitTypeFieldPhy(self)
