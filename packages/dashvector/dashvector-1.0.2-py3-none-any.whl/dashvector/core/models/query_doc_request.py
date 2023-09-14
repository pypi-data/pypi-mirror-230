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
from dashvector.core.models.collection_meta_status import CollectionMeta
from dashvector.core.proto import dashvector_pb2


class QueryDocRequest(RPCRequest):
    def __init__(self,
                 *,
                 collection_meta: CollectionMeta,
                 vector: VectorValueType,
                 # id: Optional[str] = None,
                 topk: int = 10,
                 filter: Optional[str] = None,
                 include_vector: bool = False,
                 partition: Optional[str] = None,
                 output_fields: Optional[List[str]] = None,
                 sparse_vector: Optional[Dict[int, float]] = None):

        self._collection_meta = collection_meta
        self._collection_name = collection_meta.name
        self._dtype = VectorType.get(collection_meta.dtype)
        self._dimension = collection_meta.dimension
        self._field_map = collection_meta.fields_schema
        self._origin_vector = vector
        self._metric = collection_meta.metric
        '''
        QueryRequest
        '''
        query_request = dashvector_pb2.QueryDocRequest()

        '''
        vector: Optional[VectorValueType] = None
        '''
        self._vector = vector
        if isinstance(self._vector, list):
            if len(self._vector) != self._dimension:
                raise DashVectorException(
                    code=DashVectorCode.MismatchedDimension,
                    reason=f"DashVectorSDK QueryDocRequest vector List Length({len(self._vector)}) is Invalid and must be same with Collection Dimension({self._dimension})")
            vector_data_type = VectorType.get_vector_data_type(
                type(self._vector[0]))
            if vector_data_type != self._dtype:
                raise DashVectorException(
                    code=DashVectorCode.MismatchedDataType,
                    reason=f"DashVectorSDK QueryDocRequest vector Type({type(self._vector[0])}) is Invalid and must be {collection_meta.dtype}")
            if vector_data_type == VectorType.INT:
                try:
                    self._vector = VectorType.convert_to_bytes(
                        self._vector, self._dtype, self._dimension)
                except Exception as e:
                    raise DashVectorException(
                        code=DashVectorCode.InvalidVectorFormat,
                        reason=f"DashVectorSDK QueryDocRequest vector Value({vector}) is Invalid and int value must be [-128, 127]")
        elif isinstance(self._vector, np.ndarray):
            if self._vector.ndim != 1:
                raise DashVectorException(
                    code=DashVectorCode.InvalidArgumentType,
                    reason=f"DashVectorSDK QueryDocRequest vector NumPy Dimension({self._vector.ndim}) is Invalid and must be 1")
            if self._vector.shape[0] != self._dimension:
                raise DashVectorException(
                    code=DashVectorCode.MismatchedDimension,
                    reason=f"DashVectorSDK QueryDocRequest vector NumPy Shape[0]({self._vector.shape[0]}) is Invalid and must be same with Collection Dimension({self._dimension})")
        else:
            raise DashVectorException(
                code=DashVectorCode.InvalidVectorFormat,
                reason=f"DashVectorSDK QueryDocRequest vector Type({type(self._vector)}) is Invalid")

        if isinstance(self._vector, list):
            query_request.vector.float_vector.values.extend(self._vector)
        elif isinstance(self._vector, bytes):
            query_request.vector.byte_vector = self._vector
        elif isinstance(self._vector, np.ndarray):
            if self._dtype == VectorType.INT:
                data_format_type = VectorType.get_vector_data_format(
                    self._dtype)
                self._vector = np.ascontiguousarray(
                    self._vector, dtype=f'<{data_format_type}').tobytes()
                query_request.vector.byte_vector = self._vector
            else:
                self._vector = list(self._vector)
                query_request.vector.float_vector.values.extend(self._vector)
        '''
        topk: int = 10
        '''
        self._topk = topk
        if not isinstance(topk, int):
            raise DashVectorException(
                code=DashVectorCode.InvalidTopk,
                reason=f"DashVectorSDK QueryDocRequest topk Type({type(topk)}) is Invalid")
        if topk < 1 or topk > 1024:
            raise DashVectorException(
                code=DashVectorCode.InvalidTopk,
                reason=f"DashVectorSDK GetDocRequest topk Value({topk}) is Invalid and must be in [1, 1024]")
        query_request.topk = self._topk

        '''
        filter: Optional[str] = None,
        '''
        self._filter = None
        if filter is not None:
            if not isinstance(filter, str):
                raise DashVectorException(
                    code=DashVectorCode.InvalidFilter,
                    reason=f"DashVectorSDK QueryDocRequest filter Type({type(filter)}) is Invalid")

            if len(filter) > 10240:
                raise DashVectorException(
                    code=DashVectorCode.InvalidFilter,
                    reason=f"DashVectorSDK GetDocRequest filter Length({len(filter)}) is Invalid and must be in [0, 10240]")

            if len(filter) > 0:
                self._filter = filter
        if self._filter is not None:
            query_request.filter = self._filter

        '''
        include_vector: bool = False,
        '''
        self._include_vector = include_vector
        if not isinstance(include_vector, bool):
            raise DashVectorException(
                code=DashVectorCode.InvalidArgumentType,
                reason=f"DashVectorSDK QueryDocRequest include_vector Type({type(include_vector)}) is Invalid")
        query_request.include_vector = self._include_vector

        '''
        partition: Optional[str] = None
        '''
        self._partition = None
        if partition is not None:
            if not isinstance(partition, str):
                raise DashVectorException(
                    code=DashVectorCode.InvalidPartitionName,
                    reason=f"DashVectorSDK QueryDocRequest partition Type({type(partition)}) is Invalid")

            if re.search(
                    COLLECTION_AND_PARTITION_NAME_PATTERN,
                    partition) is None:
                raise DashVectorException(
                    code=DashVectorCode.InvalidPartitionName,
                    reason=f"DashVectorSDK QueryDocRequest partition Characters({partition}) is Invalid and " +
                    COLLECTION_AND_PARTITION_NAME_PATTERN_MSG)

            self._partition = partition
        if self._partition is not None:
            query_request.partition = self._partition

        '''
        output_fields: Optional[List[str]] = None
        '''
        self._output_fields = None
        if output_fields is not None:
            if isinstance(output_fields, list):
                for output_field in output_fields:
                    if not isinstance(output_field, str):
                        raise DashVectorException(
                            code=DashVectorCode.InvalidField,
                            reason=f"DashVectorSDK QueryDocRequest output_field in output_fields Type({type(output_field)}) is Invalid and must be list[str]")

                    if re.search(FIELD_NAME_PATTERN, output_field) is None:
                        raise DashVectorException(
                            code=DashVectorCode.InvalidField,
                            reason=f"DashVectorSDK QueryDocRequest output_field in output_fields Characters({output_field}) is Invalid and " +
                            FIELD_NAME_PATTERN_MSG)

                self._output_fields = output_fields
            else:
                raise DashVectorException(
                    code=DashVectorCode.InvalidField,
                    reason=f"DashVectorSDK QueryDocRequest output_fields Type({type(output_fields)}) is Invalid")
        if self._output_fields is not None:
            query_request.output_fields.extend(self._output_fields)

        """
        sparse_vector: Optional[Dict[int, float]] = None
        """
        self._sparse_vector = sparse_vector
        if self._sparse_vector is not None:
            if self._metric != MetricStrType.DOTPRODUCT:
                raise DashVectorException(
                    code=DashVectorCode.InvalidSparseValues,
                    reason=f"DashVectorSDK supports query with sparse_vector only collection metric is dotproduct")
            if not isinstance(self._sparse_vector, dict):
                raise DashVectorException(
                    code=DashVectorCode.InvalidSparseValues,
                    reason=f"DashVectorSDK QueryDocRequest sparse_vector Type({type(sparse_vector)}) is Invalid and must be Dict[int, float]")
            for key in self._sparse_vector.keys():
                if not isinstance(
                        key, int) or not isinstance(
                        self._sparse_vector[key], float):
                    raise DashVectorException(
                        code=DashVectorCode.InvalidSparseValues,
                        reason=f"DashVectorSDK QueryDocRequest sparse_vector Type({type(sparse_vector)}) is Invalid and must be Dict[int, float]")
                query_request.sparse_vector[key] = self._sparse_vector[key]
        super().__init__(request=query_request)

    @property
    def collection_meta(self):
        return self._collection_meta

    @property
    def collection_name(self):
        return self._collection_name

    @property
    def include_vector(self):
        return self._include_vector

    def to_json(self):
        vector = self._origin_vector
        if isinstance(vector, np.ndarray):
            vector = vector.astype(np.float32).tolist()
        data = {
            "vector": vector,
            "topk": self._topk,
            "include_vector": self._include_vector,
        }
        if self._filter is not None:
            data["filter"] = self._filter
        if self._partition is not None:
            data["partition"] = self._partition
        if self._sparse_vector is not None:
            data["sparse_vector"] = self._sparse_vector
        if self._output_fields is not None:
            data["output_fields"] = self._output_fields

        return json.dumps(data)
