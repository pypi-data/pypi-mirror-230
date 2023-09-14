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

import grpc
import dashvector.core.proto.centaur_pb2 as centaur__pb2


class CentaurServiceStub(object):
  """! GRPC service
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.create_collection = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/create_collection',
        request_serializer=centaur__pb2.CreateCollectionRequest.SerializeToString,
        response_deserializer=centaur__pb2.CreateCollectionResponse.FromString,
        )
    self.drop_collection = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/drop_collection',
        request_serializer=centaur__pb2.DropCollectionRequest.SerializeToString,
        response_deserializer=centaur__pb2.DropCollectionResponse.FromString,
        )
    self.describe_collection = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/describe_collection',
        request_serializer=centaur__pb2.DescribeCollectionRequest.SerializeToString,
        response_deserializer=centaur__pb2.DescribeCollectionResponse.FromString,
        )
    self.list_collections = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/list_collections',
        request_serializer=centaur__pb2.ListCollectionRequest.SerializeToString,
        response_deserializer=centaur__pb2.ListCollectionResponse.FromString,
        )
    self.stats_collection = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/stats_collection',
        request_serializer=centaur__pb2.StatsCollectionRequest.SerializeToString,
        response_deserializer=centaur__pb2.StatsCollectionResponse.FromString,
        )
    self.insert_doc = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/insert_doc',
        request_serializer=centaur__pb2.InsertDocRequest.SerializeToString,
        response_deserializer=centaur__pb2.InsertDocResponse.FromString,
        )
    self.update_doc = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/update_doc',
        request_serializer=centaur__pb2.UpdateDocRequest.SerializeToString,
        response_deserializer=centaur__pb2.UpdateDocResponse.FromString,
        )
    self.delete_doc = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/delete_doc',
        request_serializer=centaur__pb2.DeleteDocRequest.SerializeToString,
        response_deserializer=centaur__pb2.DeleteDocResponse.FromString,
        )
    self.upsert_doc = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/upsert_doc',
        request_serializer=centaur__pb2.UpsertDocRequest.SerializeToString,
        response_deserializer=centaur__pb2.UpsertDocResponse.FromString,
        )
    self.query = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/query',
        request_serializer=centaur__pb2.QueryRequest.SerializeToString,
        response_deserializer=centaur__pb2.QueryResponse.FromString,
        )
    self.query_by_sql = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/query_by_sql',
        request_serializer=centaur__pb2.SqlQueryRequest.SerializeToString,
        response_deserializer=centaur__pb2.SqlQueryResponse.FromString,
        )
    self.get_doc_by_key = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/get_doc_by_key',
        request_serializer=centaur__pb2.GetDocRequest.SerializeToString,
        response_deserializer=centaur__pb2.GetDocResponse.FromString,
        )
    self.create_partition = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/create_partition',
        request_serializer=centaur__pb2.CreatePartitionRequest.SerializeToString,
        response_deserializer=centaur__pb2.CreatePartitionResponse.FromString,
        )
    self.drop_partition = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/drop_partition',
        request_serializer=centaur__pb2.DropPartitionRequest.SerializeToString,
        response_deserializer=centaur__pb2.DropPartitionResponse.FromString,
        )
    self.describe_partition = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/describe_partition',
        request_serializer=centaur__pb2.DescribePartitionRequest.SerializeToString,
        response_deserializer=centaur__pb2.DescribePartitionResponse.FromString,
        )
    self.get_version = channel.unary_unary(
        '/proxima.centaur.proto.CentaurService/get_version',
        request_serializer=centaur__pb2.GetVersionRequest.SerializeToString,
        response_deserializer=centaur__pb2.GetVersionResponse.FromString,
        )


class CentaurServiceServicer(object):
  """! GRPC service
  """

  def create_collection(self, request, context):
    """Create a collection
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def drop_collection(self, request, context):
    """Drop a collection
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def describe_collection(self, request, context):
    """Get information of a collection
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def list_collections(self, request, context):
    """Get all collection information
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def stats_collection(self, request, context):
    """Get collection statistics
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def insert_doc(self, request, context):
    """Insert records
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def update_doc(self, request, context):
    """Update records
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def delete_doc(self, request, context):
    """Delete records
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def upsert_doc(self, request, context):
    """Upsert records
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def query(self, request, context):
    """Knn query docs
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def query_by_sql(self, request, context):
    """Knn query docs by sql
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def get_doc_by_key(self, request, context):
    """Get doc information by primary key
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def create_partition(self, request, context):
    """Create a partition
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def drop_partition(self, request, context):
    """Drop a partition
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def describe_partition(self, request, context):
    """Get information of a partition
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def get_version(self, request, context):
    """Get server version
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_CentaurServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'create_collection': grpc.unary_unary_rpc_method_handler(
          servicer.create_collection,
          request_deserializer=centaur__pb2.CreateCollectionRequest.FromString,
          response_serializer=centaur__pb2.CreateCollectionResponse.SerializeToString,
      ),
      'drop_collection': grpc.unary_unary_rpc_method_handler(
          servicer.drop_collection,
          request_deserializer=centaur__pb2.DropCollectionRequest.FromString,
          response_serializer=centaur__pb2.DropCollectionResponse.SerializeToString,
      ),
      'describe_collection': grpc.unary_unary_rpc_method_handler(
          servicer.describe_collection,
          request_deserializer=centaur__pb2.DescribeCollectionRequest.FromString,
          response_serializer=centaur__pb2.DescribeCollectionResponse.SerializeToString,
      ),
      'list_collections': grpc.unary_unary_rpc_method_handler(
          servicer.list_collections,
          request_deserializer=centaur__pb2.ListCollectionRequest.FromString,
          response_serializer=centaur__pb2.ListCollectionResponse.SerializeToString,
      ),
      'stats_collection': grpc.unary_unary_rpc_method_handler(
          servicer.stats_collection,
          request_deserializer=centaur__pb2.StatsCollectionRequest.FromString,
          response_serializer=centaur__pb2.StatsCollectionResponse.SerializeToString,
      ),
      'insert_doc': grpc.unary_unary_rpc_method_handler(
          servicer.insert_doc,
          request_deserializer=centaur__pb2.InsertDocRequest.FromString,
          response_serializer=centaur__pb2.InsertDocResponse.SerializeToString,
      ),
      'update_doc': grpc.unary_unary_rpc_method_handler(
          servicer.update_doc,
          request_deserializer=centaur__pb2.UpdateDocRequest.FromString,
          response_serializer=centaur__pb2.UpdateDocResponse.SerializeToString,
      ),
      'delete_doc': grpc.unary_unary_rpc_method_handler(
          servicer.delete_doc,
          request_deserializer=centaur__pb2.DeleteDocRequest.FromString,
          response_serializer=centaur__pb2.DeleteDocResponse.SerializeToString,
      ),
      'upsert_doc': grpc.unary_unary_rpc_method_handler(
          servicer.upsert_doc,
          request_deserializer=centaur__pb2.UpsertDocRequest.FromString,
          response_serializer=centaur__pb2.UpsertDocResponse.SerializeToString,
      ),
      'query': grpc.unary_unary_rpc_method_handler(
          servicer.query,
          request_deserializer=centaur__pb2.QueryRequest.FromString,
          response_serializer=centaur__pb2.QueryResponse.SerializeToString,
      ),
      'query_by_sql': grpc.unary_unary_rpc_method_handler(
          servicer.query_by_sql,
          request_deserializer=centaur__pb2.SqlQueryRequest.FromString,
          response_serializer=centaur__pb2.SqlQueryResponse.SerializeToString,
      ),
      'get_doc_by_key': grpc.unary_unary_rpc_method_handler(
          servicer.get_doc_by_key,
          request_deserializer=centaur__pb2.GetDocRequest.FromString,
          response_serializer=centaur__pb2.GetDocResponse.SerializeToString,
      ),
      'create_partition': grpc.unary_unary_rpc_method_handler(
          servicer.create_partition,
          request_deserializer=centaur__pb2.CreatePartitionRequest.FromString,
          response_serializer=centaur__pb2.CreatePartitionResponse.SerializeToString,
      ),
      'drop_partition': grpc.unary_unary_rpc_method_handler(
          servicer.drop_partition,
          request_deserializer=centaur__pb2.DropPartitionRequest.FromString,
          response_serializer=centaur__pb2.DropPartitionResponse.SerializeToString,
      ),
      'describe_partition': grpc.unary_unary_rpc_method_handler(
          servicer.describe_partition,
          request_deserializer=centaur__pb2.DescribePartitionRequest.FromString,
          response_serializer=centaur__pb2.DescribePartitionResponse.SerializeToString,
      ),
      'get_version': grpc.unary_unary_rpc_method_handler(
          servicer.get_version,
          request_deserializer=centaur__pb2.GetVersionRequest.FromString,
          response_serializer=centaur__pb2.GetVersionResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'proxima.centaur.proto.CentaurService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))


class HttpCentaurServiceStub(object):
  """! Restful APIs of CentaurService
  """

  def __init__(self, channel):
    """Constructor.

    Args:
      channel: A grpc.Channel.
    """
    self.collection = channel.unary_unary(
        '/proxima.centaur.proto.HttpCentaurService/collection',
        request_serializer=centaur__pb2.HttpRequest.SerializeToString,
        response_deserializer=centaur__pb2.HttpResponse.FromString,
        )
    self.list_collections = channel.unary_unary(
        '/proxima.centaur.proto.HttpCentaurService/list_collections',
        request_serializer=centaur__pb2.HttpRequest.SerializeToString,
        response_deserializer=centaur__pb2.HttpResponse.FromString,
        )
    self.stats_collection = channel.unary_unary(
        '/proxima.centaur.proto.HttpCentaurService/stats_collection',
        request_serializer=centaur__pb2.HttpRequest.SerializeToString,
        response_deserializer=centaur__pb2.HttpResponse.FromString,
        )
    self.handle_doc = channel.unary_unary(
        '/proxima.centaur.proto.HttpCentaurService/handle_doc',
        request_serializer=centaur__pb2.HttpRequest.SerializeToString,
        response_deserializer=centaur__pb2.HttpResponse.FromString,
        )
    self.upsert_doc = channel.unary_unary(
        '/proxima.centaur.proto.HttpCentaurService/upsert_doc',
        request_serializer=centaur__pb2.HttpRequest.SerializeToString,
        response_deserializer=centaur__pb2.HttpResponse.FromString,
        )
    self.query = channel.unary_unary(
        '/proxima.centaur.proto.HttpCentaurService/query',
        request_serializer=centaur__pb2.HttpRequest.SerializeToString,
        response_deserializer=centaur__pb2.HttpResponse.FromString,
        )
    self.query_by_sql = channel.unary_unary(
        '/proxima.centaur.proto.HttpCentaurService/query_by_sql',
        request_serializer=centaur__pb2.HttpRequest.SerializeToString,
        response_deserializer=centaur__pb2.HttpResponse.FromString,
        )
    self.get_version = channel.unary_unary(
        '/proxima.centaur.proto.HttpCentaurService/get_version',
        request_serializer=centaur__pb2.HttpRequest.SerializeToString,
        response_deserializer=centaur__pb2.HttpResponse.FromString,
        )


class HttpCentaurServiceServicer(object):
  """! Restful APIs of CentaurService
  """

  def collection(self, request, context):
    """! Collection management APIS
    1. Create Collection
    Http: POST /v1/collection
    You can use the create collection API to create a new collection. When creating an
    index, you need specify the CollectionConfig as json string attached to the body
    2. Get Collection
    HTTP: GET /v1/collection/{collection_name}
    Returns information about one collection named by Path Param ${collection}.
    3. Delete Collection
    HTTP: DEL /v1/collection/{collection_name}
    Deletes an existing collection named by Path Param ${collection}

    ! Partition management APIS
    1. Create Partition
    Http: POST /v1/collection/partition
    You can use the create partition API to create a new partition.
    2. Get Partition
    HTTP: GET /v1/collection/{collection}/{partition}
    Returns information about one partition named by Path Param ${collection} and ${partition}.
    3. Delete Partition
    HTTP: DEL /v1/collection/{collection}/{partition}
    Deletes an existing partition named by Path Param ${collection} and ${partition}.
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def list_collections(self, request, context):
    """! List Collections
    HTTP: GET /v1/collections
    Returns information about collections.

    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def stats_collection(self, request, context):
    """! Retrieve Stats of Collection
    HTTP: GET /v1/collection/{collection}/stats

    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def handle_doc(self, request, context):
    """! Insert/update/delete/get doc of collection
    HTTP: POST /v1/collection/{collection}/doc
    HTTP: PUT /v1/collection/{collection}/doc
    HTTP: DELETE /v1/collection/{collection}/doc
    HTTP: GET /v1/collection/{collection}/doc?key={pk}[&partition={xxx}]

    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def upsert_doc(self, request, context):
    """! Upsert doc of collection
    HTTP: POST /v1/collection/{collection}/doc/upsert

    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def query(self, request, context):
    """! Query docs on collection
    HTTP: POST /v1/collection/{collection}/query

    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def query_by_sql(self, request, context):
    """! Query docs on collection by sql
    HTTP: POST /v1/collection/{collection}/sql

    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')

  def get_version(self, request, context):
    """! Get server version
    HTTP: GET /service_version
    Returns version string
    """
    context.set_code(grpc.StatusCode.UNIMPLEMENTED)
    context.set_details('Method not implemented!')
    raise NotImplementedError('Method not implemented!')


