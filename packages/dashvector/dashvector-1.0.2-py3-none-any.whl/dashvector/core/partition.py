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

import json

from enum import Enum, IntEnum
from typing import List, Dict, Optional
from dataclasses import dataclass

from dashvector.common.status import SegmentState, PartitionStatus

__all__ = ["PartitionStatsBuilder", "PartitionSegment", "PartitionChannel", "PartitionStats", "PartitionMetaBuilder", "PartitionMeta"]


@dataclass(frozen=True)
class PartitionSegment(object):
    segment_id: Optional[int] = None
    state: Optional[SegmentState] = None
    doc_count: Optional[int] = None
    index_file_count: Optional[int] = None
    index_file_size: Optional[int] = None
    min_doc_id: Optional[int] = None
    max_doc_id: Optional[int] = None
    min_timestamp: Optional[int] = None
    max_timestamp: Optional[int] = None
    min_offset: Optional[int] = None
    max_offset: Optional[int] = None
    segment_path: Optional[str] = None

    def __dict__(self):
        meta_dict = {}
        if self.segment_id is not None:
            meta_dict['segment_id'] = self.segment_id
        if self.state is not None:
            meta_dict['state'] = self.state
        if self.doc_count is not None:
            meta_dict['doc_count'] = self.doc_count
        if self.index_file_count is not None:
            meta_dict['index_file_count'] = self.index_file_count
        if self.index_file_size is not None:
            meta_dict['index_file_size'] = self.index_file_size
        if self.min_doc_id is not None:
            meta_dict['min_doc_id'] = self.min_doc_id
        if self.max_doc_id is not None:
            meta_dict['max_doc_id'] = self.max_doc_id
        if self.min_timestamp is not None:
            meta_dict['min_timestamp'] = self.min_timestamp
        if self.max_timestamp is not None:
            meta_dict['max_timestamp'] = self.max_timestamp
        if self.min_offset is not None:
            meta_dict['min_offset'] = self.min_offset
        if self.max_offset is not None:
            meta_dict['max_offset'] = self.max_offset
        if self.segment_path is not None:
            meta_dict['segment_path'] = self.segment_path
        return meta_dict

    def __str__(self):
        return json.dumps(self.__dict__())

    def __repr__(self):
        return self.__str__()

@dataclass(frozen=True)
class PartitionChannel(object):
    channel_id: Optional[int] = None
    segment_stats: Optional[List[PartitionSegment]] = None

    def __dict__(self):
        meta_dict = {}
        if self.channel_id is not None:
            meta_dict['channel_id'] = self.channel_id
        if self.segment_stats is not None:
            meta_dict['segment_stats'] = []
            for segment_stat in self.segment_stats:
                meta_dict['segment_stats'].append(segment_stat.__dict__())
        return meta_dict

    def __str__(self):
        return json.dumps(self.__dict__())

    def __repr__(self):
        return self.__str__()

@dataclass(frozen=True)
class PartitionStats(object):

    """
    A Stats Instance of Partition.

    Args:
        name (str): partition name
        total_doc_count (int): stats info
        total_segment_count (int): stats info
        total_index_file_count (int): stats info
        total_index_file_size (int): stats info
        total_delete_doc_count (int): stats info
    """

    name: str
    total_doc_count: int = 0
    total_segment_count: int = 0
    total_index_file_count: int = 0
    total_index_file_size: int = 0
    total_delete_doc_count: int = 0
    channel_stats: Optional[List[PartitionChannel]] = None

    def __dict__(self):
        meta_dict = {}
        if self.name is not None:
            meta_dict['name'] = self.name
        meta_dict['total_doc_count'] = self.total_doc_count
        meta_dict['total_segment_count'] = self.total_segment_count
        meta_dict['total_index_file_count'] = self.total_index_file_count
        meta_dict['total_index_file_size'] = self.total_index_file_size
        meta_dict['total_delete_doc_count'] = self.total_delete_doc_count
        # if self.channel_stats is not None:
        #     meta_dict['channel_stats'] = []
        #     for channel_stat in self.channel_stats:
        #         meta_dict['channel_stats'].append(channel_stat.__dict__())
        return meta_dict

    def __str__(self):
        return json.dumps(self.__dict__())

    def __repr__(self):
        return self.__str__()


