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

from dashvector.common.constants import *
from dashvector.common.handler import RPCRequest
from dashvector.common.types import *
from dashvector.core.proto import dashvector_pb2


class DeleteDocRequest(RPCRequest):

    def __init__(self, *,
                 collection_name: str,
                 ids: IdsType,
                 delete_all: bool = False,
                 # filter: Optional[str] = None,
                 partition: Optional[str] = None):
        """
        collection_name: str
        """
        self._collection_name = collection_name

        """
        delete_all: bool
        """
        if not isinstance(delete_all, bool):
            raise DashVectorException(
                code=DashVectorCode.InvalidArgumentType,
                reason=f"DashVectorSDK DeleteDocRequest delete_all({type(delete_all)}) type is invalid and must be bool")
        if delete_all:
            if bool(ids):
                raise DashVectorException(
                    code=DashVectorCode.EmptyDocList,
                    reason=f"DashVectorSDK DeleteDocRequest ids list must be empty when setting delete_all is True")

        """
        ids: IdsType
        """
        self._ids = []
        if not delete_all:
            if isinstance(ids, list):
                if len(ids) < 1 or len(ids) > 1024:
                    raise DashVectorException(
                        code=DashVectorCode.ExceedDocLimit,
                        reason=f"DashVectorSDK DeleteDocRequest ids list Length({len(ids)}) is Invalid and must be in [1, 1024]")

                for id in ids:
                    if isinstance(id, str):
                        if re.search(DOC_ID_PATTERN, id) is None:
                            raise DashVectorException(
                                code=DashVectorCode.InvalidDocId,
                                reason=f"DashVectorSDK DeleteDocRequest id in ids list Characters({id}) is Invalid and " +
                                DOC_ID_PATTERN_MSG)
                        self._ids.append(id)
                    else:
                        raise DashVectorException(
                            code=DashVectorCode.InvalidDocId,
                            reason=f"DashVectorSDK DeleteDocRequest id in ids list Type({type(id)}) is Invalid")
            elif isinstance(ids, str):
                if re.search(DOC_ID_PATTERN, ids) is None:
                    raise DashVectorException(
                        code=DashVectorCode.InvalidDocId,
                        reason=f"DashVectorSDK DeleteDocRequest ids str Characters({ids}) is Invalid and " +
                        DOC_ID_PATTERN_MSG)

                self._ids.append(ids)
            else:
                raise DashVectorException(
                    code=DashVectorCode.InvalidDocId,
                    reason=f"DashVectorSDK DeleteDocRequest ids Type({type(ids)}) is Invalid")

        """
        partition: Optional[str]
        """
        self._partition = None
        if partition is not None:
            if not isinstance(partition, str):
                raise DashVectorException(
                    code=DashVectorCode.InvalidPartitionName,
                    reason=f"DashVectorSDK DeleteDocRequest partition Type({type(partition)}) is Invalid")

            if re.search(
                    COLLECTION_AND_PARTITION_NAME_PATTERN,
                    partition) is None:
                raise DashVectorException(
                    code=DashVectorCode.InvalidPartitionName,
                    reason=f"DashVectorSDK DeleteDocRequest partition Characters({partition}) is Invalid and " +
                    COLLECTION_AND_PARTITION_NAME_PATTERN_MSG)

            self._partition = partition

        """
        DeleteDocRequest: google.protobuf.Message
        """
        delete_request = dashvector_pb2.DeleteDocRequest()
        delete_request.ids.extend(self._ids)
        delete_request.delete_all = delete_all
        if self._partition is not None:
            delete_request.partition = self._partition

        super().__init__(request=delete_request)

    @property
    def collection_name(self):
        return self._collection_name
