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

import sys
_b=sys.version_info[0]<3 and (lambda x:x) or (lambda x:x.encode('latin1'))
from google.protobuf.internal import enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor.FileDescriptor(
  name='centaur.proto',
  package='proxima.centaur.proto',
  syntax='proto3',
  serialized_options=_b('\n\036com.damo.proxima.centaur.protoP\001Z\025proxima/centaur/proto\200\001\001\370\001\001'),
  serialized_pb=_b('\n\rcentaur.proto\x12\x15proxima.centaur.proto\"\xef\x01\n\x0cGenericValue\x12\x15\n\x0b\x62ytes_value\x18\x01 \x01(\x0cH\x00\x12\x16\n\x0cstring_value\x18\x02 \x01(\tH\x00\x12\x14\n\nbool_value\x18\x03 \x01(\x08H\x00\x12\x15\n\x0bint32_value\x18\x04 \x01(\x05H\x00\x12\x15\n\x0bint64_value\x18\x05 \x01(\x03H\x00\x12\x16\n\x0cuint32_value\x18\x06 \x01(\rH\x00\x12\x16\n\x0cuint64_value\x18\x07 \x01(\x04H\x00\x12\x15\n\x0b\x66loat_value\x18\x08 \x01(\x02H\x00\x12\x16\n\x0c\x64ouble_value\x18\t \x01(\x01H\x00\x42\r\n\x0bvalue_oneof\"*\n\x0cKeyValuePair\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t\"&\n\x06Status\x12\x0c\n\x04\x63ode\x18\x01 \x01(\x05\x12\x0e\n\x06reason\x18\x02 \x01(\t\"I\n\x05\x46ield\x12\x0c\n\x04name\x18\x01 \x01(\t\x12\x32\n\x05value\x18\x02 \x01(\x0b\x32#.proxima.centaur.proto.GenericValue\"N\n\x03\x44oc\x12\n\n\x02pk\x18\x01 \x01(\t\x12,\n\x06\x66ields\x18\x02 \x03(\x0b\x32\x1c.proxima.centaur.proto.Field\x12\r\n\x05score\x18\x03 \x01(\x02\"\xc8\x03\n\x10\x43ollectionSchema\x12\x17\n\x0f\x63ollection_name\x18\x01 \x01(\t\x12\x43\n\x06\x66ields\x18\x02 \x03(\x0b\x32\x33.proxima.centaur.proto.CollectionSchema.FieldSchema\x12$\n\x1cmax_docs_per_mutable_segment\x18\x03 \x01(\x04\x12&\n\x1emax_docs_per_immutable_segment\x18\x04 \x01(\x04\x12\x15\n\rchannel_count\x18\x05 \x01(\r\x12\x15\n\rreplica_count\x18\x06 \x01(\r\x1a\xd9\x01\n\x0b\x46ieldSchema\x12\x12\n\nfield_name\x18\x01 \x01(\t\x12\x34\n\nindex_type\x18\x02 \x01(\x0e\x32 .proxima.centaur.proto.IndexType\x12\x32\n\tdata_type\x18\x03 \x01(\x0e\x32\x1f.proxima.centaur.proto.DataType\x12\x11\n\tdimension\x18\x04 \x01(\r\x12\x39\n\x0c\x65xtra_params\x18\x05 \x03(\x0b\x32#.proxima.centaur.proto.KeyValuePair\"F\n\tDocResult\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\x12\n\n\x02pk\x18\x02 \x01(\t\"\xef\x06\n\x0ePartitionStats\x12\x17\n\x0f\x63ollection_name\x18\x01 \x01(\t\x12\x17\n\x0ftotal_doc_count\x18\x02 \x01(\x04\x12\x1b\n\x13total_segment_count\x18\x03 \x01(\x04\x12\x1e\n\x16total_index_file_count\x18\x04 \x01(\x04\x12\x1d\n\x15total_index_file_size\x18\x05 \x01(\x04\x12I\n\rchannel_stats\x18\x06 \x03(\x0b\x32\x32.proxima.centaur.proto.PartitionStats.ChannelStats\x12\x1e\n\x16total_delete_doc_count\x18\x07 \x01(\x04\x1a\xb1\x03\n\x0cSegmentStats\x12\x12\n\nsegment_id\x18\x01 \x01(\r\x12N\n\x05state\x18\x02 \x01(\x0e\x32?.proxima.centaur.proto.PartitionStats.SegmentStats.SegmentState\x12\x11\n\tdoc_count\x18\x03 \x01(\x04\x12\x18\n\x10index_file_count\x18\x04 \x01(\x04\x12\x17\n\x0findex_file_size\x18\x05 \x01(\x04\x12\x12\n\nmin_doc_id\x18\x06 \x01(\x04\x12\x12\n\nmax_doc_id\x18\x07 \x01(\x04\x12\x15\n\rmin_timestamp\x18\n \x01(\x04\x12\x15\n\rmax_timestamp\x18\x0b \x01(\x04\x12\x12\n\nmin_offset\x18\x0c \x01(\x04\x12\x12\n\nmax_offset\x18\r \x01(\x04\x12\x14\n\x0csegment_path\x18\x0e \x01(\t\"c\n\x0cSegmentState\x12\x0e\n\nSS_CREATED\x10\x00\x12\x0e\n\nSS_MUTABLE\x10\x01\x12\x10\n\x0cSS_IMMUTABLE\x10\x02\x12\x0e\n\nSS_DUMPING\x10\x03\x12\x11\n\rSS_COMPACTING\x10\x04\x1a\xaf\x01\n\x0c\x43hannelStats\x12\x12\n\nchannel_id\x18\x01 \x01(\r\x12I\n\rsegment_stats\x18\x02 \x03(\x0b\x32\x32.proxima.centaur.proto.PartitionStats.SegmentStats\x12\x18\n\x10\x64\x65lete_doc_count\x18\x03 \x01(\x04\x12\x12\n\ncur_offset\x18\x04 \x01(\x04\x12\x12\n\nmax_offset\x18\x05 \x01(\x04\"\xd3\x01\n\x0f\x43ollectionStats\x12J\n\npartitions\x18\x01 \x03(\x0b\x32\x36.proxima.centaur.proto.CollectionStats.PartitionsEntry\x12\x1a\n\x12index_completeness\x18\x02 \x01(\x02\x1aX\n\x0fPartitionsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x34\n\x05value\x18\x02 \x01(\x0b\x32%.proxima.centaur.proto.PartitionStats:\x02\x38\x01\"3\n\x07\x44ocList\x12(\n\x04\x64ocs\x18\x01 \x03(\x0b\x32\x1a.proxima.centaur.proto.Doc\"\x99\x03\n\x0e\x43ollectionInfo\x12\x37\n\x06schema\x18\x01 \x01(\x0b\x32\'.proxima.centaur.proto.CollectionSchema\x12Q\n\x11\x63ollection_status\x18\x02 \x01(\x0e\x32\x36.proxima.centaur.proto.CollectionInfo.CollectionStatus\x12I\n\npartitions\x18\x03 \x03(\x0b\x32\x35.proxima.centaur.proto.CollectionInfo.PartitionsEntry\x1aY\n\x0fPartitionsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\x35\n\x05value\x18\x02 \x01(\x0e\x32&.proxima.centaur.proto.PartitionStatus:\x02\x38\x01\"U\n\x10\x43ollectionStatus\x12\x12\n\x0e\x43S_INITIALIZED\x10\x00\x12\x0e\n\nCS_SERVING\x10\x01\x12\x0f\n\x0b\x43S_DROPPING\x10\x02\x12\x0c\n\x08\x43S_ERROR\x10\x03\"\r\n\x0bHttpRequest\"\x0e\n\x0cHttpResponse\"R\n\x17\x43reateCollectionRequest\x12\x37\n\x06schema\x18\x01 \x01(\x0b\x32\'.proxima.centaur.proto.CollectionSchema\"I\n\x18\x43reateCollectionResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\"0\n\x15\x44ropCollectionRequest\x12\x17\n\x0f\x63ollection_name\x18\x01 \x01(\t\"G\n\x16\x44ropCollectionResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\"4\n\x19\x44\x65scribeCollectionRequest\x12\x17\n\x0f\x63ollection_name\x18\x01 \x01(\t\"\x86\x01\n\x1a\x44\x65scribeCollectionResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\x12\x39\n\ncollection\x18\x02 \x01(\x0b\x32%.proxima.centaur.proto.CollectionInfo\"\x17\n\x15ListCollectionRequest\"\x83\x01\n\x16ListCollectionResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\x12:\n\x0b\x63ollections\x18\x02 \x03(\x0b\x32%.proxima.centaur.proto.CollectionInfo\"1\n\x16StatsCollectionRequest\x12\x17\n\x0f\x63ollection_name\x18\x01 \x01(\t\"\x8a\x01\n\x17StatsCollectionResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\x12@\n\x10\x63ollection_stats\x18\x02 \x01(\x0b\x32&.proxima.centaur.proto.CollectionStats\"\x84\x01\n\x10InsertDocRequest\x12\x17\n\x0f\x63ollection_name\x18\x01 \x01(\t\x12\x30\n\x08\x64oc_list\x18\x02 \x01(\x0b\x32\x1e.proxima.centaur.proto.DocList\x12\x12\n\nrequest_id\x18\x03 \x01(\t\x12\x11\n\tpartition\x18\x04 \x01(\t\"y\n\x11InsertDocResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\x12\x35\n\x0b\x64oc_results\x18\x02 \x03(\x0b\x32 .proxima.centaur.proto.DocResult\"\x84\x01\n\x10UpdateDocRequest\x12\x17\n\x0f\x63ollection_name\x18\x01 \x01(\t\x12\x30\n\x08\x64oc_list\x18\x02 \x01(\x0b\x32\x1e.proxima.centaur.proto.DocList\x12\x12\n\nrequest_id\x18\x03 \x01(\t\x12\x11\n\tpartition\x18\x04 \x01(\t\"y\n\x11UpdateDocResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\x12\x35\n\x0b\x64oc_results\x18\x02 \x03(\x0b\x32 .proxima.centaur.proto.DocResult\"_\n\x10\x44\x65leteDocRequest\x12\x17\n\x0f\x63ollection_name\x18\x01 \x01(\t\x12\x0b\n\x03pks\x18\x02 \x03(\t\x12\x12\n\nrequest_id\x18\x03 \x01(\t\x12\x11\n\tpartition\x18\x04 \x01(\t\"y\n\x11\x44\x65leteDocResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\x12\x35\n\x0b\x64oc_results\x18\x02 \x03(\x0b\x32 .proxima.centaur.proto.DocResult\"\x84\x01\n\x10UpsertDocRequest\x12\x17\n\x0f\x63ollection_name\x18\x01 \x01(\t\x12\x30\n\x08\x64oc_list\x18\x02 \x01(\x0b\x32\x1e.proxima.centaur.proto.DocList\x12\x12\n\nrequest_id\x18\x03 \x01(\t\x12\x11\n\tpartition\x18\x04 \x01(\t\"y\n\x11UpsertDocResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\x12\x35\n\x0b\x64oc_results\x18\x02 \x03(\x0b\x32 .proxima.centaur.proto.DocResult\"\xfd\x03\n\x0cQueryRequest\x12\x17\n\x0f\x63ollection_name\x18\x01 \x01(\t\x12\x0c\n\x04topk\x18\x02 \x01(\r\x12\x12\n\ndebug_mode\x18\x03 \x01(\x08\x12I\n\x0evector_feature\x18\x04 \x01(\x0b\x32\x31.proxima.centaur.proto.QueryRequest.VectorFeature\x12\x0e\n\x06\x66ilter\x18\x05 \x01(\t\x12\x14\n\x0cquery_fields\x18\x06 \x03(\t\x12\x11\n\tpartition\x18\x07 \x01(\t\x12\x16\n\x0einclude_vector\x18\x08 \x01(\x08\x1a\x95\x02\n\rVectorFeature\x12\x12\n\nfield_name\x18\x01 \x01(\t\x12\x12\n\x08\x66\x65\x61tures\x18\x02 \x01(\x0cH\x00\x12\x10\n\x06matrix\x18\x03 \x01(\tH\x00\x12\x13\n\x0b\x62\x61tch_count\x18\x04 \x01(\r\x12\x11\n\tdimension\x18\x05 \x01(\r\x12\x32\n\tdata_type\x18\x06 \x01(\x0e\x32\x1f.proxima.centaur.proto.DataType\x12\x0e\n\x06radius\x18\x07 \x01(\x02\x12\x11\n\tis_linear\x18\x08 \x01(\x08\x12\x39\n\x0c\x65xtra_params\x18\t \x03(\x0b\x32#.proxima.centaur.proto.KeyValuePairB\x10\n\x0e\x66\x65\x61tures_value\"\x9b\x01\n\rQueryResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\x12\x33\n\x0b\x64oc_results\x18\x02 \x03(\x0b\x32\x1e.proxima.centaur.proto.DocList\x12\x12\n\ndebug_info\x18\x03 \x01(\t\x12\x12\n\nlatency_us\x18\x04 \x01(\x04\"2\n\x0fSqlQueryRequest\x12\x0b\n\x03sql\x18\x01 \x01(\t\x12\x12\n\ndebug_mode\x18\x02 \x01(\x08\"\x9e\x01\n\x10SqlQueryResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\x12\x33\n\x0b\x64oc_results\x18\x02 \x03(\x0b\x32\x1e.proxima.centaur.proto.DocList\x12\x12\n\ndebug_info\x18\x03 \x01(\t\x12\x12\n\nlatency_us\x18\x04 \x01(\x04\"\\\n\rGetDocRequest\x12\x17\n\x0f\x63ollection_name\x18\x01 \x01(\t\x12\x0b\n\x03pks\x18\x02 \x03(\t\x12\x12\n\ndebug_mode\x18\x03 \x01(\x08\x12\x11\n\tpartition\x18\x04 \x01(\t\"}\n\x0eGetDocResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\x12\x12\n\ndebug_info\x18\x02 \x01(\t\x12(\n\x04\x64ocs\x18\x03 \x03(\x0b\x32\x1a.proxima.centaur.proto.Doc\"\x13\n\x11GetVersionRequest\"T\n\x12GetVersionResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\x12\x0f\n\x07version\x18\x02 \x01(\t\"I\n\x16\x43reatePartitionRequest\x12\x17\n\x0f\x63ollection_name\x18\x01 \x01(\t\x12\x16\n\x0epartition_name\x18\x02 \x01(\t\"H\n\x17\x43reatePartitionResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\"G\n\x14\x44ropPartitionRequest\x12\x17\n\x0f\x63ollection_name\x18\x01 \x01(\t\x12\x16\n\x0epartition_name\x18\x02 \x01(\t\"F\n\x15\x44ropPartitionResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\"K\n\x18\x44\x65scribePartitionRequest\x12\x17\n\x0f\x63ollection_name\x18\x01 \x01(\t\x12\x16\n\x0epartition_name\x18\x02 \x01(\t\"\x8c\x01\n\x19\x44\x65scribePartitionResponse\x12-\n\x06status\x18\x01 \x01(\x0b\x32\x1d.proxima.centaur.proto.Status\x12@\n\x10partition_status\x18\x02 \x01(\x0e\x32&.proxima.centaur.proto.PartitionStatus*9\n\tIndexType\x12\x10\n\x0cIT_UNDEFINED\x10\x00\x12\x0b\n\x07IT_HNSW\x10\x01\x12\r\n\tIT_INVERT\x10\n*\xc7\x02\n\x08\x44\x61taType\x12\x10\n\x0c\x44T_UNDEFINED\x10\x00\x12\r\n\tDT_BINARY\x10\x01\x12\r\n\tDT_STRING\x10\x02\x12\x0b\n\x07\x44T_BOOL\x10\x03\x12\x0c\n\x08\x44T_INT32\x10\x04\x12\x0c\n\x08\x44T_INT64\x10\x05\x12\r\n\tDT_UINT32\x10\x06\x12\r\n\tDT_UINT64\x10\x07\x12\x0c\n\x08\x44T_FLOAT\x10\x08\x12\r\n\tDT_DOUBLE\x10\t\x12\x16\n\x12\x44T_VECTOR_BINARY32\x10\x14\x12\x16\n\x12\x44T_VECTOR_BINARY64\x10\x15\x12\x12\n\x0e\x44T_VECTOR_FP16\x10\x16\x12\x12\n\x0e\x44T_VECTOR_FP32\x10\x17\x12\x12\n\x0e\x44T_VECTOR_FP64\x10\x18\x12\x12\n\x0e\x44T_VECTOR_INT4\x10\x19\x12\x12\n\x0e\x44T_VECTOR_INT8\x10\x1a\x12\x13\n\x0f\x44T_VECTOR_INT16\x10\x1b*T\n\x0fPartitionStatus\x12\x12\n\x0e\x43S_INITIALIZED\x10\x00\x12\x0e\n\nCS_SERVING\x10\x01\x12\x0f\n\x0b\x43S_DROPPING\x10\x02\x12\x0c\n\x08\x43S_ERROR\x10\x03\x32\xab\r\n\x0e\x43\x65ntaurService\x12t\n\x11\x63reate_collection\x12..proxima.centaur.proto.CreateCollectionRequest\x1a/.proxima.centaur.proto.CreateCollectionResponse\x12n\n\x0f\x64rop_collection\x12,.proxima.centaur.proto.DropCollectionRequest\x1a-.proxima.centaur.proto.DropCollectionResponse\x12z\n\x13\x64\x65scribe_collection\x12\x30.proxima.centaur.proto.DescribeCollectionRequest\x1a\x31.proxima.centaur.proto.DescribeCollectionResponse\x12o\n\x10list_collections\x12,.proxima.centaur.proto.ListCollectionRequest\x1a-.proxima.centaur.proto.ListCollectionResponse\x12q\n\x10stats_collection\x12-.proxima.centaur.proto.StatsCollectionRequest\x1a..proxima.centaur.proto.StatsCollectionResponse\x12_\n\ninsert_doc\x12\'.proxima.centaur.proto.InsertDocRequest\x1a(.proxima.centaur.proto.InsertDocResponse\x12_\n\nupdate_doc\x12\'.proxima.centaur.proto.UpdateDocRequest\x1a(.proxima.centaur.proto.UpdateDocResponse\x12_\n\ndelete_doc\x12\'.proxima.centaur.proto.DeleteDocRequest\x1a(.proxima.centaur.proto.DeleteDocResponse\x12_\n\nupsert_doc\x12\'.proxima.centaur.proto.UpsertDocRequest\x1a(.proxima.centaur.proto.UpsertDocResponse\x12R\n\x05query\x12#.proxima.centaur.proto.QueryRequest\x1a$.proxima.centaur.proto.QueryResponse\x12_\n\x0cquery_by_sql\x12&.proxima.centaur.proto.SqlQueryRequest\x1a\'.proxima.centaur.proto.SqlQueryResponse\x12]\n\x0eget_doc_by_key\x12$.proxima.centaur.proto.GetDocRequest\x1a%.proxima.centaur.proto.GetDocResponse\x12q\n\x10\x63reate_partition\x12-.proxima.centaur.proto.CreatePartitionRequest\x1a..proxima.centaur.proto.CreatePartitionResponse\x12k\n\x0e\x64rop_partition\x12+.proxima.centaur.proto.DropPartitionRequest\x1a,.proxima.centaur.proto.DropPartitionResponse\x12w\n\x12\x64\x65scribe_partition\x12/.proxima.centaur.proto.DescribePartitionRequest\x1a\x30.proxima.centaur.proto.DescribePartitionResponse\x12\x62\n\x0bget_version\x12(.proxima.centaur.proto.GetVersionRequest\x1a).proxima.centaur.proto.GetVersionResponse2\xd6\x05\n\x12HttpCentaurService\x12U\n\ncollection\x12\".proxima.centaur.proto.HttpRequest\x1a#.proxima.centaur.proto.HttpResponse\x12[\n\x10list_collections\x12\".proxima.centaur.proto.HttpRequest\x1a#.proxima.centaur.proto.HttpResponse\x12[\n\x10stats_collection\x12\".proxima.centaur.proto.HttpRequest\x1a#.proxima.centaur.proto.HttpResponse\x12U\n\nhandle_doc\x12\".proxima.centaur.proto.HttpRequest\x1a#.proxima.centaur.proto.HttpResponse\x12U\n\nupsert_doc\x12\".proxima.centaur.proto.HttpRequest\x1a#.proxima.centaur.proto.HttpResponse\x12P\n\x05query\x12\".proxima.centaur.proto.HttpRequest\x1a#.proxima.centaur.proto.HttpResponse\x12W\n\x0cquery_by_sql\x12\".proxima.centaur.proto.HttpRequest\x1a#.proxima.centaur.proto.HttpResponse\x12V\n\x0bget_version\x12\".proxima.centaur.proto.HttpRequest\x1a#.proxima.centaur.proto.HttpResponseB?\n\x1e\x63om.damo.proxima.centaur.protoP\x01Z\x15proxima/centaur/proto\x80\x01\x01\xf8\x01\x01\x62\x06proto3')
)

