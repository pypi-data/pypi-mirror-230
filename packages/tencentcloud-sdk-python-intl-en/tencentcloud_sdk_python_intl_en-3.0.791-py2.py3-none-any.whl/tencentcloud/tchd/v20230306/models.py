# -*- coding: utf8 -*-
# Copyright (c) 2017-2021 THL A29 Limited, a Tencent company. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import warnings

from tencentcloud.common.abstract_model import AbstractModel


class DescribeEventsRequest(AbstractModel):
    """DescribeEvents request structure.

    """

    def __init__(self):
        r"""
        :param _EventDate: event occurrence date
        :type EventDate: str
        :param _ProductIds: Query by Product ID(s). Product ID examples: cvm, lb, cdb, cdn, crs.
        :type ProductIds: list of str
        :param _RegionIds:  1. Query by Region ID(s). Region ID examples: ap-guangzhou、ap-shanghai、ap-singapore.
2. The region ID for non-region-specific products should be set to non-regional.
        :type RegionIds: list of str
        """
        self._EventDate = None
        self._ProductIds = None
        self._RegionIds = None

    @property
    def EventDate(self):
        return self._EventDate

    @EventDate.setter
    def EventDate(self, EventDate):
        self._EventDate = EventDate

    @property
    def ProductIds(self):
        return self._ProductIds

    @ProductIds.setter
    def ProductIds(self, ProductIds):
        self._ProductIds = ProductIds

    @property
    def RegionIds(self):
        return self._RegionIds

    @RegionIds.setter
    def RegionIds(self, RegionIds):
        self._RegionIds = RegionIds


    def _deserialize(self, params):
        self._EventDate = params.get("EventDate")
        self._ProductIds = params.get("ProductIds")
        self._RegionIds = params.get("RegionIds")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeEventsResponse(AbstractModel):
    """DescribeEvents response structure.

    """

    def __init__(self):
        r"""
        :param _Data: Detailed event information.
        :type Data: :class:`tencentcloud.tchd.v20230306.models.ProductEventList`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Data = None
        self._RequestId = None

    @property
    def Data(self):
        return self._Data

    @Data.setter
    def Data(self, Data):
        self._Data = Data

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Data") is not None:
            self._Data = ProductEventList()
            self._Data._deserialize(params.get("Data"))
        self._RequestId = params.get("RequestId")


class EventDetail(AbstractModel):
    """Describes information on an event.

    """

    def __init__(self):
        r"""
        :param _ProductId: Product ID.
        :type ProductId: str
        :param _ProductName: Product name.
        :type ProductName: str
        :param _RegionId: Region ID.
        :type RegionId: str
        :param _RegionName: Region name.
        :type RegionName: str
        :param _StartTime: Event start time.
        :type StartTime: str
        :param _EndTime: Event end time. If the event is still ongoing and has not ended, the end time will be empty.
        :type EndTime: str
        :param _CurrentStatus: Current status: Normally, Informational, Degradation.
        :type CurrentStatus: str
        """
        self._ProductId = None
        self._ProductName = None
        self._RegionId = None
        self._RegionName = None
        self._StartTime = None
        self._EndTime = None
        self._CurrentStatus = None

    @property
    def ProductId(self):
        return self._ProductId

    @ProductId.setter
    def ProductId(self, ProductId):
        self._ProductId = ProductId

    @property
    def ProductName(self):
        return self._ProductName

    @ProductName.setter
    def ProductName(self, ProductName):
        self._ProductName = ProductName

    @property
    def RegionId(self):
        return self._RegionId

    @RegionId.setter
    def RegionId(self, RegionId):
        self._RegionId = RegionId

    @property
    def RegionName(self):
        return self._RegionName

    @RegionName.setter
    def RegionName(self, RegionName):
        self._RegionName = RegionName

    @property
    def StartTime(self):
        return self._StartTime

    @StartTime.setter
    def StartTime(self, StartTime):
        self._StartTime = StartTime

    @property
    def EndTime(self):
        return self._EndTime

    @EndTime.setter
    def EndTime(self, EndTime):
        self._EndTime = EndTime

    @property
    def CurrentStatus(self):
        return self._CurrentStatus

    @CurrentStatus.setter
    def CurrentStatus(self, CurrentStatus):
        self._CurrentStatus = CurrentStatus


    def _deserialize(self, params):
        self._ProductId = params.get("ProductId")
        self._ProductName = params.get("ProductName")
        self._RegionId = params.get("RegionId")
        self._RegionName = params.get("RegionName")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._CurrentStatus = params.get("CurrentStatus")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ProductEventList(AbstractModel):
    """Detailed event information.

    """

    def __init__(self):
        r"""
        :param _EventList: Detailed event information.
Note: this field may return null, indicating that no valid value is obtained.
        :type EventList: list of EventDetail
        """
        self._EventList = None

    @property
    def EventList(self):
        return self._EventList

    @EventList.setter
    def EventList(self, EventList):
        self._EventList = EventList


    def _deserialize(self, params):
        if params.get("EventList") is not None:
            self._EventList = []
            for item in params.get("EventList"):
                obj = EventDetail()
                obj._deserialize(item)
                self._EventList.append(obj)
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        