#****************************************************************************
#* type_expr_field_ref.py
#*
#* Copyright 2022 Matthew Ballance and Contributors
#*
#* Licensed under the Apache License, Version 2.0 (the "License"); you may 
#* not use this file except in compliance with the License.  
#* You may obtain a copy of the License at:
#*
#*   http://www.apache.org/licenses/LICENSE-2.0
#*
#* Unless required by applicable law or agreed to in writing, software 
#* distributed under the License is distributed on an "AS IS" BASIS, 
#* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  
#* See the License for the specific language governing permissions and 
#* limitations under the License.
#*
#* Created on:
#*     Author: 
#*
#****************************************************************************

import vsc_dataclasses.impl.context as ctxt_api

class TypeExprFieldRefElem(object):
    def __init__(self, kind, idx):
        self.kind = kind
        self.idx = idx

class TypeExprFieldRef(ctxt_api.TypeExprFieldRef):

    def __init__(self, kind, offset):
        self._kind = kind
        self._offset = offset
        self._path = []
        pass

    def getRootRefKind(self):
        return self._kind

    def addIdxRef(self, idx : int):
        self._path.append(TypeExprFieldRefElem(ctxt_api.TypeExprFieldRefElemKind.IdxOffset, idx))

    def addActiveScopeRef(self, off : int):
        self._path.append(TypeExprFieldRefElem(ctxt_api.TypeExprFieldRefElemKind.ActiveScope, off))

    def addRootRef(self):
        self._path.append(TypeExprFieldRefElem(ctxt_api.TypeExprFieldRefElemKind.Root, -1))

    def addRef(self, ref : 'TypeExprFieldRefElem'):
        raise NotImplementedError("addRef")

    def at(self, idx : int) -> 'TypeExprFieldRefElem':
        raise NotImplementedError("at")
    
    def addPathElem(self, idx):
        self._path.append(idx)

    def getPath(self) -> 'List[TypeExprFieldRefElem]':
        return self._path

    def accept(self, v):
        v.visitTypeExprFieldRef(self)