_INDEXTYPE = _descriptor.EnumDescriptor(
  name='IndexType',
  full_name='proxima.centaur.proto.IndexType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='IT_UNDEFINED', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='IT_HNSW', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='IT_INVERT', index=2, number=10,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=6187,
  serialized_end=6244,
)
_sym_db.RegisterEnumDescriptor(_INDEXTYPE)

IndexType = enum_type_wrapper.EnumTypeWrapper(_INDEXTYPE)
_DATATYPE = _descriptor.EnumDescriptor(
  name='DataType',
  full_name='proxima.centaur.proto.DataType',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='DT_UNDEFINED', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_BINARY', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_STRING', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_BOOL', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_INT32', index=4, number=4,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_INT64', index=5, number=5,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_UINT32', index=6, number=6,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_UINT64', index=7, number=7,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_FLOAT', index=8, number=8,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_DOUBLE', index=9, number=9,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_VECTOR_BINARY32', index=10, number=20,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_VECTOR_BINARY64', index=11, number=21,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_VECTOR_FP16', index=12, number=22,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_VECTOR_FP32', index=13, number=23,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_VECTOR_FP64', index=14, number=24,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_VECTOR_INT4', index=15, number=25,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_VECTOR_INT8', index=16, number=26,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='DT_VECTOR_INT16', index=17, number=27,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=6247,
  serialized_end=6574,
)
_sym_db.RegisterEnumDescriptor(_DATATYPE)

