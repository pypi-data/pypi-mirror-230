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
from dashvector.common.error import DashVectorCode, DashVectorException
from dashvector.common.handler import RPCRequest
from dashvector.core.proto import centaur_pb2


class DropCollectionRequest(RPCRequest):
    def __init__(self, *,
                 name: str):

        """
        name: str
        """
        self._name = ""
        if not isinstance(name, str):
            raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                   reason=f"DashVectorSDK DropCollectionRequest name Type({name}) is Invalid")

        if len(name) < 3 or len(name) > 32:
            raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                   reason=f"DashVectorSDK DropCollectionRequest name Length({len(name)}) is Invalid and must be in [3, 32]")

        if re.search(FIELD_NAME_PATTERN, name) is None:
            raise DashVectorException(code=DashVectorCode.InvalidArgument,
                                   reason=f"DashVectorSDK DropCollectionRequest name Characters({len(name)}) is Invalid and must be in [a-zA-Z0-9] and symbols[_, -]")
        self._name = name

        """
        DropCollectionRequest: google.protobuf.Message
        """
        drop_request = centaur_pb2.DropCollectionRequest(collection_name=self._name)

        super().__init__(request=drop_request)

    @property
    def name(self):
        return self._name
