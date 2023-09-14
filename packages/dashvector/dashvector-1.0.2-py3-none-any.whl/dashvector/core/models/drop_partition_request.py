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


class DropPartitionRequest(RPCRequest):

    def __init__(self, *,
                 collection_meta: CollectionMeta,
                 partition_name: str):

        """
        collection_meta: CollectionMeta
        """
        self._collection_meta = collection_meta
        self._collection_name = collection_meta.name

        """
        partition_name: str
        """
        self._partition_name = ""
        if not isinstance(partition_name, str):
            raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                   reason=f"DashVectorSDK DropPartitionRequest name Type({partition_name}) is Invalid")

        if len(partition_name) < 3 or len(partition_name) > 32:
            raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                   reason=f"DashVectorSDK DropPartitionRequest name Length({len(partition_name)}) is Invalid and must be in [3, 32]")

        if re.search(FIELD_NAME_PATTERN, partition_name) is None:
            raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                   reason=f"DashVectorSDK DropPartitionRequest name Characters({partition_name}) is Invalid and must be in [a-zA-Z0-9] and symbols[_, -]")
        self._partition_name = partition_name

        """
        DropPartitionRequest: google.protobuf.Message
        """
        drop_request = centaur_pb2.DropPartitionRequest()
        drop_request.collection_name = self._collection_name
        drop_request.partition_name = self._partition_name

        super().__init__(request=drop_request)

    @property
    def collection_name(self):
        return self._collection_name

    @property
    def partition_name(self):
        return self._partition_name