DataType = enum_type_wrapper.EnumTypeWrapper(_DATATYPE)
_PARTITIONSTATUS = _descriptor.EnumDescriptor(
  name='PartitionStatus',
  full_name='proxima.centaur.proto.PartitionStatus',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='CS_INITIALIZED', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CS_SERVING', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CS_DROPPING', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CS_ERROR', index=3, number=3,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=6576,
  serialized_end=6660,
)
_sym_db.RegisterEnumDescriptor(_PARTITIONSTATUS)

PartitionStatus = enum_type_wrapper.EnumTypeWrapper(_PARTITIONSTATUS)
IT_UNDEFINED = 0
IT_HNSW = 1
IT_INVERT = 10
DT_UNDEFINED = 0
DT_BINARY = 1
DT_STRING = 2
DT_BOOL = 3
DT_INT32 = 4
DT_INT64 = 5
DT_UINT32 = 6
DT_UINT64 = 7
DT_FLOAT = 8
DT_DOUBLE = 9
DT_VECTOR_BINARY32 = 20
DT_VECTOR_BINARY64 = 21
DT_VECTOR_FP16 = 22
DT_VECTOR_FP32 = 23
DT_VECTOR_FP64 = 24
DT_VECTOR_INT4 = 25
DT_VECTOR_INT8 = 26
DT_VECTOR_INT16 = 27
CS_INITIALIZED = 0
CS_SERVING = 1
CS_DROPPING = 2
CS_ERROR = 3


_PARTITIONSTATS_SEGMENTSTATS_SEGMENTSTATE = _descriptor.EnumDescriptor(
  name='SegmentState',
  full_name='proxima.centaur.proto.PartitionStats.SegmentStats.SegmentState',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='SS_CREATED', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SS_MUTABLE', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SS_IMMUTABLE', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SS_DUMPING', index=3, number=3,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='SS_COMPACTING', index=4, number=4,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=1655,
  serialized_end=1754,
)
_sym_db.RegisterEnumDescriptor(_PARTITIONSTATS_SEGMENTSTATS_SEGMENTSTATE)

_COLLECTIONINFO_COLLECTIONSTATUS = _descriptor.EnumDescriptor(
  name='CollectionStatus',
  full_name='proxima.centaur.proto.CollectionInfo.CollectionStatus',
  filename=None,
  file=DESCRIPTOR,
  values=[
    _descriptor.EnumValueDescriptor(
      name='CS_INITIALIZED', index=0, number=0,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CS_SERVING', index=1, number=1,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CS_DROPPING', index=2, number=2,
      serialized_options=None,
      type=None),
    _descriptor.EnumValueDescriptor(
      name='CS_ERROR', index=3, number=3,
      serialized_options=None,
      type=None),
  ],
  containing_type=None,
  serialized_options=None,
  serialized_start=2526,
  serialized_end=2611,
)
_sym_db.RegisterEnumDescriptor(_COLLECTIONINFO_COLLECTIONSTATUS)


_GENERICVALUE = _descriptor.Descriptor(
  name='GenericValue',
  full_name='proxima.centaur.proto.GenericValue',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='bytes_value', full_name='proxima.centaur.proto.GenericValue.bytes_value', index=0,
      number=1, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='string_value', full_name='proxima.centaur.proto.GenericValue.string_value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='bool_value', full_name='proxima.centaur.proto.GenericValue.bool_value', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='int32_value', full_name='proxima.centaur.proto.GenericValue.int32_value', index=3,
      number=4, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='int64_value', full_name='proxima.centaur.proto.GenericValue.int64_value', index=4,
      number=5, type=3, cpp_type=2, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='uint32_value', full_name='proxima.centaur.proto.GenericValue.uint32_value', index=5,
      number=6, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='uint64_value', full_name='proxima.centaur.proto.GenericValue.uint64_value', index=6,
      number=7, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='float_value', full_name='proxima.centaur.proto.GenericValue.float_value', index=7,
      number=8, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='double_value', full_name='proxima.centaur.proto.GenericValue.double_value', index=8,
      number=9, type=1, cpp_type=5, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='value_oneof', full_name='proxima.centaur.proto.GenericValue.value_oneof',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=41,
  serialized_end=280,
)


_KEYVALUEPAIR = _descriptor.Descriptor(
  name='KeyValuePair',
  full_name='proxima.centaur.proto.KeyValuePair',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='proxima.centaur.proto.KeyValuePair.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='proxima.centaur.proto.KeyValuePair.value', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=282,
  serialized_end=324,
)


_STATUS = _descriptor.Descriptor(
  name='Status',
  full_name='proxima.centaur.proto.Status',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='code', full_name='proxima.centaur.proto.Status.code', index=0,
      number=1, type=5, cpp_type=1, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='reason', full_name='proxima.centaur.proto.Status.reason', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=326,
  serialized_end=364,
)


_FIELD = _descriptor.Descriptor(
  name='Field',
  full_name='proxima.centaur.proto.Field',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='name', full_name='proxima.centaur.proto.Field.name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='proxima.centaur.proto.Field.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=366,
  serialized_end=439,
)


_DOC = _descriptor.Descriptor(
  name='Doc',
  full_name='proxima.centaur.proto.Doc',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='pk', full_name='proxima.centaur.proto.Doc.pk', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fields', full_name='proxima.centaur.proto.Doc.fields', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='score', full_name='proxima.centaur.proto.Doc.score', index=2,
      number=3, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=441,
  serialized_end=519,
)


_COLLECTIONSCHEMA_FIELDSCHEMA = _descriptor.Descriptor(
  name='FieldSchema',
  full_name='proxima.centaur.proto.CollectionSchema.FieldSchema',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='field_name', full_name='proxima.centaur.proto.CollectionSchema.FieldSchema.field_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='index_type', full_name='proxima.centaur.proto.CollectionSchema.FieldSchema.index_type', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data_type', full_name='proxima.centaur.proto.CollectionSchema.FieldSchema.data_type', index=2,
      number=3, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='dimension', full_name='proxima.centaur.proto.CollectionSchema.FieldSchema.dimension', index=3,
      number=4, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='extra_params', full_name='proxima.centaur.proto.CollectionSchema.FieldSchema.extra_params', index=4,
      number=5, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=761,
  serialized_end=978,
)

_COLLECTIONSCHEMA = _descriptor.Descriptor(
  name='CollectionSchema',
  full_name='proxima.centaur.proto.CollectionSchema',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection_name', full_name='proxima.centaur.proto.CollectionSchema.collection_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='fields', full_name='proxima.centaur.proto.CollectionSchema.fields', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='max_docs_per_mutable_segment', full_name='proxima.centaur.proto.CollectionSchema.max_docs_per_mutable_segment', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='max_docs_per_immutable_segment', full_name='proxima.centaur.proto.CollectionSchema.max_docs_per_immutable_segment', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='channel_count', full_name='proxima.centaur.proto.CollectionSchema.channel_count', index=4,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='replica_count', full_name='proxima.centaur.proto.CollectionSchema.replica_count', index=5,
      number=6, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_COLLECTIONSCHEMA_FIELDSCHEMA, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=522,
  serialized_end=978,
)


_DOCRESULT = _descriptor.Descriptor(
  name='DocResult',
  full_name='proxima.centaur.proto.DocResult',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.DocResult.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pk', full_name='proxima.centaur.proto.DocResult.pk', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=980,
  serialized_end=1050,
)


_PARTITIONSTATS_SEGMENTSTATS = _descriptor.Descriptor(
  name='SegmentStats',
  full_name='proxima.centaur.proto.PartitionStats.SegmentStats',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='segment_id', full_name='proxima.centaur.proto.PartitionStats.SegmentStats.segment_id', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='state', full_name='proxima.centaur.proto.PartitionStats.SegmentStats.state', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='doc_count', full_name='proxima.centaur.proto.PartitionStats.SegmentStats.doc_count', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='index_file_count', full_name='proxima.centaur.proto.PartitionStats.SegmentStats.index_file_count', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='index_file_size', full_name='proxima.centaur.proto.PartitionStats.SegmentStats.index_file_size', index=4,
      number=5, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='min_doc_id', full_name='proxima.centaur.proto.PartitionStats.SegmentStats.min_doc_id', index=5,
      number=6, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='max_doc_id', full_name='proxima.centaur.proto.PartitionStats.SegmentStats.max_doc_id', index=6,
      number=7, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='min_timestamp', full_name='proxima.centaur.proto.PartitionStats.SegmentStats.min_timestamp', index=7,
      number=10, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='max_timestamp', full_name='proxima.centaur.proto.PartitionStats.SegmentStats.max_timestamp', index=8,
      number=11, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='min_offset', full_name='proxima.centaur.proto.PartitionStats.SegmentStats.min_offset', index=9,
      number=12, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='max_offset', full_name='proxima.centaur.proto.PartitionStats.SegmentStats.max_offset', index=10,
      number=13, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='segment_path', full_name='proxima.centaur.proto.PartitionStats.SegmentStats.segment_path', index=11,
      number=14, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
    _PARTITIONSTATS_SEGMENTSTATS_SEGMENTSTATE,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1321,
  serialized_end=1754,
)

_PARTITIONSTATS_CHANNELSTATS = _descriptor.Descriptor(
  name='ChannelStats',
  full_name='proxima.centaur.proto.PartitionStats.ChannelStats',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='channel_id', full_name='proxima.centaur.proto.PartitionStats.ChannelStats.channel_id', index=0,
      number=1, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='segment_stats', full_name='proxima.centaur.proto.PartitionStats.ChannelStats.segment_stats', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='delete_doc_count', full_name='proxima.centaur.proto.PartitionStats.ChannelStats.delete_doc_count', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='cur_offset', full_name='proxima.centaur.proto.PartitionStats.ChannelStats.cur_offset', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='max_offset', full_name='proxima.centaur.proto.PartitionStats.ChannelStats.max_offset', index=4,
      number=5, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1757,
  serialized_end=1932,
)