def add_HttpCentaurServiceServicer_to_server(servicer, server):
  rpc_method_handlers = {
      'collection': grpc.unary_unary_rpc_method_handler(
          servicer.collection,
          request_deserializer=centaur__pb2.HttpRequest.FromString,
          response_serializer=centaur__pb2.HttpResponse.SerializeToString,
      ),
      'list_collections': grpc.unary_unary_rpc_method_handler(
          servicer.list_collections,
          request_deserializer=centaur__pb2.HttpRequest.FromString,
          response_serializer=centaur__pb2.HttpResponse.SerializeToString,
      ),
      'stats_collection': grpc.unary_unary_rpc_method_handler(
          servicer.stats_collection,
          request_deserializer=centaur__pb2.HttpRequest.FromString,
          response_serializer=centaur__pb2.HttpResponse.SerializeToString,
      ),
      'handle_doc': grpc.unary_unary_rpc_method_handler(
          servicer.handle_doc,
          request_deserializer=centaur__pb2.HttpRequest.FromString,
          response_serializer=centaur__pb2.HttpResponse.SerializeToString,
      ),
      'upsert_doc': grpc.unary_unary_rpc_method_handler(
          servicer.upsert_doc,
          request_deserializer=centaur__pb2.HttpRequest.FromString,
          response_serializer=centaur__pb2.HttpResponse.SerializeToString,
      ),
      'query': grpc.unary_unary_rpc_method_handler(
          servicer.query,
          request_deserializer=centaur__pb2.HttpRequest.FromString,
          response_serializer=centaur__pb2.HttpResponse.SerializeToString,
      ),
      'query_by_sql': grpc.unary_unary_rpc_method_handler(
          servicer.query_by_sql,
          request_deserializer=centaur__pb2.HttpRequest.FromString,
          response_serializer=centaur__pb2.HttpResponse.SerializeToString,
      ),
      'get_version': grpc.unary_unary_rpc_method_handler(
          servicer.get_version,
          request_deserializer=centaur__pb2.HttpRequest.FromString,
          response_serializer=centaur__pb2.HttpResponse.SerializeToString,
      ),
  }
  generic_handler = grpc.method_handlers_generic_handler(
      'proxima.centaur.proto.HttpCentaurService', rpc_method_handlers)
  server.add_generic_rpc_handlers((generic_handler,))
