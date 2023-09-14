##
#   Copyright 2021 Alibaba, Inc. and its affiliates. All Rights Reserved.
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
##

# -*- coding: utf-8 -*-

import re
from dashvector.common.constants import FIELD_NAME_PATTERN
from dashvector.common.types import *
from dashvector.common.error import DashVectorCode, DashVectorException
from dashvector.common.handler import RPCRequest
from dashvector.core.proto import centaur_pb2


class GetDocRequest(RPCRequest):
    def __init__(self, *,
                 collection_meta: CollectionMeta,
                 ids: IdsType,
                 partition: Optional[str] = None):

        """
        collection_meta: CollectionMeta
        """
        self._collection_meta = collection_meta
        self._collection_name = collection_meta.name

        """
        ids: IdsType
        """
        self._ids = []
        self._ids_original = []
        self._ids_is_single = False
        if isinstance(ids, list):
            if len(ids) < 1 or len(ids) > 1024:
                raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                       reason=f"DashVectorSDK GetDocRequest ids list Length({len(ids)}) is Invalid and must be in [1, 1024]")

            for id in ids:
                if isinstance(id, int):
                    _id_str = str(id)
                    if len(_id_str) < 1 or len(_id_str) > 64:
                        raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                               reason=f"DashVectorSDK GetDocRequest id in ids list Length({len(_id_str)}) is Invalid and must be in [1, 64]")
                    self._ids.append(_id_str)
                    self._ids_original.append(id)
                elif isinstance(id, str):
                    if len(id) < 1 or len(id) > 64:
                        raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                               reason=f"DashVectorSDK GetDocRequest id in ids list Length({len(id)}) is Invalid and must be in [1, 64]")

                    if re.search('^[a-zA-Z0-9_\-!@#$%+=.]{0,64}$', id) is None:
                        raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                               reason=f"DashVectorSDK GetDocRequest id in ids list Characters({id}) is Invalid and must be in [a-zA-Z0-9] and symbols[_-!@#$%+=.]")
                    self._ids.append(id)
                    self._ids_original.append(id)
                else:
                    raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                           reason=f"DashVectorSDK GetDocRequest id in ids list Type({type(id)}) is Invalid")

        elif isinstance(ids, int):
            _ids_str = str(ids)

            if len(_ids_str) < 1 or len(_ids_str) > 128:
                raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                       reason=f"DashVectorSDK GetDocRequest ids int Length({len(_ids_str)}) is Invalid and must be in [2, 128]")

            self._ids.append(str(ids))
            self._ids_original.append(ids)
            self._ids_is_single = True
        elif isinstance(ids, str):
            if len(ids) < 1 or len(ids) > 64:
                raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                       reason=f"DashVectorSDK GetDocRequest ids str Length({len(ids)}) is Invalid and must be in [1, 64]")

            if re.search('^[a-zA-Z0-9_\-!@#$%+=.]{0,64}$', ids) is None:
                raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                       reason=f"DashVectorSDK GetDocRequest ids str Characters({ids}) is Invalid and must be in [a-zA-Z0-9] and symbols[_-!@#$%+=.]")

            self._ids.append(ids)
            self._ids_original.append(ids)
            self._ids_is_single = True
        else:
            raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                   reason=f"DashVectorSDK GetDocRequest ids Type({type(ids)}) is Invalid")

        """
        partition: Optional[str]
        """
        self._partition = None
        if partition is not None:
            if not isinstance(partition, str):
                raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                       reason=f"DashVectorSDK GetDocRequest partition Type({type(partition)}) is Invalid")

            if len(partition) < 3 or len(partition) > 32:
                raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                       reason=f"DashVectorSDK GetDocRequest partition Length({len(partition)}) is Invalid and must be in [3, 32]")

            if re.search(FIELD_NAME_PATTERN,partition) is None:
                raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                       reason=f"DashVectorSDK GetDocRequest partition Characters({partition}) is Invalid and must be in [a-zA-Z0-9] and symbols[_, -]")

            self._partition = partition

        """
        GetDocRequest: google.protobuf.Message
        """
        get_request = centaur_pb2.GetDocRequest()
        get_request.collection_name = self._collection_name
        get_request.pks.extend(self._ids)
        if self._partition is not None:
            get_request.partition = self._partition

        super().__init__(request=get_request)

    @property
    def collection_meta(self):
        return self._collection_meta

    @property
    def collection_name(self):
        return self._collection_name

    @property
    def include_vector(self):
        return True

    @property
    def ids(self):
        return self._ids_original

    @property
    def ids_is_single(self):
        return self._ids_is_single