_PARTITIONSTATS = _descriptor.Descriptor(
  name='PartitionStats',
  full_name='proxima.centaur.proto.PartitionStats',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection_name', full_name='proxima.centaur.proto.PartitionStats.collection_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='total_doc_count', full_name='proxima.centaur.proto.PartitionStats.total_doc_count', index=1,
      number=2, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='total_segment_count', full_name='proxima.centaur.proto.PartitionStats.total_segment_count', index=2,
      number=3, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='total_index_file_count', full_name='proxima.centaur.proto.PartitionStats.total_index_file_count', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='total_index_file_size', full_name='proxima.centaur.proto.PartitionStats.total_index_file_size', index=4,
      number=5, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='channel_stats', full_name='proxima.centaur.proto.PartitionStats.channel_stats', index=5,
      number=6, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='total_delete_doc_count', full_name='proxima.centaur.proto.PartitionStats.total_delete_doc_count', index=6,
      number=7, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_PARTITIONSTATS_SEGMENTSTATS, _PARTITIONSTATS_CHANNELSTATS, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1053,
  serialized_end=1932,
)


_COLLECTIONSTATS_PARTITIONSENTRY = _descriptor.Descriptor(
  name='PartitionsEntry',
  full_name='proxima.centaur.proto.CollectionStats.PartitionsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='proxima.centaur.proto.CollectionStats.PartitionsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='proxima.centaur.proto.CollectionStats.PartitionsEntry.value', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=2058,
  serialized_end=2146,
)

_COLLECTIONSTATS = _descriptor.Descriptor(
  name='CollectionStats',
  full_name='proxima.centaur.proto.CollectionStats',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='partitions', full_name='proxima.centaur.proto.CollectionStats.partitions', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='index_completeness', full_name='proxima.centaur.proto.CollectionStats.index_completeness', index=1,
      number=2, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_COLLECTIONSTATS_PARTITIONSENTRY, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=1935,
  serialized_end=2146,
)


_DOCLIST = _descriptor.Descriptor(
  name='DocList',
  full_name='proxima.centaur.proto.DocList',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='docs', full_name='proxima.centaur.proto.DocList.docs', index=0,
      number=1, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=2148,
  serialized_end=2199,
)


_COLLECTIONINFO_PARTITIONSENTRY = _descriptor.Descriptor(
  name='PartitionsEntry',
  full_name='proxima.centaur.proto.CollectionInfo.PartitionsEntry',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='key', full_name='proxima.centaur.proto.CollectionInfo.PartitionsEntry.key', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='value', full_name='proxima.centaur.proto.CollectionInfo.PartitionsEntry.value', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=_b('8\001'),
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=2435,
  serialized_end=2524,
)

_COLLECTIONINFO = _descriptor.Descriptor(
  name='CollectionInfo',
  full_name='proxima.centaur.proto.CollectionInfo',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='schema', full_name='proxima.centaur.proto.CollectionInfo.schema', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='collection_status', full_name='proxima.centaur.proto.CollectionInfo.collection_status', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='partitions', full_name='proxima.centaur.proto.CollectionInfo.partitions', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_COLLECTIONINFO_PARTITIONSENTRY, ],
  enum_types=[
    _COLLECTIONINFO_COLLECTIONSTATUS,
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=2202,
  serialized_end=2611,
)


_HTTPREQUEST = _descriptor.Descriptor(
  name='HttpRequest',
  full_name='proxima.centaur.proto.HttpRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=2613,
  serialized_end=2626,
)


_HTTPRESPONSE = _descriptor.Descriptor(
  name='HttpResponse',
  full_name='proxima.centaur.proto.HttpResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=2628,
  serialized_end=2642,
)


_CREATECOLLECTIONREQUEST = _descriptor.Descriptor(
  name='CreateCollectionRequest',
  full_name='proxima.centaur.proto.CreateCollectionRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='schema', full_name='proxima.centaur.proto.CreateCollectionRequest.schema', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=2644,
  serialized_end=2726,
)


_CREATECOLLECTIONRESPONSE = _descriptor.Descriptor(
  name='CreateCollectionResponse',
  full_name='proxima.centaur.proto.CreateCollectionResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.CreateCollectionResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=2728,
  serialized_end=2801,
)


_DROPCOLLECTIONREQUEST = _descriptor.Descriptor(
  name='DropCollectionRequest',
  full_name='proxima.centaur.proto.DropCollectionRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection_name', full_name='proxima.centaur.proto.DropCollectionRequest.collection_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=2803,
  serialized_end=2851,
)


_DROPCOLLECTIONRESPONSE = _descriptor.Descriptor(
  name='DropCollectionResponse',
  full_name='proxima.centaur.proto.DropCollectionResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.DropCollectionResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=2853,
  serialized_end=2924,
)


_DESCRIBECOLLECTIONREQUEST = _descriptor.Descriptor(
  name='DescribeCollectionRequest',
  full_name='proxima.centaur.proto.DescribeCollectionRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection_name', full_name='proxima.centaur.proto.DescribeCollectionRequest.collection_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=2926,
  serialized_end=2978,
)


_DESCRIBECOLLECTIONRESPONSE = _descriptor.Descriptor(
  name='DescribeCollectionResponse',
  full_name='proxima.centaur.proto.DescribeCollectionResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.DescribeCollectionResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='collection', full_name='proxima.centaur.proto.DescribeCollectionResponse.collection', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=2981,
  serialized_end=3115,
)


_LISTCOLLECTIONREQUEST = _descriptor.Descriptor(
  name='ListCollectionRequest',
  full_name='proxima.centaur.proto.ListCollectionRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=3117,
  serialized_end=3140,
)


_LISTCOLLECTIONRESPONSE = _descriptor.Descriptor(
  name='ListCollectionResponse',
  full_name='proxima.centaur.proto.ListCollectionResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.ListCollectionResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='collections', full_name='proxima.centaur.proto.ListCollectionResponse.collections', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=3143,
  serialized_end=3274,
)


_STATSCOLLECTIONREQUEST = _descriptor.Descriptor(
  name='StatsCollectionRequest',
  full_name='proxima.centaur.proto.StatsCollectionRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection_name', full_name='proxima.centaur.proto.StatsCollectionRequest.collection_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=3276,
  serialized_end=3325,
)


_STATSCOLLECTIONRESPONSE = _descriptor.Descriptor(
  name='StatsCollectionResponse',
  full_name='proxima.centaur.proto.StatsCollectionResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.StatsCollectionResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='collection_stats', full_name='proxima.centaur.proto.StatsCollectionResponse.collection_stats', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=3328,
  serialized_end=3466,
)


_INSERTDOCREQUEST = _descriptor.Descriptor(
  name='InsertDocRequest',
  full_name='proxima.centaur.proto.InsertDocRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection_name', full_name='proxima.centaur.proto.InsertDocRequest.collection_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='doc_list', full_name='proxima.centaur.proto.InsertDocRequest.doc_list', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='request_id', full_name='proxima.centaur.proto.InsertDocRequest.request_id', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='partition', full_name='proxima.centaur.proto.InsertDocRequest.partition', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=3469,
  serialized_end=3601,
)


_INSERTDOCRESPONSE = _descriptor.Descriptor(
  name='InsertDocResponse',
  full_name='proxima.centaur.proto.InsertDocResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.InsertDocResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='doc_results', full_name='proxima.centaur.proto.InsertDocResponse.doc_results', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=3603,
  serialized_end=3724,
)


_UPDATEDOCREQUEST = _descriptor.Descriptor(
  name='UpdateDocRequest',
  full_name='proxima.centaur.proto.UpdateDocRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection_name', full_name='proxima.centaur.proto.UpdateDocRequest.collection_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='doc_list', full_name='proxima.centaur.proto.UpdateDocRequest.doc_list', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='request_id', full_name='proxima.centaur.proto.UpdateDocRequest.request_id', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='partition', full_name='proxima.centaur.proto.UpdateDocRequest.partition', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=3727,
  serialized_end=3859,
)


_UPDATEDOCRESPONSE = _descriptor.Descriptor(
  name='UpdateDocResponse',
  full_name='proxima.centaur.proto.UpdateDocResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.UpdateDocResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='doc_results', full_name='proxima.centaur.proto.UpdateDocResponse.doc_results', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=3861,
  serialized_end=3982,
)


_DELETEDOCREQUEST = _descriptor.Descriptor(
  name='DeleteDocRequest',
  full_name='proxima.centaur.proto.DeleteDocRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection_name', full_name='proxima.centaur.proto.DeleteDocRequest.collection_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pks', full_name='proxima.centaur.proto.DeleteDocRequest.pks', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='request_id', full_name='proxima.centaur.proto.DeleteDocRequest.request_id', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='partition', full_name='proxima.centaur.proto.DeleteDocRequest.partition', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=3984,
  serialized_end=4079,
)


_DELETEDOCRESPONSE = _descriptor.Descriptor(
  name='DeleteDocResponse',
  full_name='proxima.centaur.proto.DeleteDocResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.DeleteDocResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='doc_results', full_name='proxima.centaur.proto.DeleteDocResponse.doc_results', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=4081,
  serialized_end=4202,
)


_UPSERTDOCREQUEST = _descriptor.Descriptor(
  name='UpsertDocRequest',
  full_name='proxima.centaur.proto.UpsertDocRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection_name', full_name='proxima.centaur.proto.UpsertDocRequest.collection_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='doc_list', full_name='proxima.centaur.proto.UpsertDocRequest.doc_list', index=1,
      number=2, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='request_id', full_name='proxima.centaur.proto.UpsertDocRequest.request_id', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='partition', full_name='proxima.centaur.proto.UpsertDocRequest.partition', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=4205,
  serialized_end=4337,
)


_UPSERTDOCRESPONSE = _descriptor.Descriptor(
  name='UpsertDocResponse',
  full_name='proxima.centaur.proto.UpsertDocResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.UpsertDocResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='doc_results', full_name='proxima.centaur.proto.UpsertDocResponse.doc_results', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=4339,
  serialized_end=4460,
)


_QUERYREQUEST_VECTORFEATURE = _descriptor.Descriptor(
  name='VectorFeature',
  full_name='proxima.centaur.proto.QueryRequest.VectorFeature',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='field_name', full_name='proxima.centaur.proto.QueryRequest.VectorFeature.field_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='features', full_name='proxima.centaur.proto.QueryRequest.VectorFeature.features', index=1,
      number=2, type=12, cpp_type=9, label=1,
      has_default_value=False, default_value=_b(""),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='matrix', full_name='proxima.centaur.proto.QueryRequest.VectorFeature.matrix', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='batch_count', full_name='proxima.centaur.proto.QueryRequest.VectorFeature.batch_count', index=3,
      number=4, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='dimension', full_name='proxima.centaur.proto.QueryRequest.VectorFeature.dimension', index=4,
      number=5, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='data_type', full_name='proxima.centaur.proto.QueryRequest.VectorFeature.data_type', index=5,
      number=6, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='radius', full_name='proxima.centaur.proto.QueryRequest.VectorFeature.radius', index=6,
      number=7, type=2, cpp_type=6, label=1,
      has_default_value=False, default_value=float(0),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='is_linear', full_name='proxima.centaur.proto.QueryRequest.VectorFeature.is_linear', index=7,
      number=8, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='extra_params', full_name='proxima.centaur.proto.QueryRequest.VectorFeature.extra_params', index=8,
      number=9, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
    _descriptor.OneofDescriptor(
      name='features_value', full_name='proxima.centaur.proto.QueryRequest.VectorFeature.features_value',
      index=0, containing_type=None, fields=[]),
  ],
  serialized_start=4695,
  serialized_end=4972,
)