class PartitionStatsBuilder(object):
    @staticmethod
    def from_meta(partition_name: str,
                  partition_meta: Dict):
        """
        partition_name:str
        """
        _partition_name = partition_name

        """
        total_doc_count: int
        """
        _total_doc_count = 0
        if 'total_doc_count' in partition_meta:
            _total_doc_count = int(partition_meta['total_doc_count'])

        """
        total_segment_count: int
        """
        _total_segment_count = 0
        if 'total_segment_count' in partition_meta:
            _total_segment_count = int(partition_meta['total_segment_count'])

        """
        total_index_file_count: int
        """
        _total_index_file_count = 0
        if 'total_index_file_count' in partition_meta:
            _total_index_file_count = int(partition_meta['total_index_file_count'])

        """
        total_index_file_size: int
        """
        _total_index_file_size = 0
        if 'total_index_file_size' in partition_meta:
            _total_index_file_size = int(partition_meta['total_index_file_size'])

        """
        total_delete_doc_count: int
        """
        _total_delete_doc_count = 0
        if 'total_delete_doc_count' in partition_meta:
            _total_delete_doc_count = int(partition_meta['total_delete_doc_count'])

        """
        channel_stats: Optional[List[PartitionChannel]]
        """
        _channel_stats = None
        if 'channel_stats' in partition_meta:
            _channel_stats = []
            for channel_stat in partition_meta['channel_stats']:
                """
                channel_id: int
                """
                _channel_id = None
                if 'channel_id' in channel_stat:
                    _channel_id = int(channel_stat['channel_id'])
                """
                segment_stats: Optional[List[PartitionSegment]]
                """
                _segment_stats = None
                if 'segment_stats' in channel_stat:
                    _segment_stats = []
                    for segment_stat in channel_stat['segment_stats']:
                        _segment_id = None
                        if 'segment_id' in segment_stat:
                            _segment_id = segment_stat['segment_id']
                        _state = None
                        if 'state' in segment_stat:
                            _state = SegmentState.get(segment_stat['state'])
                        _doc_count = None
                        if 'doc_count' in segment_stat:
                            _doc_count = int(segment_stat['doc_count'])
                        _index_file_count = None
                        if 'index_file_count' in segment_stat:
                            _index_file_count = int(segment_stat['index_file_count'])
                        _index_file_size = None
                        if 'index_file_size' in segment_stat:
                            _index_file_size = int(segment_stat['index_file_size'])
                        _min_doc_id = None
                        if 'min_doc_id' in segment_stat:
                            _min_doc_id = int(segment_stat['min_doc_id'])
                        _max_doc_id = None
                        if 'max_doc_id' in segment_stat:
                            _max_doc_id = int(segment_stat['max_doc_id'])
                        _min_timestamp = None
                        if 'min_timestamp' in segment_stat:
                            _min_timestamp = int(segment_stat['min_timestamp'])
                        _max_timestamp = None
                        if 'max_timestamp' in segment_stat:
                            _max_timestamp = int(segment_stat['max_timestamp'])
                        _min_offset = None
                        if 'min_offset' in segment_stat:
                            _min_offset = int(segment_stat['min_offset'])
                        _max_offset = None
                        if 'max_offset' in segment_stat:
                            _max_offset = int(segment_stat['max_offset'])
                        _segment_path = None
                        if 'segment_path' in segment_stat:
                            _segment_path = str(segment_stat['segment_path'])

                        _segment_stats.append(PartitionSegment(segment_id=_segment_id,
                                                               state=_state,
                                                               doc_count=_doc_count,
                                                               index_file_count=_index_file_count,
                                                               index_file_size=_index_file_size,
                                                               min_doc_id=_min_doc_id,
                                                               max_doc_id=_max_doc_id,
                                                               min_timestamp=_min_timestamp,
                                                               max_timestamp=_max_timestamp,
                                                               min_offset=_min_offset,
                                                               max_offset=_max_offset,
                                                               segment_path=_segment_path))

                _channel_stats.append(PartitionChannel(channel_id=_channel_id,
                                                       segment_stats=_segment_stats))
        return PartitionStats(name=_partition_name,
                              total_doc_count=_total_doc_count,
                              total_segment_count=_total_segment_count,
                              total_index_file_count=_total_index_file_count,
                              total_index_file_size=_total_index_file_size,
                              total_delete_doc_count=_total_delete_doc_count,
                              channel_stats=_channel_stats)


@dataclass(frozen=True)
class PartitionMeta(object):

    """
    A Meta Instance of Partition.

    Args:
        name (str): partition name
        state (int): partition status
    """

    name: str
    state: int

    def __dict__(self):
        meta_dict = {
            'name': self.name,
            'state': PartitionStatus.str(self.state)
        }
        return meta_dict

    def __str__(self):
        return json.dumps(self.__dict__())

    def __repr__(self):
        return self.__str__()


class PartitionMetaBuilder(object):
    @staticmethod
    def from_meta(partition_name: str,
                  partition_meta: str):
        return PartitionMeta(name=partition_name,
                             state=PartitionStatus.get(partition_meta))