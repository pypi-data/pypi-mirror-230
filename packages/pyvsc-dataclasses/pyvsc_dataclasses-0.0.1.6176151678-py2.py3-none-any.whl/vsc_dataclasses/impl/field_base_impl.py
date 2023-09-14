#****************************************************************************
# Copyright 2019-2022 Matthew Ballance and contributors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Created on May 25, 2022
#
# @author: mballance
#****************************************************************************

import logging

from .context import Context
from .context import TypeExprFieldRefKind

from .ctor import Ctor
from .expr import Expr
from .modelinfo import ModelInfo


class FieldBaseImpl(object):
    
    def __init__(self, name, typeinfo, idx):
        self._modelinfo = ModelInfo(self, name, typeinfo, idx)
        self._logger = logging.getLogger(type(self).__name__)
        
    def _to_expr(self):
        ctor = Ctor.inst()

        if ctor.is_type_mode():
            self._logger.debug("FieldScalarImpl._to_expr (%s)" % self._modelinfo.name)
            mi = self._modelinfo
            self._logger.debug("is_topdown_scope: %d" % mi._is_topdown_scope)
            offset_l = []
            if mi._is_topdown_scope:            
                ref = ctor.ctxt().mkTypeExprFieldRef(
                    TypeExprFieldRefKind.TopDownScope,
                    -1
                )
            else:
                # Determine the location of the target scope by
                # traversing the bottom-up scopes until
                # we find the scope that the field belongs to
                level = 0

                for s in ctor.bottom_up_scopes()[::-1]:
                    if s is mi._parent:
                        break
                    level +=1

                ref = ctor.ctxt().mkTypeExprFieldRef(
                    TypeExprFieldRefKind.BottomUpScope,
                    level
                )

            while mi._parent is not None:
                self._logger.debug("  IDX: %d" % mi._idx)
                offset_l.insert(0, mi._idx)
                self._logger.debug("MI: %s" % str(mi))
                mi = mi._parent
            
            for off in offset_l:
                ref.addPathElem(off)
        else:        
            self._logger.debug("FieldScalarImpl._to_expr (%s)" % self.model().name())
            ref = ctor.ctxt().mkModelExprFieldRef(self.model())
        
        return Expr(ref)
    