_QUERYREQUEST = _descriptor.Descriptor(
  name='QueryRequest',
  full_name='proxima.centaur.proto.QueryRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection_name', full_name='proxima.centaur.proto.QueryRequest.collection_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='topk', full_name='proxima.centaur.proto.QueryRequest.topk', index=1,
      number=2, type=13, cpp_type=3, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='debug_mode', full_name='proxima.centaur.proto.QueryRequest.debug_mode', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='vector_feature', full_name='proxima.centaur.proto.QueryRequest.vector_feature', index=3,
      number=4, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='filter', full_name='proxima.centaur.proto.QueryRequest.filter', index=4,
      number=5, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='query_fields', full_name='proxima.centaur.proto.QueryRequest.query_fields', index=5,
      number=6, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='partition', full_name='proxima.centaur.proto.QueryRequest.partition', index=6,
      number=7, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='include_vector', full_name='proxima.centaur.proto.QueryRequest.include_vector', index=7,
      number=8, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[_QUERYREQUEST_VECTORFEATURE, ],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=4463,
  serialized_end=4972,
)


_QUERYRESPONSE = _descriptor.Descriptor(
  name='QueryResponse',
  full_name='proxima.centaur.proto.QueryResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.QueryResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='doc_results', full_name='proxima.centaur.proto.QueryResponse.doc_results', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='debug_info', full_name='proxima.centaur.proto.QueryResponse.debug_info', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='latency_us', full_name='proxima.centaur.proto.QueryResponse.latency_us', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=4975,
  serialized_end=5130,
)


_SQLQUERYREQUEST = _descriptor.Descriptor(
  name='SqlQueryRequest',
  full_name='proxima.centaur.proto.SqlQueryRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='sql', full_name='proxima.centaur.proto.SqlQueryRequest.sql', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='debug_mode', full_name='proxima.centaur.proto.SqlQueryRequest.debug_mode', index=1,
      number=2, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=5132,
  serialized_end=5182,
)


_SQLQUERYRESPONSE = _descriptor.Descriptor(
  name='SqlQueryResponse',
  full_name='proxima.centaur.proto.SqlQueryResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.SqlQueryResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='doc_results', full_name='proxima.centaur.proto.SqlQueryResponse.doc_results', index=1,
      number=2, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='debug_info', full_name='proxima.centaur.proto.SqlQueryResponse.debug_info', index=2,
      number=3, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='latency_us', full_name='proxima.centaur.proto.SqlQueryResponse.latency_us', index=3,
      number=4, type=4, cpp_type=4, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=5185,
  serialized_end=5343,
)


_GETDOCREQUEST = _descriptor.Descriptor(
  name='GetDocRequest',
  full_name='proxima.centaur.proto.GetDocRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection_name', full_name='proxima.centaur.proto.GetDocRequest.collection_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='pks', full_name='proxima.centaur.proto.GetDocRequest.pks', index=1,
      number=2, type=9, cpp_type=9, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='debug_mode', full_name='proxima.centaur.proto.GetDocRequest.debug_mode', index=2,
      number=3, type=8, cpp_type=7, label=1,
      has_default_value=False, default_value=False,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='partition', full_name='proxima.centaur.proto.GetDocRequest.partition', index=3,
      number=4, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=5345,
  serialized_end=5437,
)


_GETDOCRESPONSE = _descriptor.Descriptor(
  name='GetDocResponse',
  full_name='proxima.centaur.proto.GetDocResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.GetDocResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='debug_info', full_name='proxima.centaur.proto.GetDocResponse.debug_info', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='docs', full_name='proxima.centaur.proto.GetDocResponse.docs', index=2,
      number=3, type=11, cpp_type=10, label=3,
      has_default_value=False, default_value=[],
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=5439,
  serialized_end=5564,
)


_GETVERSIONREQUEST = _descriptor.Descriptor(
  name='GetVersionRequest',
  full_name='proxima.centaur.proto.GetVersionRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=5566,
  serialized_end=5585,
)


_GETVERSIONRESPONSE = _descriptor.Descriptor(
  name='GetVersionResponse',
  full_name='proxima.centaur.proto.GetVersionResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.GetVersionResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='version', full_name='proxima.centaur.proto.GetVersionResponse.version', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=5587,
  serialized_end=5671,
)


_CREATEPARTITIONREQUEST = _descriptor.Descriptor(
  name='CreatePartitionRequest',
  full_name='proxima.centaur.proto.CreatePartitionRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection_name', full_name='proxima.centaur.proto.CreatePartitionRequest.collection_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='partition_name', full_name='proxima.centaur.proto.CreatePartitionRequest.partition_name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=5673,
  serialized_end=5746,
)


_CREATEPARTITIONRESPONSE = _descriptor.Descriptor(
  name='CreatePartitionResponse',
  full_name='proxima.centaur.proto.CreatePartitionResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.CreatePartitionResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=5748,
  serialized_end=5820,
)


_DROPPARTITIONREQUEST = _descriptor.Descriptor(
  name='DropPartitionRequest',
  full_name='proxima.centaur.proto.DropPartitionRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection_name', full_name='proxima.centaur.proto.DropPartitionRequest.collection_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='partition_name', full_name='proxima.centaur.proto.DropPartitionRequest.partition_name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=5822,
  serialized_end=5893,
)


_DROPPARTITIONRESPONSE = _descriptor.Descriptor(
  name='DropPartitionResponse',
  full_name='proxima.centaur.proto.DropPartitionResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.DropPartitionResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=5895,
  serialized_end=5965,
)


_DESCRIBEPARTITIONREQUEST = _descriptor.Descriptor(
  name='DescribePartitionRequest',
  full_name='proxima.centaur.proto.DescribePartitionRequest',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='collection_name', full_name='proxima.centaur.proto.DescribePartitionRequest.collection_name', index=0,
      number=1, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='partition_name', full_name='proxima.centaur.proto.DescribePartitionRequest.partition_name', index=1,
      number=2, type=9, cpp_type=9, label=1,
      has_default_value=False, default_value=_b("").decode('utf-8'),
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=5967,
  serialized_end=6042,
)


_DESCRIBEPARTITIONRESPONSE = _descriptor.Descriptor(
  name='DescribePartitionResponse',
  full_name='proxima.centaur.proto.DescribePartitionResponse',
  filename=None,
  file=DESCRIPTOR,
  containing_type=None,
  fields=[
    _descriptor.FieldDescriptor(
      name='status', full_name='proxima.centaur.proto.DescribePartitionResponse.status', index=0,
      number=1, type=11, cpp_type=10, label=1,
      has_default_value=False, default_value=None,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
    _descriptor.FieldDescriptor(
      name='partition_status', full_name='proxima.centaur.proto.DescribePartitionResponse.partition_status', index=1,
      number=2, type=14, cpp_type=8, label=1,
      has_default_value=False, default_value=0,
      message_type=None, enum_type=None, containing_type=None,
      is_extension=False, extension_scope=None,
      serialized_options=None, file=DESCRIPTOR),
  ],
  extensions=[
  ],
  nested_types=[],
  enum_types=[
  ],
  serialized_options=None,
  is_extendable=False,
  syntax='proto3',
  extension_ranges=[],
  oneofs=[
  ],
  serialized_start=6045,
  serialized_end=6185,
)

_GENERICVALUE.oneofs_by_name['value_oneof'].fields.append(
  _GENERICVALUE.fields_by_name['bytes_value'])
_GENERICVALUE.fields_by_name['bytes_value'].containing_oneof = _GENERICVALUE.oneofs_by_name['value_oneof']
_GENERICVALUE.oneofs_by_name['value_oneof'].fields.append(
  _GENERICVALUE.fields_by_name['string_value'])
_GENERICVALUE.fields_by_name['string_value'].containing_oneof = _GENERICVALUE.oneofs_by_name['value_oneof']
_GENERICVALUE.oneofs_by_name['value_oneof'].fields.append(
  _GENERICVALUE.fields_by_name['bool_value'])
_GENERICVALUE.fields_by_name['bool_value'].containing_oneof = _GENERICVALUE.oneofs_by_name['value_oneof']
_GENERICVALUE.oneofs_by_name['value_oneof'].fields.append(
  _GENERICVALUE.fields_by_name['int32_value'])
_GENERICVALUE.fields_by_name['int32_value'].containing_oneof = _GENERICVALUE.oneofs_by_name['value_oneof']
_GENERICVALUE.oneofs_by_name['value_oneof'].fields.append(
  _GENERICVALUE.fields_by_name['int64_value'])
_GENERICVALUE.fields_by_name['int64_value'].containing_oneof = _GENERICVALUE.oneofs_by_name['value_oneof']
_GENERICVALUE.oneofs_by_name['value_oneof'].fields.append(
  _GENERICVALUE.fields_by_name['uint32_value'])
_GENERICVALUE.fields_by_name['uint32_value'].containing_oneof = _GENERICVALUE.oneofs_by_name['value_oneof']
_GENERICVALUE.oneofs_by_name['value_oneof'].fields.append(
  _GENERICVALUE.fields_by_name['uint64_value'])
_GENERICVALUE.fields_by_name['uint64_value'].containing_oneof = _GENERICVALUE.oneofs_by_name['value_oneof']
_GENERICVALUE.oneofs_by_name['value_oneof'].fields.append(
  _GENERICVALUE.fields_by_name['float_value'])
_GENERICVALUE.fields_by_name['float_value'].containing_oneof = _GENERICVALUE.oneofs_by_name['value_oneof']
_GENERICVALUE.oneofs_by_name['value_oneof'].fields.append(
  _GENERICVALUE.fields_by_name['double_value'])
_GENERICVALUE.fields_by_name['double_value'].containing_oneof = _GENERICVALUE.oneofs_by_name['value_oneof']
_FIELD.fields_by_name['value'].message_type = _GENERICVALUE
_DOC.fields_by_name['fields'].message_type = _FIELD
_COLLECTIONSCHEMA_FIELDSCHEMA.fields_by_name['index_type'].enum_type = _INDEXTYPE
_COLLECTIONSCHEMA_FIELDSCHEMA.fields_by_name['data_type'].enum_type = _DATATYPE
_COLLECTIONSCHEMA_FIELDSCHEMA.fields_by_name['extra_params'].message_type = _KEYVALUEPAIR
_COLLECTIONSCHEMA_FIELDSCHEMA.containing_type = _COLLECTIONSCHEMA
_COLLECTIONSCHEMA.fields_by_name['fields'].message_type = _COLLECTIONSCHEMA_FIELDSCHEMA
_DOCRESULT.fields_by_name['status'].message_type = _STATUS
_PARTITIONSTATS_SEGMENTSTATS.fields_by_name['state'].enum_type = _PARTITIONSTATS_SEGMENTSTATS_SEGMENTSTATE
_PARTITIONSTATS_SEGMENTSTATS.containing_type = _PARTITIONSTATS
_PARTITIONSTATS_SEGMENTSTATS_SEGMENTSTATE.containing_type = _PARTITIONSTATS_SEGMENTSTATS
_PARTITIONSTATS_CHANNELSTATS.fields_by_name['segment_stats'].message_type = _PARTITIONSTATS_SEGMENTSTATS
_PARTITIONSTATS_CHANNELSTATS.containing_type = _PARTITIONSTATS
_PARTITIONSTATS.fields_by_name['channel_stats'].message_type = _PARTITIONSTATS_CHANNELSTATS
_COLLECTIONSTATS_PARTITIONSENTRY.fields_by_name['value'].message_type = _PARTITIONSTATS
_COLLECTIONSTATS_PARTITIONSENTRY.containing_type = _COLLECTIONSTATS
_COLLECTIONSTATS.fields_by_name['partitions'].message_type = _COLLECTIONSTATS_PARTITIONSENTRY
_DOCLIST.fields_by_name['docs'].message_type = _DOC
_COLLECTIONINFO_PARTITIONSENTRY.fields_by_name['value'].enum_type = _PARTITIONSTATUS
_COLLECTIONINFO_PARTITIONSENTRY.containing_type = _COLLECTIONINFO
_COLLECTIONINFO.fields_by_name['schema'].message_type = _COLLECTIONSCHEMA
_COLLECTIONINFO.fields_by_name['collection_status'].enum_type = _COLLECTIONINFO_COLLECTIONSTATUS
_COLLECTIONINFO.fields_by_name['partitions'].message_type = _COLLECTIONINFO_PARTITIONSENTRY
_COLLECTIONINFO_COLLECTIONSTATUS.containing_type = _COLLECTIONINFO
_CREATECOLLECTIONREQUEST.fields_by_name['schema'].message_type = _COLLECTIONSCHEMA
_CREATECOLLECTIONRESPONSE.fields_by_name['status'].message_type = _STATUS
_DROPCOLLECTIONRESPONSE.fields_by_name['status'].message_type = _STATUS
_DESCRIBECOLLECTIONRESPONSE.fields_by_name['status'].message_type = _STATUS
_DESCRIBECOLLECTIONRESPONSE.fields_by_name['collection'].message_type = _COLLECTIONINFO
_LISTCOLLECTIONRESPONSE.fields_by_name['status'].message_type = _STATUS
_LISTCOLLECTIONRESPONSE.fields_by_name['collections'].message_type = _COLLECTIONINFO
_STATSCOLLECTIONRESPONSE.fields_by_name['status'].message_type = _STATUS
_STATSCOLLECTIONRESPONSE.fields_by_name['collection_stats'].message_type = _COLLECTIONSTATS
_INSERTDOCREQUEST.fields_by_name['doc_list'].message_type = _DOCLIST
_INSERTDOCRESPONSE.fields_by_name['status'].message_type = _STATUS
_INSERTDOCRESPONSE.fields_by_name['doc_results'].message_type = _DOCRESULT
_UPDATEDOCREQUEST.fields_by_name['doc_list'].message_type = _DOCLIST
_UPDATEDOCRESPONSE.fields_by_name['status'].message_type = _STATUS
_UPDATEDOCRESPONSE.fields_by_name['doc_results'].message_type = _DOCRESULT
_DELETEDOCRESPONSE.fields_by_name['status'].message_type = _STATUS
_DELETEDOCRESPONSE.fields_by_name['doc_results'].message_type = _DOCRESULT
_UPSERTDOCREQUEST.fields_by_name['doc_list'].message_type = _DOCLIST
_UPSERTDOCRESPONSE.fields_by_name['status'].message_type = _STATUS
_UPSERTDOCRESPONSE.fields_by_name['doc_results'].message_type = _DOCRESULT
_QUERYREQUEST_VECTORFEATURE.fields_by_name['data_type'].enum_type = _DATATYPE
_QUERYREQUEST_VECTORFEATURE.fields_by_name['extra_params'].message_type = _KEYVALUEPAIR
_QUERYREQUEST_VECTORFEATURE.containing_type = _QUERYREQUEST
_QUERYREQUEST_VECTORFEATURE.oneofs_by_name['features_value'].fields.append(
  _QUERYREQUEST_VECTORFEATURE.fields_by_name['features'])
_QUERYREQUEST_VECTORFEATURE.fields_by_name['features'].containing_oneof = _QUERYREQUEST_VECTORFEATURE.oneofs_by_name['features_value']
_QUERYREQUEST_VECTORFEATURE.oneofs_by_name['features_value'].fields.append(
  _QUERYREQUEST_VECTORFEATURE.fields_by_name['matrix'])
_QUERYREQUEST_VECTORFEATURE.fields_by_name['matrix'].containing_oneof = _QUERYREQUEST_VECTORFEATURE.oneofs_by_name['features_value']
_QUERYREQUEST.fields_by_name['vector_feature'].message_type = _QUERYREQUEST_VECTORFEATURE
_QUERYRESPONSE.fields_by_name['status'].message_type = _STATUS
_QUERYRESPONSE.fields_by_name['doc_results'].message_type = _DOCLIST
_SQLQUERYRESPONSE.fields_by_name['status'].message_type = _STATUS
_SQLQUERYRESPONSE.fields_by_name['doc_results'].message_type = _DOCLIST
_GETDOCRESPONSE.fields_by_name['status'].message_type = _STATUS
_GETDOCRESPONSE.fields_by_name['docs'].message_type = _DOC
_GETVERSIONRESPONSE.fields_by_name['status'].message_type = _STATUS
_CREATEPARTITIONRESPONSE.fields_by_name['status'].message_type = _STATUS
_DROPPARTITIONRESPONSE.fields_by_name['status'].message_type = _STATUS
_DESCRIBEPARTITIONRESPONSE.fields_by_name['status'].message_type = _STATUS
_DESCRIBEPARTITIONRESPONSE.fields_by_name['partition_status'].enum_type = _PARTITIONSTATUS
DESCRIPTOR.message_types_by_name['GenericValue'] = _GENERICVALUE
DESCRIPTOR.message_types_by_name['KeyValuePair'] = _KEYVALUEPAIR
DESCRIPTOR.message_types_by_name['Status'] = _STATUS
DESCRIPTOR.message_types_by_name['Field'] = _FIELD
DESCRIPTOR.message_types_by_name['Doc'] = _DOC
DESCRIPTOR.message_types_by_name['CollectionSchema'] = _COLLECTIONSCHEMA
DESCRIPTOR.message_types_by_name['DocResult'] = _DOCRESULT
DESCRIPTOR.message_types_by_name['PartitionStats'] = _PARTITIONSTATS
DESCRIPTOR.message_types_by_name['CollectionStats'] = _COLLECTIONSTATS
DESCRIPTOR.message_types_by_name['DocList'] = _DOCLIST
DESCRIPTOR.message_types_by_name['CollectionInfo'] = _COLLECTIONINFO
DESCRIPTOR.message_types_by_name['HttpRequest'] = _HTTPREQUEST
DESCRIPTOR.message_types_by_name['HttpResponse'] = _HTTPRESPONSE
DESCRIPTOR.message_types_by_name['CreateCollectionRequest'] = _CREATECOLLECTIONREQUEST
DESCRIPTOR.message_types_by_name['CreateCollectionResponse'] = _CREATECOLLECTIONRESPONSE
DESCRIPTOR.message_types_by_name['DropCollectionRequest'] = _DROPCOLLECTIONREQUEST
DESCRIPTOR.message_types_by_name['DropCollectionResponse'] = _DROPCOLLECTIONRESPONSE
DESCRIPTOR.message_types_by_name['DescribeCollectionRequest'] = _DESCRIBECOLLECTIONREQUEST
DESCRIPTOR.message_types_by_name['DescribeCollectionResponse'] = _DESCRIBECOLLECTIONRESPONSE
DESCRIPTOR.message_types_by_name['ListCollectionRequest'] = _LISTCOLLECTIONREQUEST
DESCRIPTOR.message_types_by_name['ListCollectionResponse'] = _LISTCOLLECTIONRESPONSE
DESCRIPTOR.message_types_by_name['StatsCollectionRequest'] = _STATSCOLLECTIONREQUEST
DESCRIPTOR.message_types_by_name['StatsCollectionResponse'] = _STATSCOLLECTIONRESPONSE
DESCRIPTOR.message_types_by_name['InsertDocRequest'] = _INSERTDOCREQUEST
DESCRIPTOR.message_types_by_name['InsertDocResponse'] = _INSERTDOCRESPONSE
DESCRIPTOR.message_types_by_name['UpdateDocRequest'] = _UPDATEDOCREQUEST
DESCRIPTOR.message_types_by_name['UpdateDocResponse'] = _UPDATEDOCRESPONSE
DESCRIPTOR.message_types_by_name['DeleteDocRequest'] = _DELETEDOCREQUEST
DESCRIPTOR.message_types_by_name['DeleteDocResponse'] = _DELETEDOCRESPONSE
DESCRIPTOR.message_types_by_name['UpsertDocRequest'] = _UPSERTDOCREQUEST
DESCRIPTOR.message_types_by_name['UpsertDocResponse'] = _UPSERTDOCRESPONSE
DESCRIPTOR.message_types_by_name['QueryRequest'] = _QUERYREQUEST
DESCRIPTOR.message_types_by_name['QueryResponse'] = _QUERYRESPONSE
DESCRIPTOR.message_types_by_name['SqlQueryRequest'] = _SQLQUERYREQUEST
DESCRIPTOR.message_types_by_name['SqlQueryResponse'] = _SQLQUERYRESPONSE
DESCRIPTOR.message_types_by_name['GetDocRequest'] = _GETDOCREQUEST
DESCRIPTOR.message_types_by_name['GetDocResponse'] = _GETDOCRESPONSE
DESCRIPTOR.message_types_by_name['GetVersionRequest'] = _GETVERSIONREQUEST
DESCRIPTOR.message_types_by_name['GetVersionResponse'] = _GETVERSIONRESPONSE
DESCRIPTOR.message_types_by_name['CreatePartitionRequest'] = _CREATEPARTITIONREQUEST
DESCRIPTOR.message_types_by_name['CreatePartitionResponse'] = _CREATEPARTITIONRESPONSE
DESCRIPTOR.message_types_by_name['DropPartitionRequest'] = _DROPPARTITIONREQUEST
DESCRIPTOR.message_types_by_name['DropPartitionResponse'] = _DROPPARTITIONRESPONSE
DESCRIPTOR.message_types_by_name['DescribePartitionRequest'] = _DESCRIBEPARTITIONREQUEST
DESCRIPTOR.message_types_by_name['DescribePartitionResponse'] = _DESCRIBEPARTITIONRESPONSE
DESCRIPTOR.enum_types_by_name['IndexType'] = _INDEXTYPE
DESCRIPTOR.enum_types_by_name['DataType'] = _DATATYPE
DESCRIPTOR.enum_types_by_name['PartitionStatus'] = _PARTITIONSTATUS
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

GenericValue = _reflection.GeneratedProtocolMessageType('GenericValue', (_message.Message,), {
  'DESCRIPTOR' : _GENERICVALUE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.GenericValue)
  })
_sym_db.RegisterMessage(GenericValue)

KeyValuePair = _reflection.GeneratedProtocolMessageType('KeyValuePair', (_message.Message,), {
  'DESCRIPTOR' : _KEYVALUEPAIR,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.KeyValuePair)
  })
_sym_db.RegisterMessage(KeyValuePair)

Status = _reflection.GeneratedProtocolMessageType('Status', (_message.Message,), {
  'DESCRIPTOR' : _STATUS,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.Status)
  })
_sym_db.RegisterMessage(Status)

Field = _reflection.GeneratedProtocolMessageType('Field', (_message.Message,), {
  'DESCRIPTOR' : _FIELD,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.Field)
  })
_sym_db.RegisterMessage(Field)

Doc = _reflection.GeneratedProtocolMessageType('Doc', (_message.Message,), {
  'DESCRIPTOR' : _DOC,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.Doc)
  })
_sym_db.RegisterMessage(Doc)

CollectionSchema = _reflection.GeneratedProtocolMessageType('CollectionSchema', (_message.Message,), {

  'FieldSchema' : _reflection.GeneratedProtocolMessageType('FieldSchema', (_message.Message,), {
    'DESCRIPTOR' : _COLLECTIONSCHEMA_FIELDSCHEMA,
    '__module__' : 'centaur_pb2'
    # @@protoc_insertion_point(class_scope:proxima.centaur.proto.CollectionSchema.FieldSchema)
    })
  ,
  'DESCRIPTOR' : _COLLECTIONSCHEMA,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.CollectionSchema)
  })
_sym_db.RegisterMessage(CollectionSchema)
_sym_db.RegisterMessage(CollectionSchema.FieldSchema)

DocResult = _reflection.GeneratedProtocolMessageType('DocResult', (_message.Message,), {
  'DESCRIPTOR' : _DOCRESULT,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.DocResult)
  })
_sym_db.RegisterMessage(DocResult)

PartitionStats = _reflection.GeneratedProtocolMessageType('PartitionStats', (_message.Message,), {

  'SegmentStats' : _reflection.GeneratedProtocolMessageType('SegmentStats', (_message.Message,), {
    'DESCRIPTOR' : _PARTITIONSTATS_SEGMENTSTATS,
    '__module__' : 'centaur_pb2'
    # @@protoc_insertion_point(class_scope:proxima.centaur.proto.PartitionStats.SegmentStats)
    })
  ,

  'ChannelStats' : _reflection.GeneratedProtocolMessageType('ChannelStats', (_message.Message,), {
    'DESCRIPTOR' : _PARTITIONSTATS_CHANNELSTATS,
    '__module__' : 'centaur_pb2'
    # @@protoc_insertion_point(class_scope:proxima.centaur.proto.PartitionStats.ChannelStats)
    })
  ,
  'DESCRIPTOR' : _PARTITIONSTATS,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.PartitionStats)
  })
_sym_db.RegisterMessage(PartitionStats)
_sym_db.RegisterMessage(PartitionStats.SegmentStats)
_sym_db.RegisterMessage(PartitionStats.ChannelStats)

CollectionStats = _reflection.GeneratedProtocolMessageType('CollectionStats', (_message.Message,), {

  'PartitionsEntry' : _reflection.GeneratedProtocolMessageType('PartitionsEntry', (_message.Message,), {
    'DESCRIPTOR' : _COLLECTIONSTATS_PARTITIONSENTRY,
    '__module__' : 'centaur_pb2'
    # @@protoc_insertion_point(class_scope:proxima.centaur.proto.CollectionStats.PartitionsEntry)
    })
  ,
  'DESCRIPTOR' : _COLLECTIONSTATS,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.CollectionStats)
  })
_sym_db.RegisterMessage(CollectionStats)
_sym_db.RegisterMessage(CollectionStats.PartitionsEntry)

DocList = _reflection.GeneratedProtocolMessageType('DocList', (_message.Message,), {
  'DESCRIPTOR' : _DOCLIST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.DocList)
  })
_sym_db.RegisterMessage(DocList)

CollectionInfo = _reflection.GeneratedProtocolMessageType('CollectionInfo', (_message.Message,), {

  'PartitionsEntry' : _reflection.GeneratedProtocolMessageType('PartitionsEntry', (_message.Message,), {
    'DESCRIPTOR' : _COLLECTIONINFO_PARTITIONSENTRY,
    '__module__' : 'centaur_pb2'
    # @@protoc_insertion_point(class_scope:proxima.centaur.proto.CollectionInfo.PartitionsEntry)
    })
  ,
  'DESCRIPTOR' : _COLLECTIONINFO,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.CollectionInfo)
  })
_sym_db.RegisterMessage(CollectionInfo)
_sym_db.RegisterMessage(CollectionInfo.PartitionsEntry)

HttpRequest = _reflection.GeneratedProtocolMessageType('HttpRequest', (_message.Message,), {
  'DESCRIPTOR' : _HTTPREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.HttpRequest)
  })
_sym_db.RegisterMessage(HttpRequest)

HttpResponse = _reflection.GeneratedProtocolMessageType('HttpResponse', (_message.Message,), {
  'DESCRIPTOR' : _HTTPRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.HttpResponse)
  })
_sym_db.RegisterMessage(HttpResponse)

CreateCollectionRequest = _reflection.GeneratedProtocolMessageType('CreateCollectionRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATECOLLECTIONREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.CreateCollectionRequest)
  })
_sym_db.RegisterMessage(CreateCollectionRequest)

CreateCollectionResponse = _reflection.GeneratedProtocolMessageType('CreateCollectionResponse', (_message.Message,), {
  'DESCRIPTOR' : _CREATECOLLECTIONRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.CreateCollectionResponse)
  })
_sym_db.RegisterMessage(CreateCollectionResponse)

DropCollectionRequest = _reflection.GeneratedProtocolMessageType('DropCollectionRequest', (_message.Message,), {
  'DESCRIPTOR' : _DROPCOLLECTIONREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.DropCollectionRequest)
  })
_sym_db.RegisterMessage(DropCollectionRequest)

DropCollectionResponse = _reflection.GeneratedProtocolMessageType('DropCollectionResponse', (_message.Message,), {
  'DESCRIPTOR' : _DROPCOLLECTIONRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.DropCollectionResponse)
  })
_sym_db.RegisterMessage(DropCollectionResponse)

DescribeCollectionRequest = _reflection.GeneratedProtocolMessageType('DescribeCollectionRequest', (_message.Message,), {
  'DESCRIPTOR' : _DESCRIBECOLLECTIONREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.DescribeCollectionRequest)
  })
_sym_db.RegisterMessage(DescribeCollectionRequest)

DescribeCollectionResponse = _reflection.GeneratedProtocolMessageType('DescribeCollectionResponse', (_message.Message,), {
  'DESCRIPTOR' : _DESCRIBECOLLECTIONRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.DescribeCollectionResponse)
  })
_sym_db.RegisterMessage(DescribeCollectionResponse)

ListCollectionRequest = _reflection.GeneratedProtocolMessageType('ListCollectionRequest', (_message.Message,), {
  'DESCRIPTOR' : _LISTCOLLECTIONREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.ListCollectionRequest)
  })
_sym_db.RegisterMessage(ListCollectionRequest)

ListCollectionResponse = _reflection.GeneratedProtocolMessageType('ListCollectionResponse', (_message.Message,), {
  'DESCRIPTOR' : _LISTCOLLECTIONRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.ListCollectionResponse)
  })
_sym_db.RegisterMessage(ListCollectionResponse)

StatsCollectionRequest = _reflection.GeneratedProtocolMessageType('StatsCollectionRequest', (_message.Message,), {
  'DESCRIPTOR' : _STATSCOLLECTIONREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.StatsCollectionRequest)
  })
_sym_db.RegisterMessage(StatsCollectionRequest)

StatsCollectionResponse = _reflection.GeneratedProtocolMessageType('StatsCollectionResponse', (_message.Message,), {
  'DESCRIPTOR' : _STATSCOLLECTIONRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.StatsCollectionResponse)
  })
_sym_db.RegisterMessage(StatsCollectionResponse)

InsertDocRequest = _reflection.GeneratedProtocolMessageType('InsertDocRequest', (_message.Message,), {
  'DESCRIPTOR' : _INSERTDOCREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.InsertDocRequest)
  })
_sym_db.RegisterMessage(InsertDocRequest)

InsertDocResponse = _reflection.GeneratedProtocolMessageType('InsertDocResponse', (_message.Message,), {
  'DESCRIPTOR' : _INSERTDOCRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.InsertDocResponse)
  })
_sym_db.RegisterMessage(InsertDocResponse)

UpdateDocRequest = _reflection.GeneratedProtocolMessageType('UpdateDocRequest', (_message.Message,), {
  'DESCRIPTOR' : _UPDATEDOCREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.UpdateDocRequest)
  })
_sym_db.RegisterMessage(UpdateDocRequest)

UpdateDocResponse = _reflection.GeneratedProtocolMessageType('UpdateDocResponse', (_message.Message,), {
  'DESCRIPTOR' : _UPDATEDOCRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.UpdateDocResponse)
  })
_sym_db.RegisterMessage(UpdateDocResponse)

DeleteDocRequest = _reflection.GeneratedProtocolMessageType('DeleteDocRequest', (_message.Message,), {
  'DESCRIPTOR' : _DELETEDOCREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.DeleteDocRequest)
  })
_sym_db.RegisterMessage(DeleteDocRequest)

DeleteDocResponse = _reflection.GeneratedProtocolMessageType('DeleteDocResponse', (_message.Message,), {
  'DESCRIPTOR' : _DELETEDOCRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.DeleteDocResponse)
  })
_sym_db.RegisterMessage(DeleteDocResponse)

UpsertDocRequest = _reflection.GeneratedProtocolMessageType('UpsertDocRequest', (_message.Message,), {
  'DESCRIPTOR' : _UPSERTDOCREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.UpsertDocRequest)
  })
_sym_db.RegisterMessage(UpsertDocRequest)

UpsertDocResponse = _reflection.GeneratedProtocolMessageType('UpsertDocResponse', (_message.Message,), {
  'DESCRIPTOR' : _UPSERTDOCRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.UpsertDocResponse)
  })
_sym_db.RegisterMessage(UpsertDocResponse)

QueryRequest = _reflection.GeneratedProtocolMessageType('QueryRequest', (_message.Message,), {

  'VectorFeature' : _reflection.GeneratedProtocolMessageType('VectorFeature', (_message.Message,), {
    'DESCRIPTOR' : _QUERYREQUEST_VECTORFEATURE,
    '__module__' : 'centaur_pb2'
    # @@protoc_insertion_point(class_scope:proxima.centaur.proto.QueryRequest.VectorFeature)
    })
  ,
  'DESCRIPTOR' : _QUERYREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.QueryRequest)
  })
_sym_db.RegisterMessage(QueryRequest)
_sym_db.RegisterMessage(QueryRequest.VectorFeature)

QueryResponse = _reflection.GeneratedProtocolMessageType('QueryResponse', (_message.Message,), {
  'DESCRIPTOR' : _QUERYRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.QueryResponse)
  })
_sym_db.RegisterMessage(QueryResponse)

SqlQueryRequest = _reflection.GeneratedProtocolMessageType('SqlQueryRequest', (_message.Message,), {
  'DESCRIPTOR' : _SQLQUERYREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.SqlQueryRequest)
  })
_sym_db.RegisterMessage(SqlQueryRequest)

SqlQueryResponse = _reflection.GeneratedProtocolMessageType('SqlQueryResponse', (_message.Message,), {
  'DESCRIPTOR' : _SQLQUERYRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.SqlQueryResponse)
  })
_sym_db.RegisterMessage(SqlQueryResponse)

GetDocRequest = _reflection.GeneratedProtocolMessageType('GetDocRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETDOCREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.GetDocRequest)
  })
_sym_db.RegisterMessage(GetDocRequest)

GetDocResponse = _reflection.GeneratedProtocolMessageType('GetDocResponse', (_message.Message,), {
  'DESCRIPTOR' : _GETDOCRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.GetDocResponse)
  })
_sym_db.RegisterMessage(GetDocResponse)

GetVersionRequest = _reflection.GeneratedProtocolMessageType('GetVersionRequest', (_message.Message,), {
  'DESCRIPTOR' : _GETVERSIONREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.GetVersionRequest)
  })
_sym_db.RegisterMessage(GetVersionRequest)

GetVersionResponse = _reflection.GeneratedProtocolMessageType('GetVersionResponse', (_message.Message,), {
  'DESCRIPTOR' : _GETVERSIONRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.GetVersionResponse)
  })
_sym_db.RegisterMessage(GetVersionResponse)

CreatePartitionRequest = _reflection.GeneratedProtocolMessageType('CreatePartitionRequest', (_message.Message,), {
  'DESCRIPTOR' : _CREATEPARTITIONREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.CreatePartitionRequest)
  })
_sym_db.RegisterMessage(CreatePartitionRequest)

CreatePartitionResponse = _reflection.GeneratedProtocolMessageType('CreatePartitionResponse', (_message.Message,), {
  'DESCRIPTOR' : _CREATEPARTITIONRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.CreatePartitionResponse)
  })
_sym_db.RegisterMessage(CreatePartitionResponse)

DropPartitionRequest = _reflection.GeneratedProtocolMessageType('DropPartitionRequest', (_message.Message,), {
  'DESCRIPTOR' : _DROPPARTITIONREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.DropPartitionRequest)
  })
_sym_db.RegisterMessage(DropPartitionRequest)

DropPartitionResponse = _reflection.GeneratedProtocolMessageType('DropPartitionResponse', (_message.Message,), {
  'DESCRIPTOR' : _DROPPARTITIONRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.DropPartitionResponse)
  })
_sym_db.RegisterMessage(DropPartitionResponse)

DescribePartitionRequest = _reflection.GeneratedProtocolMessageType('DescribePartitionRequest', (_message.Message,), {
  'DESCRIPTOR' : _DESCRIBEPARTITIONREQUEST,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.DescribePartitionRequest)
  })
_sym_db.RegisterMessage(DescribePartitionRequest)

DescribePartitionResponse = _reflection.GeneratedProtocolMessageType('DescribePartitionResponse', (_message.Message,), {
  'DESCRIPTOR' : _DESCRIBEPARTITIONRESPONSE,
  '__module__' : 'centaur_pb2'
  # @@protoc_insertion_point(class_scope:proxima.centaur.proto.DescribePartitionResponse)
  })
_sym_db.RegisterMessage(DescribePartitionResponse)


DESCRIPTOR._options = None
_COLLECTIONSTATS_PARTITIONSENTRY._options = None
_COLLECTIONINFO_PARTITIONSENTRY._options = None

_CENTAURSERVICE = _descriptor.ServiceDescriptor(
  name='CentaurService',
  full_name='proxima.centaur.proto.CentaurService',
  file=DESCRIPTOR,
  index=0,
  serialized_options=None,
  serialized_start=6663,
  serialized_end=8370,
  methods=[
  _descriptor.MethodDescriptor(
    name='create_collection',
    full_name='proxima.centaur.proto.CentaurService.create_collection',
    index=0,
    containing_service=None,
    input_type=_CREATECOLLECTIONREQUEST,
    output_type=_CREATECOLLECTIONRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='drop_collection',
    full_name='proxima.centaur.proto.CentaurService.drop_collection',
    index=1,
    containing_service=None,
    input_type=_DROPCOLLECTIONREQUEST,
    output_type=_DROPCOLLECTIONRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='describe_collection',
    full_name='proxima.centaur.proto.CentaurService.describe_collection',
    index=2,
    containing_service=None,
    input_type=_DESCRIBECOLLECTIONREQUEST,
    output_type=_DESCRIBECOLLECTIONRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='list_collections',
    full_name='proxima.centaur.proto.CentaurService.list_collections',
    index=3,
    containing_service=None,
    input_type=_LISTCOLLECTIONREQUEST,
    output_type=_LISTCOLLECTIONRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='stats_collection',
    full_name='proxima.centaur.proto.CentaurService.stats_collection',
    index=4,
    containing_service=None,
    input_type=_STATSCOLLECTIONREQUEST,
    output_type=_STATSCOLLECTIONRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='insert_doc',
    full_name='proxima.centaur.proto.CentaurService.insert_doc',
    index=5,
    containing_service=None,
    input_type=_INSERTDOCREQUEST,
    output_type=_INSERTDOCRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='update_doc',
    full_name='proxima.centaur.proto.CentaurService.update_doc',
    index=6,
    containing_service=None,
    input_type=_UPDATEDOCREQUEST,
    output_type=_UPDATEDOCRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='delete_doc',
    full_name='proxima.centaur.proto.CentaurService.delete_doc',
    index=7,
    containing_service=None,
    input_type=_DELETEDOCREQUEST,
    output_type=_DELETEDOCRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='upsert_doc',
    full_name='proxima.centaur.proto.CentaurService.upsert_doc',
    index=8,
    containing_service=None,
    input_type=_UPSERTDOCREQUEST,
    output_type=_UPSERTDOCRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='query',
    full_name='proxima.centaur.proto.CentaurService.query',
    index=9,
    containing_service=None,
    input_type=_QUERYREQUEST,
    output_type=_QUERYRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='query_by_sql',
    full_name='proxima.centaur.proto.CentaurService.query_by_sql',
    index=10,
    containing_service=None,
    input_type=_SQLQUERYREQUEST,
    output_type=_SQLQUERYRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='get_doc_by_key',
    full_name='proxima.centaur.proto.CentaurService.get_doc_by_key',
    index=11,
    containing_service=None,
    input_type=_GETDOCREQUEST,
    output_type=_GETDOCRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='create_partition',
    full_name='proxima.centaur.proto.CentaurService.create_partition',
    index=12,
    containing_service=None,
    input_type=_CREATEPARTITIONREQUEST,
    output_type=_CREATEPARTITIONRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='drop_partition',
    full_name='proxima.centaur.proto.CentaurService.drop_partition',
    index=13,
    containing_service=None,
    input_type=_DROPPARTITIONREQUEST,
    output_type=_DROPPARTITIONRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='describe_partition',
    full_name='proxima.centaur.proto.CentaurService.describe_partition',
    index=14,
    containing_service=None,
    input_type=_DESCRIBEPARTITIONREQUEST,
    output_type=_DESCRIBEPARTITIONRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='get_version',
    full_name='proxima.centaur.proto.CentaurService.get_version',
    index=15,
    containing_service=None,
    input_type=_GETVERSIONREQUEST,
    output_type=_GETVERSIONRESPONSE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_CENTAURSERVICE)

DESCRIPTOR.services_by_name['CentaurService'] = _CENTAURSERVICE


_HTTPCENTAURSERVICE = _descriptor.ServiceDescriptor(
  name='HttpCentaurService',
  full_name='proxima.centaur.proto.HttpCentaurService',
  file=DESCRIPTOR,
  index=1,
  serialized_options=None,
  serialized_start=8373,
  serialized_end=9099,
  methods=[
  _descriptor.MethodDescriptor(
    name='collection',
    full_name='proxima.centaur.proto.HttpCentaurService.collection',
    index=0,
    containing_service=None,
    input_type=_HTTPREQUEST,
    output_type=_HTTPRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='list_collections',
    full_name='proxima.centaur.proto.HttpCentaurService.list_collections',
    index=1,
    containing_service=None,
    input_type=_HTTPREQUEST,
    output_type=_HTTPRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='stats_collection',
    full_name='proxima.centaur.proto.HttpCentaurService.stats_collection',
    index=2,
    containing_service=None,
    input_type=_HTTPREQUEST,
    output_type=_HTTPRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='handle_doc',
    full_name='proxima.centaur.proto.HttpCentaurService.handle_doc',
    index=3,
    containing_service=None,
    input_type=_HTTPREQUEST,
    output_type=_HTTPRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='upsert_doc',
    full_name='proxima.centaur.proto.HttpCentaurService.upsert_doc',
    index=4,
    containing_service=None,
    input_type=_HTTPREQUEST,
    output_type=_HTTPRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='query',
    full_name='proxima.centaur.proto.HttpCentaurService.query',
    index=5,
    containing_service=None,
    input_type=_HTTPREQUEST,
    output_type=_HTTPRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='query_by_sql',
    full_name='proxima.centaur.proto.HttpCentaurService.query_by_sql',
    index=6,
    containing_service=None,
    input_type=_HTTPREQUEST,
    output_type=_HTTPRESPONSE,
    serialized_options=None,
  ),
  _descriptor.MethodDescriptor(
    name='get_version',
    full_name='proxima.centaur.proto.HttpCentaurService.get_version',
    index=7,
    containing_service=None,
    input_type=_HTTPREQUEST,
    output_type=_HTTPRESPONSE,
    serialized_options=None,
  ),
])
_sym_db.RegisterServiceDescriptor(_HTTPCENTAURSERVICE)

DESCRIPTOR.services_by_name['HttpCentaurService'] = _HTTPCENTAURSERVICE

# @@protoc_insertion_point(module_scope)
