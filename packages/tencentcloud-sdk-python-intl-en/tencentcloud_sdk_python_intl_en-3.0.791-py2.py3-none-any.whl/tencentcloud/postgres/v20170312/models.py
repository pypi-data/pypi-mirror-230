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


class AccountInfo(AbstractModel):
    """Account information

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of postgres-lnp6j617
        :type DBInstanceId: str
        :param _UserName: Account
        :type UserName: str
        :param _Remark: Account remarks
        :type Remark: str
        :param _Status: Account status. 1: creating, 2: normal, 3: modifying, 4: resetting password, -1: deleting
        :type Status: int
        :param _CreateTime: Account creation time
        :type CreateTime: str
        :param _UpdateTime: Account last modified time
        :type UpdateTime: str
        """
        self._DBInstanceId = None
        self._UserName = None
        self._Remark = None
        self._Status = None
        self._CreateTime = None
        self._UpdateTime = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def UserName(self):
        return self._UserName

    @UserName.setter
    def UserName(self, UserName):
        self._UserName = UserName

    @property
    def Remark(self):
        return self._Remark

    @Remark.setter
    def Remark(self, Remark):
        self._Remark = Remark

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status

    @property
    def CreateTime(self):
        return self._CreateTime

    @CreateTime.setter
    def CreateTime(self, CreateTime):
        self._CreateTime = CreateTime

    @property
    def UpdateTime(self):
        return self._UpdateTime

    @UpdateTime.setter
    def UpdateTime(self, UpdateTime):
        self._UpdateTime = UpdateTime


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._UserName = params.get("UserName")
        self._Remark = params.get("Remark")
        self._Status = params.get("Status")
        self._CreateTime = params.get("CreateTime")
        self._UpdateTime = params.get("UpdateTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class AddDBInstanceToReadOnlyGroupRequest(AbstractModel):
    """AddDBInstanceToReadOnlyGroup request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _ReadOnlyGroupId: RO group ID
        :type ReadOnlyGroupId: str
        """
        self._DBInstanceId = None
        self._ReadOnlyGroupId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def ReadOnlyGroupId(self):
        return self._ReadOnlyGroupId

    @ReadOnlyGroupId.setter
    def ReadOnlyGroupId(self, ReadOnlyGroupId):
        self._ReadOnlyGroupId = ReadOnlyGroupId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._ReadOnlyGroupId = params.get("ReadOnlyGroupId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class AddDBInstanceToReadOnlyGroupResponse(AbstractModel):
    """AddDBInstanceToReadOnlyGroup response structure.

    """

    def __init__(self):
        r"""
        :param _FlowId: Task ID
        :type FlowId: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._FlowId = None
        self._RequestId = None

    @property
    def FlowId(self):
        return self._FlowId

    @FlowId.setter
    def FlowId(self, FlowId):
        self._FlowId = FlowId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._FlowId = params.get("FlowId")
        self._RequestId = params.get("RequestId")


class AnalysisItems(AbstractModel):
    """Detailed analysis of a slow query statement with abstract parameter values, which is returned by the `DescribeSlowQueryAnalysis` API

    """

    def __init__(self):
        r"""
        :param _DatabaseName: The name of the database queried by the slow query statement
        :type DatabaseName: str
        :param _UserName: The name of the user who executes the slow query statement
        :type UserName: str
        :param _NormalQuery: The slow query statement whose parameter values are abstracted
        :type NormalQuery: str
        :param _ClientAddr: The address of the client that executes the slow query statement
        :type ClientAddr: str
        :param _CallNum: The number of executions of the slow query statement during the specified period of time
        :type CallNum: int
        :param _CallPercent: The ratio (in decimal form) of the number of executions of the slow query statement to that of all slow query statements during the specified period of time
        :type CallPercent: float
        :param _CostTime: The total execution time of the slow query statement during the specified period of time
        :type CostTime: float
        :param _CostPercent: The ratio (in decimal form) of the total execution time of the slow query statement to that of all slow query statements during the specified period of time
        :type CostPercent: float
        :param _MinCostTime: The shortest execution time (in ms) of the slow query statement during the specified period of time
        :type MinCostTime: float
        :param _MaxCostTime: The longest execution time (in ms) of the slow query statement during the specified period of time
        :type MaxCostTime: float
        :param _AvgCostTime: The average execution time (in ms) of the slow query statement during the specified period of time
        :type AvgCostTime: float
        :param _FirstTime: The timestamp when the slow query statement starts to execute for the first time during the specified period of time
        :type FirstTime: str
        :param _LastTime: The timestamp when the slow query statement starts to execute for the last time during the specified period of time
        :type LastTime: str
        """
        self._DatabaseName = None
        self._UserName = None
        self._NormalQuery = None
        self._ClientAddr = None
        self._CallNum = None
        self._CallPercent = None
        self._CostTime = None
        self._CostPercent = None
        self._MinCostTime = None
        self._MaxCostTime = None
        self._AvgCostTime = None
        self._FirstTime = None
        self._LastTime = None

    @property
    def DatabaseName(self):
        return self._DatabaseName

    @DatabaseName.setter
    def DatabaseName(self, DatabaseName):
        self._DatabaseName = DatabaseName

    @property
    def UserName(self):
        return self._UserName

    @UserName.setter
    def UserName(self, UserName):
        self._UserName = UserName

    @property
    def NormalQuery(self):
        return self._NormalQuery

    @NormalQuery.setter
    def NormalQuery(self, NormalQuery):
        self._NormalQuery = NormalQuery

    @property
    def ClientAddr(self):
        return self._ClientAddr

    @ClientAddr.setter
    def ClientAddr(self, ClientAddr):
        self._ClientAddr = ClientAddr

    @property
    def CallNum(self):
        return self._CallNum

    @CallNum.setter
    def CallNum(self, CallNum):
        self._CallNum = CallNum

    @property
    def CallPercent(self):
        return self._CallPercent

    @CallPercent.setter
    def CallPercent(self, CallPercent):
        self._CallPercent = CallPercent

    @property
    def CostTime(self):
        return self._CostTime

    @CostTime.setter
    def CostTime(self, CostTime):
        self._CostTime = CostTime

    @property
    def CostPercent(self):
        return self._CostPercent

    @CostPercent.setter
    def CostPercent(self, CostPercent):
        self._CostPercent = CostPercent

    @property
    def MinCostTime(self):
        return self._MinCostTime

    @MinCostTime.setter
    def MinCostTime(self, MinCostTime):
        self._MinCostTime = MinCostTime

    @property
    def MaxCostTime(self):
        return self._MaxCostTime

    @MaxCostTime.setter
    def MaxCostTime(self, MaxCostTime):
        self._MaxCostTime = MaxCostTime

    @property
    def AvgCostTime(self):
        return self._AvgCostTime

    @AvgCostTime.setter
    def AvgCostTime(self, AvgCostTime):
        self._AvgCostTime = AvgCostTime

    @property
    def FirstTime(self):
        return self._FirstTime

    @FirstTime.setter
    def FirstTime(self, FirstTime):
        self._FirstTime = FirstTime

    @property
    def LastTime(self):
        return self._LastTime

    @LastTime.setter
    def LastTime(self, LastTime):
        self._LastTime = LastTime


    def _deserialize(self, params):
        self._DatabaseName = params.get("DatabaseName")
        self._UserName = params.get("UserName")
        self._NormalQuery = params.get("NormalQuery")
        self._ClientAddr = params.get("ClientAddr")
        self._CallNum = params.get("CallNum")
        self._CallPercent = params.get("CallPercent")
        self._CostTime = params.get("CostTime")
        self._CostPercent = params.get("CostPercent")
        self._MinCostTime = params.get("MinCostTime")
        self._MaxCostTime = params.get("MaxCostTime")
        self._AvgCostTime = params.get("AvgCostTime")
        self._FirstTime = params.get("FirstTime")
        self._LastTime = params.get("LastTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class BackupDownloadRestriction(AbstractModel):
    """Restriction information for downloading a backup

    """

    def __init__(self):
        r"""
        :param _RestrictionType: Type of the network restrictions for downloading backup files. Valid values: `NONE` (backups can be downloaded over both private and public networks), `INTRANET` (backups can only be downloaded over the private network), `CUSTOMIZE` (backups can be downloaded over specified VPCs or at specified IPs).
        :type RestrictionType: str
        :param _VpcRestrictionEffect: Whether VPC is allowed. Valid values: `ALLOW` (allow), `DENY` (deny).
        :type VpcRestrictionEffect: str
        :param _VpcIdSet: Whether it is allowed to download the VPC ID list of the backup files.
        :type VpcIdSet: list of str
        :param _IpRestrictionEffect: Whether IP is allowed. Valid values: `ALLOW` (allow), `DENY` (deny).
        :type IpRestrictionEffect: str
        :param _IpSet: Whether it is allowed to download IP list of the backup files.
        :type IpSet: list of str
        """
        self._RestrictionType = None
        self._VpcRestrictionEffect = None
        self._VpcIdSet = None
        self._IpRestrictionEffect = None
        self._IpSet = None

    @property
    def RestrictionType(self):
        return self._RestrictionType

    @RestrictionType.setter
    def RestrictionType(self, RestrictionType):
        self._RestrictionType = RestrictionType

    @property
    def VpcRestrictionEffect(self):
        return self._VpcRestrictionEffect

    @VpcRestrictionEffect.setter
    def VpcRestrictionEffect(self, VpcRestrictionEffect):
        self._VpcRestrictionEffect = VpcRestrictionEffect

    @property
    def VpcIdSet(self):
        return self._VpcIdSet

    @VpcIdSet.setter
    def VpcIdSet(self, VpcIdSet):
        self._VpcIdSet = VpcIdSet

    @property
    def IpRestrictionEffect(self):
        return self._IpRestrictionEffect

    @IpRestrictionEffect.setter
    def IpRestrictionEffect(self, IpRestrictionEffect):
        self._IpRestrictionEffect = IpRestrictionEffect

    @property
    def IpSet(self):
        return self._IpSet

    @IpSet.setter
    def IpSet(self, IpSet):
        self._IpSet = IpSet


    def _deserialize(self, params):
        self._RestrictionType = params.get("RestrictionType")
        self._VpcRestrictionEffect = params.get("VpcRestrictionEffect")
        self._VpcIdSet = params.get("VpcIdSet")
        self._IpRestrictionEffect = params.get("IpRestrictionEffect")
        self._IpSet = params.get("IpSet")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class BackupPlan(AbstractModel):
    """Backup plan

    """

    def __init__(self):
        r"""
        :param _BackupPeriod: Backup cycle
        :type BackupPeriod: str
        :param _BaseBackupRetentionPeriod: Retention period of basic backups
        :type BaseBackupRetentionPeriod: int
        :param _MinBackupStartTime: The earliest time to start a backup
        :type MinBackupStartTime: str
        :param _MaxBackupStartTime: The latest time to start a backup
        :type MaxBackupStartTime: str
        """
        self._BackupPeriod = None
        self._BaseBackupRetentionPeriod = None
        self._MinBackupStartTime = None
        self._MaxBackupStartTime = None

    @property
    def BackupPeriod(self):
        return self._BackupPeriod

    @BackupPeriod.setter
    def BackupPeriod(self, BackupPeriod):
        self._BackupPeriod = BackupPeriod

    @property
    def BaseBackupRetentionPeriod(self):
        return self._BaseBackupRetentionPeriod

    @BaseBackupRetentionPeriod.setter
    def BaseBackupRetentionPeriod(self, BaseBackupRetentionPeriod):
        self._BaseBackupRetentionPeriod = BaseBackupRetentionPeriod

    @property
    def MinBackupStartTime(self):
        return self._MinBackupStartTime

    @MinBackupStartTime.setter
    def MinBackupStartTime(self, MinBackupStartTime):
        self._MinBackupStartTime = MinBackupStartTime

    @property
    def MaxBackupStartTime(self):
        return self._MaxBackupStartTime

    @MaxBackupStartTime.setter
    def MaxBackupStartTime(self, MaxBackupStartTime):
        self._MaxBackupStartTime = MaxBackupStartTime


    def _deserialize(self, params):
        self._BackupPeriod = params.get("BackupPeriod")
        self._BaseBackupRetentionPeriod = params.get("BaseBackupRetentionPeriod")
        self._MinBackupStartTime = params.get("MinBackupStartTime")
        self._MaxBackupStartTime = params.get("MaxBackupStartTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class BackupSummary(AbstractModel):
    """Instance backup statistics

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _LogBackupCount: Number of log backups of an instance
        :type LogBackupCount: int
        :param _LogBackupSize: Size of log backups of an instance
        :type LogBackupSize: int
        :param _ManualBaseBackupCount: Number of manually created full backups of an instance
        :type ManualBaseBackupCount: int
        :param _ManualBaseBackupSize: Size of manually created full backups of an instance
        :type ManualBaseBackupSize: int
        :param _AutoBaseBackupCount: Number of automatically created full backups of an instance
        :type AutoBaseBackupCount: int
        :param _AutoBaseBackupSize: Size of automatically created full backups of an instance
        :type AutoBaseBackupSize: int
        :param _TotalBackupCount: Total number of backups
        :type TotalBackupCount: int
        :param _TotalBackupSize: Total backup size
        :type TotalBackupSize: int
        """
        self._DBInstanceId = None
        self._LogBackupCount = None
        self._LogBackupSize = None
        self._ManualBaseBackupCount = None
        self._ManualBaseBackupSize = None
        self._AutoBaseBackupCount = None
        self._AutoBaseBackupSize = None
        self._TotalBackupCount = None
        self._TotalBackupSize = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def LogBackupCount(self):
        return self._LogBackupCount

    @LogBackupCount.setter
    def LogBackupCount(self, LogBackupCount):
        self._LogBackupCount = LogBackupCount

    @property
    def LogBackupSize(self):
        return self._LogBackupSize

    @LogBackupSize.setter
    def LogBackupSize(self, LogBackupSize):
        self._LogBackupSize = LogBackupSize

    @property
    def ManualBaseBackupCount(self):
        return self._ManualBaseBackupCount

    @ManualBaseBackupCount.setter
    def ManualBaseBackupCount(self, ManualBaseBackupCount):
        self._ManualBaseBackupCount = ManualBaseBackupCount

    @property
    def ManualBaseBackupSize(self):
        return self._ManualBaseBackupSize

    @ManualBaseBackupSize.setter
    def ManualBaseBackupSize(self, ManualBaseBackupSize):
        self._ManualBaseBackupSize = ManualBaseBackupSize

    @property
    def AutoBaseBackupCount(self):
        return self._AutoBaseBackupCount

    @AutoBaseBackupCount.setter
    def AutoBaseBackupCount(self, AutoBaseBackupCount):
        self._AutoBaseBackupCount = AutoBaseBackupCount

    @property
    def AutoBaseBackupSize(self):
        return self._AutoBaseBackupSize

    @AutoBaseBackupSize.setter
    def AutoBaseBackupSize(self, AutoBaseBackupSize):
        self._AutoBaseBackupSize = AutoBaseBackupSize

    @property
    def TotalBackupCount(self):
        return self._TotalBackupCount

    @TotalBackupCount.setter
    def TotalBackupCount(self, TotalBackupCount):
        self._TotalBackupCount = TotalBackupCount

    @property
    def TotalBackupSize(self):
        return self._TotalBackupSize

    @TotalBackupSize.setter
    def TotalBackupSize(self, TotalBackupSize):
        self._TotalBackupSize = TotalBackupSize


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._LogBackupCount = params.get("LogBackupCount")
        self._LogBackupSize = params.get("LogBackupSize")
        self._ManualBaseBackupCount = params.get("ManualBaseBackupCount")
        self._ManualBaseBackupSize = params.get("ManualBaseBackupSize")
        self._AutoBaseBackupCount = params.get("AutoBaseBackupCount")
        self._AutoBaseBackupSize = params.get("AutoBaseBackupSize")
        self._TotalBackupCount = params.get("TotalBackupCount")
        self._TotalBackupSize = params.get("TotalBackupSize")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class BaseBackup(AbstractModel):
    """Full backup information of a database

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _Id: Unique ID of a backup file
        :type Id: str
        :param _Name: Backup file name.
        :type Name: str
        :param _BackupMethod: Backup method, including physical and logical.
        :type BackupMethod: str
        :param _BackupMode: Backup mode, including automatic and manual.
        :type BackupMode: str
        :param _State: Backup task status
        :type State: str
        :param _Size: Backup set size in bytes
        :type Size: int
        :param _StartTime: Backup start time
        :type StartTime: str
        :param _FinishTime: Backup end time
        :type FinishTime: str
        :param _ExpireTime: Backup expiration time
        :type ExpireTime: str
        """
        self._DBInstanceId = None
        self._Id = None
        self._Name = None
        self._BackupMethod = None
        self._BackupMode = None
        self._State = None
        self._Size = None
        self._StartTime = None
        self._FinishTime = None
        self._ExpireTime = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def Id(self):
        return self._Id

    @Id.setter
    def Id(self, Id):
        self._Id = Id

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, Name):
        self._Name = Name

    @property
    def BackupMethod(self):
        return self._BackupMethod

    @BackupMethod.setter
    def BackupMethod(self, BackupMethod):
        self._BackupMethod = BackupMethod

    @property
    def BackupMode(self):
        return self._BackupMode

    @BackupMode.setter
    def BackupMode(self, BackupMode):
        self._BackupMode = BackupMode

    @property
    def State(self):
        return self._State

    @State.setter
    def State(self, State):
        self._State = State

    @property
    def Size(self):
        return self._Size

    @Size.setter
    def Size(self, Size):
        self._Size = Size

    @property
    def StartTime(self):
        return self._StartTime

    @StartTime.setter
    def StartTime(self, StartTime):
        self._StartTime = StartTime

    @property
    def FinishTime(self):
        return self._FinishTime

    @FinishTime.setter
    def FinishTime(self, FinishTime):
        self._FinishTime = FinishTime

    @property
    def ExpireTime(self):
        return self._ExpireTime

    @ExpireTime.setter
    def ExpireTime(self, ExpireTime):
        self._ExpireTime = ExpireTime


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._Id = params.get("Id")
        self._Name = params.get("Name")
        self._BackupMethod = params.get("BackupMethod")
        self._BackupMode = params.get("BackupMode")
        self._State = params.get("State")
        self._Size = params.get("Size")
        self._StartTime = params.get("StartTime")
        self._FinishTime = params.get("FinishTime")
        self._ExpireTime = params.get("ExpireTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ClassInfo(AbstractModel):
    """Database instance specification

    """

    def __init__(self):
        r"""
        :param _SpecCode: Specification ID
        :type SpecCode: str
        :param _CPU: Number of CPU cores
        :type CPU: int
        :param _Memory: Memory size in MB
        :type Memory: int
        :param _MaxStorage: Maximum storage capacity in GB supported by this specification
        :type MaxStorage: int
        :param _MinStorage: Minimum storage capacity in GB supported by this specification
        :type MinStorage: int
        :param _QPS: Estimated QPS for this specification
        :type QPS: int
        """
        self._SpecCode = None
        self._CPU = None
        self._Memory = None
        self._MaxStorage = None
        self._MinStorage = None
        self._QPS = None

    @property
    def SpecCode(self):
        return self._SpecCode

    @SpecCode.setter
    def SpecCode(self, SpecCode):
        self._SpecCode = SpecCode

    @property
    def CPU(self):
        return self._CPU

    @CPU.setter
    def CPU(self, CPU):
        self._CPU = CPU

    @property
    def Memory(self):
        return self._Memory

    @Memory.setter
    def Memory(self, Memory):
        self._Memory = Memory

    @property
    def MaxStorage(self):
        return self._MaxStorage

    @MaxStorage.setter
    def MaxStorage(self, MaxStorage):
        self._MaxStorage = MaxStorage

    @property
    def MinStorage(self):
        return self._MinStorage

    @MinStorage.setter
    def MinStorage(self, MinStorage):
        self._MinStorage = MinStorage

    @property
    def QPS(self):
        return self._QPS

    @QPS.setter
    def QPS(self, QPS):
        self._QPS = QPS


    def _deserialize(self, params):
        self._SpecCode = params.get("SpecCode")
        self._CPU = params.get("CPU")
        self._Memory = params.get("Memory")
        self._MaxStorage = params.get("MaxStorage")
        self._MinStorage = params.get("MinStorage")
        self._QPS = params.get("QPS")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CloneDBInstanceRequest(AbstractModel):
    """CloneDBInstance request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: ID of the original instance to be cloned.
        :type DBInstanceId: str
        :param _SpecCode: Purchasable specification ID, which can be obtained through the `SpecCode` field in the returned value of the `DescribeProductConfig` API.
        :type SpecCode: str
        :param _Storage: Instance storage capacity in GB.
        :type Storage: int
        :param _Period: Valid period in months of the purchased instance. Valid values: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`, `12`, `24`, `36`. This parameter is set to `1` when the pay-as-you-go billing mode is used.
        :type Period: int
        :param _AutoRenewFlag: Renewal flag. Valid values: `0` (manual renewal), `1` (auto-renewal). Default value: `0`.
        :type AutoRenewFlag: int
        :param _VpcId: VPC ID.
        :type VpcId: str
        :param _SubnetId: ID of a subnet in the VPC specified by `VpcId`.
        :type SubnetId: str
        :param _Name: Name of the purchased instance.
        :type Name: str
        :param _InstanceChargeType: Instance billing mode. Valid values: `PREPAID` (monthly subscription), `POSTPAID_BY_HOUR` (pay-as-you-go).
        :type InstanceChargeType: str
        :param _SecurityGroupIds: Security group ID.
        :type SecurityGroupIds: list of str
        :param _ProjectId: Project ID.
        :type ProjectId: int
        :param _TagList: The information of tags to be bound with the purchased instance. This parameter is left empty by default.
        :type TagList: list of Tag
        :param _DBNodeSet: This parameter is required if you purchase a multi-AZ deployed instance.
        :type DBNodeSet: list of DBNode
        :param _AutoVoucher: Whether to automatically use vouchers. Valid values: `1` (yes), `0` (no). Default value: `0`.
        :type AutoVoucher: int
        :param _VoucherIds: Voucher ID list.
        :type VoucherIds: str
        :param _ActivityId: Campaign ID.
        :type ActivityId: int
        :param _BackupSetId: Basic backup set ID.
        :type BackupSetId: str
        :param _RecoveryTargetTime: Restoration point in time.
        :type RecoveryTargetTime: str
        """
        self._DBInstanceId = None
        self._SpecCode = None
        self._Storage = None
        self._Period = None
        self._AutoRenewFlag = None
        self._VpcId = None
        self._SubnetId = None
        self._Name = None
        self._InstanceChargeType = None
        self._SecurityGroupIds = None
        self._ProjectId = None
        self._TagList = None
        self._DBNodeSet = None
        self._AutoVoucher = None
        self._VoucherIds = None
        self._ActivityId = None
        self._BackupSetId = None
        self._RecoveryTargetTime = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def SpecCode(self):
        return self._SpecCode

    @SpecCode.setter
    def SpecCode(self, SpecCode):
        self._SpecCode = SpecCode

    @property
    def Storage(self):
        return self._Storage

    @Storage.setter
    def Storage(self, Storage):
        self._Storage = Storage

    @property
    def Period(self):
        return self._Period

    @Period.setter
    def Period(self, Period):
        self._Period = Period

    @property
    def AutoRenewFlag(self):
        return self._AutoRenewFlag

    @AutoRenewFlag.setter
    def AutoRenewFlag(self, AutoRenewFlag):
        self._AutoRenewFlag = AutoRenewFlag

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, Name):
        self._Name = Name

    @property
    def InstanceChargeType(self):
        return self._InstanceChargeType

    @InstanceChargeType.setter
    def InstanceChargeType(self, InstanceChargeType):
        self._InstanceChargeType = InstanceChargeType

    @property
    def SecurityGroupIds(self):
        return self._SecurityGroupIds

    @SecurityGroupIds.setter
    def SecurityGroupIds(self, SecurityGroupIds):
        self._SecurityGroupIds = SecurityGroupIds

    @property
    def ProjectId(self):
        return self._ProjectId

    @ProjectId.setter
    def ProjectId(self, ProjectId):
        self._ProjectId = ProjectId

    @property
    def TagList(self):
        return self._TagList

    @TagList.setter
    def TagList(self, TagList):
        self._TagList = TagList

    @property
    def DBNodeSet(self):
        return self._DBNodeSet

    @DBNodeSet.setter
    def DBNodeSet(self, DBNodeSet):
        self._DBNodeSet = DBNodeSet

    @property
    def AutoVoucher(self):
        return self._AutoVoucher

    @AutoVoucher.setter
    def AutoVoucher(self, AutoVoucher):
        self._AutoVoucher = AutoVoucher

    @property
    def VoucherIds(self):
        return self._VoucherIds

    @VoucherIds.setter
    def VoucherIds(self, VoucherIds):
        self._VoucherIds = VoucherIds

    @property
    def ActivityId(self):
        return self._ActivityId

    @ActivityId.setter
    def ActivityId(self, ActivityId):
        self._ActivityId = ActivityId

    @property
    def BackupSetId(self):
        return self._BackupSetId

    @BackupSetId.setter
    def BackupSetId(self, BackupSetId):
        self._BackupSetId = BackupSetId

    @property
    def RecoveryTargetTime(self):
        return self._RecoveryTargetTime

    @RecoveryTargetTime.setter
    def RecoveryTargetTime(self, RecoveryTargetTime):
        self._RecoveryTargetTime = RecoveryTargetTime


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._SpecCode = params.get("SpecCode")
        self._Storage = params.get("Storage")
        self._Period = params.get("Period")
        self._AutoRenewFlag = params.get("AutoRenewFlag")
        self._VpcId = params.get("VpcId")
        self._SubnetId = params.get("SubnetId")
        self._Name = params.get("Name")
        self._InstanceChargeType = params.get("InstanceChargeType")
        self._SecurityGroupIds = params.get("SecurityGroupIds")
        self._ProjectId = params.get("ProjectId")
        if params.get("TagList") is not None:
            self._TagList = []
            for item in params.get("TagList"):
                obj = Tag()
                obj._deserialize(item)
                self._TagList.append(obj)
        if params.get("DBNodeSet") is not None:
            self._DBNodeSet = []
            for item in params.get("DBNodeSet"):
                obj = DBNode()
                obj._deserialize(item)
                self._DBNodeSet.append(obj)
        self._AutoVoucher = params.get("AutoVoucher")
        self._VoucherIds = params.get("VoucherIds")
        self._ActivityId = params.get("ActivityId")
        self._BackupSetId = params.get("BackupSetId")
        self._RecoveryTargetTime = params.get("RecoveryTargetTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CloneDBInstanceResponse(AbstractModel):
    """CloneDBInstance response structure.

    """

    def __init__(self):
        r"""
        :param _DealName: Order ID.
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DealName: str
        :param _BillId: Bill ID.
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type BillId: str
        :param _DBInstanceId: ID of the cloned instance, which will be returned only when the instance is pay-as-you-go.
Note: This field may return null, indicating that no valid values can be obtained.
        :type DBInstanceId: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DealName = None
        self._BillId = None
        self._DBInstanceId = None
        self._RequestId = None

    @property
    def DealName(self):
        return self._DealName

    @DealName.setter
    def DealName(self, DealName):
        self._DealName = DealName

    @property
    def BillId(self):
        return self._BillId

    @BillId.setter
    def BillId(self, BillId):
        self._BillId = BillId

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._DealName = params.get("DealName")
        self._BillId = params.get("BillId")
        self._DBInstanceId = params.get("DBInstanceId")
        self._RequestId = params.get("RequestId")


class CloseDBExtranetAccessRequest(AbstractModel):
    """CloseDBExtranetAccess request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of postgres-6r233v55
        :type DBInstanceId: str
        :param _IsIpv6: Whether to disable public network access over IPv6 address. Valid values: 1 (yes), 0 (no)
        :type IsIpv6: int
        """
        self._DBInstanceId = None
        self._IsIpv6 = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def IsIpv6(self):
        return self._IsIpv6

    @IsIpv6.setter
    def IsIpv6(self, IsIpv6):
        self._IsIpv6 = IsIpv6


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._IsIpv6 = params.get("IsIpv6")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CloseDBExtranetAccessResponse(AbstractModel):
    """CloseDBExtranetAccess response structure.

    """

    def __init__(self):
        r"""
        :param _FlowId: Async task flow ID
        :type FlowId: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._FlowId = None
        self._RequestId = None

    @property
    def FlowId(self):
        return self._FlowId

    @FlowId.setter
    def FlowId(self, FlowId):
        self._FlowId = FlowId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._FlowId = params.get("FlowId")
        self._RequestId = params.get("RequestId")


class CloseServerlessDBExtranetAccessRequest(AbstractModel):
    """CloseServerlessDBExtranetAccess request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Unique ID of an instance
        :type DBInstanceId: str
        :param _DBInstanceName: Instance name
        :type DBInstanceName: str
        """
        self._DBInstanceId = None
        self._DBInstanceName = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def DBInstanceName(self):
        return self._DBInstanceName

    @DBInstanceName.setter
    def DBInstanceName(self, DBInstanceName):
        self._DBInstanceName = DBInstanceName


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._DBInstanceName = params.get("DBInstanceName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CloseServerlessDBExtranetAccessResponse(AbstractModel):
    """CloseServerlessDBExtranetAccess response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class CreateBaseBackupRequest(AbstractModel):
    """CreateBaseBackup request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        """
        self._DBInstanceId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateBaseBackupResponse(AbstractModel):
    """CreateBaseBackup response structure.

    """

    def __init__(self):
        r"""
        :param _BaseBackupId: Full backup set ID
        :type BaseBackupId: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._BaseBackupId = None
        self._RequestId = None

    @property
    def BaseBackupId(self):
        return self._BaseBackupId

    @BaseBackupId.setter
    def BaseBackupId(self, BaseBackupId):
        self._BaseBackupId = BaseBackupId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._BaseBackupId = params.get("BaseBackupId")
        self._RequestId = params.get("RequestId")


class CreateDBInstanceNetworkAccessRequest(AbstractModel):
    """CreateDBInstanceNetworkAccess request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of postgres-6bwgamo3.
        :type DBInstanceId: str
        :param _VpcId: Unified VPC ID.
        :type VpcId: str
        :param _SubnetId: Subnet ID.
        :type SubnetId: str
        :param _IsAssignVip: Whether to manually assign the VIP. Valid values: `true` (manually assign), `false` (automatically assign).
        :type IsAssignVip: bool
        :param _Vip: Target VIP.
        :type Vip: str
        """
        self._DBInstanceId = None
        self._VpcId = None
        self._SubnetId = None
        self._IsAssignVip = None
        self._Vip = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def IsAssignVip(self):
        return self._IsAssignVip

    @IsAssignVip.setter
    def IsAssignVip(self, IsAssignVip):
        self._IsAssignVip = IsAssignVip

    @property
    def Vip(self):
        return self._Vip

    @Vip.setter
    def Vip(self, Vip):
        self._Vip = Vip


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._VpcId = params.get("VpcId")
        self._SubnetId = params.get("SubnetId")
        self._IsAssignVip = params.get("IsAssignVip")
        self._Vip = params.get("Vip")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateDBInstanceNetworkAccessResponse(AbstractModel):
    """CreateDBInstanceNetworkAccess response structure.

    """

    def __init__(self):
        r"""
        :param _FlowId: Task ID.
Note: This field may return `null`, indicating that no valid values can be obtained.
        :type FlowId: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._FlowId = None
        self._RequestId = None

    @property
    def FlowId(self):
        return self._FlowId

    @FlowId.setter
    def FlowId(self, FlowId):
        self._FlowId = FlowId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._FlowId = params.get("FlowId")
        self._RequestId = params.get("RequestId")


class CreateDBInstancesRequest(AbstractModel):
    """CreateDBInstances request structure.

    """

    def __init__(self):
        r"""
        :param _SpecCode: Purchasable specification ID, which can be obtained through the `SpecCode` field in the returned value of the `DescribeProductConfig` API.
        :type SpecCode: str
        :param _Storage: Instance capacity size in GB.
        :type Storage: int
        :param _InstanceCount: Number of instances purchased at a time. Value range: 1-100.
        :type InstanceCount: int
        :param _Period: Length of purchase in months. Currently, only 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 24, and 36 are supported.
        :type Period: int
        :param _Zone: AZ ID, which can be obtained through the `Zone` field in the returned value of the `DescribeZones` API.
        :type Zone: str
        :param _ProjectId: Project ID.
        :type ProjectId: int
        :param _DBVersion: PostgreSQL version. If it is specified, an instance running the latest kernel of PostgreSQL `DBVersion` will be created. You must pass in at least one of the following parameters: DBVersion, DBMajorVersion, DBKernelVersion.
        :type DBVersion: str
        :param _InstanceChargeType: Instance billing type.
        :type InstanceChargeType: str
        :param _AutoVoucher: Whether to automatically use vouchers. 1: yes, 0: no. Default value: no.
        :type AutoVoucher: int
        :param _VoucherIds: Voucher ID list (only one voucher can be specified currently).
        :type VoucherIds: list of str
        :param _VpcId: VPC ID.
        :type VpcId: str
        :param _SubnetId: VPC subnet ID.
        :type SubnetId: str
        :param _AutoRenewFlag: Renewal flag. 0: normal renewal (default), 1: auto-renewal.
        :type AutoRenewFlag: int
        :param _ActivityId: Activity ID
        :type ActivityId: int
        :param _Name: Instance name (which will be supported in the future)
        :type Name: str
        :param _NeedSupportIpv6: Whether to support IPv6 address access. Valid values: 1 (yes), 0 (no)
        :type NeedSupportIpv6: int
        :param _TagList: The information of tags to be associated with instances. This parameter is left empty by default.
        :type TagList: list of Tag
        :param _SecurityGroupIds: Security group ID
        :type SecurityGroupIds: list of str
        :param _DBMajorVersion: PostgreSQL major version. If it is specified, an instance running the latest kernel of PostgreSQL `DBMajorVersion` will be created. You must pass in at least one of the following parameters: DBMajorVersion, DBVersion, DBKernelVersion.
        :type DBMajorVersion: str
        :param _DBKernelVersion: PostgreSQL kernel version. If it is specified, an instance running the latest kernel of PostgreSQL `DBKernelVersion` will be created. You must pass in one of the following parameters: DBKernelVersion, DBVersion, DBMajorVersion.
        :type DBKernelVersion: str
        """
        self._SpecCode = None
        self._Storage = None
        self._InstanceCount = None
        self._Period = None
        self._Zone = None
        self._ProjectId = None
        self._DBVersion = None
        self._InstanceChargeType = None
        self._AutoVoucher = None
        self._VoucherIds = None
        self._VpcId = None
        self._SubnetId = None
        self._AutoRenewFlag = None
        self._ActivityId = None
        self._Name = None
        self._NeedSupportIpv6 = None
        self._TagList = None
        self._SecurityGroupIds = None
        self._DBMajorVersion = None
        self._DBKernelVersion = None

    @property
    def SpecCode(self):
        return self._SpecCode

    @SpecCode.setter
    def SpecCode(self, SpecCode):
        self._SpecCode = SpecCode

    @property
    def Storage(self):
        return self._Storage

    @Storage.setter
    def Storage(self, Storage):
        self._Storage = Storage

    @property
    def InstanceCount(self):
        return self._InstanceCount

    @InstanceCount.setter
    def InstanceCount(self, InstanceCount):
        self._InstanceCount = InstanceCount

    @property
    def Period(self):
        return self._Period

    @Period.setter
    def Period(self, Period):
        self._Period = Period

    @property
    def Zone(self):
        return self._Zone

    @Zone.setter
    def Zone(self, Zone):
        self._Zone = Zone

    @property
    def ProjectId(self):
        return self._ProjectId

    @ProjectId.setter
    def ProjectId(self, ProjectId):
        self._ProjectId = ProjectId

    @property
    def DBVersion(self):
        return self._DBVersion

    @DBVersion.setter
    def DBVersion(self, DBVersion):
        self._DBVersion = DBVersion

    @property
    def InstanceChargeType(self):
        return self._InstanceChargeType

    @InstanceChargeType.setter
    def InstanceChargeType(self, InstanceChargeType):
        self._InstanceChargeType = InstanceChargeType

    @property
    def AutoVoucher(self):
        return self._AutoVoucher

    @AutoVoucher.setter
    def AutoVoucher(self, AutoVoucher):
        self._AutoVoucher = AutoVoucher

    @property
    def VoucherIds(self):
        return self._VoucherIds

    @VoucherIds.setter
    def VoucherIds(self, VoucherIds):
        self._VoucherIds = VoucherIds

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def AutoRenewFlag(self):
        return self._AutoRenewFlag

    @AutoRenewFlag.setter
    def AutoRenewFlag(self, AutoRenewFlag):
        self._AutoRenewFlag = AutoRenewFlag

    @property
    def ActivityId(self):
        return self._ActivityId

    @ActivityId.setter
    def ActivityId(self, ActivityId):
        self._ActivityId = ActivityId

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, Name):
        self._Name = Name

    @property
    def NeedSupportIpv6(self):
        return self._NeedSupportIpv6

    @NeedSupportIpv6.setter
    def NeedSupportIpv6(self, NeedSupportIpv6):
        self._NeedSupportIpv6 = NeedSupportIpv6

    @property
    def TagList(self):
        return self._TagList

    @TagList.setter
    def TagList(self, TagList):
        self._TagList = TagList

    @property
    def SecurityGroupIds(self):
        return self._SecurityGroupIds

    @SecurityGroupIds.setter
    def SecurityGroupIds(self, SecurityGroupIds):
        self._SecurityGroupIds = SecurityGroupIds

    @property
    def DBMajorVersion(self):
        return self._DBMajorVersion

    @DBMajorVersion.setter
    def DBMajorVersion(self, DBMajorVersion):
        self._DBMajorVersion = DBMajorVersion

    @property
    def DBKernelVersion(self):
        return self._DBKernelVersion

    @DBKernelVersion.setter
    def DBKernelVersion(self, DBKernelVersion):
        self._DBKernelVersion = DBKernelVersion


    def _deserialize(self, params):
        self._SpecCode = params.get("SpecCode")
        self._Storage = params.get("Storage")
        self._InstanceCount = params.get("InstanceCount")
        self._Period = params.get("Period")
        self._Zone = params.get("Zone")
        self._ProjectId = params.get("ProjectId")
        self._DBVersion = params.get("DBVersion")
        self._InstanceChargeType = params.get("InstanceChargeType")
        self._AutoVoucher = params.get("AutoVoucher")
        self._VoucherIds = params.get("VoucherIds")
        self._VpcId = params.get("VpcId")
        self._SubnetId = params.get("SubnetId")
        self._AutoRenewFlag = params.get("AutoRenewFlag")
        self._ActivityId = params.get("ActivityId")
        self._Name = params.get("Name")
        self._NeedSupportIpv6 = params.get("NeedSupportIpv6")
        if params.get("TagList") is not None:
            self._TagList = []
            for item in params.get("TagList"):
                obj = Tag()
                obj._deserialize(item)
                self._TagList.append(obj)
        self._SecurityGroupIds = params.get("SecurityGroupIds")
        self._DBMajorVersion = params.get("DBMajorVersion")
        self._DBKernelVersion = params.get("DBKernelVersion")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateDBInstancesResponse(AbstractModel):
    """CreateDBInstances response structure.

    """

    def __init__(self):
        r"""
        :param _DealNames: Order number list. Each instance corresponds to an order number.
        :type DealNames: list of str
        :param _BillId: Bill ID of frozen fees
        :type BillId: str
        :param _DBInstanceIdSet: ID set of instances which have been created successfully. The parameter value will be returned only when the billing mode is postpaid.
        :type DBInstanceIdSet: list of str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DealNames = None
        self._BillId = None
        self._DBInstanceIdSet = None
        self._RequestId = None

    @property
    def DealNames(self):
        return self._DealNames

    @DealNames.setter
    def DealNames(self, DealNames):
        self._DealNames = DealNames

    @property
    def BillId(self):
        return self._BillId

    @BillId.setter
    def BillId(self, BillId):
        self._BillId = BillId

    @property
    def DBInstanceIdSet(self):
        return self._DBInstanceIdSet

    @DBInstanceIdSet.setter
    def DBInstanceIdSet(self, DBInstanceIdSet):
        self._DBInstanceIdSet = DBInstanceIdSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._DealNames = params.get("DealNames")
        self._BillId = params.get("BillId")
        self._DBInstanceIdSet = params.get("DBInstanceIdSet")
        self._RequestId = params.get("RequestId")


class CreateInstancesRequest(AbstractModel):
    """CreateInstances request structure.

    """

    def __init__(self):
        r"""
        :param _SpecCode: Purchasable specification ID, which can be obtained through the `SpecCode` field in the returned value of the `DescribeProductConfig` API.
        :type SpecCode: str
        :param _Storage: Instance storage capacity in GB
        :type Storage: int
        :param _InstanceCount: The number of instances purchased at a time. Value range: 1-10.
        :type InstanceCount: int
        :param _Period: Valid period in months of purchased instances. Valid values: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`, `12`, `24`, `36`. This parameter is set to `1` when the pay-as-you-go billing mode is used.
        :type Period: int
        :param _Zone: Availability zone ID, which can be obtained through the `Zone` field in the returned value of the `DescribeZones` API.
        :type Zone: str
        :param _Charset: Instance character set. Valid values: `UTF8`, `LATIN1`.
        :type Charset: str
        :param _AdminName: Instance root account name
        :type AdminName: str
        :param _AdminPassword: Instance root account password
        :type AdminPassword: str
        :param _ProjectId: Project ID
        :type ProjectId: int
        :param _DBVersion: PostgreSQL version. If it is specified, an instance running the latest kernel of PostgreSQL `DBVersion` will be created. You must pass in at least one of the following parameters: DBVersion, DBMajorVersion, DBKernelVersion.
        :type DBVersion: str
        :param _InstanceChargeType: Instance billing mode. Valid values: `PREPAID` (monthly subscription), `POSTPAID_BY_HOUR` (pay-as-you-go).
        :type InstanceChargeType: str
        :param _AutoVoucher: Whether to automatically use vouchers. Valid values: `1` (yes), `0` (no). Default value: `0`.
        :type AutoVoucher: int
        :param _VoucherIds: Voucher ID list. Currently, you can specify only one voucher.
        :type VoucherIds: list of str
        :param _VpcId: VPC ID
        :type VpcId: str
        :param _SubnetId: ID of a subnet in the VPC specified by `VpcId`
        :type SubnetId: str
        :param _AutoRenewFlag: Renewal flag. Valid values: `0` (manual renewal), `1` (auto-renewal). Default value: `0`.
        :type AutoRenewFlag: int
        :param _ActivityId: Campaign ID
        :type ActivityId: int
        :param _Name: Instance name
        :type Name: str
        :param _NeedSupportIpv6: Whether to support IPv6 address access. Valid values: `1` (yes), `0` (no). Default value: `0`
        :type NeedSupportIpv6: int
        :param _TagList: The information of tags to be associated with instances. This parameter is left empty by default.
        :type TagList: list of Tag
        :param _SecurityGroupIds: Security group IDs
        :type SecurityGroupIds: list of str
        :param _DBMajorVersion: PostgreSQL major version. Valid values: `10`, `11`, `12`, `13`. If it is specified, an instance running the latest kernel of PostgreSQL `DBMajorVersion` will be created. You must pass in at least one of the following parameters: DBMajorVersion, DBVersion, DBKernelVersion.
        :type DBMajorVersion: str
        :param _DBKernelVersion: PostgreSQL kernel version. If it is specified, an instance running the latest kernel of PostgreSQL `DBKernelVersion` will be created. You must pass in one of the following parameters: DBKernelVersion, DBVersion, DBMajorVersion.
        :type DBKernelVersion: str
        :param _DBNodeSet: Instance node information, which is required if you purchase a multi-AZ deployed instance.
        :type DBNodeSet: list of DBNode
        :param _NeedSupportTDE: Whether to support transparent data encryption. Valid values: 1 (yes), 0 (no). Default value: 0.
        :type NeedSupportTDE: int
        :param _KMSKeyId: KeyId of custom key, which is required if you select custom key encryption. It is also the unique CMK identifier.
        :type KMSKeyId: str
        :param _KMSRegion: The region where the KMS service is enabled. When `KMSRegion` is left empty, the KMS of the current region will be enabled by default. If the current region is not supported, you need to select another region supported by KMS.
        :type KMSRegion: str
        :param _DBEngine: Database engine. Valid values:
1. `postgresql` (TencentDB for PostgreSQL)
2. `mssql_compatible`（MSSQL compatible-TencentDB for PostgreSQL)
Default value: `postgresql`
        :type DBEngine: str
        :param _DBEngineConfig: Configuration information of database engine in the following format:
{"$key1":"$value1", "$key2":"$value2"}

Valid values:
1. mssql_compatible engine：
`migrationMode`: Database mode. Valid values: `single-db` (single-database mode), `multi-db` (multi-database mode). Default value: `single-db`.
`defaultLocale`: Default locale, which can’t be modified after the initialization. Default value: `en_US`. Valid values:
"af_ZA", "sq_AL", "ar_DZ", "ar_BH", "ar_EG", "ar_IQ", "ar_JO", "ar_KW", "ar_LB", "ar_LY", "ar_MA", "ar_OM", "ar_QA", "ar_SA", "ar_SY", "ar_TN", "ar_AE", "ar_YE", "hy_AM", "az_Cyrl_AZ", "az_Latn_AZ", "eu_ES", "be_BY", "bg_BG", "ca_ES", "zh_HK", "zh_MO", "zh_CN", "zh_SG", "zh_TW", "hr_HR", "cs_CZ", "da_DK", "nl_BE", "nl_NL", "en_AU", "en_BZ", "en_CA", "en_IE", "en_JM", "en_NZ", "en_PH", "en_ZA", "en_TT", "en_GB", "en_US", "en_ZW", "et_EE", "fo_FO", "fa_IR", "fi_FI", "fr_BE", "fr_CA", "fr_FR", "fr_LU", "fr_MC", "fr_CH", "mk_MK", "ka_GE", "de_AT", "de_DE", "de_LI", "de_LU", "de_CH", "el_GR", "gu_IN", "he_IL", "hi_IN", "hu_HU", "is_IS", "id_ID", "it_IT", "it_CH", "ja_JP", "kn_IN", "kok_IN", "ko_KR", "ky_KG", "lv_LV", "lt_LT", "ms_BN", "ms_MY", "mr_IN", "mn_MN", "nb_NO", "nn_NO", "pl_PL", "pt_BR", "pt_PT", "pa_IN", "ro_RO", "ru_RU", "sa_IN", "sr_Cyrl_RS", "sr_Latn_RS", "sk_SK", "sl_SI", "es_AR", "es_BO", "es_CL", "es_CO", "es_CR", "es_DO", "es_EC", "es_SV", "es_GT", "es_HN", "es_MX", "es_NI", "es_PA", "es_PY","es_PE", "es_PR", "es_ES", "es_TRADITIONAL", "es_UY", "es_VE", "sw_KE", "sv_FI", "sv_SE", "tt_RU", "te_IN", "th_TH", "tr_TR", "uk_UA", "ur_IN", "ur_PK", "uz_Cyrl_UZ", "uz_Latn_UZ", "vi_VN".
`serverCollationName`: Name of collation rule, which can’t be modified after the initialization. Default value: `sql_latin1_general_cp1_ci_as`. Valid values:
"bbf_unicode_general_ci_as", "bbf_unicode_cp1_ci_as", "bbf_unicode_CP1250_ci_as", "bbf_unicode_CP1251_ci_as", "bbf_unicode_cp1253_ci_as", "bbf_unicode_cp1254_ci_as", "bbf_unicode_cp1255_ci_as", "bbf_unicode_cp1256_ci_as", "bbf_unicode_cp1257_ci_as", "bbf_unicode_cp1258_ci_as", "bbf_unicode_cp874_ci_as", "sql_latin1_general_cp1250_ci_as", "sql_latin1_general_cp1251_ci_as", "sql_latin1_general_cp1_ci_as", "sql_latin1_general_cp1253_ci_as", "sql_latin1_general_cp1254_ci_as", "sql_latin1_general_cp1255_ci_as","sql_latin1_general_cp1256_ci_as", "sql_latin1_general_cp1257_ci_as", "sql_latin1_general_cp1258_ci_as", "chinese_prc_ci_as", "cyrillic_general_ci_as", "finnish_swedish_ci_as", "french_ci_as", "japanese_ci_as", "korean_wansung_ci_as", "latin1_general_ci_as", "modern_spanish_ci_as", "polish_ci_as", "thai_ci_as", "traditional_spanish_ci_as", "turkish_ci_as", "ukrainian_ci_as", "vietnamese_ci_as".
        :type DBEngineConfig: str
        """
        self._SpecCode = None
        self._Storage = None
        self._InstanceCount = None
        self._Period = None
        self._Zone = None
        self._Charset = None
        self._AdminName = None
        self._AdminPassword = None
        self._ProjectId = None
        self._DBVersion = None
        self._InstanceChargeType = None
        self._AutoVoucher = None
        self._VoucherIds = None
        self._VpcId = None
        self._SubnetId = None
        self._AutoRenewFlag = None
        self._ActivityId = None
        self._Name = None
        self._NeedSupportIpv6 = None
        self._TagList = None
        self._SecurityGroupIds = None
        self._DBMajorVersion = None
        self._DBKernelVersion = None
        self._DBNodeSet = None
        self._NeedSupportTDE = None
        self._KMSKeyId = None
        self._KMSRegion = None
        self._DBEngine = None
        self._DBEngineConfig = None

    @property
    def SpecCode(self):
        return self._SpecCode

    @SpecCode.setter
    def SpecCode(self, SpecCode):
        self._SpecCode = SpecCode

    @property
    def Storage(self):
        return self._Storage

    @Storage.setter
    def Storage(self, Storage):
        self._Storage = Storage

    @property
    def InstanceCount(self):
        return self._InstanceCount

    @InstanceCount.setter
    def InstanceCount(self, InstanceCount):
        self._InstanceCount = InstanceCount

    @property
    def Period(self):
        return self._Period

    @Period.setter
    def Period(self, Period):
        self._Period = Period

    @property
    def Zone(self):
        return self._Zone

    @Zone.setter
    def Zone(self, Zone):
        self._Zone = Zone

    @property
    def Charset(self):
        return self._Charset

    @Charset.setter
    def Charset(self, Charset):
        self._Charset = Charset

    @property
    def AdminName(self):
        return self._AdminName

    @AdminName.setter
    def AdminName(self, AdminName):
        self._AdminName = AdminName

    @property
    def AdminPassword(self):
        return self._AdminPassword

    @AdminPassword.setter
    def AdminPassword(self, AdminPassword):
        self._AdminPassword = AdminPassword

    @property
    def ProjectId(self):
        return self._ProjectId

    @ProjectId.setter
    def ProjectId(self, ProjectId):
        self._ProjectId = ProjectId

    @property
    def DBVersion(self):
        return self._DBVersion

    @DBVersion.setter
    def DBVersion(self, DBVersion):
        self._DBVersion = DBVersion

    @property
    def InstanceChargeType(self):
        return self._InstanceChargeType

    @InstanceChargeType.setter
    def InstanceChargeType(self, InstanceChargeType):
        self._InstanceChargeType = InstanceChargeType

    @property
    def AutoVoucher(self):
        return self._AutoVoucher

    @AutoVoucher.setter
    def AutoVoucher(self, AutoVoucher):
        self._AutoVoucher = AutoVoucher

    @property
    def VoucherIds(self):
        return self._VoucherIds

    @VoucherIds.setter
    def VoucherIds(self, VoucherIds):
        self._VoucherIds = VoucherIds

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def AutoRenewFlag(self):
        return self._AutoRenewFlag

    @AutoRenewFlag.setter
    def AutoRenewFlag(self, AutoRenewFlag):
        self._AutoRenewFlag = AutoRenewFlag

    @property
    def ActivityId(self):
        return self._ActivityId

    @ActivityId.setter
    def ActivityId(self, ActivityId):
        self._ActivityId = ActivityId

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, Name):
        self._Name = Name

    @property
    def NeedSupportIpv6(self):
        return self._NeedSupportIpv6

    @NeedSupportIpv6.setter
    def NeedSupportIpv6(self, NeedSupportIpv6):
        self._NeedSupportIpv6 = NeedSupportIpv6

    @property
    def TagList(self):
        return self._TagList

    @TagList.setter
    def TagList(self, TagList):
        self._TagList = TagList

    @property
    def SecurityGroupIds(self):
        return self._SecurityGroupIds

    @SecurityGroupIds.setter
    def SecurityGroupIds(self, SecurityGroupIds):
        self._SecurityGroupIds = SecurityGroupIds

    @property
    def DBMajorVersion(self):
        return self._DBMajorVersion

    @DBMajorVersion.setter
    def DBMajorVersion(self, DBMajorVersion):
        self._DBMajorVersion = DBMajorVersion

    @property
    def DBKernelVersion(self):
        return self._DBKernelVersion

    @DBKernelVersion.setter
    def DBKernelVersion(self, DBKernelVersion):
        self._DBKernelVersion = DBKernelVersion

    @property
    def DBNodeSet(self):
        return self._DBNodeSet

    @DBNodeSet.setter
    def DBNodeSet(self, DBNodeSet):
        self._DBNodeSet = DBNodeSet

    @property
    def NeedSupportTDE(self):
        return self._NeedSupportTDE

    @NeedSupportTDE.setter
    def NeedSupportTDE(self, NeedSupportTDE):
        self._NeedSupportTDE = NeedSupportTDE

    @property
    def KMSKeyId(self):
        return self._KMSKeyId

    @KMSKeyId.setter
    def KMSKeyId(self, KMSKeyId):
        self._KMSKeyId = KMSKeyId

    @property
    def KMSRegion(self):
        return self._KMSRegion

    @KMSRegion.setter
    def KMSRegion(self, KMSRegion):
        self._KMSRegion = KMSRegion

    @property
    def DBEngine(self):
        return self._DBEngine

    @DBEngine.setter
    def DBEngine(self, DBEngine):
        self._DBEngine = DBEngine

    @property
    def DBEngineConfig(self):
        return self._DBEngineConfig

    @DBEngineConfig.setter
    def DBEngineConfig(self, DBEngineConfig):
        self._DBEngineConfig = DBEngineConfig


    def _deserialize(self, params):
        self._SpecCode = params.get("SpecCode")
        self._Storage = params.get("Storage")
        self._InstanceCount = params.get("InstanceCount")
        self._Period = params.get("Period")
        self._Zone = params.get("Zone")
        self._Charset = params.get("Charset")
        self._AdminName = params.get("AdminName")
        self._AdminPassword = params.get("AdminPassword")
        self._ProjectId = params.get("ProjectId")
        self._DBVersion = params.get("DBVersion")
        self._InstanceChargeType = params.get("InstanceChargeType")
        self._AutoVoucher = params.get("AutoVoucher")
        self._VoucherIds = params.get("VoucherIds")
        self._VpcId = params.get("VpcId")
        self._SubnetId = params.get("SubnetId")
        self._AutoRenewFlag = params.get("AutoRenewFlag")
        self._ActivityId = params.get("ActivityId")
        self._Name = params.get("Name")
        self._NeedSupportIpv6 = params.get("NeedSupportIpv6")
        if params.get("TagList") is not None:
            self._TagList = []
            for item in params.get("TagList"):
                obj = Tag()
                obj._deserialize(item)
                self._TagList.append(obj)
        self._SecurityGroupIds = params.get("SecurityGroupIds")
        self._DBMajorVersion = params.get("DBMajorVersion")
        self._DBKernelVersion = params.get("DBKernelVersion")
        if params.get("DBNodeSet") is not None:
            self._DBNodeSet = []
            for item in params.get("DBNodeSet"):
                obj = DBNode()
                obj._deserialize(item)
                self._DBNodeSet.append(obj)
        self._NeedSupportTDE = params.get("NeedSupportTDE")
        self._KMSKeyId = params.get("KMSKeyId")
        self._KMSRegion = params.get("KMSRegion")
        self._DBEngine = params.get("DBEngine")
        self._DBEngineConfig = params.get("DBEngineConfig")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateInstancesResponse(AbstractModel):
    """CreateInstances response structure.

    """

    def __init__(self):
        r"""
        :param _DealNames: Order number list. Each instance corresponds to an order number.
        :type DealNames: list of str
        :param _BillId: Bill ID of frozen fees
        :type BillId: str
        :param _DBInstanceIdSet: ID set of instances which have been created successfully. The parameter value will be returned only when the pay-as-you-go billing mode is used.
        :type DBInstanceIdSet: list of str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DealNames = None
        self._BillId = None
        self._DBInstanceIdSet = None
        self._RequestId = None

    @property
    def DealNames(self):
        return self._DealNames

    @DealNames.setter
    def DealNames(self, DealNames):
        self._DealNames = DealNames

    @property
    def BillId(self):
        return self._BillId

    @BillId.setter
    def BillId(self, BillId):
        self._BillId = BillId

    @property
    def DBInstanceIdSet(self):
        return self._DBInstanceIdSet

    @DBInstanceIdSet.setter
    def DBInstanceIdSet(self, DBInstanceIdSet):
        self._DBInstanceIdSet = DBInstanceIdSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._DealNames = params.get("DealNames")
        self._BillId = params.get("BillId")
        self._DBInstanceIdSet = params.get("DBInstanceIdSet")
        self._RequestId = params.get("RequestId")


class CreateParameterTemplateRequest(AbstractModel):
    """CreateParameterTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateName: Template name, which can contain 1-60 letters, digits, and symbols (-_./()[]()+=:@).
        :type TemplateName: str
        :param _DBMajorVersion: The major database version number, such as 11, 12, 13.
        :type DBMajorVersion: str
        :param _DBEngine: Database engine, such as postgresql, mssql_compatible.
        :type DBEngine: str
        :param _TemplateDescription: Parameter template description, which can contain 1-60 letters, digits, and symbols (-_./()[]()+=:@).
        :type TemplateDescription: str
        """
        self._TemplateName = None
        self._DBMajorVersion = None
        self._DBEngine = None
        self._TemplateDescription = None

    @property
    def TemplateName(self):
        return self._TemplateName

    @TemplateName.setter
    def TemplateName(self, TemplateName):
        self._TemplateName = TemplateName

    @property
    def DBMajorVersion(self):
        return self._DBMajorVersion

    @DBMajorVersion.setter
    def DBMajorVersion(self, DBMajorVersion):
        self._DBMajorVersion = DBMajorVersion

    @property
    def DBEngine(self):
        return self._DBEngine

    @DBEngine.setter
    def DBEngine(self, DBEngine):
        self._DBEngine = DBEngine

    @property
    def TemplateDescription(self):
        return self._TemplateDescription

    @TemplateDescription.setter
    def TemplateDescription(self, TemplateDescription):
        self._TemplateDescription = TemplateDescription


    def _deserialize(self, params):
        self._TemplateName = params.get("TemplateName")
        self._DBMajorVersion = params.get("DBMajorVersion")
        self._DBEngine = params.get("DBEngine")
        self._TemplateDescription = params.get("TemplateDescription")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateParameterTemplateResponse(AbstractModel):
    """CreateParameterTemplate response structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Parameter template ID, which uniquely identifies a parameter template.
        :type TemplateId: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TemplateId = None
        self._RequestId = None

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TemplateId = params.get("TemplateId")
        self._RequestId = params.get("RequestId")


class CreateReadOnlyDBInstanceRequest(AbstractModel):
    """CreateReadOnlyDBInstance request structure.

    """

    def __init__(self):
        r"""
        :param _SpecCode: Purchasable specification ID, which can be obtained through the `SpecCode` field in the returned value of the `DescribeProductConfig` API.
        :type SpecCode: str
        :param _Storage: Instance storage capacity in GB
        :type Storage: int
        :param _InstanceCount: Number of instances purchased at a time. Value range: 1–100.
        :type InstanceCount: int
        :param _Period: Valid period in months of purchased instances. Valid values: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`, `12`, `24`, `36`. This parameter is set to `1` when the pay-as-you-go billing mode is used.
        :type Period: int
        :param _MasterDBInstanceId: ID of the primary instance to which the read-only replica belongs
        :type MasterDBInstanceId: str
        :param _Zone: Availability zone ID, which can be obtained through the `Zone` field in the returned value of the `DescribeZones` API.
        :type Zone: str
        :param _ProjectId: Project ID
        :type ProjectId: int
        :param _DBVersion: (Disused) You don’t need to specify a version, as the kernel version is as the same as that of the instance.
        :type DBVersion: str
        :param _InstanceChargeType: Instance billing mode. Valid value: `POSTPAID_BY_HOUR` (pay-as-you-go). If the source instance is pay-as-you-go, so is the read-only instance.
        :type InstanceChargeType: str
        :param _AutoVoucher: Whether to automatically use vouchers. Valid values: `1` (yes), `0` (no). Default value: `0`.
        :type AutoVoucher: int
        :param _VoucherIds: Voucher ID list. Currently, you can specify only one voucher.
        :type VoucherIds: list of str
        :param _AutoRenewFlag: Renewal flag. Valid values: `0` (manual renewal), `1` (auto-renewal). Default value: `0`.
        :type AutoRenewFlag: int
        :param _VpcId: VPC ID
        :type VpcId: str
        :param _SubnetId: VPC subnet ID
        :type SubnetId: str
        :param _ActivityId: Special offer ID
        :type ActivityId: int
        :param _Name: Instance name (which will be supported in the future)
        :type Name: str
        :param _NeedSupportIpv6: Whether to support IPv6 address access. Valid values: `1` (yes), `0` (no).
        :type NeedSupportIpv6: int
        :param _ReadOnlyGroupId: RO group ID
        :type ReadOnlyGroupId: str
        :param _TagList: The information of tags to be bound with the purchased instance, which is left empty by default (type: tag array).
        :type TagList: :class:`tencentcloud.postgres.v20170312.models.Tag`
        :param _SecurityGroupIds: Security group ID
        :type SecurityGroupIds: list of str
        """
        self._SpecCode = None
        self._Storage = None
        self._InstanceCount = None
        self._Period = None
        self._MasterDBInstanceId = None
        self._Zone = None
        self._ProjectId = None
        self._DBVersion = None
        self._InstanceChargeType = None
        self._AutoVoucher = None
        self._VoucherIds = None
        self._AutoRenewFlag = None
        self._VpcId = None
        self._SubnetId = None
        self._ActivityId = None
        self._Name = None
        self._NeedSupportIpv6 = None
        self._ReadOnlyGroupId = None
        self._TagList = None
        self._SecurityGroupIds = None

    @property
    def SpecCode(self):
        return self._SpecCode

    @SpecCode.setter
    def SpecCode(self, SpecCode):
        self._SpecCode = SpecCode

    @property
    def Storage(self):
        return self._Storage

    @Storage.setter
    def Storage(self, Storage):
        self._Storage = Storage

    @property
    def InstanceCount(self):
        return self._InstanceCount

    @InstanceCount.setter
    def InstanceCount(self, InstanceCount):
        self._InstanceCount = InstanceCount

    @property
    def Period(self):
        return self._Period

    @Period.setter
    def Period(self, Period):
        self._Period = Period

    @property
    def MasterDBInstanceId(self):
        return self._MasterDBInstanceId

    @MasterDBInstanceId.setter
    def MasterDBInstanceId(self, MasterDBInstanceId):
        self._MasterDBInstanceId = MasterDBInstanceId

    @property
    def Zone(self):
        return self._Zone

    @Zone.setter
    def Zone(self, Zone):
        self._Zone = Zone

    @property
    def ProjectId(self):
        return self._ProjectId

    @ProjectId.setter
    def ProjectId(self, ProjectId):
        self._ProjectId = ProjectId

    @property
    def DBVersion(self):
        return self._DBVersion

    @DBVersion.setter
    def DBVersion(self, DBVersion):
        self._DBVersion = DBVersion

    @property
    def InstanceChargeType(self):
        return self._InstanceChargeType

    @InstanceChargeType.setter
    def InstanceChargeType(self, InstanceChargeType):
        self._InstanceChargeType = InstanceChargeType

    @property
    def AutoVoucher(self):
        return self._AutoVoucher

    @AutoVoucher.setter
    def AutoVoucher(self, AutoVoucher):
        self._AutoVoucher = AutoVoucher

    @property
    def VoucherIds(self):
        return self._VoucherIds

    @VoucherIds.setter
    def VoucherIds(self, VoucherIds):
        self._VoucherIds = VoucherIds

    @property
    def AutoRenewFlag(self):
        return self._AutoRenewFlag

    @AutoRenewFlag.setter
    def AutoRenewFlag(self, AutoRenewFlag):
        self._AutoRenewFlag = AutoRenewFlag

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def ActivityId(self):
        return self._ActivityId

    @ActivityId.setter
    def ActivityId(self, ActivityId):
        self._ActivityId = ActivityId

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, Name):
        self._Name = Name

    @property
    def NeedSupportIpv6(self):
        return self._NeedSupportIpv6

    @NeedSupportIpv6.setter
    def NeedSupportIpv6(self, NeedSupportIpv6):
        self._NeedSupportIpv6 = NeedSupportIpv6

    @property
    def ReadOnlyGroupId(self):
        return self._ReadOnlyGroupId

    @ReadOnlyGroupId.setter
    def ReadOnlyGroupId(self, ReadOnlyGroupId):
        self._ReadOnlyGroupId = ReadOnlyGroupId

    @property
    def TagList(self):
        return self._TagList

    @TagList.setter
    def TagList(self, TagList):
        self._TagList = TagList

    @property
    def SecurityGroupIds(self):
        return self._SecurityGroupIds

    @SecurityGroupIds.setter
    def SecurityGroupIds(self, SecurityGroupIds):
        self._SecurityGroupIds = SecurityGroupIds


    def _deserialize(self, params):
        self._SpecCode = params.get("SpecCode")
        self._Storage = params.get("Storage")
        self._InstanceCount = params.get("InstanceCount")
        self._Period = params.get("Period")
        self._MasterDBInstanceId = params.get("MasterDBInstanceId")
        self._Zone = params.get("Zone")
        self._ProjectId = params.get("ProjectId")
        self._DBVersion = params.get("DBVersion")
        self._InstanceChargeType = params.get("InstanceChargeType")
        self._AutoVoucher = params.get("AutoVoucher")
        self._VoucherIds = params.get("VoucherIds")
        self._AutoRenewFlag = params.get("AutoRenewFlag")
        self._VpcId = params.get("VpcId")
        self._SubnetId = params.get("SubnetId")
        self._ActivityId = params.get("ActivityId")
        self._Name = params.get("Name")
        self._NeedSupportIpv6 = params.get("NeedSupportIpv6")
        self._ReadOnlyGroupId = params.get("ReadOnlyGroupId")
        if params.get("TagList") is not None:
            self._TagList = Tag()
            self._TagList._deserialize(params.get("TagList"))
        self._SecurityGroupIds = params.get("SecurityGroupIds")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateReadOnlyDBInstanceResponse(AbstractModel):
    """CreateReadOnlyDBInstance response structure.

    """

    def __init__(self):
        r"""
        :param _DealNames: Order number list. Each instance corresponds to an order number.
        :type DealNames: list of str
        :param _BillId: Bill ID of frozen fees
        :type BillId: str
        :param _DBInstanceIdSet: ID set of instances which have been created successfully. The parameter value will be returned only when the pay-as-you-go billing mode is used.
        :type DBInstanceIdSet: list of str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DealNames = None
        self._BillId = None
        self._DBInstanceIdSet = None
        self._RequestId = None

    @property
    def DealNames(self):
        return self._DealNames

    @DealNames.setter
    def DealNames(self, DealNames):
        self._DealNames = DealNames

    @property
    def BillId(self):
        return self._BillId

    @BillId.setter
    def BillId(self, BillId):
        self._BillId = BillId

    @property
    def DBInstanceIdSet(self):
        return self._DBInstanceIdSet

    @DBInstanceIdSet.setter
    def DBInstanceIdSet(self, DBInstanceIdSet):
        self._DBInstanceIdSet = DBInstanceIdSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._DealNames = params.get("DealNames")
        self._BillId = params.get("BillId")
        self._DBInstanceIdSet = params.get("DBInstanceIdSet")
        self._RequestId = params.get("RequestId")


class CreateReadOnlyGroupNetworkAccessRequest(AbstractModel):
    """CreateReadOnlyGroupNetworkAccess request structure.

    """

    def __init__(self):
        r"""
        :param _ReadOnlyGroupId: RO group ID in the format of pgro-4t9c6g7k.
        :type ReadOnlyGroupId: str
        :param _VpcId: Unified VPC ID.
        :type VpcId: str
        :param _SubnetId: Subnet ID.
        :type SubnetId: str
        :param _IsAssignVip: Whether to manually assign the VIP. Valid values: `true` (manually assign), `false` (automatically assign).
        :type IsAssignVip: bool
        :param _Vip: Target VIP.
        :type Vip: str
        """
        self._ReadOnlyGroupId = None
        self._VpcId = None
        self._SubnetId = None
        self._IsAssignVip = None
        self._Vip = None

    @property
    def ReadOnlyGroupId(self):
        return self._ReadOnlyGroupId

    @ReadOnlyGroupId.setter
    def ReadOnlyGroupId(self, ReadOnlyGroupId):
        self._ReadOnlyGroupId = ReadOnlyGroupId

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def IsAssignVip(self):
        return self._IsAssignVip

    @IsAssignVip.setter
    def IsAssignVip(self, IsAssignVip):
        self._IsAssignVip = IsAssignVip

    @property
    def Vip(self):
        return self._Vip

    @Vip.setter
    def Vip(self, Vip):
        self._Vip = Vip


    def _deserialize(self, params):
        self._ReadOnlyGroupId = params.get("ReadOnlyGroupId")
        self._VpcId = params.get("VpcId")
        self._SubnetId = params.get("SubnetId")
        self._IsAssignVip = params.get("IsAssignVip")
        self._Vip = params.get("Vip")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateReadOnlyGroupNetworkAccessResponse(AbstractModel):
    """CreateReadOnlyGroupNetworkAccess response structure.

    """

    def __init__(self):
        r"""
        :param _FlowId: Task ID.
Note: This field may return `null`, indicating that no valid values can be obtained.
        :type FlowId: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._FlowId = None
        self._RequestId = None

    @property
    def FlowId(self):
        return self._FlowId

    @FlowId.setter
    def FlowId(self, FlowId):
        self._FlowId = FlowId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._FlowId = params.get("FlowId")
        self._RequestId = params.get("RequestId")


class CreateReadOnlyGroupRequest(AbstractModel):
    """CreateReadOnlyGroup request structure.

    """

    def __init__(self):
        r"""
        :param _MasterDBInstanceId: Primary instance ID
        :type MasterDBInstanceId: str
        :param _Name: RO group name
        :type Name: str
        :param _ProjectId: Project ID
        :type ProjectId: int
        :param _VpcId: VPC ID
        :type VpcId: str
        :param _SubnetId: Subnet ID
        :type SubnetId: str
        :param _ReplayLagEliminate: Whether to remove a read-only replica from an RO group if the delay between the read-only replica and the primary instance exceeds the threshold. Valid values: `0` (no), `1` (yes).
        :type ReplayLagEliminate: int
        :param _ReplayLatencyEliminate: Whether to remove a read-only replica from an RO group if the sync log size difference between the read-only replica and the primary instance exceeds the threshold. Valid values: `0` (no), `1` (yes).
        :type ReplayLatencyEliminate: int
        :param _MaxReplayLag: Delay threshold in ms
        :type MaxReplayLag: int
        :param _MaxReplayLatency: Delayed log size threshold in MB
        :type MaxReplayLatency: int
        :param _MinDelayEliminateReserve: The minimum number of read-only replicas that must be retained in an RO group
        :type MinDelayEliminateReserve: int
        :param _SecurityGroupIds: Security group ID
        :type SecurityGroupIds: list of str
        """
        self._MasterDBInstanceId = None
        self._Name = None
        self._ProjectId = None
        self._VpcId = None
        self._SubnetId = None
        self._ReplayLagEliminate = None
        self._ReplayLatencyEliminate = None
        self._MaxReplayLag = None
        self._MaxReplayLatency = None
        self._MinDelayEliminateReserve = None
        self._SecurityGroupIds = None

    @property
    def MasterDBInstanceId(self):
        return self._MasterDBInstanceId

    @MasterDBInstanceId.setter
    def MasterDBInstanceId(self, MasterDBInstanceId):
        self._MasterDBInstanceId = MasterDBInstanceId

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, Name):
        self._Name = Name

    @property
    def ProjectId(self):
        return self._ProjectId

    @ProjectId.setter
    def ProjectId(self, ProjectId):
        self._ProjectId = ProjectId

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def ReplayLagEliminate(self):
        return self._ReplayLagEliminate

    @ReplayLagEliminate.setter
    def ReplayLagEliminate(self, ReplayLagEliminate):
        self._ReplayLagEliminate = ReplayLagEliminate

    @property
    def ReplayLatencyEliminate(self):
        return self._ReplayLatencyEliminate

    @ReplayLatencyEliminate.setter
    def ReplayLatencyEliminate(self, ReplayLatencyEliminate):
        self._ReplayLatencyEliminate = ReplayLatencyEliminate

    @property
    def MaxReplayLag(self):
        return self._MaxReplayLag

    @MaxReplayLag.setter
    def MaxReplayLag(self, MaxReplayLag):
        self._MaxReplayLag = MaxReplayLag

    @property
    def MaxReplayLatency(self):
        return self._MaxReplayLatency

    @MaxReplayLatency.setter
    def MaxReplayLatency(self, MaxReplayLatency):
        self._MaxReplayLatency = MaxReplayLatency

    @property
    def MinDelayEliminateReserve(self):
        return self._MinDelayEliminateReserve

    @MinDelayEliminateReserve.setter
    def MinDelayEliminateReserve(self, MinDelayEliminateReserve):
        self._MinDelayEliminateReserve = MinDelayEliminateReserve

    @property
    def SecurityGroupIds(self):
        return self._SecurityGroupIds

    @SecurityGroupIds.setter
    def SecurityGroupIds(self, SecurityGroupIds):
        self._SecurityGroupIds = SecurityGroupIds


    def _deserialize(self, params):
        self._MasterDBInstanceId = params.get("MasterDBInstanceId")
        self._Name = params.get("Name")
        self._ProjectId = params.get("ProjectId")
        self._VpcId = params.get("VpcId")
        self._SubnetId = params.get("SubnetId")
        self._ReplayLagEliminate = params.get("ReplayLagEliminate")
        self._ReplayLatencyEliminate = params.get("ReplayLatencyEliminate")
        self._MaxReplayLag = params.get("MaxReplayLag")
        self._MaxReplayLatency = params.get("MaxReplayLatency")
        self._MinDelayEliminateReserve = params.get("MinDelayEliminateReserve")
        self._SecurityGroupIds = params.get("SecurityGroupIds")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateReadOnlyGroupResponse(AbstractModel):
    """CreateReadOnlyGroup response structure.

    """

    def __init__(self):
        r"""
        :param _ReadOnlyGroupId: RO group ID
        :type ReadOnlyGroupId: str
        :param _FlowId: Task ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type FlowId: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._ReadOnlyGroupId = None
        self._FlowId = None
        self._RequestId = None

    @property
    def ReadOnlyGroupId(self):
        return self._ReadOnlyGroupId

    @ReadOnlyGroupId.setter
    def ReadOnlyGroupId(self, ReadOnlyGroupId):
        self._ReadOnlyGroupId = ReadOnlyGroupId

    @property
    def FlowId(self):
        return self._FlowId

    @FlowId.setter
    def FlowId(self, FlowId):
        self._FlowId = FlowId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._ReadOnlyGroupId = params.get("ReadOnlyGroupId")
        self._FlowId = params.get("FlowId")
        self._RequestId = params.get("RequestId")


class CreateServerlessDBInstanceRequest(AbstractModel):
    """CreateServerlessDBInstance request structure.

    """

    def __init__(self):
        r"""
        :param _Zone: Availability zone ID. Only ap-shanghai-2, ap-beijing-1, and ap-guangzhou-2 are supported during the beta test.
        :type Zone: str
        :param _DBInstanceName: Instance name. The value must be unique for the same account.
        :type DBInstanceName: str
        :param _DBVersion: Kernel version of a PostgreSQL instance. Currently, only 10.4 is supported.
        :type DBVersion: str
        :param _DBCharset: Database character set of a PostgreSQL instance. Currently, only UTF-8 is supported.
        :type DBCharset: str
        :param _ProjectId: Project ID.
        :type ProjectId: int
        :param _VpcId: VPC ID.
        :type VpcId: str
        :param _SubnetId: VPC subnet ID.
        :type SubnetId: str
        :param _TagList: Array of tags to be bound with the instance
        :type TagList: list of Tag
        """
        self._Zone = None
        self._DBInstanceName = None
        self._DBVersion = None
        self._DBCharset = None
        self._ProjectId = None
        self._VpcId = None
        self._SubnetId = None
        self._TagList = None

    @property
    def Zone(self):
        return self._Zone

    @Zone.setter
    def Zone(self, Zone):
        self._Zone = Zone

    @property
    def DBInstanceName(self):
        return self._DBInstanceName

    @DBInstanceName.setter
    def DBInstanceName(self, DBInstanceName):
        self._DBInstanceName = DBInstanceName

    @property
    def DBVersion(self):
        return self._DBVersion

    @DBVersion.setter
    def DBVersion(self, DBVersion):
        self._DBVersion = DBVersion

    @property
    def DBCharset(self):
        return self._DBCharset

    @DBCharset.setter
    def DBCharset(self, DBCharset):
        self._DBCharset = DBCharset

    @property
    def ProjectId(self):
        return self._ProjectId

    @ProjectId.setter
    def ProjectId(self, ProjectId):
        self._ProjectId = ProjectId

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def TagList(self):
        return self._TagList

    @TagList.setter
    def TagList(self, TagList):
        self._TagList = TagList


    def _deserialize(self, params):
        self._Zone = params.get("Zone")
        self._DBInstanceName = params.get("DBInstanceName")
        self._DBVersion = params.get("DBVersion")
        self._DBCharset = params.get("DBCharset")
        self._ProjectId = params.get("ProjectId")
        self._VpcId = params.get("VpcId")
        self._SubnetId = params.get("SubnetId")
        if params.get("TagList") is not None:
            self._TagList = []
            for item in params.get("TagList"):
                obj = Tag()
                obj._deserialize(item)
                self._TagList.append(obj)
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateServerlessDBInstanceResponse(AbstractModel):
    """CreateServerlessDBInstance response structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID, such as "postgres-xxxxx". The value must be globally unique.
        :type DBInstanceId: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DBInstanceId = None
        self._RequestId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._RequestId = params.get("RequestId")


class DBBackup(AbstractModel):
    """Database backup information

    """

    def __init__(self):
        r"""
        :param _Id: Unique backup file ID
        :type Id: int
        :param _StartTime: File generation start time
        :type StartTime: str
        :param _EndTime: File generation end time
        :type EndTime: str
        :param _Size: File size in KB
        :type Size: int
        :param _Strategy: Policy (0: instance backup, 1: multi-database backup)
        :type Strategy: int
        :param _Way: Type (0: scheduled)
        :type Way: int
        :param _Type: Backup mode (1: full)
        :type Type: int
        :param _Status: Status (1: creating, 2: success, 3: failure)
        :type Status: int
        :param _DbList: DB list
        :type DbList: list of str
        :param _InternalAddr: Download address on private network
        :type InternalAddr: str
        :param _ExternalAddr: Download address on public network
        :type ExternalAddr: str
        :param _SetId: Backup set ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type SetId: str
        """
        self._Id = None
        self._StartTime = None
        self._EndTime = None
        self._Size = None
        self._Strategy = None
        self._Way = None
        self._Type = None
        self._Status = None
        self._DbList = None
        self._InternalAddr = None
        self._ExternalAddr = None
        self._SetId = None

    @property
    def Id(self):
        return self._Id

    @Id.setter
    def Id(self, Id):
        self._Id = Id

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
    def Size(self):
        return self._Size

    @Size.setter
    def Size(self, Size):
        self._Size = Size

    @property
    def Strategy(self):
        return self._Strategy

    @Strategy.setter
    def Strategy(self, Strategy):
        self._Strategy = Strategy

    @property
    def Way(self):
        return self._Way

    @Way.setter
    def Way(self, Way):
        self._Way = Way

    @property
    def Type(self):
        return self._Type

    @Type.setter
    def Type(self, Type):
        self._Type = Type

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status

    @property
    def DbList(self):
        return self._DbList

    @DbList.setter
    def DbList(self, DbList):
        self._DbList = DbList

    @property
    def InternalAddr(self):
        return self._InternalAddr

    @InternalAddr.setter
    def InternalAddr(self, InternalAddr):
        self._InternalAddr = InternalAddr

    @property
    def ExternalAddr(self):
        return self._ExternalAddr

    @ExternalAddr.setter
    def ExternalAddr(self, ExternalAddr):
        self._ExternalAddr = ExternalAddr

    @property
    def SetId(self):
        return self._SetId

    @SetId.setter
    def SetId(self, SetId):
        self._SetId = SetId


    def _deserialize(self, params):
        self._Id = params.get("Id")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._Size = params.get("Size")
        self._Strategy = params.get("Strategy")
        self._Way = params.get("Way")
        self._Type = params.get("Type")
        self._Status = params.get("Status")
        self._DbList = params.get("DbList")
        self._InternalAddr = params.get("InternalAddr")
        self._ExternalAddr = params.get("ExternalAddr")
        self._SetId = params.get("SetId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DBInstance(AbstractModel):
    """Instance details

    """

    def __init__(self):
        r"""
        :param _Region: Instance region such as ap-guangzhou, which corresponds to the `Region` field of `RegionSet`
        :type Region: str
        :param _Zone: Instance AZ such as ap-guangzhou-3, which corresponds to the `Zone` field of `ZoneSet`
        :type Zone: str
        :param _ProjectId: Project ID
        :type ProjectId: int
        :param _VpcId: VPC ID
        :type VpcId: str
        :param _SubnetId: SubnetId
        :type SubnetId: str
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _DBInstanceName: Instance name
        :type DBInstanceName: str
        :param _DBInstanceStatus: Instance status.  Valid values: `applying`, `init` (to be initialized), `initing` (initializing), `running`, `limited run`, `isolating`, `isolated`, `recycling`, `recycled`, `job running`, `offline`, `migrating`, `expanding`, `waitSwitch` (waiting for switch), `switching`, `readonly`, `restarting`, `network changing`, `upgrading` (upgrading kernel version).
        :type DBInstanceStatus: str
        :param _DBInstanceMemory: Assigned instance memory size in GB
        :type DBInstanceMemory: int
        :param _DBInstanceStorage: Assigned instance storage capacity in GB
        :type DBInstanceStorage: int
        :param _DBInstanceCpu: Number of assigned CPUs
        :type DBInstanceCpu: int
        :param _DBInstanceClass: Purchasable specification ID
        :type DBInstanceClass: str
        :param _DBInstanceType: Instance type. 1: primary (master instance), 2: readonly (read-only instance), 3: guard (disaster recovery instance), 4: temp (temp instance)
        :type DBInstanceType: str
        :param _DBInstanceVersion: Instance edition. Currently, only `standard` edition (dual-server high-availability one-master-one-slave edition) is supported
        :type DBInstanceVersion: str
        :param _DBCharset: Instance database character set
        :type DBCharset: str
        :param _DBVersion: PostgreSQL version number
        :type DBVersion: str
        :param _CreateTime: Instance creation time
        :type CreateTime: str
        :param _UpdateTime: Instance last modified time
        :type UpdateTime: str
        :param _ExpireTime: Instance expiration time
        :type ExpireTime: str
        :param _IsolatedTime: Instance isolation time
        :type IsolatedTime: str
        :param _PayType: Billing mode. postpaid: pay-as-you-go
        :type PayType: str
        :param _AutoRenew: Whether to renew automatically. 1: yes, 0: no
        :type AutoRenew: int
        :param _DBInstanceNetInfo: Instance network connection information
        :type DBInstanceNetInfo: list of DBInstanceNetInfo
        :param _Type: Machine type
        :type Type: str
        :param _AppId: User `AppId`
        :type AppId: int
        :param _Uid: Instance `Uid`
        :type Uid: int
        :param _SupportIpv6: Whether the instance supports IPv6 address access. Valid values: 1 (yes), 0 (no)
        :type SupportIpv6: int
        :param _TagList: The information of tags associated with instances.
Note: this field may return null, indicating that no valid values can be obtained.
        :type TagList: list of Tag
        :param _MasterDBInstanceId: Primary instance information, which is returned only when the instance is read-only
Note: this field may return null, indicating that no valid values can be obtained.
        :type MasterDBInstanceId: str
        :param _ReadOnlyInstanceNum: Number of read-only instances
Note: this field may return null, indicating that no valid values can be obtained.
        :type ReadOnlyInstanceNum: int
        :param _StatusInReadonlyGroup: The status of a instance in a read-only group
Note: this field may return null, indicating that no valid values can be obtained.
        :type StatusInReadonlyGroup: str
        :param _OfflineTime: Elimination time
Note: this field may return null, indicating that no valid values can be obtained.
        :type OfflineTime: str
        :param _DBKernelVersion: Database kernel version
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBKernelVersion: str
        :param _NetworkAccessList: Network access list of the instance (this field has been deprecated)
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type NetworkAccessList: list of NetworkAccess
        :param _DBMajorVersion: PostgreSQL major version number
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBMajorVersion: str
        :param _DBNodeSet: Instance node information
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBNodeSet: list of DBNode
        :param _IsSupportTDE: Whether the instance supports TDE data encryption. Valid values: 0 (no), 1 (yes)
Note: This field may return `null`, indicating that no valid values can be obtained.
        :type IsSupportTDE: int
        :param _DBEngine: 
        :type DBEngine: str
        :param _DBEngineConfig: Configuration information of database engine
Note: This field may return null, indicating that no valid values can be obtained.
        :type DBEngineConfig: str
        """
        self._Region = None
        self._Zone = None
        self._ProjectId = None
        self._VpcId = None
        self._SubnetId = None
        self._DBInstanceId = None
        self._DBInstanceName = None
        self._DBInstanceStatus = None
        self._DBInstanceMemory = None
        self._DBInstanceStorage = None
        self._DBInstanceCpu = None
        self._DBInstanceClass = None
        self._DBInstanceType = None
        self._DBInstanceVersion = None
        self._DBCharset = None
        self._DBVersion = None
        self._CreateTime = None
        self._UpdateTime = None
        self._ExpireTime = None
        self._IsolatedTime = None
        self._PayType = None
        self._AutoRenew = None
        self._DBInstanceNetInfo = None
        self._Type = None
        self._AppId = None
        self._Uid = None
        self._SupportIpv6 = None
        self._TagList = None
        self._MasterDBInstanceId = None
        self._ReadOnlyInstanceNum = None
        self._StatusInReadonlyGroup = None
        self._OfflineTime = None
        self._DBKernelVersion = None
        self._NetworkAccessList = None
        self._DBMajorVersion = None
        self._DBNodeSet = None
        self._IsSupportTDE = None
        self._DBEngine = None
        self._DBEngineConfig = None

    @property
    def Region(self):
        return self._Region

    @Region.setter
    def Region(self, Region):
        self._Region = Region

    @property
    def Zone(self):
        return self._Zone

    @Zone.setter
    def Zone(self, Zone):
        self._Zone = Zone

    @property
    def ProjectId(self):
        return self._ProjectId

    @ProjectId.setter
    def ProjectId(self, ProjectId):
        self._ProjectId = ProjectId

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def DBInstanceName(self):
        return self._DBInstanceName

    @DBInstanceName.setter
    def DBInstanceName(self, DBInstanceName):
        self._DBInstanceName = DBInstanceName

    @property
    def DBInstanceStatus(self):
        return self._DBInstanceStatus

    @DBInstanceStatus.setter
    def DBInstanceStatus(self, DBInstanceStatus):
        self._DBInstanceStatus = DBInstanceStatus

    @property
    def DBInstanceMemory(self):
        return self._DBInstanceMemory

    @DBInstanceMemory.setter
    def DBInstanceMemory(self, DBInstanceMemory):
        self._DBInstanceMemory = DBInstanceMemory

    @property
    def DBInstanceStorage(self):
        return self._DBInstanceStorage

    @DBInstanceStorage.setter
    def DBInstanceStorage(self, DBInstanceStorage):
        self._DBInstanceStorage = DBInstanceStorage

    @property
    def DBInstanceCpu(self):
        return self._DBInstanceCpu

    @DBInstanceCpu.setter
    def DBInstanceCpu(self, DBInstanceCpu):
        self._DBInstanceCpu = DBInstanceCpu

    @property
    def DBInstanceClass(self):
        return self._DBInstanceClass

    @DBInstanceClass.setter
    def DBInstanceClass(self, DBInstanceClass):
        self._DBInstanceClass = DBInstanceClass

    @property
    def DBInstanceType(self):
        return self._DBInstanceType

    @DBInstanceType.setter
    def DBInstanceType(self, DBInstanceType):
        self._DBInstanceType = DBInstanceType

    @property
    def DBInstanceVersion(self):
        return self._DBInstanceVersion

    @DBInstanceVersion.setter
    def DBInstanceVersion(self, DBInstanceVersion):
        self._DBInstanceVersion = DBInstanceVersion

    @property
    def DBCharset(self):
        return self._DBCharset

    @DBCharset.setter
    def DBCharset(self, DBCharset):
        self._DBCharset = DBCharset

    @property
    def DBVersion(self):
        return self._DBVersion

    @DBVersion.setter
    def DBVersion(self, DBVersion):
        self._DBVersion = DBVersion

    @property
    def CreateTime(self):
        return self._CreateTime

    @CreateTime.setter
    def CreateTime(self, CreateTime):
        self._CreateTime = CreateTime

    @property
    def UpdateTime(self):
        return self._UpdateTime

    @UpdateTime.setter
    def UpdateTime(self, UpdateTime):
        self._UpdateTime = UpdateTime

    @property
    def ExpireTime(self):
        return self._ExpireTime

    @ExpireTime.setter
    def ExpireTime(self, ExpireTime):
        self._ExpireTime = ExpireTime

    @property
    def IsolatedTime(self):
        return self._IsolatedTime

    @IsolatedTime.setter
    def IsolatedTime(self, IsolatedTime):
        self._IsolatedTime = IsolatedTime

    @property
    def PayType(self):
        return self._PayType

    @PayType.setter
    def PayType(self, PayType):
        self._PayType = PayType

    @property
    def AutoRenew(self):
        return self._AutoRenew

    @AutoRenew.setter
    def AutoRenew(self, AutoRenew):
        self._AutoRenew = AutoRenew

    @property
    def DBInstanceNetInfo(self):
        return self._DBInstanceNetInfo

    @DBInstanceNetInfo.setter
    def DBInstanceNetInfo(self, DBInstanceNetInfo):
        self._DBInstanceNetInfo = DBInstanceNetInfo

    @property
    def Type(self):
        return self._Type

    @Type.setter
    def Type(self, Type):
        self._Type = Type

    @property
    def AppId(self):
        return self._AppId

    @AppId.setter
    def AppId(self, AppId):
        self._AppId = AppId

    @property
    def Uid(self):
        return self._Uid

    @Uid.setter
    def Uid(self, Uid):
        self._Uid = Uid

    @property
    def SupportIpv6(self):
        return self._SupportIpv6

    @SupportIpv6.setter
    def SupportIpv6(self, SupportIpv6):
        self._SupportIpv6 = SupportIpv6

    @property
    def TagList(self):
        return self._TagList

    @TagList.setter
    def TagList(self, TagList):
        self._TagList = TagList

    @property
    def MasterDBInstanceId(self):
        return self._MasterDBInstanceId

    @MasterDBInstanceId.setter
    def MasterDBInstanceId(self, MasterDBInstanceId):
        self._MasterDBInstanceId = MasterDBInstanceId

    @property
    def ReadOnlyInstanceNum(self):
        return self._ReadOnlyInstanceNum

    @ReadOnlyInstanceNum.setter
    def ReadOnlyInstanceNum(self, ReadOnlyInstanceNum):
        self._ReadOnlyInstanceNum = ReadOnlyInstanceNum

    @property
    def StatusInReadonlyGroup(self):
        return self._StatusInReadonlyGroup

    @StatusInReadonlyGroup.setter
    def StatusInReadonlyGroup(self, StatusInReadonlyGroup):
        self._StatusInReadonlyGroup = StatusInReadonlyGroup

    @property
    def OfflineTime(self):
        return self._OfflineTime

    @OfflineTime.setter
    def OfflineTime(self, OfflineTime):
        self._OfflineTime = OfflineTime

    @property
    def DBKernelVersion(self):
        return self._DBKernelVersion

    @DBKernelVersion.setter
    def DBKernelVersion(self, DBKernelVersion):
        self._DBKernelVersion = DBKernelVersion

    @property
    def NetworkAccessList(self):
        return self._NetworkAccessList

    @NetworkAccessList.setter
    def NetworkAccessList(self, NetworkAccessList):
        self._NetworkAccessList = NetworkAccessList

    @property
    def DBMajorVersion(self):
        return self._DBMajorVersion

    @DBMajorVersion.setter
    def DBMajorVersion(self, DBMajorVersion):
        self._DBMajorVersion = DBMajorVersion

    @property
    def DBNodeSet(self):
        return self._DBNodeSet

    @DBNodeSet.setter
    def DBNodeSet(self, DBNodeSet):
        self._DBNodeSet = DBNodeSet

    @property
    def IsSupportTDE(self):
        return self._IsSupportTDE

    @IsSupportTDE.setter
    def IsSupportTDE(self, IsSupportTDE):
        self._IsSupportTDE = IsSupportTDE

    @property
    def DBEngine(self):
        return self._DBEngine

    @DBEngine.setter
    def DBEngine(self, DBEngine):
        self._DBEngine = DBEngine

    @property
    def DBEngineConfig(self):
        return self._DBEngineConfig

    @DBEngineConfig.setter
    def DBEngineConfig(self, DBEngineConfig):
        self._DBEngineConfig = DBEngineConfig


    def _deserialize(self, params):
        self._Region = params.get("Region")
        self._Zone = params.get("Zone")
        self._ProjectId = params.get("ProjectId")
        self._VpcId = params.get("VpcId")
        self._SubnetId = params.get("SubnetId")
        self._DBInstanceId = params.get("DBInstanceId")
        self._DBInstanceName = params.get("DBInstanceName")
        self._DBInstanceStatus = params.get("DBInstanceStatus")
        self._DBInstanceMemory = params.get("DBInstanceMemory")
        self._DBInstanceStorage = params.get("DBInstanceStorage")
        self._DBInstanceCpu = params.get("DBInstanceCpu")
        self._DBInstanceClass = params.get("DBInstanceClass")
        self._DBInstanceType = params.get("DBInstanceType")
        self._DBInstanceVersion = params.get("DBInstanceVersion")
        self._DBCharset = params.get("DBCharset")
        self._DBVersion = params.get("DBVersion")
        self._CreateTime = params.get("CreateTime")
        self._UpdateTime = params.get("UpdateTime")
        self._ExpireTime = params.get("ExpireTime")
        self._IsolatedTime = params.get("IsolatedTime")
        self._PayType = params.get("PayType")
        self._AutoRenew = params.get("AutoRenew")
        if params.get("DBInstanceNetInfo") is not None:
            self._DBInstanceNetInfo = []
            for item in params.get("DBInstanceNetInfo"):
                obj = DBInstanceNetInfo()
                obj._deserialize(item)
                self._DBInstanceNetInfo.append(obj)
        self._Type = params.get("Type")
        self._AppId = params.get("AppId")
        self._Uid = params.get("Uid")
        self._SupportIpv6 = params.get("SupportIpv6")
        if params.get("TagList") is not None:
            self._TagList = []
            for item in params.get("TagList"):
                obj = Tag()
                obj._deserialize(item)
                self._TagList.append(obj)
        self._MasterDBInstanceId = params.get("MasterDBInstanceId")
        self._ReadOnlyInstanceNum = params.get("ReadOnlyInstanceNum")
        self._StatusInReadonlyGroup = params.get("StatusInReadonlyGroup")
        self._OfflineTime = params.get("OfflineTime")
        self._DBKernelVersion = params.get("DBKernelVersion")
        if params.get("NetworkAccessList") is not None:
            self._NetworkAccessList = []
            for item in params.get("NetworkAccessList"):
                obj = NetworkAccess()
                obj._deserialize(item)
                self._NetworkAccessList.append(obj)
        self._DBMajorVersion = params.get("DBMajorVersion")
        if params.get("DBNodeSet") is not None:
            self._DBNodeSet = []
            for item in params.get("DBNodeSet"):
                obj = DBNode()
                obj._deserialize(item)
                self._DBNodeSet.append(obj)
        self._IsSupportTDE = params.get("IsSupportTDE")
        self._DBEngine = params.get("DBEngine")
        self._DBEngineConfig = params.get("DBEngineConfig")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DBInstanceNetInfo(AbstractModel):
    """Instance network connection information

    """

    def __init__(self):
        r"""
        :param _Address: DNS domain name
        :type Address: str
        :param _Ip: Ip
        :type Ip: str
        :param _Port: Connection port address
        :type Port: int
        :param _NetType: Network type. 1: inner (private network address), 2: public (public network address)
        :type NetType: str
        :param _Status: Network connection status. Valid values: `initing` (never enabled before), `opened` (enabled), `closed` (disabled), `opening` (enabling), `closing` (disabling)
        :type Status: str
        :param _VpcId: VPC ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type VpcId: str
        :param _SubnetId: Subnet ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type SubnetId: str
        :param _ProtocolType: Database connection protocol type. Valid values: `postgresql`, `mssql` (MSSQL-compatible)
Note: This field may return null, indicating that no valid values can be obtained.
        :type ProtocolType: str
        """
        self._Address = None
        self._Ip = None
        self._Port = None
        self._NetType = None
        self._Status = None
        self._VpcId = None
        self._SubnetId = None
        self._ProtocolType = None

    @property
    def Address(self):
        return self._Address

    @Address.setter
    def Address(self, Address):
        self._Address = Address

    @property
    def Ip(self):
        return self._Ip

    @Ip.setter
    def Ip(self, Ip):
        self._Ip = Ip

    @property
    def Port(self):
        return self._Port

    @Port.setter
    def Port(self, Port):
        self._Port = Port

    @property
    def NetType(self):
        return self._NetType

    @NetType.setter
    def NetType(self, NetType):
        self._NetType = NetType

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def ProtocolType(self):
        return self._ProtocolType

    @ProtocolType.setter
    def ProtocolType(self, ProtocolType):
        self._ProtocolType = ProtocolType


    def _deserialize(self, params):
        self._Address = params.get("Address")
        self._Ip = params.get("Ip")
        self._Port = params.get("Port")
        self._NetType = params.get("NetType")
        self._Status = params.get("Status")
        self._VpcId = params.get("VpcId")
        self._SubnetId = params.get("SubnetId")
        self._ProtocolType = params.get("ProtocolType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DBNode(AbstractModel):
    """Instance node information including node type and AZ.

    """

    def __init__(self):
        r"""
        :param _Role: Node type. Valid values:
`Primary`;
`Standby`.
        :type Role: str
        :param _Zone: AZ where the node resides, such as ap-guangzhou-1.
        :type Zone: str
        """
        self._Role = None
        self._Zone = None

    @property
    def Role(self):
        return self._Role

    @Role.setter
    def Role(self, Role):
        self._Role = Role

    @property
    def Zone(self):
        return self._Zone

    @Zone.setter
    def Zone(self, Zone):
        self._Zone = Zone


    def _deserialize(self, params):
        self._Role = params.get("Role")
        self._Zone = params.get("Zone")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteBaseBackupRequest(AbstractModel):
    """DeleteBaseBackup request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _BaseBackupId: Base backup ID
        :type BaseBackupId: str
        """
        self._DBInstanceId = None
        self._BaseBackupId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def BaseBackupId(self):
        return self._BaseBackupId

    @BaseBackupId.setter
    def BaseBackupId(self, BaseBackupId):
        self._BaseBackupId = BaseBackupId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._BaseBackupId = params.get("BaseBackupId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteBaseBackupResponse(AbstractModel):
    """DeleteBaseBackup response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class DeleteDBInstanceNetworkAccessRequest(AbstractModel):
    """DeleteDBInstanceNetworkAccess request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of postgres-6bwgamo3.
        :type DBInstanceId: str
        :param _VpcId: Unified VPC ID. If you want to delete the classic network, set the parameter to `0`.
        :type VpcId: str
        :param _SubnetId: Subnet ID. If you want to delete the classic network, set the parameter to `0`.
        :type SubnetId: str
        :param _Vip: Target VIP.
        :type Vip: str
        """
        self._DBInstanceId = None
        self._VpcId = None
        self._SubnetId = None
        self._Vip = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def Vip(self):
        return self._Vip

    @Vip.setter
    def Vip(self, Vip):
        self._Vip = Vip


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._VpcId = params.get("VpcId")
        self._SubnetId = params.get("SubnetId")
        self._Vip = params.get("Vip")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteDBInstanceNetworkAccessResponse(AbstractModel):
    """DeleteDBInstanceNetworkAccess response structure.

    """

    def __init__(self):
        r"""
        :param _FlowId: Task ID.
Note: This field may return `null`, indicating that no valid values can be obtained.
        :type FlowId: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._FlowId = None
        self._RequestId = None

    @property
    def FlowId(self):
        return self._FlowId

    @FlowId.setter
    def FlowId(self, FlowId):
        self._FlowId = FlowId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._FlowId = params.get("FlowId")
        self._RequestId = params.get("RequestId")


class DeleteLogBackupRequest(AbstractModel):
    """DeleteLogBackup request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _LogBackupId: Log backup ID
        :type LogBackupId: str
        """
        self._DBInstanceId = None
        self._LogBackupId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def LogBackupId(self):
        return self._LogBackupId

    @LogBackupId.setter
    def LogBackupId(self, LogBackupId):
        self._LogBackupId = LogBackupId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._LogBackupId = params.get("LogBackupId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteLogBackupResponse(AbstractModel):
    """DeleteLogBackup response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class DeleteParameterTemplateRequest(AbstractModel):
    """DeleteParameterTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Parameter template ID, which uniquely identifies the parameter template to be operated.
        :type TemplateId: str
        """
        self._TemplateId = None

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId


    def _deserialize(self, params):
        self._TemplateId = params.get("TemplateId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteParameterTemplateResponse(AbstractModel):
    """DeleteParameterTemplate response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class DeleteReadOnlyGroupNetworkAccessRequest(AbstractModel):
    """DeleteReadOnlyGroupNetworkAccess request structure.

    """

    def __init__(self):
        r"""
        :param _ReadOnlyGroupId: RO group ID in the format of pgro-4t9c6g7k.
        :type ReadOnlyGroupId: str
        :param _VpcId: Unified VPC ID. If you want to delete the classic network, set the parameter to `0`.
        :type VpcId: str
        :param _SubnetId: Subnet ID. If you want to delete the classic network, set the parameter to `0`.
        :type SubnetId: str
        :param _Vip: Target VIP.
        :type Vip: str
        """
        self._ReadOnlyGroupId = None
        self._VpcId = None
        self._SubnetId = None
        self._Vip = None

    @property
    def ReadOnlyGroupId(self):
        return self._ReadOnlyGroupId

    @ReadOnlyGroupId.setter
    def ReadOnlyGroupId(self, ReadOnlyGroupId):
        self._ReadOnlyGroupId = ReadOnlyGroupId

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def Vip(self):
        return self._Vip

    @Vip.setter
    def Vip(self, Vip):
        self._Vip = Vip


    def _deserialize(self, params):
        self._ReadOnlyGroupId = params.get("ReadOnlyGroupId")
        self._VpcId = params.get("VpcId")
        self._SubnetId = params.get("SubnetId")
        self._Vip = params.get("Vip")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteReadOnlyGroupNetworkAccessResponse(AbstractModel):
    """DeleteReadOnlyGroupNetworkAccess response structure.

    """

    def __init__(self):
        r"""
        :param _FlowId: Task ID.
Note: This field may return `null`, indicating that no valid values can be obtained.
        :type FlowId: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._FlowId = None
        self._RequestId = None

    @property
    def FlowId(self):
        return self._FlowId

    @FlowId.setter
    def FlowId(self, FlowId):
        self._FlowId = FlowId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._FlowId = params.get("FlowId")
        self._RequestId = params.get("RequestId")


class DeleteReadOnlyGroupRequest(AbstractModel):
    """DeleteReadOnlyGroup request structure.

    """

    def __init__(self):
        r"""
        :param _ReadOnlyGroupId: ID of the RO group to be deleted
        :type ReadOnlyGroupId: str
        """
        self._ReadOnlyGroupId = None

    @property
    def ReadOnlyGroupId(self):
        return self._ReadOnlyGroupId

    @ReadOnlyGroupId.setter
    def ReadOnlyGroupId(self, ReadOnlyGroupId):
        self._ReadOnlyGroupId = ReadOnlyGroupId


    def _deserialize(self, params):
        self._ReadOnlyGroupId = params.get("ReadOnlyGroupId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteReadOnlyGroupResponse(AbstractModel):
    """DeleteReadOnlyGroup response structure.

    """

    def __init__(self):
        r"""
        :param _FlowId: Task ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type FlowId: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._FlowId = None
        self._RequestId = None

    @property
    def FlowId(self):
        return self._FlowId

    @FlowId.setter
    def FlowId(self, FlowId):
        self._FlowId = FlowId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._FlowId = params.get("FlowId")
        self._RequestId = params.get("RequestId")


class DeleteServerlessDBInstanceRequest(AbstractModel):
    """DeleteServerlessDBInstance request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceName: Instance name. Either instance name or instance ID (or both) must be passed in. If both are passed in, the instance ID will prevail.
        :type DBInstanceName: str
        :param _DBInstanceId: Instance ID. Either instance name or instance ID (or both) must be passed in. If both are passed in, the instance ID will prevail.
        :type DBInstanceId: str
        """
        self._DBInstanceName = None
        self._DBInstanceId = None

    @property
    def DBInstanceName(self):
        return self._DBInstanceName

    @DBInstanceName.setter
    def DBInstanceName(self, DBInstanceName):
        self._DBInstanceName = DBInstanceName

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId


    def _deserialize(self, params):
        self._DBInstanceName = params.get("DBInstanceName")
        self._DBInstanceId = params.get("DBInstanceId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteServerlessDBInstanceResponse(AbstractModel):
    """DeleteServerlessDBInstance response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class DescribeAccountsRequest(AbstractModel):
    """DescribeAccounts request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of postgres-6fego161
        :type DBInstanceId: str
        :param _Limit: Number of entries returned per page. Default value: 10. Value range: 1–100.
        :type Limit: int
        :param _Offset: Data offset, which starts from 0.
        :type Offset: int
        :param _OrderBy: Whether to sort by creation time or username. Valid values: `createTime` (sort by creation time), `name` (sort by username)
        :type OrderBy: str
        :param _OrderByType: Whether returns are sorted in ascending or descending order. Valid values: `desc` (descending), `asc` (ascending)
        :type OrderByType: str
        """
        self._DBInstanceId = None
        self._Limit = None
        self._Offset = None
        self._OrderBy = None
        self._OrderByType = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def Limit(self):
        return self._Limit

    @Limit.setter
    def Limit(self, Limit):
        self._Limit = Limit

    @property
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, Offset):
        self._Offset = Offset

    @property
    def OrderBy(self):
        return self._OrderBy

    @OrderBy.setter
    def OrderBy(self, OrderBy):
        self._OrderBy = OrderBy

    @property
    def OrderByType(self):
        return self._OrderByType

    @OrderByType.setter
    def OrderByType(self, OrderByType):
        self._OrderByType = OrderByType


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._Limit = params.get("Limit")
        self._Offset = params.get("Offset")
        self._OrderBy = params.get("OrderBy")
        self._OrderByType = params.get("OrderByType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeAccountsResponse(AbstractModel):
    """DescribeAccounts response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: Number of date entries returned for this API call.
        :type TotalCount: int
        :param _Details: Account list details.
        :type Details: list of AccountInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._Details = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def Details(self):
        return self._Details

    @Details.setter
    def Details(self, Details):
        self._Details = Details

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("Details") is not None:
            self._Details = []
            for item in params.get("Details"):
                obj = AccountInfo()
                obj._deserialize(item)
                self._Details.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeAvailableRecoveryTimeRequest(AbstractModel):
    """DescribeAvailableRecoveryTime request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        """
        self._DBInstanceId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeAvailableRecoveryTimeResponse(AbstractModel):
    """DescribeAvailableRecoveryTime response structure.

    """

    def __init__(self):
        r"""
        :param _RecoveryBeginTime: The earliest restoration time (UTC+8).
        :type RecoveryBeginTime: str
        :param _RecoveryEndTime: The latest restoration time (UTC+8).
        :type RecoveryEndTime: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RecoveryBeginTime = None
        self._RecoveryEndTime = None
        self._RequestId = None

    @property
    def RecoveryBeginTime(self):
        return self._RecoveryBeginTime

    @RecoveryBeginTime.setter
    def RecoveryBeginTime(self, RecoveryBeginTime):
        self._RecoveryBeginTime = RecoveryBeginTime

    @property
    def RecoveryEndTime(self):
        return self._RecoveryEndTime

    @RecoveryEndTime.setter
    def RecoveryEndTime(self, RecoveryEndTime):
        self._RecoveryEndTime = RecoveryEndTime

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RecoveryBeginTime = params.get("RecoveryBeginTime")
        self._RecoveryEndTime = params.get("RecoveryEndTime")
        self._RequestId = params.get("RequestId")


class DescribeBackupDownloadRestrictionRequest(AbstractModel):
    """DescribeBackupDownloadRestriction request structure.

    """


class DescribeBackupDownloadRestrictionResponse(AbstractModel):
    """DescribeBackupDownloadRestriction response structure.

    """

    def __init__(self):
        r"""
        :param _RestrictionType: Type of the network restrictions for downloading a backup file. Valid values: `NONE` (backups can be downloaded over both private and public networks), `INTRANET` (backups can only be downloaded over the private network), `CUSTOMIZE` (backups can be downloaded over specified VPCs or at specified IPs).
        :type RestrictionType: str
        :param _VpcRestrictionEffect: Whether VPC is allowed. Valid values: `ALLOW` (allow), `DENY` (deny). 
Note:  This field may return null, indicating that no valid values can be obtained.
        :type VpcRestrictionEffect: str
        :param _VpcIdSet: Whether it is allowed to download the VPC ID list of the backup files. 
Note:  This field may return null, indicating that no valid values can be obtained.
        :type VpcIdSet: list of str
        :param _IpRestrictionEffect: Whether IP is allowed. Valid values: `ALLOW` (allow), `DENY` (deny). 
Note: Note: This field may return null, indicating that no valid values can be obtained.
        :type IpRestrictionEffect: str
        :param _IpSet: Whether it is allowed to download the IP list of the backup files. 
Note:  This field may return null, indicating that no valid values can be obtained.
        :type IpSet: list of str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RestrictionType = None
        self._VpcRestrictionEffect = None
        self._VpcIdSet = None
        self._IpRestrictionEffect = None
        self._IpSet = None
        self._RequestId = None

    @property
    def RestrictionType(self):
        return self._RestrictionType

    @RestrictionType.setter
    def RestrictionType(self, RestrictionType):
        self._RestrictionType = RestrictionType

    @property
    def VpcRestrictionEffect(self):
        return self._VpcRestrictionEffect

    @VpcRestrictionEffect.setter
    def VpcRestrictionEffect(self, VpcRestrictionEffect):
        self._VpcRestrictionEffect = VpcRestrictionEffect

    @property
    def VpcIdSet(self):
        return self._VpcIdSet

    @VpcIdSet.setter
    def VpcIdSet(self, VpcIdSet):
        self._VpcIdSet = VpcIdSet

    @property
    def IpRestrictionEffect(self):
        return self._IpRestrictionEffect

    @IpRestrictionEffect.setter
    def IpRestrictionEffect(self, IpRestrictionEffect):
        self._IpRestrictionEffect = IpRestrictionEffect

    @property
    def IpSet(self):
        return self._IpSet

    @IpSet.setter
    def IpSet(self, IpSet):
        self._IpSet = IpSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RestrictionType = params.get("RestrictionType")
        self._VpcRestrictionEffect = params.get("VpcRestrictionEffect")
        self._VpcIdSet = params.get("VpcIdSet")
        self._IpRestrictionEffect = params.get("IpRestrictionEffect")
        self._IpSet = params.get("IpSet")
        self._RequestId = params.get("RequestId")


class DescribeBackupDownloadURLRequest(AbstractModel):
    """DescribeBackupDownloadURL request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID.
        :type DBInstanceId: str
        :param _BackupType: Backup type. Valid values: `LogBackup`, `BaseBackup`.
        :type BackupType: str
        :param _BackupId: Unique backup ID.
        :type BackupId: str
        :param _URLExpireTime: Validity period of a URL, which is 12 hours by default.
        :type URLExpireTime: int
        :param _BackupDownloadRestriction: Backup download restriction
        :type BackupDownloadRestriction: :class:`tencentcloud.postgres.v20170312.models.BackupDownloadRestriction`
        """
        self._DBInstanceId = None
        self._BackupType = None
        self._BackupId = None
        self._URLExpireTime = None
        self._BackupDownloadRestriction = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def BackupType(self):
        return self._BackupType

    @BackupType.setter
    def BackupType(self, BackupType):
        self._BackupType = BackupType

    @property
    def BackupId(self):
        return self._BackupId

    @BackupId.setter
    def BackupId(self, BackupId):
        self._BackupId = BackupId

    @property
    def URLExpireTime(self):
        return self._URLExpireTime

    @URLExpireTime.setter
    def URLExpireTime(self, URLExpireTime):
        self._URLExpireTime = URLExpireTime

    @property
    def BackupDownloadRestriction(self):
        return self._BackupDownloadRestriction

    @BackupDownloadRestriction.setter
    def BackupDownloadRestriction(self, BackupDownloadRestriction):
        self._BackupDownloadRestriction = BackupDownloadRestriction


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._BackupType = params.get("BackupType")
        self._BackupId = params.get("BackupId")
        self._URLExpireTime = params.get("URLExpireTime")
        if params.get("BackupDownloadRestriction") is not None:
            self._BackupDownloadRestriction = BackupDownloadRestriction()
            self._BackupDownloadRestriction._deserialize(params.get("BackupDownloadRestriction"))
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeBackupDownloadURLResponse(AbstractModel):
    """DescribeBackupDownloadURL response structure.

    """

    def __init__(self):
        r"""
        :param _BackupDownloadURL: Backup download URL
        :type BackupDownloadURL: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._BackupDownloadURL = None
        self._RequestId = None

    @property
    def BackupDownloadURL(self):
        return self._BackupDownloadURL

    @BackupDownloadURL.setter
    def BackupDownloadURL(self, BackupDownloadURL):
        self._BackupDownloadURL = BackupDownloadURL

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._BackupDownloadURL = params.get("BackupDownloadURL")
        self._RequestId = params.get("RequestId")


class DescribeBackupOverviewRequest(AbstractModel):
    """DescribeBackupOverview request structure.

    """


class DescribeBackupOverviewResponse(AbstractModel):
    """DescribeBackupOverview response structure.

    """

    def __init__(self):
        r"""
        :param _TotalFreeSize: Total free space size in bytes
        :type TotalFreeSize: int
        :param _UsedFreeSize: Used free space size in bytes
        :type UsedFreeSize: int
        :param _UsedBillingSize: Used paid space size in bytes
        :type UsedBillingSize: int
        :param _LogBackupCount: Number of log backups
        :type LogBackupCount: int
        :param _LogBackupSize: Log backup size in bytes
        :type LogBackupSize: int
        :param _ManualBaseBackupCount: Number of manually created full backups
        :type ManualBaseBackupCount: int
        :param _ManualBaseBackupSize: Size of manually created full backups in bytes
        :type ManualBaseBackupSize: int
        :param _AutoBaseBackupCount: Number of automatically created full backups
        :type AutoBaseBackupCount: int
        :param _AutoBaseBackupSize: Size of automatically created full backups in bytes
        :type AutoBaseBackupSize: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalFreeSize = None
        self._UsedFreeSize = None
        self._UsedBillingSize = None
        self._LogBackupCount = None
        self._LogBackupSize = None
        self._ManualBaseBackupCount = None
        self._ManualBaseBackupSize = None
        self._AutoBaseBackupCount = None
        self._AutoBaseBackupSize = None
        self._RequestId = None

    @property
    def TotalFreeSize(self):
        return self._TotalFreeSize

    @TotalFreeSize.setter
    def TotalFreeSize(self, TotalFreeSize):
        self._TotalFreeSize = TotalFreeSize

    @property
    def UsedFreeSize(self):
        return self._UsedFreeSize

    @UsedFreeSize.setter
    def UsedFreeSize(self, UsedFreeSize):
        self._UsedFreeSize = UsedFreeSize

    @property
    def UsedBillingSize(self):
        return self._UsedBillingSize

    @UsedBillingSize.setter
    def UsedBillingSize(self, UsedBillingSize):
        self._UsedBillingSize = UsedBillingSize

    @property
    def LogBackupCount(self):
        return self._LogBackupCount

    @LogBackupCount.setter
    def LogBackupCount(self, LogBackupCount):
        self._LogBackupCount = LogBackupCount

    @property
    def LogBackupSize(self):
        return self._LogBackupSize

    @LogBackupSize.setter
    def LogBackupSize(self, LogBackupSize):
        self._LogBackupSize = LogBackupSize

    @property
    def ManualBaseBackupCount(self):
        return self._ManualBaseBackupCount

    @ManualBaseBackupCount.setter
    def ManualBaseBackupCount(self, ManualBaseBackupCount):
        self._ManualBaseBackupCount = ManualBaseBackupCount

    @property
    def ManualBaseBackupSize(self):
        return self._ManualBaseBackupSize

    @ManualBaseBackupSize.setter
    def ManualBaseBackupSize(self, ManualBaseBackupSize):
        self._ManualBaseBackupSize = ManualBaseBackupSize

    @property
    def AutoBaseBackupCount(self):
        return self._AutoBaseBackupCount

    @AutoBaseBackupCount.setter
    def AutoBaseBackupCount(self, AutoBaseBackupCount):
        self._AutoBaseBackupCount = AutoBaseBackupCount

    @property
    def AutoBaseBackupSize(self):
        return self._AutoBaseBackupSize

    @AutoBaseBackupSize.setter
    def AutoBaseBackupSize(self, AutoBaseBackupSize):
        self._AutoBaseBackupSize = AutoBaseBackupSize

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalFreeSize = params.get("TotalFreeSize")
        self._UsedFreeSize = params.get("UsedFreeSize")
        self._UsedBillingSize = params.get("UsedBillingSize")
        self._LogBackupCount = params.get("LogBackupCount")
        self._LogBackupSize = params.get("LogBackupSize")
        self._ManualBaseBackupCount = params.get("ManualBaseBackupCount")
        self._ManualBaseBackupSize = params.get("ManualBaseBackupSize")
        self._AutoBaseBackupCount = params.get("AutoBaseBackupCount")
        self._AutoBaseBackupSize = params.get("AutoBaseBackupSize")
        self._RequestId = params.get("RequestId")


class DescribeBackupPlansRequest(AbstractModel):
    """DescribeBackupPlans request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        """
        self._DBInstanceId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeBackupPlansResponse(AbstractModel):
    """DescribeBackupPlans response structure.

    """

    def __init__(self):
        r"""
        :param _Plans: The set of instance backup plans
        :type Plans: list of BackupPlan
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Plans = None
        self._RequestId = None

    @property
    def Plans(self):
        return self._Plans

    @Plans.setter
    def Plans(self, Plans):
        self._Plans = Plans

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Plans") is not None:
            self._Plans = []
            for item in params.get("Plans"):
                obj = BackupPlan()
                obj._deserialize(item)
                self._Plans.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeBackupSummariesRequest(AbstractModel):
    """DescribeBackupSummaries request structure.

    """

    def __init__(self):
        r"""
        :param _Limit: The maximum number of results returned per page. Value range: 1-100. Default: `10`
        :type Limit: int
        :param _Offset: Data offset, which starts from 0.
        :type Offset: int
        :param _Filters: Filter instances using one or more criteria. Valid filter names:
db-instance-id: Filter by instance ID (in string format).
db-instance-name: Filter by instance name (in string format).
db-instance-ip: Filter by instance VPC IP (in string format).
        :type Filters: list of Filter
        :param _OrderBy: Sorting field. Valid values: `TotalBackupSize`, `LogBackupSize`, `ManualBaseBackupSize`, `AutoBaseBackupSize`.
        :type OrderBy: str
        :param _OrderByType: Sorting order. Valid values: `asc` (ascending), `desc` (descending).
        :type OrderByType: str
        """
        self._Limit = None
        self._Offset = None
        self._Filters = None
        self._OrderBy = None
        self._OrderByType = None

    @property
    def Limit(self):
        return self._Limit

    @Limit.setter
    def Limit(self, Limit):
        self._Limit = Limit

    @property
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, Offset):
        self._Offset = Offset

    @property
    def Filters(self):
        return self._Filters

    @Filters.setter
    def Filters(self, Filters):
        self._Filters = Filters

    @property
    def OrderBy(self):
        return self._OrderBy

    @OrderBy.setter
    def OrderBy(self, OrderBy):
        self._OrderBy = OrderBy

    @property
    def OrderByType(self):
        return self._OrderByType

    @OrderByType.setter
    def OrderByType(self, OrderByType):
        self._OrderByType = OrderByType


    def _deserialize(self, params):
        self._Limit = params.get("Limit")
        self._Offset = params.get("Offset")
        if params.get("Filters") is not None:
            self._Filters = []
            for item in params.get("Filters"):
                obj = Filter()
                obj._deserialize(item)
                self._Filters.append(obj)
        self._OrderBy = params.get("OrderBy")
        self._OrderByType = params.get("OrderByType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeBackupSummariesResponse(AbstractModel):
    """DescribeBackupSummaries response structure.

    """

    def __init__(self):
        r"""
        :param _BackupSummarySet: Backup statistics list.
        :type BackupSummarySet: list of BackupSummary
        :param _TotalCount: Number of all queried backups.
        :type TotalCount: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._BackupSummarySet = None
        self._TotalCount = None
        self._RequestId = None

    @property
    def BackupSummarySet(self):
        return self._BackupSummarySet

    @BackupSummarySet.setter
    def BackupSummarySet(self, BackupSummarySet):
        self._BackupSummarySet = BackupSummarySet

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("BackupSummarySet") is not None:
            self._BackupSummarySet = []
            for item in params.get("BackupSummarySet"):
                obj = BackupSummary()
                obj._deserialize(item)
                self._BackupSummarySet.append(obj)
        self._TotalCount = params.get("TotalCount")
        self._RequestId = params.get("RequestId")


class DescribeBaseBackupsRequest(AbstractModel):
    """DescribeBaseBackups request structure.

    """

    def __init__(self):
        r"""
        :param _MinFinishTime: Minimum end time of a backup in the format of `2018-01-01 00:00:00`. It is 7 days ago by default.
        :type MinFinishTime: str
        :param _MaxFinishTime: Maximum end time of a backup in the format of `2018-01-01 00:00:00`. It is the current time by default.
        :type MaxFinishTime: str
        :param _Filters: Filter instances by using one or more filters. Valid values:  `db-instance-idFilter` (filter by instance ID in string),  `db-instance-name` (filter by instance name in string),  `db-instance-ip` (filter by instance VPC IP address in string),  `base-backup-id` (filter by backup set ID in string), 
        :type Filters: list of Filter
        :param _Limit: The maximum number of results returned per page. Value range: 1-100. Default: `10`
        :type Limit: int
        :param _Offset: Data offset, which starts from 0.
        :type Offset: int
        :param _OrderBy: Sorting field. Valid values: `StartTime`, `FinishTime`, `Size`.
        :type OrderBy: str
        :param _OrderByType: Sorting order. Valid values: `asc` (ascending), `desc` (descending).
        :type OrderByType: str
        """
        self._MinFinishTime = None
        self._MaxFinishTime = None
        self._Filters = None
        self._Limit = None
        self._Offset = None
        self._OrderBy = None
        self._OrderByType = None

    @property
    def MinFinishTime(self):
        return self._MinFinishTime

    @MinFinishTime.setter
    def MinFinishTime(self, MinFinishTime):
        self._MinFinishTime = MinFinishTime

    @property
    def MaxFinishTime(self):
        return self._MaxFinishTime

    @MaxFinishTime.setter
    def MaxFinishTime(self, MaxFinishTime):
        self._MaxFinishTime = MaxFinishTime

    @property
    def Filters(self):
        return self._Filters

    @Filters.setter
    def Filters(self, Filters):
        self._Filters = Filters

    @property
    def Limit(self):
        return self._Limit

    @Limit.setter
    def Limit(self, Limit):
        self._Limit = Limit

    @property
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, Offset):
        self._Offset = Offset

    @property
    def OrderBy(self):
        return self._OrderBy

    @OrderBy.setter
    def OrderBy(self, OrderBy):
        self._OrderBy = OrderBy

    @property
    def OrderByType(self):
        return self._OrderByType

    @OrderByType.setter
    def OrderByType(self, OrderByType):
        self._OrderByType = OrderByType


    def _deserialize(self, params):
        self._MinFinishTime = params.get("MinFinishTime")
        self._MaxFinishTime = params.get("MaxFinishTime")
        if params.get("Filters") is not None:
            self._Filters = []
            for item in params.get("Filters"):
                obj = Filter()
                obj._deserialize(item)
                self._Filters.append(obj)
        self._Limit = params.get("Limit")
        self._Offset = params.get("Offset")
        self._OrderBy = params.get("OrderBy")
        self._OrderByType = params.get("OrderByType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeBaseBackupsResponse(AbstractModel):
    """DescribeBaseBackups response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: Number of queried full backups
        :type TotalCount: int
        :param _BaseBackupSet: List of full backup details
        :type BaseBackupSet: list of BaseBackup
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._BaseBackupSet = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def BaseBackupSet(self):
        return self._BaseBackupSet

    @BaseBackupSet.setter
    def BaseBackupSet(self, BaseBackupSet):
        self._BaseBackupSet = BaseBackupSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("BaseBackupSet") is not None:
            self._BaseBackupSet = []
            for item in params.get("BaseBackupSet"):
                obj = BaseBackup()
                obj._deserialize(item)
                self._BaseBackupSet.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeClassesRequest(AbstractModel):
    """DescribeClasses request structure.

    """

    def __init__(self):
        r"""
        :param _Zone: AZ ID, which can be obtained through the `DescribeZones` API.
        :type Zone: str
        :param _DBEngine: Database engines. Valid values:
1. `postgresql` (TencentDB for PostgreSQL)
2. `mssql_compatible` (MSSQL compatible-TencentDB for PostgreSQL)
        :type DBEngine: str
        :param _DBMajorVersion: Major version of a database, such as 12 or 13, which can be obtained through the `DescribeDBVersions` API.
        :type DBMajorVersion: str
        """
        self._Zone = None
        self._DBEngine = None
        self._DBMajorVersion = None

    @property
    def Zone(self):
        return self._Zone

    @Zone.setter
    def Zone(self, Zone):
        self._Zone = Zone

    @property
    def DBEngine(self):
        return self._DBEngine

    @DBEngine.setter
    def DBEngine(self, DBEngine):
        self._DBEngine = DBEngine

    @property
    def DBMajorVersion(self):
        return self._DBMajorVersion

    @DBMajorVersion.setter
    def DBMajorVersion(self, DBMajorVersion):
        self._DBMajorVersion = DBMajorVersion


    def _deserialize(self, params):
        self._Zone = params.get("Zone")
        self._DBEngine = params.get("DBEngine")
        self._DBMajorVersion = params.get("DBMajorVersion")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeClassesResponse(AbstractModel):
    """DescribeClasses response structure.

    """

    def __init__(self):
        r"""
        :param _ClassInfoSet: List of database specifications
        :type ClassInfoSet: list of ClassInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._ClassInfoSet = None
        self._RequestId = None

    @property
    def ClassInfoSet(self):
        return self._ClassInfoSet

    @ClassInfoSet.setter
    def ClassInfoSet(self, ClassInfoSet):
        self._ClassInfoSet = ClassInfoSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("ClassInfoSet") is not None:
            self._ClassInfoSet = []
            for item in params.get("ClassInfoSet"):
                obj = ClassInfo()
                obj._deserialize(item)
                self._ClassInfoSet.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeCloneDBInstanceSpecRequest(AbstractModel):
    """DescribeCloneDBInstanceSpec request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID.
        :type DBInstanceId: str
        :param _BackupSetId: Basic backup set ID. Either this parameter or `RecoveryTargetTime` must be passed in. If both are passed in, only this parameter takes effect.
        :type BackupSetId: str
        :param _RecoveryTargetTime: Restoration time (UTC+8). Either this parameter or `BackupSetId` must be passed in.
        :type RecoveryTargetTime: str
        """
        self._DBInstanceId = None
        self._BackupSetId = None
        self._RecoveryTargetTime = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def BackupSetId(self):
        return self._BackupSetId

    @BackupSetId.setter
    def BackupSetId(self, BackupSetId):
        self._BackupSetId = BackupSetId

    @property
    def RecoveryTargetTime(self):
        return self._RecoveryTargetTime

    @RecoveryTargetTime.setter
    def RecoveryTargetTime(self, RecoveryTargetTime):
        self._RecoveryTargetTime = RecoveryTargetTime


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._BackupSetId = params.get("BackupSetId")
        self._RecoveryTargetTime = params.get("RecoveryTargetTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeCloneDBInstanceSpecResponse(AbstractModel):
    """DescribeCloneDBInstanceSpec response structure.

    """

    def __init__(self):
        r"""
        :param _MinSpecCode: Code of the minimum specification available for purchase.
        :type MinSpecCode: str
        :param _MinStorage: The minimum disk capacity in GB available for purchase.
        :type MinStorage: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._MinSpecCode = None
        self._MinStorage = None
        self._RequestId = None

    @property
    def MinSpecCode(self):
        return self._MinSpecCode

    @MinSpecCode.setter
    def MinSpecCode(self, MinSpecCode):
        self._MinSpecCode = MinSpecCode

    @property
    def MinStorage(self):
        return self._MinStorage

    @MinStorage.setter
    def MinStorage(self, MinStorage):
        self._MinStorage = MinStorage

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._MinSpecCode = params.get("MinSpecCode")
        self._MinStorage = params.get("MinStorage")
        self._RequestId = params.get("RequestId")


class DescribeDBBackupsRequest(AbstractModel):
    """DescribeDBBackups request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of postgres-4wdeb0zv.
        :type DBInstanceId: str
        :param _Type: Backup mode (1: full). Currently, only full backup is supported. The value is 1.
        :type Type: int
        :param _StartTime: Query start time in the format of 2018-06-10 17:06:38, which cannot be more than 7 days ago
        :type StartTime: str
        :param _EndTime: Query end time in the format of 2018-06-10 17:06:38
        :type EndTime: str
        :param _Limit: Number of entries to be returned per page for backup list. Default value: 20. Minimum value: 1. Maximum value: 100. (If this parameter is left empty or 0, the default value will be used)
        :type Limit: int
        :param _Offset: Page number for data return in paged query. Pagination starts from 0. Default value: 0.
        :type Offset: int
        """
        self._DBInstanceId = None
        self._Type = None
        self._StartTime = None
        self._EndTime = None
        self._Limit = None
        self._Offset = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def Type(self):
        return self._Type

    @Type.setter
    def Type(self, Type):
        self._Type = Type

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
    def Limit(self):
        return self._Limit

    @Limit.setter
    def Limit(self, Limit):
        self._Limit = Limit

    @property
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, Offset):
        self._Offset = Offset


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._Type = params.get("Type")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._Limit = params.get("Limit")
        self._Offset = params.get("Offset")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeDBBackupsResponse(AbstractModel):
    """DescribeDBBackups response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: Number of backup files in the returned backup list
        :type TotalCount: int
        :param _BackupList: Backup list
        :type BackupList: list of DBBackup
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._BackupList = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def BackupList(self):
        return self._BackupList

    @BackupList.setter
    def BackupList(self, BackupList):
        self._BackupList = BackupList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("BackupList") is not None:
            self._BackupList = []
            for item in params.get("BackupList"):
                obj = DBBackup()
                obj._deserialize(item)
                self._BackupList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeDBErrlogsRequest(AbstractModel):
    """DescribeDBErrlogs request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of postgres-5bq3wfjd
        :type DBInstanceId: str
        :param _StartTime: Query start time in the format of 2018-01-01 00:00:00, which cannot be more than 7 days ago
        :type StartTime: str
        :param _EndTime: Query end time in the format of 2018-01-01 00:00:00
        :type EndTime: str
        :param _DatabaseName: Database name
        :type DatabaseName: str
        :param _SearchKeys: Search keyword
        :type SearchKeys: list of str
        :param _Limit: Number of entries returned per page. Value range: 1-100
        :type Limit: int
        :param _Offset: Page number for data return in paged query. Pagination starts from 0
        :type Offset: int
        """
        self._DBInstanceId = None
        self._StartTime = None
        self._EndTime = None
        self._DatabaseName = None
        self._SearchKeys = None
        self._Limit = None
        self._Offset = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

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
    def DatabaseName(self):
        return self._DatabaseName

    @DatabaseName.setter
    def DatabaseName(self, DatabaseName):
        self._DatabaseName = DatabaseName

    @property
    def SearchKeys(self):
        return self._SearchKeys

    @SearchKeys.setter
    def SearchKeys(self, SearchKeys):
        self._SearchKeys = SearchKeys

    @property
    def Limit(self):
        return self._Limit

    @Limit.setter
    def Limit(self, Limit):
        self._Limit = Limit

    @property
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, Offset):
        self._Offset = Offset


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._DatabaseName = params.get("DatabaseName")
        self._SearchKeys = params.get("SearchKeys")
        self._Limit = params.get("Limit")
        self._Offset = params.get("Offset")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeDBErrlogsResponse(AbstractModel):
    """DescribeDBErrlogs response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: Number of date entries returned for this call
        :type TotalCount: int
        :param _Details: Error log list
        :type Details: list of ErrLogDetail
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._Details = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def Details(self):
        return self._Details

    @Details.setter
    def Details(self, Details):
        self._Details = Details

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("Details") is not None:
            self._Details = []
            for item in params.get("Details"):
                obj = ErrLogDetail()
                obj._deserialize(item)
                self._Details.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeDBInstanceAttributeRequest(AbstractModel):
    """DescribeDBInstanceAttribute request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        """
        self._DBInstanceId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeDBInstanceAttributeResponse(AbstractModel):
    """DescribeDBInstanceAttribute response structure.

    """

    def __init__(self):
        r"""
        :param _DBInstance: Instance details.
        :type DBInstance: :class:`tencentcloud.postgres.v20170312.models.DBInstance`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DBInstance = None
        self._RequestId = None

    @property
    def DBInstance(self):
        return self._DBInstance

    @DBInstance.setter
    def DBInstance(self, DBInstance):
        self._DBInstance = DBInstance

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DBInstance") is not None:
            self._DBInstance = DBInstance()
            self._DBInstance._deserialize(params.get("DBInstance"))
        self._RequestId = params.get("RequestId")


class DescribeDBInstanceParametersRequest(AbstractModel):
    """DescribeDBInstanceParameters request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _ParamName: Name of the parameter to be queried. If `ParamName` is left empty or not passed in, the list of all parameters will be returned.
        :type ParamName: str
        """
        self._DBInstanceId = None
        self._ParamName = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def ParamName(self):
        return self._ParamName

    @ParamName.setter
    def ParamName(self, ParamName):
        self._ParamName = ParamName


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._ParamName = params.get("ParamName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeDBInstanceParametersResponse(AbstractModel):
    """DescribeDBInstanceParameters response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: Total number of the parameters in the returned list
        :type TotalCount: int
        :param _Detail: Details of the returned parameter list
        :type Detail: list of ParamInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._Detail = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def Detail(self):
        return self._Detail

    @Detail.setter
    def Detail(self, Detail):
        self._Detail = Detail

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("Detail") is not None:
            self._Detail = []
            for item in params.get("Detail"):
                obj = ParamInfo()
                obj._deserialize(item)
                self._Detail.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeDBInstanceSecurityGroupsRequest(AbstractModel):
    """DescribeDBInstanceSecurityGroups request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID. Either this parameter or `ReadOnlyGroupId` must be passed in. If both parameters are passed in, `ReadOnlyGroupId` will be ignored.
        :type DBInstanceId: str
        :param _ReadOnlyGroupId: RO group ID. Either this parameter or `DBInstanceId` must be passed in. To query the security groups associated with the RO groups, only pass in `ReadOnlyGroupId`.
        :type ReadOnlyGroupId: str
        """
        self._DBInstanceId = None
        self._ReadOnlyGroupId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def ReadOnlyGroupId(self):
        return self._ReadOnlyGroupId

    @ReadOnlyGroupId.setter
    def ReadOnlyGroupId(self, ReadOnlyGroupId):
        self._ReadOnlyGroupId = ReadOnlyGroupId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._ReadOnlyGroupId = params.get("ReadOnlyGroupId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeDBInstanceSecurityGroupsResponse(AbstractModel):
    """DescribeDBInstanceSecurityGroups response structure.

    """

    def __init__(self):
        r"""
        :param _SecurityGroupSet: Information of security groups in array
        :type SecurityGroupSet: list of SecurityGroup
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._SecurityGroupSet = None
        self._RequestId = None

    @property
    def SecurityGroupSet(self):
        return self._SecurityGroupSet

    @SecurityGroupSet.setter
    def SecurityGroupSet(self, SecurityGroupSet):
        self._SecurityGroupSet = SecurityGroupSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("SecurityGroupSet") is not None:
            self._SecurityGroupSet = []
            for item in params.get("SecurityGroupSet"):
                obj = SecurityGroup()
                obj._deserialize(item)
                self._SecurityGroupSet.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeDBInstancesRequest(AbstractModel):
    """DescribeDBInstances request structure.

    """

    def __init__(self):
        r"""
        :param _Filters: Filter instances using one or more criteria. Valid filter names:
db-instance-id: filter by instance ID (in string format)
db-instance-name: filter by instance name (in string format)
db-project-id: filter by project ID (in integer format)
db-pay-mode: filter by billing mode (in string format)
db-tag-key: filter by tag key (in string format)
        :type Filters: list of Filter
        :param _Limit: The maximum number of results returned per page. Value range: 1-100. Default: `10`
        :type Limit: int
        :param _Offset: Data offset, which starts from 0.
        :type Offset: int
        :param _OrderBy: Sorting metric, such as instance name or creation time. Valid values: DBInstanceId, CreateTime, Name, EndTime
        :type OrderBy: str
        :param _OrderByType: Sorting order. Valid values: `asc` (ascending), `desc` (descending)
        :type OrderByType: str
        """
        self._Filters = None
        self._Limit = None
        self._Offset = None
        self._OrderBy = None
        self._OrderByType = None

    @property
    def Filters(self):
        return self._Filters

    @Filters.setter
    def Filters(self, Filters):
        self._Filters = Filters

    @property
    def Limit(self):
        return self._Limit

    @Limit.setter
    def Limit(self, Limit):
        self._Limit = Limit

    @property
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, Offset):
        self._Offset = Offset

    @property
    def OrderBy(self):
        return self._OrderBy

    @OrderBy.setter
    def OrderBy(self, OrderBy):
        self._OrderBy = OrderBy

    @property
    def OrderByType(self):
        return self._OrderByType

    @OrderByType.setter
    def OrderByType(self, OrderByType):
        self._OrderByType = OrderByType


    def _deserialize(self, params):
        if params.get("Filters") is not None:
            self._Filters = []
            for item in params.get("Filters"):
                obj = Filter()
                obj._deserialize(item)
                self._Filters.append(obj)
        self._Limit = params.get("Limit")
        self._Offset = params.get("Offset")
        self._OrderBy = params.get("OrderBy")
        self._OrderByType = params.get("OrderByType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeDBInstancesResponse(AbstractModel):
    """DescribeDBInstances response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: Number of instances found.
        :type TotalCount: int
        :param _DBInstanceSet: Instance details set.
        :type DBInstanceSet: list of DBInstance
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._DBInstanceSet = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def DBInstanceSet(self):
        return self._DBInstanceSet

    @DBInstanceSet.setter
    def DBInstanceSet(self, DBInstanceSet):
        self._DBInstanceSet = DBInstanceSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("DBInstanceSet") is not None:
            self._DBInstanceSet = []
            for item in params.get("DBInstanceSet"):
                obj = DBInstance()
                obj._deserialize(item)
                self._DBInstanceSet.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeDBSlowlogsRequest(AbstractModel):
    """DescribeDBSlowlogs request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of postgres-lnp6j617
        :type DBInstanceId: str
        :param _StartTime: Query start time in the format of 2018-06-10 17:06:38, which cannot be more than 7 days ago
        :type StartTime: str
        :param _EndTime: Query end time in the format of 2018-06-10 17:06:38
        :type EndTime: str
        :param _DatabaseName: Database name
        :type DatabaseName: str
        :param _OrderBy: Metric for sorting. Valid values: `sum_calls` (total number of calls), `sum_cost_time` (total time consumed)
        :type OrderBy: str
        :param _OrderByType: Sorting order. desc: descending, asc: ascending
        :type OrderByType: str
        :param _Limit: Number of entries returned per page. Value range: 1-100. Default value: 20.
        :type Limit: int
        :param _Offset: Page number for data return in paged query. Pagination starts from 0
        :type Offset: int
        """
        self._DBInstanceId = None
        self._StartTime = None
        self._EndTime = None
        self._DatabaseName = None
        self._OrderBy = None
        self._OrderByType = None
        self._Limit = None
        self._Offset = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

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
    def DatabaseName(self):
        return self._DatabaseName

    @DatabaseName.setter
    def DatabaseName(self, DatabaseName):
        self._DatabaseName = DatabaseName

    @property
    def OrderBy(self):
        return self._OrderBy

    @OrderBy.setter
    def OrderBy(self, OrderBy):
        self._OrderBy = OrderBy

    @property
    def OrderByType(self):
        return self._OrderByType

    @OrderByType.setter
    def OrderByType(self, OrderByType):
        self._OrderByType = OrderByType

    @property
    def Limit(self):
        return self._Limit

    @Limit.setter
    def Limit(self, Limit):
        self._Limit = Limit

    @property
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, Offset):
        self._Offset = Offset


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._DatabaseName = params.get("DatabaseName")
        self._OrderBy = params.get("OrderBy")
        self._OrderByType = params.get("OrderByType")
        self._Limit = params.get("Limit")
        self._Offset = params.get("Offset")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeDBSlowlogsResponse(AbstractModel):
    """DescribeDBSlowlogs response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: Number of date entries returned this time
        :type TotalCount: int
        :param _Detail: Slow query log details
        :type Detail: :class:`tencentcloud.postgres.v20170312.models.SlowlogDetail`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._Detail = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def Detail(self):
        return self._Detail

    @Detail.setter
    def Detail(self, Detail):
        self._Detail = Detail

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("Detail") is not None:
            self._Detail = SlowlogDetail()
            self._Detail._deserialize(params.get("Detail"))
        self._RequestId = params.get("RequestId")


class DescribeDBVersionsRequest(AbstractModel):
    """DescribeDBVersions request structure.

    """


class DescribeDBVersionsResponse(AbstractModel):
    """DescribeDBVersions response structure.

    """

    def __init__(self):
        r"""
        :param _VersionSet: List of database versions
        :type VersionSet: list of Version
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._VersionSet = None
        self._RequestId = None

    @property
    def VersionSet(self):
        return self._VersionSet

    @VersionSet.setter
    def VersionSet(self, VersionSet):
        self._VersionSet = VersionSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("VersionSet") is not None:
            self._VersionSet = []
            for item in params.get("VersionSet"):
                obj = Version()
                obj._deserialize(item)
                self._VersionSet.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeDBXlogsRequest(AbstractModel):
    """DescribeDBXlogs request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of postgres-4wdeb0zv.
        :type DBInstanceId: str
        :param _StartTime: Query start time in the format of 2018-06-10 17:06:38, which cannot be more than 7 days ago
        :type StartTime: str
        :param _EndTime: Query end time in the format of 2018-06-10 17:06:38
        :type EndTime: str
        :param _Offset: Page number for data return in paged query. Pagination starts from 0
        :type Offset: int
        :param _Limit: Number of entries returned per page in paged query. Value range: 1-100.
        :type Limit: int
        """
        self._DBInstanceId = None
        self._StartTime = None
        self._EndTime = None
        self._Offset = None
        self._Limit = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

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
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, Offset):
        self._Offset = Offset

    @property
    def Limit(self):
        return self._Limit

    @Limit.setter
    def Limit(self, Limit):
        self._Limit = Limit


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._Offset = params.get("Offset")
        self._Limit = params.get("Limit")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeDBXlogsResponse(AbstractModel):
    """DescribeDBXlogs response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: Number of date entries returned this time.
        :type TotalCount: int
        :param _XlogList: Xlog list
        :type XlogList: list of Xlog
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._XlogList = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def XlogList(self):
        return self._XlogList

    @XlogList.setter
    def XlogList(self, XlogList):
        self._XlogList = XlogList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("XlogList") is not None:
            self._XlogList = []
            for item in params.get("XlogList"):
                obj = Xlog()
                obj._deserialize(item)
                self._XlogList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeDatabasesRequest(AbstractModel):
    """DescribeDatabases request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        """
        self._DBInstanceId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeDatabasesResponse(AbstractModel):
    """DescribeDatabases response structure.

    """

    def __init__(self):
        r"""
        :param _Items: Database information
        :type Items: list of str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Items = None
        self._RequestId = None

    @property
    def Items(self):
        return self._Items

    @Items.setter
    def Items(self, Items):
        self._Items = Items

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._Items = params.get("Items")
        self._RequestId = params.get("RequestId")


class DescribeDefaultParametersRequest(AbstractModel):
    """DescribeDefaultParameters request structure.

    """

    def __init__(self):
        r"""
        :param _DBMajorVersion: The major database version number, such as 11, 12, 13.
        :type DBMajorVersion: str
        :param _DBEngine: Database engine, such as postgresql, mssql_compatible.
        :type DBEngine: str
        """
        self._DBMajorVersion = None
        self._DBEngine = None

    @property
    def DBMajorVersion(self):
        return self._DBMajorVersion

    @DBMajorVersion.setter
    def DBMajorVersion(self, DBMajorVersion):
        self._DBMajorVersion = DBMajorVersion

    @property
    def DBEngine(self):
        return self._DBEngine

    @DBEngine.setter
    def DBEngine(self, DBEngine):
        self._DBEngine = DBEngine


    def _deserialize(self, params):
        self._DBMajorVersion = params.get("DBMajorVersion")
        self._DBEngine = params.get("DBEngine")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeDefaultParametersResponse(AbstractModel):
    """DescribeDefaultParameters response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: Number of parameters
        :type TotalCount: int
        :param _ParamInfoSet: Parameter information
Note: This field may return null, indicating that no valid values can be obtained.
        :type ParamInfoSet: list of ParamInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._ParamInfoSet = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def ParamInfoSet(self):
        return self._ParamInfoSet

    @ParamInfoSet.setter
    def ParamInfoSet(self, ParamInfoSet):
        self._ParamInfoSet = ParamInfoSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("ParamInfoSet") is not None:
            self._ParamInfoSet = []
            for item in params.get("ParamInfoSet"):
                obj = ParamInfo()
                obj._deserialize(item)
                self._ParamInfoSet.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeEncryptionKeysRequest(AbstractModel):
    """DescribeEncryptionKeys request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        """
        self._DBInstanceId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeEncryptionKeysResponse(AbstractModel):
    """DescribeEncryptionKeys response structure.

    """

    def __init__(self):
        r"""
        :param _EncryptionKeys: Instance key list
Note: This field may return `null`, indicating that no valid value can be obtained.
        :type EncryptionKeys: list of EncryptionKey
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._EncryptionKeys = None
        self._RequestId = None

    @property
    def EncryptionKeys(self):
        return self._EncryptionKeys

    @EncryptionKeys.setter
    def EncryptionKeys(self, EncryptionKeys):
        self._EncryptionKeys = EncryptionKeys

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("EncryptionKeys") is not None:
            self._EncryptionKeys = []
            for item in params.get("EncryptionKeys"):
                obj = EncryptionKey()
                obj._deserialize(item)
                self._EncryptionKeys.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLogBackupsRequest(AbstractModel):
    """DescribeLogBackups request structure.

    """

    def __init__(self):
        r"""
        :param _MinFinishTime: Minimum end time of a backup in the format of `2018-01-01 00:00:00`. It is 7 days ago by default.
        :type MinFinishTime: str
        :param _MaxFinishTime: Maximum end time of a backup in the format of `2018-01-01 00:00:00`. It is the current time by default.
        :type MaxFinishTime: str
        :param _Filters: Filter instances using one or more criteria. Valid filter names:
db-instance-id: Filter by instance ID (in string format).
db-instance-name: Filter by instance name (in string format).
db-instance-ip: Filter by instance VPC IP (in string format).
        :type Filters: list of Filter
        :param _Limit: The maximum number of results returned per page. Value range: 1-100. Default: `10`.
        :type Limit: int
        :param _Offset: Data offset, which starts from 0.
        :type Offset: int
        :param _OrderBy: Sorting field. Valid values: `StartTime`, `FinishTime`, `Size`.
        :type OrderBy: str
        :param _OrderByType: Sorting order. Valid values: `asc` (ascending), `desc` (descending).
        :type OrderByType: str
        """
        self._MinFinishTime = None
        self._MaxFinishTime = None
        self._Filters = None
        self._Limit = None
        self._Offset = None
        self._OrderBy = None
        self._OrderByType = None

    @property
    def MinFinishTime(self):
        return self._MinFinishTime

    @MinFinishTime.setter
    def MinFinishTime(self, MinFinishTime):
        self._MinFinishTime = MinFinishTime

    @property
    def MaxFinishTime(self):
        return self._MaxFinishTime

    @MaxFinishTime.setter
    def MaxFinishTime(self, MaxFinishTime):
        self._MaxFinishTime = MaxFinishTime

    @property
    def Filters(self):
        return self._Filters

    @Filters.setter
    def Filters(self, Filters):
        self._Filters = Filters

    @property
    def Limit(self):
        return self._Limit

    @Limit.setter
    def Limit(self, Limit):
        self._Limit = Limit

    @property
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, Offset):
        self._Offset = Offset

    @property
    def OrderBy(self):
        return self._OrderBy

    @OrderBy.setter
    def OrderBy(self, OrderBy):
        self._OrderBy = OrderBy

    @property
    def OrderByType(self):
        return self._OrderByType

    @OrderByType.setter
    def OrderByType(self, OrderByType):
        self._OrderByType = OrderByType


    def _deserialize(self, params):
        self._MinFinishTime = params.get("MinFinishTime")
        self._MaxFinishTime = params.get("MaxFinishTime")
        if params.get("Filters") is not None:
            self._Filters = []
            for item in params.get("Filters"):
                obj = Filter()
                obj._deserialize(item)
                self._Filters.append(obj)
        self._Limit = params.get("Limit")
        self._Offset = params.get("Offset")
        self._OrderBy = params.get("OrderBy")
        self._OrderByType = params.get("OrderByType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLogBackupsResponse(AbstractModel):
    """DescribeLogBackups response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: Number of queried log backups
        :type TotalCount: int
        :param _LogBackupSet: List of log backup details
        :type LogBackupSet: list of LogBackup
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._LogBackupSet = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def LogBackupSet(self):
        return self._LogBackupSet

    @LogBackupSet.setter
    def LogBackupSet(self, LogBackupSet):
        self._LogBackupSet = LogBackupSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("LogBackupSet") is not None:
            self._LogBackupSet = []
            for item in params.get("LogBackupSet"):
                obj = LogBackup()
                obj._deserialize(item)
                self._LogBackupSet.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeOrdersRequest(AbstractModel):
    """DescribeOrders request structure.

    """

    def __init__(self):
        r"""
        :param _DealNames: Order name set
        :type DealNames: list of str
        """
        self._DealNames = None

    @property
    def DealNames(self):
        return self._DealNames

    @DealNames.setter
    def DealNames(self, DealNames):
        self._DealNames = DealNames


    def _deserialize(self, params):
        self._DealNames = params.get("DealNames")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeOrdersResponse(AbstractModel):
    """DescribeOrders response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: Number of orders
        :type TotalCount: int
        :param _Deals: Order array
        :type Deals: list of PgDeal
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._Deals = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def Deals(self):
        return self._Deals

    @Deals.setter
    def Deals(self, Deals):
        self._Deals = Deals

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("Deals") is not None:
            self._Deals = []
            for item in params.get("Deals"):
                obj = PgDeal()
                obj._deserialize(item)
                self._Deals.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeParameterTemplateAttributesRequest(AbstractModel):
    """DescribeParameterTemplateAttributes request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Parameter template ID
        :type TemplateId: str
        """
        self._TemplateId = None

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId


    def _deserialize(self, params):
        self._TemplateId = params.get("TemplateId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeParameterTemplateAttributesResponse(AbstractModel):
    """DescribeParameterTemplateAttributes response structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Parameter template ID
Note: This field may return null, indicating that no valid values can be obtained.
        :type TemplateId: str
        :param _TotalCount: Number of parameters contained in the parameter template
Note: This field may return null, indicating that no valid values can be obtained.
        :type TotalCount: int
        :param _ParamInfoSet: Parameter information contained in the parameter template
Note: This field may return null, indicating that no valid values can be obtained.
        :type ParamInfoSet: list of ParamInfo
        :param _TemplateName: Parameter template name
Note: This field may return null, indicating that no valid values can be obtained.
        :type TemplateName: str
        :param _DBMajorVersion: Database version applicable to a parameter template
Note: This field may return null, indicating that no valid values can be obtained.
        :type DBMajorVersion: str
        :param _DBEngine: Database engine applicable to a parameter template
Note: This field may return null, indicating that no valid values can be obtained.
        :type DBEngine: str
        :param _TemplateDescription: Parameter template description
Note: This field may return null, indicating that no valid values can be obtained.
        :type TemplateDescription: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TemplateId = None
        self._TotalCount = None
        self._ParamInfoSet = None
        self._TemplateName = None
        self._DBMajorVersion = None
        self._DBEngine = None
        self._TemplateDescription = None
        self._RequestId = None

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def ParamInfoSet(self):
        return self._ParamInfoSet

    @ParamInfoSet.setter
    def ParamInfoSet(self, ParamInfoSet):
        self._ParamInfoSet = ParamInfoSet

    @property
    def TemplateName(self):
        return self._TemplateName

    @TemplateName.setter
    def TemplateName(self, TemplateName):
        self._TemplateName = TemplateName

    @property
    def DBMajorVersion(self):
        return self._DBMajorVersion

    @DBMajorVersion.setter
    def DBMajorVersion(self, DBMajorVersion):
        self._DBMajorVersion = DBMajorVersion

    @property
    def DBEngine(self):
        return self._DBEngine

    @DBEngine.setter
    def DBEngine(self, DBEngine):
        self._DBEngine = DBEngine

    @property
    def TemplateDescription(self):
        return self._TemplateDescription

    @TemplateDescription.setter
    def TemplateDescription(self, TemplateDescription):
        self._TemplateDescription = TemplateDescription

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TemplateId = params.get("TemplateId")
        self._TotalCount = params.get("TotalCount")
        if params.get("ParamInfoSet") is not None:
            self._ParamInfoSet = []
            for item in params.get("ParamInfoSet"):
                obj = ParamInfo()
                obj._deserialize(item)
                self._ParamInfoSet.append(obj)
        self._TemplateName = params.get("TemplateName")
        self._DBMajorVersion = params.get("DBMajorVersion")
        self._DBEngine = params.get("DBEngine")
        self._TemplateDescription = params.get("TemplateDescription")
        self._RequestId = params.get("RequestId")


class DescribeParameterTemplatesRequest(AbstractModel):
    """DescribeParameterTemplates request structure.

    """

    def __init__(self):
        r"""
        :param _Filters: Filter conditions. Valid values: `TemplateName`, `TemplateId`, `DBMajorVersion`, `DBEngine`.
        :type Filters: list of Filter
        :param _Limit: The maximum number of results returned per page. Value range: 0-100. Default: `20`.
        :type Limit: int
        :param _Offset: Data offset
        :type Offset: int
        :param _OrderBy: Sorting metric. Valid values: `CreateTime`, `TemplateName`, `DBMajorVersion`.
        :type OrderBy: str
        :param _OrderByType: Sorting order. Valid values: `asc` (ascending order),`desc` (descending order).
        :type OrderByType: str
        """
        self._Filters = None
        self._Limit = None
        self._Offset = None
        self._OrderBy = None
        self._OrderByType = None

    @property
    def Filters(self):
        return self._Filters

    @Filters.setter
    def Filters(self, Filters):
        self._Filters = Filters

    @property
    def Limit(self):
        return self._Limit

    @Limit.setter
    def Limit(self, Limit):
        self._Limit = Limit

    @property
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, Offset):
        self._Offset = Offset

    @property
    def OrderBy(self):
        return self._OrderBy

    @OrderBy.setter
    def OrderBy(self, OrderBy):
        self._OrderBy = OrderBy

    @property
    def OrderByType(self):
        return self._OrderByType

    @OrderByType.setter
    def OrderByType(self, OrderByType):
        self._OrderByType = OrderByType


    def _deserialize(self, params):
        if params.get("Filters") is not None:
            self._Filters = []
            for item in params.get("Filters"):
                obj = Filter()
                obj._deserialize(item)
                self._Filters.append(obj)
        self._Limit = params.get("Limit")
        self._Offset = params.get("Offset")
        self._OrderBy = params.get("OrderBy")
        self._OrderByType = params.get("OrderByType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeParameterTemplatesResponse(AbstractModel):
    """DescribeParameterTemplates response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: The total number of eligible parameter templates
        :type TotalCount: int
        :param _ParameterTemplateSet: Parameter template list
        :type ParameterTemplateSet: list of ParameterTemplate
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._ParameterTemplateSet = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def ParameterTemplateSet(self):
        return self._ParameterTemplateSet

    @ParameterTemplateSet.setter
    def ParameterTemplateSet(self, ParameterTemplateSet):
        self._ParameterTemplateSet = ParameterTemplateSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("ParameterTemplateSet") is not None:
            self._ParameterTemplateSet = []
            for item in params.get("ParameterTemplateSet"):
                obj = ParameterTemplate()
                obj._deserialize(item)
                self._ParameterTemplateSet.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeParamsEventRequest(AbstractModel):
    """DescribeParamsEvent request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        """
        self._DBInstanceId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeParamsEventResponse(AbstractModel):
    """DescribeParamsEvent response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: Total number of modified parameters
        :type TotalCount: int
        :param _EventItems: Details of parameter modification events
        :type EventItems: list of EventItem
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._EventItems = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def EventItems(self):
        return self._EventItems

    @EventItems.setter
    def EventItems(self, EventItems):
        self._EventItems = EventItems

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("EventItems") is not None:
            self._EventItems = []
            for item in params.get("EventItems"):
                obj = EventItem()
                obj._deserialize(item)
                self._EventItems.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeProductConfigRequest(AbstractModel):
    """DescribeProductConfig request structure.

    """

    def __init__(self):
        r"""
        :param _Zone: AZ name
        :type Zone: str
        :param _DBEngine: Database engines. Valid values:
1. `postgresql` (TencentDB for PostgreSQL)
2. `mssql_compatible` (MSSQL compatible-TencentDB for PostgreSQL)
Default value: `postgresql`
        :type DBEngine: str
        """
        self._Zone = None
        self._DBEngine = None

    @property
    def Zone(self):
        return self._Zone

    @Zone.setter
    def Zone(self, Zone):
        self._Zone = Zone

    @property
    def DBEngine(self):
        return self._DBEngine

    @DBEngine.setter
    def DBEngine(self, DBEngine):
        self._DBEngine = DBEngine


    def _deserialize(self, params):
        self._Zone = params.get("Zone")
        self._DBEngine = params.get("DBEngine")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeProductConfigResponse(AbstractModel):
    """DescribeProductConfig response structure.

    """

    def __init__(self):
        r"""
        :param _SpecInfoList: Purchasable specification list.
        :type SpecInfoList: list of SpecInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._SpecInfoList = None
        self._RequestId = None

    @property
    def SpecInfoList(self):
        return self._SpecInfoList

    @SpecInfoList.setter
    def SpecInfoList(self, SpecInfoList):
        self._SpecInfoList = SpecInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("SpecInfoList") is not None:
            self._SpecInfoList = []
            for item in params.get("SpecInfoList"):
                obj = SpecInfo()
                obj._deserialize(item)
                self._SpecInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeReadOnlyGroupsRequest(AbstractModel):
    """DescribeReadOnlyGroups request structure.

    """

    def __init__(self):
        r"""
        :param _Filters: Filter instances by using one or more filters. Valid values:  `db-master-instance-id` (filter by the primary instance ID in string), `read-only-group-id` (filter by the read-only group ID in string),
        :type Filters: list of Filter
        :param _PageSize: The number of results per page. Default value: 10.
        :type PageSize: int
        :param _PageNumber: Specify which page is displayed. Default value: 1 (the first page).
        :type PageNumber: int
        :param _OrderBy: Sorting criterion. Valid values: `ROGroupId`, `CreateTime`, `Name`.
        :type OrderBy: str
        :param _OrderByType: Sorting order. Valid values: `desc`, `asc`.
        :type OrderByType: str
        """
        self._Filters = None
        self._PageSize = None
        self._PageNumber = None
        self._OrderBy = None
        self._OrderByType = None

    @property
    def Filters(self):
        return self._Filters

    @Filters.setter
    def Filters(self, Filters):
        self._Filters = Filters

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def PageNumber(self):
        return self._PageNumber

    @PageNumber.setter
    def PageNumber(self, PageNumber):
        self._PageNumber = PageNumber

    @property
    def OrderBy(self):
        return self._OrderBy

    @OrderBy.setter
    def OrderBy(self, OrderBy):
        self._OrderBy = OrderBy

    @property
    def OrderByType(self):
        return self._OrderByType

    @OrderByType.setter
    def OrderByType(self, OrderByType):
        self._OrderByType = OrderByType


    def _deserialize(self, params):
        if params.get("Filters") is not None:
            self._Filters = []
            for item in params.get("Filters"):
                obj = Filter()
                obj._deserialize(item)
                self._Filters.append(obj)
        self._PageSize = params.get("PageSize")
        self._PageNumber = params.get("PageNumber")
        self._OrderBy = params.get("OrderBy")
        self._OrderByType = params.get("OrderByType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeReadOnlyGroupsResponse(AbstractModel):
    """DescribeReadOnlyGroups response structure.

    """

    def __init__(self):
        r"""
        :param _ReadOnlyGroupList: RO group list
        :type ReadOnlyGroupList: list of ReadOnlyGroup
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._ReadOnlyGroupList = None
        self._RequestId = None

    @property
    def ReadOnlyGroupList(self):
        return self._ReadOnlyGroupList

    @ReadOnlyGroupList.setter
    def ReadOnlyGroupList(self, ReadOnlyGroupList):
        self._ReadOnlyGroupList = ReadOnlyGroupList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("ReadOnlyGroupList") is not None:
            self._ReadOnlyGroupList = []
            for item in params.get("ReadOnlyGroupList"):
                obj = ReadOnlyGroup()
                obj._deserialize(item)
                self._ReadOnlyGroupList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeRegionsRequest(AbstractModel):
    """DescribeRegions request structure.

    """


class DescribeRegionsResponse(AbstractModel):
    """DescribeRegions response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: Number of returned results.
        :type TotalCount: int
        :param _RegionSet: Region information set.
        :type RegionSet: list of RegionInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._RegionSet = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def RegionSet(self):
        return self._RegionSet

    @RegionSet.setter
    def RegionSet(self, RegionSet):
        self._RegionSet = RegionSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("RegionSet") is not None:
            self._RegionSet = []
            for item in params.get("RegionSet"):
                obj = RegionInfo()
                obj._deserialize(item)
                self._RegionSet.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeServerlessDBInstancesRequest(AbstractModel):
    """DescribeServerlessDBInstances request structure.

    """

    def __init__(self):
        r"""
        :param _Filter: Query conditions
        :type Filter: list of Filter
        :param _Limit: The number of queries
        :type Limit: int
        :param _Offset: The offset value
        :type Offset: int
        :param _OrderBy: Sorting metric. Currently, only "CreateTime" (instance creation time) is supported.
        :type OrderBy: str
        :param _OrderByType: Sorting order. Ascending and descending are supported.
        :type OrderByType: str
        """
        self._Filter = None
        self._Limit = None
        self._Offset = None
        self._OrderBy = None
        self._OrderByType = None

    @property
    def Filter(self):
        return self._Filter

    @Filter.setter
    def Filter(self, Filter):
        self._Filter = Filter

    @property
    def Limit(self):
        return self._Limit

    @Limit.setter
    def Limit(self, Limit):
        self._Limit = Limit

    @property
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, Offset):
        self._Offset = Offset

    @property
    def OrderBy(self):
        return self._OrderBy

    @OrderBy.setter
    def OrderBy(self, OrderBy):
        self._OrderBy = OrderBy

    @property
    def OrderByType(self):
        return self._OrderByType

    @OrderByType.setter
    def OrderByType(self, OrderByType):
        self._OrderByType = OrderByType


    def _deserialize(self, params):
        if params.get("Filter") is not None:
            self._Filter = []
            for item in params.get("Filter"):
                obj = Filter()
                obj._deserialize(item)
                self._Filter.append(obj)
        self._Limit = params.get("Limit")
        self._Offset = params.get("Offset")
        self._OrderBy = params.get("OrderBy")
        self._OrderByType = params.get("OrderByType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeServerlessDBInstancesResponse(AbstractModel):
    """DescribeServerlessDBInstances response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: The number of query results
        :type TotalCount: int
        :param _DBInstanceSet: Query results
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBInstanceSet: list of ServerlessDBInstance
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._DBInstanceSet = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def DBInstanceSet(self):
        return self._DBInstanceSet

    @DBInstanceSet.setter
    def DBInstanceSet(self, DBInstanceSet):
        self._DBInstanceSet = DBInstanceSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("DBInstanceSet") is not None:
            self._DBInstanceSet = []
            for item in params.get("DBInstanceSet"):
                obj = ServerlessDBInstance()
                obj._deserialize(item)
                self._DBInstanceSet.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeSlowQueryAnalysisRequest(AbstractModel):
    """DescribeSlowQueryAnalysis request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID.
        :type DBInstanceId: str
        :param _StartTime: Start timestamp of the query range in the format of "YYYY-MM-DD HH:mm:ss". The log is retained for seven days by default, so the start timestamp must fall within the retention period.
        :type StartTime: str
        :param _EndTime: End timestamp of the query range in the format of "YYYY-MM-DD HH:mm:ss".
        :type EndTime: str
        :param _DatabaseName: Filter by database name. This parameter is optional.
        :type DatabaseName: str
        :param _OrderBy: Sort by field. Valid values: `CallNum`, `CostTime`, `AvgCostTime`. Default value: `CallNum`.
        :type OrderBy: str
        :param _OrderByType: Sorting order. Valid values: `asc` (ascending), `desc` (descending). Default value: `desc`.
        :type OrderByType: str
        :param _Limit: Number of entries per page. Value range: [1,100]. Default value: `50`.
        :type Limit: int
        :param _Offset: Pagination offset. Value range: [0,INF). Default value: `0`.
        :type Offset: int
        """
        self._DBInstanceId = None
        self._StartTime = None
        self._EndTime = None
        self._DatabaseName = None
        self._OrderBy = None
        self._OrderByType = None
        self._Limit = None
        self._Offset = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

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
    def DatabaseName(self):
        return self._DatabaseName

    @DatabaseName.setter
    def DatabaseName(self, DatabaseName):
        self._DatabaseName = DatabaseName

    @property
    def OrderBy(self):
        return self._OrderBy

    @OrderBy.setter
    def OrderBy(self, OrderBy):
        self._OrderBy = OrderBy

    @property
    def OrderByType(self):
        return self._OrderByType

    @OrderByType.setter
    def OrderByType(self, OrderByType):
        self._OrderByType = OrderByType

    @property
    def Limit(self):
        return self._Limit

    @Limit.setter
    def Limit(self, Limit):
        self._Limit = Limit

    @property
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, Offset):
        self._Offset = Offset


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._DatabaseName = params.get("DatabaseName")
        self._OrderBy = params.get("OrderBy")
        self._OrderByType = params.get("OrderByType")
        self._Limit = params.get("Limit")
        self._Offset = params.get("Offset")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeSlowQueryAnalysisResponse(AbstractModel):
    """DescribeSlowQueryAnalysis response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: The total number of query results.
        :type TotalCount: int
        :param _Detail: Detailed analysis.
        :type Detail: :class:`tencentcloud.postgres.v20170312.models.Detail`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._Detail = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def Detail(self):
        return self._Detail

    @Detail.setter
    def Detail(self, Detail):
        self._Detail = Detail

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("Detail") is not None:
            self._Detail = Detail()
            self._Detail._deserialize(params.get("Detail"))
        self._RequestId = params.get("RequestId")


class DescribeSlowQueryListRequest(AbstractModel):
    """DescribeSlowQueryList request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID.
        :type DBInstanceId: str
        :param _StartTime: Start timestamp of the query range in the format of "YYYY-MM-DD HH:mm:ss". The log is retained for seven days by default, so the start timestamp must fall within the retention period.
        :type StartTime: str
        :param _EndTime: End timestamp of the query range in the format of "YYYY-MM-DD HH:mm:ss".
        :type EndTime: str
        :param _DatabaseName: Filter by database name. This parameter is optional.
        :type DatabaseName: str
        :param _OrderByType: Sorting order. Valid values: `asc` (ascending), `desc` (descending). Default value: `desc`.
        :type OrderByType: str
        :param _OrderBy: Sort by field. Valid values: `SessionStartTime` (default), `Duration`.
        :type OrderBy: str
        :param _Limit: Number of entries per page. Value range: [1,100]. Default value: `20`.
        :type Limit: int
        :param _Offset: Pagination offset. Value range: [0,INF). Default value: `0`.
        :type Offset: int
        """
        self._DBInstanceId = None
        self._StartTime = None
        self._EndTime = None
        self._DatabaseName = None
        self._OrderByType = None
        self._OrderBy = None
        self._Limit = None
        self._Offset = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

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
    def DatabaseName(self):
        return self._DatabaseName

    @DatabaseName.setter
    def DatabaseName(self, DatabaseName):
        self._DatabaseName = DatabaseName

    @property
    def OrderByType(self):
        return self._OrderByType

    @OrderByType.setter
    def OrderByType(self, OrderByType):
        self._OrderByType = OrderByType

    @property
    def OrderBy(self):
        return self._OrderBy

    @OrderBy.setter
    def OrderBy(self, OrderBy):
        self._OrderBy = OrderBy

    @property
    def Limit(self):
        return self._Limit

    @Limit.setter
    def Limit(self, Limit):
        self._Limit = Limit

    @property
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, Offset):
        self._Offset = Offset


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._DatabaseName = params.get("DatabaseName")
        self._OrderByType = params.get("OrderByType")
        self._OrderBy = params.get("OrderBy")
        self._Limit = params.get("Limit")
        self._Offset = params.get("Offset")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeSlowQueryListResponse(AbstractModel):
    """DescribeSlowQueryList response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: The total number of slow query statements during the specified period of time.
        :type TotalCount: int
        :param _DurationAnalysis: Analysis of the execution time of slow query statements by classifying them to different time ranges. These slow query statements fall within the query range you specified in the request parameters.
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DurationAnalysis: list of DurationAnalysis
        :param _RawSlowQueryList: The list of slow query details during the specified period of time.
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type RawSlowQueryList: list of RawSlowQuery
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._DurationAnalysis = None
        self._RawSlowQueryList = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def DurationAnalysis(self):
        return self._DurationAnalysis

    @DurationAnalysis.setter
    def DurationAnalysis(self, DurationAnalysis):
        self._DurationAnalysis = DurationAnalysis

    @property
    def RawSlowQueryList(self):
        return self._RawSlowQueryList

    @RawSlowQueryList.setter
    def RawSlowQueryList(self, RawSlowQueryList):
        self._RawSlowQueryList = RawSlowQueryList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("DurationAnalysis") is not None:
            self._DurationAnalysis = []
            for item in params.get("DurationAnalysis"):
                obj = DurationAnalysis()
                obj._deserialize(item)
                self._DurationAnalysis.append(obj)
        if params.get("RawSlowQueryList") is not None:
            self._RawSlowQueryList = []
            for item in params.get("RawSlowQueryList"):
                obj = RawSlowQuery()
                obj._deserialize(item)
                self._RawSlowQueryList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeZonesRequest(AbstractModel):
    """DescribeZones request structure.

    """


class DescribeZonesResponse(AbstractModel):
    """DescribeZones response structure.

    """

    def __init__(self):
        r"""
        :param _TotalCount: Number of returned results.
        :type TotalCount: int
        :param _ZoneSet: AZ information set.
        :type ZoneSet: list of ZoneInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalCount = None
        self._ZoneSet = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def ZoneSet(self):
        return self._ZoneSet

    @ZoneSet.setter
    def ZoneSet(self, ZoneSet):
        self._ZoneSet = ZoneSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("ZoneSet") is not None:
            self._ZoneSet = []
            for item in params.get("ZoneSet"):
                obj = ZoneInfo()
                obj._deserialize(item)
                self._ZoneSet.append(obj)
        self._RequestId = params.get("RequestId")


class DestroyDBInstanceRequest(AbstractModel):
    """DestroyDBInstance request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: The ID of the instance to be eliminated
        :type DBInstanceId: str
        """
        self._DBInstanceId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DestroyDBInstanceResponse(AbstractModel):
    """DestroyDBInstance response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class Detail(AbstractModel):
    """Details returned by the `DescribeSlowQueryAnalysis` API

    """

    def __init__(self):
        r"""
        :param _TotalTime: The total execution time (in ms) of all slow query statements during the specified period of time
        :type TotalTime: float
        :param _TotalCallNum: The total number of all slow query statements during the specified period of time
        :type TotalCallNum: int
        :param _AnalysisItems: The statistical analysis list of slow queries
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type AnalysisItems: list of AnalysisItems
        """
        self._TotalTime = None
        self._TotalCallNum = None
        self._AnalysisItems = None

    @property
    def TotalTime(self):
        return self._TotalTime

    @TotalTime.setter
    def TotalTime(self, TotalTime):
        self._TotalTime = TotalTime

    @property
    def TotalCallNum(self):
        return self._TotalCallNum

    @TotalCallNum.setter
    def TotalCallNum(self, TotalCallNum):
        self._TotalCallNum = TotalCallNum

    @property
    def AnalysisItems(self):
        return self._AnalysisItems

    @AnalysisItems.setter
    def AnalysisItems(self, AnalysisItems):
        self._AnalysisItems = AnalysisItems


    def _deserialize(self, params):
        self._TotalTime = params.get("TotalTime")
        self._TotalCallNum = params.get("TotalCallNum")
        if params.get("AnalysisItems") is not None:
            self._AnalysisItems = []
            for item in params.get("AnalysisItems"):
                obj = AnalysisItems()
                obj._deserialize(item)
                self._AnalysisItems.append(obj)
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DisIsolateDBInstancesRequest(AbstractModel):
    """DisIsolateDBInstances request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceIdSet: List of resource IDs. Note that currently you cannot remove multiple instances from isolation at the same time. Only one instance ID can be passed in here.
        :type DBInstanceIdSet: list of str
        :param _Period: The valid period (in months) of the monthly-subscribed instance when removing it from isolation
        :type Period: int
        :param _AutoVoucher: Whether to use vouchers. Valid values: `true` (yes), `false` (no). Default value: `false`.
        :type AutoVoucher: bool
        :param _VoucherIds: Voucher ID list
        :type VoucherIds: list of str
        """
        self._DBInstanceIdSet = None
        self._Period = None
        self._AutoVoucher = None
        self._VoucherIds = None

    @property
    def DBInstanceIdSet(self):
        return self._DBInstanceIdSet

    @DBInstanceIdSet.setter
    def DBInstanceIdSet(self, DBInstanceIdSet):
        self._DBInstanceIdSet = DBInstanceIdSet

    @property
    def Period(self):
        return self._Period

    @Period.setter
    def Period(self, Period):
        self._Period = Period

    @property
    def AutoVoucher(self):
        return self._AutoVoucher

    @AutoVoucher.setter
    def AutoVoucher(self, AutoVoucher):
        self._AutoVoucher = AutoVoucher

    @property
    def VoucherIds(self):
        return self._VoucherIds

    @VoucherIds.setter
    def VoucherIds(self, VoucherIds):
        self._VoucherIds = VoucherIds


    def _deserialize(self, params):
        self._DBInstanceIdSet = params.get("DBInstanceIdSet")
        self._Period = params.get("Period")
        self._AutoVoucher = params.get("AutoVoucher")
        self._VoucherIds = params.get("VoucherIds")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DisIsolateDBInstancesResponse(AbstractModel):
    """DisIsolateDBInstances response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class DurationAnalysis(AbstractModel):
    """Analyze the execution time of slow query statements by classifying them to different time ranges

    """

    def __init__(self):
        r"""
        :param _TimeSegment: Time range
        :type TimeSegment: str
        :param _Count: The number of slow query statements whose execution time falls within the time range
        :type Count: int
        """
        self._TimeSegment = None
        self._Count = None

    @property
    def TimeSegment(self):
        return self._TimeSegment

    @TimeSegment.setter
    def TimeSegment(self, TimeSegment):
        self._TimeSegment = TimeSegment

    @property
    def Count(self):
        return self._Count

    @Count.setter
    def Count(self, Count):
        self._Count = Count


    def _deserialize(self, params):
        self._TimeSegment = params.get("TimeSegment")
        self._Count = params.get("Count")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class EncryptionKey(AbstractModel):
    """KMS key information

    """

    def __init__(self):
        r"""
        :param _KeyId: Encrypted KeyId of KMS instance
Note: This field may return `null`, indicating that no valid value can be obtained.
        :type KeyId: str
        :param _KeyAlias: Encryption key alias of KMS instance 
Note: This field may return `null`, indicating that no valid value can be obtained.
        :type KeyAlias: str
        :param _DEKCipherTextBlob: Instance DEK ciphertext
Note: This field may return `null`, indicating that no valid value can be obtained.
        :type DEKCipherTextBlob: str
        :param _IsEnabled: Whether the key is enabled. Valid values: `1` (yes), `0` (no)
Note: This field may return `null`, indicating that no valid value can be obtained.
        :type IsEnabled: int
        :param _KeyRegion: Region where KMS key resides
Note: This field may return `null`, indicating that no valid value can be obtained.
        :type KeyRegion: str
        :param _CreateTime: DEK key creation time
Note: This field may return `null`, indicating that no valid value can be obtained.
        :type CreateTime: str
        """
        self._KeyId = None
        self._KeyAlias = None
        self._DEKCipherTextBlob = None
        self._IsEnabled = None
        self._KeyRegion = None
        self._CreateTime = None

    @property
    def KeyId(self):
        return self._KeyId

    @KeyId.setter
    def KeyId(self, KeyId):
        self._KeyId = KeyId

    @property
    def KeyAlias(self):
        return self._KeyAlias

    @KeyAlias.setter
    def KeyAlias(self, KeyAlias):
        self._KeyAlias = KeyAlias

    @property
    def DEKCipherTextBlob(self):
        return self._DEKCipherTextBlob

    @DEKCipherTextBlob.setter
    def DEKCipherTextBlob(self, DEKCipherTextBlob):
        self._DEKCipherTextBlob = DEKCipherTextBlob

    @property
    def IsEnabled(self):
        return self._IsEnabled

    @IsEnabled.setter
    def IsEnabled(self, IsEnabled):
        self._IsEnabled = IsEnabled

    @property
    def KeyRegion(self):
        return self._KeyRegion

    @KeyRegion.setter
    def KeyRegion(self, KeyRegion):
        self._KeyRegion = KeyRegion

    @property
    def CreateTime(self):
        return self._CreateTime

    @CreateTime.setter
    def CreateTime(self, CreateTime):
        self._CreateTime = CreateTime


    def _deserialize(self, params):
        self._KeyId = params.get("KeyId")
        self._KeyAlias = params.get("KeyAlias")
        self._DEKCipherTextBlob = params.get("DEKCipherTextBlob")
        self._IsEnabled = params.get("IsEnabled")
        self._KeyRegion = params.get("KeyRegion")
        self._CreateTime = params.get("CreateTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ErrLogDetail(AbstractModel):
    """Error log details

    """

    def __init__(self):
        r"""
        :param _UserName: Username
        :type UserName: str
        :param _Database: Database name
        :type Database: str
        :param _ErrTime: Error occurrence time
        :type ErrTime: str
        :param _ErrMsg: Error message
        :type ErrMsg: str
        """
        self._UserName = None
        self._Database = None
        self._ErrTime = None
        self._ErrMsg = None

    @property
    def UserName(self):
        return self._UserName

    @UserName.setter
    def UserName(self, UserName):
        self._UserName = UserName

    @property
    def Database(self):
        return self._Database

    @Database.setter
    def Database(self, Database):
        self._Database = Database

    @property
    def ErrTime(self):
        return self._ErrTime

    @ErrTime.setter
    def ErrTime(self, ErrTime):
        self._ErrTime = ErrTime

    @property
    def ErrMsg(self):
        return self._ErrMsg

    @ErrMsg.setter
    def ErrMsg(self, ErrMsg):
        self._ErrMsg = ErrMsg


    def _deserialize(self, params):
        self._UserName = params.get("UserName")
        self._Database = params.get("Database")
        self._ErrTime = params.get("ErrTime")
        self._ErrMsg = params.get("ErrMsg")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class EventInfo(AbstractModel):
    """Parameter modification event information

    """

    def __init__(self):
        r"""
        :param _ParamName: Parameter name
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ParamName: str
        :param _OldValue: Original parameter value
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type OldValue: str
        :param _NewValue: New parameter value in this modification event
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type NewValue: str
        :param _ModifyTime: Start time of parameter modification
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ModifyTime: str
        :param _EffectiveTime: Start time when the modified parameter takes effect
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type EffectiveTime: str
        :param _State: Modification status
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type State: str
        :param _Operator: Operator (generally, the value is the UIN of a sub-user)
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type Operator: str
        :param _EventLog: Event log
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type EventLog: str
        """
        self._ParamName = None
        self._OldValue = None
        self._NewValue = None
        self._ModifyTime = None
        self._EffectiveTime = None
        self._State = None
        self._Operator = None
        self._EventLog = None

    @property
    def ParamName(self):
        return self._ParamName

    @ParamName.setter
    def ParamName(self, ParamName):
        self._ParamName = ParamName

    @property
    def OldValue(self):
        return self._OldValue

    @OldValue.setter
    def OldValue(self, OldValue):
        self._OldValue = OldValue

    @property
    def NewValue(self):
        return self._NewValue

    @NewValue.setter
    def NewValue(self, NewValue):
        self._NewValue = NewValue

    @property
    def ModifyTime(self):
        return self._ModifyTime

    @ModifyTime.setter
    def ModifyTime(self, ModifyTime):
        self._ModifyTime = ModifyTime

    @property
    def EffectiveTime(self):
        return self._EffectiveTime

    @EffectiveTime.setter
    def EffectiveTime(self, EffectiveTime):
        self._EffectiveTime = EffectiveTime

    @property
    def State(self):
        return self._State

    @State.setter
    def State(self, State):
        self._State = State

    @property
    def Operator(self):
        return self._Operator

    @Operator.setter
    def Operator(self, Operator):
        self._Operator = Operator

    @property
    def EventLog(self):
        return self._EventLog

    @EventLog.setter
    def EventLog(self, EventLog):
        self._EventLog = EventLog


    def _deserialize(self, params):
        self._ParamName = params.get("ParamName")
        self._OldValue = params.get("OldValue")
        self._NewValue = params.get("NewValue")
        self._ModifyTime = params.get("ModifyTime")
        self._EffectiveTime = params.get("EffectiveTime")
        self._State = params.get("State")
        self._Operator = params.get("Operator")
        self._EventLog = params.get("EventLog")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class EventItem(AbstractModel):
    """Modification details of one parameter

    """

    def __init__(self):
        r"""
        :param _ParamName: Parameter name
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ParamName: str
        :param _EventCount: The number of modification events
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type EventCount: int
        :param _EventDetail: Modification event details
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type EventDetail: list of EventInfo
        """
        self._ParamName = None
        self._EventCount = None
        self._EventDetail = None

    @property
    def ParamName(self):
        return self._ParamName

    @ParamName.setter
    def ParamName(self, ParamName):
        self._ParamName = ParamName

    @property
    def EventCount(self):
        return self._EventCount

    @EventCount.setter
    def EventCount(self, EventCount):
        self._EventCount = EventCount

    @property
    def EventDetail(self):
        return self._EventDetail

    @EventDetail.setter
    def EventDetail(self, EventDetail):
        self._EventDetail = EventDetail


    def _deserialize(self, params):
        self._ParamName = params.get("ParamName")
        self._EventCount = params.get("EventCount")
        if params.get("EventDetail") is not None:
            self._EventDetail = []
            for item in params.get("EventDetail"):
                obj = EventInfo()
                obj._deserialize(item)
                self._EventDetail.append(obj)
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class Filter(AbstractModel):
    """Key-value pair filter for conditional filtering queries, such as filter ID and name
    * If more than one filter exists, the logical relationship between these filters is `AND`.
    * If multiple values exist in one filter, the logical relationship between these values is `OR`.

    """

    def __init__(self):
        r"""
        :param _Name: Filter name.
        :type Name: str
        :param _Values: One or more filter values.
        :type Values: list of str
        """
        self._Name = None
        self._Values = None

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, Name):
        self._Name = Name

    @property
    def Values(self):
        return self._Values

    @Values.setter
    def Values(self, Values):
        self._Values = Values


    def _deserialize(self, params):
        self._Name = params.get("Name")
        self._Values = params.get("Values")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class InitDBInstancesRequest(AbstractModel):
    """InitDBInstances request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceIdSet: Instance ID set.
        :type DBInstanceIdSet: list of str
        :param _AdminName: Instance admin account username.
        :type AdminName: str
        :param _AdminPassword: Password corresponding to instance root account username.
        :type AdminPassword: str
        :param _Charset: Instance character set. Valid values: UTF8, LATIN1.
        :type Charset: str
        """
        self._DBInstanceIdSet = None
        self._AdminName = None
        self._AdminPassword = None
        self._Charset = None

    @property
    def DBInstanceIdSet(self):
        return self._DBInstanceIdSet

    @DBInstanceIdSet.setter
    def DBInstanceIdSet(self, DBInstanceIdSet):
        self._DBInstanceIdSet = DBInstanceIdSet

    @property
    def AdminName(self):
        return self._AdminName

    @AdminName.setter
    def AdminName(self, AdminName):
        self._AdminName = AdminName

    @property
    def AdminPassword(self):
        return self._AdminPassword

    @AdminPassword.setter
    def AdminPassword(self, AdminPassword):
        self._AdminPassword = AdminPassword

    @property
    def Charset(self):
        return self._Charset

    @Charset.setter
    def Charset(self, Charset):
        self._Charset = Charset


    def _deserialize(self, params):
        self._DBInstanceIdSet = params.get("DBInstanceIdSet")
        self._AdminName = params.get("AdminName")
        self._AdminPassword = params.get("AdminPassword")
        self._Charset = params.get("Charset")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class InitDBInstancesResponse(AbstractModel):
    """InitDBInstances response structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceIdSet: Instance ID set.
        :type DBInstanceIdSet: list of str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DBInstanceIdSet = None
        self._RequestId = None

    @property
    def DBInstanceIdSet(self):
        return self._DBInstanceIdSet

    @DBInstanceIdSet.setter
    def DBInstanceIdSet(self, DBInstanceIdSet):
        self._DBInstanceIdSet = DBInstanceIdSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._DBInstanceIdSet = params.get("DBInstanceIdSet")
        self._RequestId = params.get("RequestId")


class InquiryPriceCreateDBInstancesRequest(AbstractModel):
    """InquiryPriceCreateDBInstances request structure.

    """

    def __init__(self):
        r"""
        :param _Zone: AZ ID, which can be obtained through the `Zone` field in the returned value of the `DescribeZones` API.
        :type Zone: str
        :param _SpecCode: Specification ID, which can be obtained through the `SpecCode` field in the returned value of the `DescribeProductConfig` API.
        :type SpecCode: str
        :param _Storage: Storage capacity size in GB.
        :type Storage: int
        :param _InstanceCount: Number of instances. Maximum value: 100. If you need to create more instances at a time, please contact customer service.
        :type InstanceCount: int
        :param _Period: Length of purchase in months. Currently, only 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 24, and 36 are supported.
        :type Period: int
        :param _Pid: [Disused] Billing ID, which can be obtained through the `Pid` field in the returned value of the `DescribeProductConfig` API.
        :type Pid: int
        :param _InstanceChargeType: Instance billing type. Valid value: POSTPAID_BY_HOUR (pay-as-you-go)
        :type InstanceChargeType: str
        :param _InstanceType: Instance type. Default value: `primary`. Valid values:
`primary` (dual-server high-availability, one-primary-one-standby)
`readonly` (read-only instance)
        :type InstanceType: str
        :param _DBEngine: 
        :type DBEngine: str
        """
        self._Zone = None
        self._SpecCode = None
        self._Storage = None
        self._InstanceCount = None
        self._Period = None
        self._Pid = None
        self._InstanceChargeType = None
        self._InstanceType = None
        self._DBEngine = None

    @property
    def Zone(self):
        return self._Zone

    @Zone.setter
    def Zone(self, Zone):
        self._Zone = Zone

    @property
    def SpecCode(self):
        return self._SpecCode

    @SpecCode.setter
    def SpecCode(self, SpecCode):
        self._SpecCode = SpecCode

    @property
    def Storage(self):
        return self._Storage

    @Storage.setter
    def Storage(self, Storage):
        self._Storage = Storage

    @property
    def InstanceCount(self):
        return self._InstanceCount

    @InstanceCount.setter
    def InstanceCount(self, InstanceCount):
        self._InstanceCount = InstanceCount

    @property
    def Period(self):
        return self._Period

    @Period.setter
    def Period(self, Period):
        self._Period = Period

    @property
    def Pid(self):
        return self._Pid

    @Pid.setter
    def Pid(self, Pid):
        self._Pid = Pid

    @property
    def InstanceChargeType(self):
        return self._InstanceChargeType

    @InstanceChargeType.setter
    def InstanceChargeType(self, InstanceChargeType):
        self._InstanceChargeType = InstanceChargeType

    @property
    def InstanceType(self):
        return self._InstanceType

    @InstanceType.setter
    def InstanceType(self, InstanceType):
        self._InstanceType = InstanceType

    @property
    def DBEngine(self):
        return self._DBEngine

    @DBEngine.setter
    def DBEngine(self, DBEngine):
        self._DBEngine = DBEngine


    def _deserialize(self, params):
        self._Zone = params.get("Zone")
        self._SpecCode = params.get("SpecCode")
        self._Storage = params.get("Storage")
        self._InstanceCount = params.get("InstanceCount")
        self._Period = params.get("Period")
        self._Pid = params.get("Pid")
        self._InstanceChargeType = params.get("InstanceChargeType")
        self._InstanceType = params.get("InstanceType")
        self._DBEngine = params.get("DBEngine")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class InquiryPriceCreateDBInstancesResponse(AbstractModel):
    """InquiryPriceCreateDBInstances response structure.

    """

    def __init__(self):
        r"""
        :param _OriginalPrice: Published price in US Cent
        :type OriginalPrice: int
        :param _Price: Discounted total amount in US Cent
        :type Price: int
        :param _Currency: Currency, such as USD.
        :type Currency: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._OriginalPrice = None
        self._Price = None
        self._Currency = None
        self._RequestId = None

    @property
    def OriginalPrice(self):
        return self._OriginalPrice

    @OriginalPrice.setter
    def OriginalPrice(self, OriginalPrice):
        self._OriginalPrice = OriginalPrice

    @property
    def Price(self):
        return self._Price

    @Price.setter
    def Price(self, Price):
        self._Price = Price

    @property
    def Currency(self):
        return self._Currency

    @Currency.setter
    def Currency(self, Currency):
        self._Currency = Currency

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._OriginalPrice = params.get("OriginalPrice")
        self._Price = params.get("Price")
        self._Currency = params.get("Currency")
        self._RequestId = params.get("RequestId")


class InquiryPriceRenewDBInstanceRequest(AbstractModel):
    """InquiryPriceRenewDBInstance request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _Period: Renewal duration in months. Maximum value: 48
        :type Period: int
        """
        self._DBInstanceId = None
        self._Period = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def Period(self):
        return self._Period

    @Period.setter
    def Period(self, Period):
        self._Period = Period


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._Period = params.get("Period")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class InquiryPriceRenewDBInstanceResponse(AbstractModel):
    """InquiryPriceRenewDBInstance response structure.

    """

    def __init__(self):
        r"""
        :param _OriginalPrice: Published price in cents. For example, 24650 indicates 246.5 USD.
        :type OriginalPrice: int
        :param _Price: Discounted total amount. For example, 24650 indicates 246.5 USD.
        :type Price: int
        :param _Currency: Currency, such as USD.
        :type Currency: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._OriginalPrice = None
        self._Price = None
        self._Currency = None
        self._RequestId = None

    @property
    def OriginalPrice(self):
        return self._OriginalPrice

    @OriginalPrice.setter
    def OriginalPrice(self, OriginalPrice):
        self._OriginalPrice = OriginalPrice

    @property
    def Price(self):
        return self._Price

    @Price.setter
    def Price(self, Price):
        self._Price = Price

    @property
    def Currency(self):
        return self._Currency

    @Currency.setter
    def Currency(self, Currency):
        self._Currency = Currency

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._OriginalPrice = params.get("OriginalPrice")
        self._Price = params.get("Price")
        self._Currency = params.get("Currency")
        self._RequestId = params.get("RequestId")


class InquiryPriceUpgradeDBInstanceRequest(AbstractModel):
    """InquiryPriceUpgradeDBInstance request structure.

    """

    def __init__(self):
        r"""
        :param _Storage: Instance disk size in GB
        :type Storage: int
        :param _Memory: Instance memory size in GB
        :type Memory: int
        :param _DBInstanceId: Instance ID in the format of postgres-hez4fh0v
        :type DBInstanceId: str
        :param _InstanceChargeType: Instance billing type. Valid value: `POSTPAID_BY_HOUR` (pay-as-you-go hourly)
        :type InstanceChargeType: str
        """
        self._Storage = None
        self._Memory = None
        self._DBInstanceId = None
        self._InstanceChargeType = None

    @property
    def Storage(self):
        return self._Storage

    @Storage.setter
    def Storage(self, Storage):
        self._Storage = Storage

    @property
    def Memory(self):
        return self._Memory

    @Memory.setter
    def Memory(self, Memory):
        self._Memory = Memory

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def InstanceChargeType(self):
        return self._InstanceChargeType

    @InstanceChargeType.setter
    def InstanceChargeType(self, InstanceChargeType):
        self._InstanceChargeType = InstanceChargeType


    def _deserialize(self, params):
        self._Storage = params.get("Storage")
        self._Memory = params.get("Memory")
        self._DBInstanceId = params.get("DBInstanceId")
        self._InstanceChargeType = params.get("InstanceChargeType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class InquiryPriceUpgradeDBInstanceResponse(AbstractModel):
    """InquiryPriceUpgradeDBInstance response structure.

    """

    def __init__(self):
        r"""
        :param _OriginalPrice: Total cost before discount.
        :type OriginalPrice: int
        :param _Price: Discounted total amount
        :type Price: int
        :param _Currency: Currency, such as USD.
        :type Currency: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._OriginalPrice = None
        self._Price = None
        self._Currency = None
        self._RequestId = None

    @property
    def OriginalPrice(self):
        return self._OriginalPrice

    @OriginalPrice.setter
    def OriginalPrice(self, OriginalPrice):
        self._OriginalPrice = OriginalPrice

    @property
    def Price(self):
        return self._Price

    @Price.setter
    def Price(self, Price):
        self._Price = Price

    @property
    def Currency(self):
        return self._Currency

    @Currency.setter
    def Currency(self, Currency):
        self._Currency = Currency

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._OriginalPrice = params.get("OriginalPrice")
        self._Price = params.get("Price")
        self._Currency = params.get("Currency")
        self._RequestId = params.get("RequestId")


class IsolateDBInstancesRequest(AbstractModel):
    """IsolateDBInstances request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceIdSet: List of instance IDs. Note that currently you cannot isolate multiple instances at the same time. Only one instance ID can be passed in here.
        :type DBInstanceIdSet: list of str
        """
        self._DBInstanceIdSet = None

    @property
    def DBInstanceIdSet(self):
        return self._DBInstanceIdSet

    @DBInstanceIdSet.setter
    def DBInstanceIdSet(self, DBInstanceIdSet):
        self._DBInstanceIdSet = DBInstanceIdSet


    def _deserialize(self, params):
        self._DBInstanceIdSet = params.get("DBInstanceIdSet")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class IsolateDBInstancesResponse(AbstractModel):
    """IsolateDBInstances response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class LogBackup(AbstractModel):
    """Log backup information of a database

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _Id: Unique ID of a backup file
        :type Id: str
        :param _Name: Backup file name
        :type Name: str
        :param _BackupMethod: Backup method, including physical and logical.
        :type BackupMethod: str
        :param _BackupMode: Backup mode, including automatic and manual.
        :type BackupMode: str
        :param _State: Backup task status
        :type State: str
        :param _Size: Backup set size in bytes
        :type Size: int
        :param _StartTime: Backup start time
        :type StartTime: str
        :param _FinishTime: Backup end time
        :type FinishTime: str
        :param _ExpireTime: Backup expiration time
        :type ExpireTime: str
        """
        self._DBInstanceId = None
        self._Id = None
        self._Name = None
        self._BackupMethod = None
        self._BackupMode = None
        self._State = None
        self._Size = None
        self._StartTime = None
        self._FinishTime = None
        self._ExpireTime = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def Id(self):
        return self._Id

    @Id.setter
    def Id(self, Id):
        self._Id = Id

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, Name):
        self._Name = Name

    @property
    def BackupMethod(self):
        return self._BackupMethod

    @BackupMethod.setter
    def BackupMethod(self, BackupMethod):
        self._BackupMethod = BackupMethod

    @property
    def BackupMode(self):
        return self._BackupMode

    @BackupMode.setter
    def BackupMode(self, BackupMode):
        self._BackupMode = BackupMode

    @property
    def State(self):
        return self._State

    @State.setter
    def State(self, State):
        self._State = State

    @property
    def Size(self):
        return self._Size

    @Size.setter
    def Size(self, Size):
        self._Size = Size

    @property
    def StartTime(self):
        return self._StartTime

    @StartTime.setter
    def StartTime(self, StartTime):
        self._StartTime = StartTime

    @property
    def FinishTime(self):
        return self._FinishTime

    @FinishTime.setter
    def FinishTime(self, FinishTime):
        self._FinishTime = FinishTime

    @property
    def ExpireTime(self):
        return self._ExpireTime

    @ExpireTime.setter
    def ExpireTime(self, ExpireTime):
        self._ExpireTime = ExpireTime


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._Id = params.get("Id")
        self._Name = params.get("Name")
        self._BackupMethod = params.get("BackupMethod")
        self._BackupMode = params.get("BackupMode")
        self._State = params.get("State")
        self._Size = params.get("Size")
        self._StartTime = params.get("StartTime")
        self._FinishTime = params.get("FinishTime")
        self._ExpireTime = params.get("ExpireTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyAccountRemarkRequest(AbstractModel):
    """ModifyAccountRemark request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of postgres-4wdeb0zv
        :type DBInstanceId: str
        :param _UserName: Instance username
        :type UserName: str
        :param _Remark: New remarks corresponding to user `UserName`
        :type Remark: str
        """
        self._DBInstanceId = None
        self._UserName = None
        self._Remark = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def UserName(self):
        return self._UserName

    @UserName.setter
    def UserName(self, UserName):
        self._UserName = UserName

    @property
    def Remark(self):
        return self._Remark

    @Remark.setter
    def Remark(self, Remark):
        self._Remark = Remark


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._UserName = params.get("UserName")
        self._Remark = params.get("Remark")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyAccountRemarkResponse(AbstractModel):
    """ModifyAccountRemark response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class ModifyBackupDownloadRestrictionRequest(AbstractModel):
    """ModifyBackupDownloadRestriction request structure.

    """

    def __init__(self):
        r"""
        :param _RestrictionType: Type of the network restrictions for downloading a backup file. Valid values: `NONE` (backups can be downloaded over both private and public networks), `INTRANET` (backups can only be downloaded over the private network), `CUSTOMIZE` (backups can be downloaded over specified VPCs or at specified IPs).
        :type RestrictionType: str
        :param _VpcRestrictionEffect: Whether VPC is allowed. Valid values: `ALLOW` (allow), `DENY` (deny).
        :type VpcRestrictionEffect: str
        :param _VpcIdSet: Whether it is allowed to download the VPC ID list of the backup files.
        :type VpcIdSet: list of str
        :param _IpRestrictionEffect: Whether IP is allowed. Valid values: `ALLOW` (allow), `DENY` (deny).
        :type IpRestrictionEffect: str
        :param _IpSet: Whether it is allowed to download the IP list of the backup files.
        :type IpSet: list of str
        """
        self._RestrictionType = None
        self._VpcRestrictionEffect = None
        self._VpcIdSet = None
        self._IpRestrictionEffect = None
        self._IpSet = None

    @property
    def RestrictionType(self):
        return self._RestrictionType

    @RestrictionType.setter
    def RestrictionType(self, RestrictionType):
        self._RestrictionType = RestrictionType

    @property
    def VpcRestrictionEffect(self):
        return self._VpcRestrictionEffect

    @VpcRestrictionEffect.setter
    def VpcRestrictionEffect(self, VpcRestrictionEffect):
        self._VpcRestrictionEffect = VpcRestrictionEffect

    @property
    def VpcIdSet(self):
        return self._VpcIdSet

    @VpcIdSet.setter
    def VpcIdSet(self, VpcIdSet):
        self._VpcIdSet = VpcIdSet

    @property
    def IpRestrictionEffect(self):
        return self._IpRestrictionEffect

    @IpRestrictionEffect.setter
    def IpRestrictionEffect(self, IpRestrictionEffect):
        self._IpRestrictionEffect = IpRestrictionEffect

    @property
    def IpSet(self):
        return self._IpSet

    @IpSet.setter
    def IpSet(self, IpSet):
        self._IpSet = IpSet


    def _deserialize(self, params):
        self._RestrictionType = params.get("RestrictionType")
        self._VpcRestrictionEffect = params.get("VpcRestrictionEffect")
        self._VpcIdSet = params.get("VpcIdSet")
        self._IpRestrictionEffect = params.get("IpRestrictionEffect")
        self._IpSet = params.get("IpSet")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyBackupDownloadRestrictionResponse(AbstractModel):
    """ModifyBackupDownloadRestriction response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class ModifyBackupPlanRequest(AbstractModel):
    """ModifyBackupPlan request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _MinBackupStartTime: The earliest time to start a backup
        :type MinBackupStartTime: str
        :param _MaxBackupStartTime: The latest time to start a backup
        :type MaxBackupStartTime: str
        :param _BaseBackupRetentionPeriod: Backup retention period in days. Value range: 3-7
        :type BaseBackupRetentionPeriod: int
        :param _BackupPeriod: Backup cycle, which means on which days each week the instance will be backed up. The parameter value should be the lowercase names of the days of the week.
        :type BackupPeriod: list of str
        """
        self._DBInstanceId = None
        self._MinBackupStartTime = None
        self._MaxBackupStartTime = None
        self._BaseBackupRetentionPeriod = None
        self._BackupPeriod = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def MinBackupStartTime(self):
        return self._MinBackupStartTime

    @MinBackupStartTime.setter
    def MinBackupStartTime(self, MinBackupStartTime):
        self._MinBackupStartTime = MinBackupStartTime

    @property
    def MaxBackupStartTime(self):
        return self._MaxBackupStartTime

    @MaxBackupStartTime.setter
    def MaxBackupStartTime(self, MaxBackupStartTime):
        self._MaxBackupStartTime = MaxBackupStartTime

    @property
    def BaseBackupRetentionPeriod(self):
        return self._BaseBackupRetentionPeriod

    @BaseBackupRetentionPeriod.setter
    def BaseBackupRetentionPeriod(self, BaseBackupRetentionPeriod):
        self._BaseBackupRetentionPeriod = BaseBackupRetentionPeriod

    @property
    def BackupPeriod(self):
        return self._BackupPeriod

    @BackupPeriod.setter
    def BackupPeriod(self, BackupPeriod):
        self._BackupPeriod = BackupPeriod


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._MinBackupStartTime = params.get("MinBackupStartTime")
        self._MaxBackupStartTime = params.get("MaxBackupStartTime")
        self._BaseBackupRetentionPeriod = params.get("BaseBackupRetentionPeriod")
        self._BackupPeriod = params.get("BackupPeriod")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyBackupPlanResponse(AbstractModel):
    """ModifyBackupPlan response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class ModifyBaseBackupExpireTimeRequest(AbstractModel):
    """ModifyBaseBackupExpireTime request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _BaseBackupId: Base backup ID
        :type BaseBackupId: str
        :param _NewExpireTime: New expiration time
        :type NewExpireTime: str
        """
        self._DBInstanceId = None
        self._BaseBackupId = None
        self._NewExpireTime = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def BaseBackupId(self):
        return self._BaseBackupId

    @BaseBackupId.setter
    def BaseBackupId(self, BaseBackupId):
        self._BaseBackupId = BaseBackupId

    @property
    def NewExpireTime(self):
        return self._NewExpireTime

    @NewExpireTime.setter
    def NewExpireTime(self, NewExpireTime):
        self._NewExpireTime = NewExpireTime


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._BaseBackupId = params.get("BaseBackupId")
        self._NewExpireTime = params.get("NewExpireTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyBaseBackupExpireTimeResponse(AbstractModel):
    """ModifyBaseBackupExpireTime response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class ModifyDBInstanceChargeTypeRequest(AbstractModel):
    """ModifyDBInstanceChargeType request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of `postgres-6fego161`
        :type DBInstanceId: str
        :param _InstanceChargeType: Instance billing mode.  Valid values:  `PREPAID` (monthly subscription), `POSTPAID_BY_HOUR` (pay-as-you-go). Default value:  `PREPAID`.
        :type InstanceChargeType: str
        :param _Period: Validity period  in months. Valid values:  Valid period in months of the purchased instance. Valid values: `1`, `2`, `3`, `4`, `5`, `6`, `7`, `8`, `9`, `10`, `11`, `12`, `24`, `36`. This parameter is set to `1` when the pay-as-you-go billing mode is used.
        :type Period: int
        :param _AutoRenewFlag: Renewal flag. Valid values；  Valid values: `0` (manual renewal), `1` (auto-renewal).
        :type AutoRenewFlag: int
        :param _AutoVoucher: Whether to automatically use vouchers. Valid values: `1` (yes), `0` (no). Default value: `0`.
        :type AutoVoucher: int
        """
        self._DBInstanceId = None
        self._InstanceChargeType = None
        self._Period = None
        self._AutoRenewFlag = None
        self._AutoVoucher = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def InstanceChargeType(self):
        return self._InstanceChargeType

    @InstanceChargeType.setter
    def InstanceChargeType(self, InstanceChargeType):
        self._InstanceChargeType = InstanceChargeType

    @property
    def Period(self):
        return self._Period

    @Period.setter
    def Period(self, Period):
        self._Period = Period

    @property
    def AutoRenewFlag(self):
        return self._AutoRenewFlag

    @AutoRenewFlag.setter
    def AutoRenewFlag(self, AutoRenewFlag):
        self._AutoRenewFlag = AutoRenewFlag

    @property
    def AutoVoucher(self):
        return self._AutoVoucher

    @AutoVoucher.setter
    def AutoVoucher(self, AutoVoucher):
        self._AutoVoucher = AutoVoucher


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._InstanceChargeType = params.get("InstanceChargeType")
        self._Period = params.get("Period")
        self._AutoRenewFlag = params.get("AutoRenewFlag")
        self._AutoVoucher = params.get("AutoVoucher")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyDBInstanceChargeTypeResponse(AbstractModel):
    """ModifyDBInstanceChargeType response structure.

    """

    def __init__(self):
        r"""
        :param _DealName: Order name
        :type DealName: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DealName = None
        self._RequestId = None

    @property
    def DealName(self):
        return self._DealName

    @DealName.setter
    def DealName(self, DealName):
        self._DealName = DealName

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._DealName = params.get("DealName")
        self._RequestId = params.get("RequestId")


class ModifyDBInstanceDeploymentRequest(AbstractModel):
    """ModifyDBInstanceDeployment request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID.
        :type DBInstanceId: str
        :param _DBNodeSet: Instance node information.
        :type DBNodeSet: list of DBNode
        :param _SwitchTag: Switch time. Valid values: `0` (switch now), `1` (switch at a specified time), `2` (switch during maintenance time). Default value: `0`.
        :type SwitchTag: int
        :param _SwitchStartTime: Switch start time in the format of `HH:MM:SS`, such as 01:00:00. When `SwitchTag` is 0 or 2, this parameter becomes invalid.
        :type SwitchStartTime: str
        :param _SwitchEndTime: Switch end time in the format of `HH:MM:SS`, such as 01:30:00. When `SwitchTag` is 0 or 2, this parameter becomes invalid.
        :type SwitchEndTime: str
        """
        self._DBInstanceId = None
        self._DBNodeSet = None
        self._SwitchTag = None
        self._SwitchStartTime = None
        self._SwitchEndTime = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def DBNodeSet(self):
        return self._DBNodeSet

    @DBNodeSet.setter
    def DBNodeSet(self, DBNodeSet):
        self._DBNodeSet = DBNodeSet

    @property
    def SwitchTag(self):
        return self._SwitchTag

    @SwitchTag.setter
    def SwitchTag(self, SwitchTag):
        self._SwitchTag = SwitchTag

    @property
    def SwitchStartTime(self):
        return self._SwitchStartTime

    @SwitchStartTime.setter
    def SwitchStartTime(self, SwitchStartTime):
        self._SwitchStartTime = SwitchStartTime

    @property
    def SwitchEndTime(self):
        return self._SwitchEndTime

    @SwitchEndTime.setter
    def SwitchEndTime(self, SwitchEndTime):
        self._SwitchEndTime = SwitchEndTime


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        if params.get("DBNodeSet") is not None:
            self._DBNodeSet = []
            for item in params.get("DBNodeSet"):
                obj = DBNode()
                obj._deserialize(item)
                self._DBNodeSet.append(obj)
        self._SwitchTag = params.get("SwitchTag")
        self._SwitchStartTime = params.get("SwitchStartTime")
        self._SwitchEndTime = params.get("SwitchEndTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyDBInstanceDeploymentResponse(AbstractModel):
    """ModifyDBInstanceDeployment response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class ModifyDBInstanceNameRequest(AbstractModel):
    """ModifyDBInstanceName request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Database instance ID in the format of postgres-6fego161
        :type DBInstanceId: str
        :param _InstanceName: New name of database instance
        :type InstanceName: str
        """
        self._DBInstanceId = None
        self._InstanceName = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def InstanceName(self):
        return self._InstanceName

    @InstanceName.setter
    def InstanceName(self, InstanceName):
        self._InstanceName = InstanceName


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._InstanceName = params.get("InstanceName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyDBInstanceNameResponse(AbstractModel):
    """ModifyDBInstanceName response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class ModifyDBInstanceParametersRequest(AbstractModel):
    """ModifyDBInstanceParameters request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _ParamList: Parameters to be modified and their new values
        :type ParamList: list of ParamEntry
        """
        self._DBInstanceId = None
        self._ParamList = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def ParamList(self):
        return self._ParamList

    @ParamList.setter
    def ParamList(self, ParamList):
        self._ParamList = ParamList


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        if params.get("ParamList") is not None:
            self._ParamList = []
            for item in params.get("ParamList"):
                obj = ParamEntry()
                obj._deserialize(item)
                self._ParamList.append(obj)
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyDBInstanceParametersResponse(AbstractModel):
    """ModifyDBInstanceParameters response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class ModifyDBInstanceReadOnlyGroupRequest(AbstractModel):
    """ModifyDBInstanceReadOnlyGroup request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _ReadOnlyGroupId: ID of the RO group to which the read-only replica belongs
        :type ReadOnlyGroupId: str
        :param _NewReadOnlyGroupId: ID of the new RO group into which the read-only replica will move
        :type NewReadOnlyGroupId: str
        """
        self._DBInstanceId = None
        self._ReadOnlyGroupId = None
        self._NewReadOnlyGroupId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def ReadOnlyGroupId(self):
        return self._ReadOnlyGroupId

    @ReadOnlyGroupId.setter
    def ReadOnlyGroupId(self, ReadOnlyGroupId):
        self._ReadOnlyGroupId = ReadOnlyGroupId

    @property
    def NewReadOnlyGroupId(self):
        return self._NewReadOnlyGroupId

    @NewReadOnlyGroupId.setter
    def NewReadOnlyGroupId(self, NewReadOnlyGroupId):
        self._NewReadOnlyGroupId = NewReadOnlyGroupId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._ReadOnlyGroupId = params.get("ReadOnlyGroupId")
        self._NewReadOnlyGroupId = params.get("NewReadOnlyGroupId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyDBInstanceReadOnlyGroupResponse(AbstractModel):
    """ModifyDBInstanceReadOnlyGroup response structure.

    """

    def __init__(self):
        r"""
        :param _FlowId: Task ID
        :type FlowId: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._FlowId = None
        self._RequestId = None

    @property
    def FlowId(self):
        return self._FlowId

    @FlowId.setter
    def FlowId(self, FlowId):
        self._FlowId = FlowId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._FlowId = params.get("FlowId")
        self._RequestId = params.get("RequestId")


class ModifyDBInstanceSecurityGroupsRequest(AbstractModel):
    """ModifyDBInstanceSecurityGroups request structure.

    """

    def __init__(self):
        r"""
        :param _SecurityGroupIdSet: The list of security groups to be associated with the instance or RO groups
        :type SecurityGroupIdSet: list of str
        :param _DBInstanceId: Instance ID. Either this parameter or `ReadOnlyGroupId` must be passed in. If both parameters are passed in, `ReadOnlyGroupId` will be ignored.
        :type DBInstanceId: str
        :param _ReadOnlyGroupId: RO group ID. Either this parameter or `DBInstanceId` must be passed in. To modify  the security groups associated with the RO groups, only pass in `ReadOnlyGroupId`.
        :type ReadOnlyGroupId: str
        """
        self._SecurityGroupIdSet = None
        self._DBInstanceId = None
        self._ReadOnlyGroupId = None

    @property
    def SecurityGroupIdSet(self):
        return self._SecurityGroupIdSet

    @SecurityGroupIdSet.setter
    def SecurityGroupIdSet(self, SecurityGroupIdSet):
        self._SecurityGroupIdSet = SecurityGroupIdSet

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def ReadOnlyGroupId(self):
        return self._ReadOnlyGroupId

    @ReadOnlyGroupId.setter
    def ReadOnlyGroupId(self, ReadOnlyGroupId):
        self._ReadOnlyGroupId = ReadOnlyGroupId


    def _deserialize(self, params):
        self._SecurityGroupIdSet = params.get("SecurityGroupIdSet")
        self._DBInstanceId = params.get("DBInstanceId")
        self._ReadOnlyGroupId = params.get("ReadOnlyGroupId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyDBInstanceSecurityGroupsResponse(AbstractModel):
    """ModifyDBInstanceSecurityGroups response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class ModifyDBInstanceSpecRequest(AbstractModel):
    """ModifyDBInstanceSpec request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of postgres-6bwgamo3.
        :type DBInstanceId: str
        :param _Memory: Instance memory size in GiB after modification.
        :type Memory: int
        :param _Storage: Instance disk size in GiB after modification.
        :type Storage: int
        :param _AutoVoucher: Whether to automatically use vouchers. Valid values: `1` (yes), `0` (no). Default value: `0`.
        :type AutoVoucher: int
        :param _VoucherIds: Voucher ID list. Currently, you can specify only one voucher.
        :type VoucherIds: list of str
        :param _ActivityId: Campaign ID.
        :type ActivityId: int
        :param _SwitchTag: Switch time after instance configurations are modified. Valid values: `0` (switch now), `1` (switch at a specified time), `2` (switch during maintenance time). Default value: `0`.
        :type SwitchTag: int
        :param _SwitchStartTime: Switch start time in the format of `HH:MM:SS`, such as 01:00:00. When `SwitchTag` is 0 or 2, this parameter becomes invalid.
        :type SwitchStartTime: str
        :param _SwitchEndTime: Switch end time in the format of `HH:MM:SS`, such as 01:30:00. When `SwitchTag` is 0 or 2, this parameter becomes invalid.
        :type SwitchEndTime: str
        """
        self._DBInstanceId = None
        self._Memory = None
        self._Storage = None
        self._AutoVoucher = None
        self._VoucherIds = None
        self._ActivityId = None
        self._SwitchTag = None
        self._SwitchStartTime = None
        self._SwitchEndTime = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def Memory(self):
        return self._Memory

    @Memory.setter
    def Memory(self, Memory):
        self._Memory = Memory

    @property
    def Storage(self):
        return self._Storage

    @Storage.setter
    def Storage(self, Storage):
        self._Storage = Storage

    @property
    def AutoVoucher(self):
        return self._AutoVoucher

    @AutoVoucher.setter
    def AutoVoucher(self, AutoVoucher):
        self._AutoVoucher = AutoVoucher

    @property
    def VoucherIds(self):
        return self._VoucherIds

    @VoucherIds.setter
    def VoucherIds(self, VoucherIds):
        self._VoucherIds = VoucherIds

    @property
    def ActivityId(self):
        return self._ActivityId

    @ActivityId.setter
    def ActivityId(self, ActivityId):
        self._ActivityId = ActivityId

    @property
    def SwitchTag(self):
        return self._SwitchTag

    @SwitchTag.setter
    def SwitchTag(self, SwitchTag):
        self._SwitchTag = SwitchTag

    @property
    def SwitchStartTime(self):
        return self._SwitchStartTime

    @SwitchStartTime.setter
    def SwitchStartTime(self, SwitchStartTime):
        self._SwitchStartTime = SwitchStartTime

    @property
    def SwitchEndTime(self):
        return self._SwitchEndTime

    @SwitchEndTime.setter
    def SwitchEndTime(self, SwitchEndTime):
        self._SwitchEndTime = SwitchEndTime


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._Memory = params.get("Memory")
        self._Storage = params.get("Storage")
        self._AutoVoucher = params.get("AutoVoucher")
        self._VoucherIds = params.get("VoucherIds")
        self._ActivityId = params.get("ActivityId")
        self._SwitchTag = params.get("SwitchTag")
        self._SwitchStartTime = params.get("SwitchStartTime")
        self._SwitchEndTime = params.get("SwitchEndTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyDBInstanceSpecResponse(AbstractModel):
    """ModifyDBInstanceSpec response structure.

    """

    def __init__(self):
        r"""
        :param _DealName: Order ID.
        :type DealName: str
        :param _BillId: Bill ID of frozen fees.
        :type BillId: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DealName = None
        self._BillId = None
        self._RequestId = None

    @property
    def DealName(self):
        return self._DealName

    @DealName.setter
    def DealName(self, DealName):
        self._DealName = DealName

    @property
    def BillId(self):
        return self._BillId

    @BillId.setter
    def BillId(self, BillId):
        self._BillId = BillId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._DealName = params.get("DealName")
        self._BillId = params.get("BillId")
        self._RequestId = params.get("RequestId")


class ModifyDBInstancesProjectRequest(AbstractModel):
    """ModifyDBInstancesProject request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceIdSet: List of instance IDs. Note that currently you cannot manipulate multiple instances at the same time. Only one instance ID can be passed in here.
        :type DBInstanceIdSet: list of str
        :param _ProjectId: ID of the new project
        :type ProjectId: str
        """
        self._DBInstanceIdSet = None
        self._ProjectId = None

    @property
    def DBInstanceIdSet(self):
        return self._DBInstanceIdSet

    @DBInstanceIdSet.setter
    def DBInstanceIdSet(self, DBInstanceIdSet):
        self._DBInstanceIdSet = DBInstanceIdSet

    @property
    def ProjectId(self):
        return self._ProjectId

    @ProjectId.setter
    def ProjectId(self, ProjectId):
        self._ProjectId = ProjectId


    def _deserialize(self, params):
        self._DBInstanceIdSet = params.get("DBInstanceIdSet")
        self._ProjectId = params.get("ProjectId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyDBInstancesProjectResponse(AbstractModel):
    """ModifyDBInstancesProject response structure.

    """

    def __init__(self):
        r"""
        :param _Count: Number of successfully transferred instances
        :type Count: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Count = None
        self._RequestId = None

    @property
    def Count(self):
        return self._Count

    @Count.setter
    def Count(self, Count):
        self._Count = Count

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._Count = params.get("Count")
        self._RequestId = params.get("RequestId")


class ModifyParameterTemplateRequest(AbstractModel):
    """ModifyParameterTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Parameter template ID, which uniquely identifies a parameter template and cannot be modified.
        :type TemplateId: str
        :param _TemplateName: Parameter template name, which can contain 1-60 letters, digits, and symbols (-_./()[]()+=:@). If this field is empty, the original parameter template name will be used.
        :type TemplateName: str
        :param _TemplateDescription: Parameter template description, which can contain 1-60 letters, digits, and symbols (-_./()[]()+=:@). If this parameter is not passed in, the original parameter template description will be used.
        :type TemplateDescription: str
        :param _ModifyParamEntrySet: The set of parameters to be modified or added. A parameter cannot be put to `ModifyParamEntrySet` and `DeleteParamSet` at the same time, that is, it cannot be modified/added and deleted at the same time.
        :type ModifyParamEntrySet: list of ParamEntry
        :param _DeleteParamSet: The set of parameters to be deleted in the template. A parameter cannot be put to `ModifyParamEntrySet` and `DeleteParamSet` at the same time, that is, it cannot be modified/added and deleted at the same time.
        :type DeleteParamSet: list of str
        """
        self._TemplateId = None
        self._TemplateName = None
        self._TemplateDescription = None
        self._ModifyParamEntrySet = None
        self._DeleteParamSet = None

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId

    @property
    def TemplateName(self):
        return self._TemplateName

    @TemplateName.setter
    def TemplateName(self, TemplateName):
        self._TemplateName = TemplateName

    @property
    def TemplateDescription(self):
        return self._TemplateDescription

    @TemplateDescription.setter
    def TemplateDescription(self, TemplateDescription):
        self._TemplateDescription = TemplateDescription

    @property
    def ModifyParamEntrySet(self):
        return self._ModifyParamEntrySet

    @ModifyParamEntrySet.setter
    def ModifyParamEntrySet(self, ModifyParamEntrySet):
        self._ModifyParamEntrySet = ModifyParamEntrySet

    @property
    def DeleteParamSet(self):
        return self._DeleteParamSet

    @DeleteParamSet.setter
    def DeleteParamSet(self, DeleteParamSet):
        self._DeleteParamSet = DeleteParamSet


    def _deserialize(self, params):
        self._TemplateId = params.get("TemplateId")
        self._TemplateName = params.get("TemplateName")
        self._TemplateDescription = params.get("TemplateDescription")
        if params.get("ModifyParamEntrySet") is not None:
            self._ModifyParamEntrySet = []
            for item in params.get("ModifyParamEntrySet"):
                obj = ParamEntry()
                obj._deserialize(item)
                self._ModifyParamEntrySet.append(obj)
        self._DeleteParamSet = params.get("DeleteParamSet")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyParameterTemplateResponse(AbstractModel):
    """ModifyParameterTemplate response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class ModifyReadOnlyGroupConfigRequest(AbstractModel):
    """ModifyReadOnlyGroupConfig request structure.

    """

    def __init__(self):
        r"""
        :param _ReadOnlyGroupId: RO group ID
        :type ReadOnlyGroupId: str
        :param _ReadOnlyGroupName: RO group name
        :type ReadOnlyGroupName: str
        :param _ReplayLagEliminate: Whether to remove a read-only replica from an RO group if the delay between the read-only replica and the primary instance exceeds the threshold. Valid values: `0` (no), `1` (yes).
        :type ReplayLagEliminate: int
        :param _ReplayLatencyEliminate: Whether to remove a read-only replica from an RO group if the sync log size difference between the read-only replica and the primary instance exceeds the threshold. Valid values: `0` (no), `1` (yes).
        :type ReplayLatencyEliminate: int
        :param _MaxReplayLatency: Delayed log size threshold in MB
        :type MaxReplayLatency: int
        :param _MaxReplayLag: Delay threshold in ms
        :type MaxReplayLag: int
        :param _Rebalance: Whether to enable automatic load balancing. Valid values: `0` (disable), `1` (enable).
        :type Rebalance: int
        :param _MinDelayEliminateReserve: The minimum number of read-only replicas that must be retained in an RO group
        :type MinDelayEliminateReserve: int
        """
        self._ReadOnlyGroupId = None
        self._ReadOnlyGroupName = None
        self._ReplayLagEliminate = None
        self._ReplayLatencyEliminate = None
        self._MaxReplayLatency = None
        self._MaxReplayLag = None
        self._Rebalance = None
        self._MinDelayEliminateReserve = None

    @property
    def ReadOnlyGroupId(self):
        return self._ReadOnlyGroupId

    @ReadOnlyGroupId.setter
    def ReadOnlyGroupId(self, ReadOnlyGroupId):
        self._ReadOnlyGroupId = ReadOnlyGroupId

    @property
    def ReadOnlyGroupName(self):
        return self._ReadOnlyGroupName

    @ReadOnlyGroupName.setter
    def ReadOnlyGroupName(self, ReadOnlyGroupName):
        self._ReadOnlyGroupName = ReadOnlyGroupName

    @property
    def ReplayLagEliminate(self):
        return self._ReplayLagEliminate

    @ReplayLagEliminate.setter
    def ReplayLagEliminate(self, ReplayLagEliminate):
        self._ReplayLagEliminate = ReplayLagEliminate

    @property
    def ReplayLatencyEliminate(self):
        return self._ReplayLatencyEliminate

    @ReplayLatencyEliminate.setter
    def ReplayLatencyEliminate(self, ReplayLatencyEliminate):
        self._ReplayLatencyEliminate = ReplayLatencyEliminate

    @property
    def MaxReplayLatency(self):
        return self._MaxReplayLatency

    @MaxReplayLatency.setter
    def MaxReplayLatency(self, MaxReplayLatency):
        self._MaxReplayLatency = MaxReplayLatency

    @property
    def MaxReplayLag(self):
        return self._MaxReplayLag

    @MaxReplayLag.setter
    def MaxReplayLag(self, MaxReplayLag):
        self._MaxReplayLag = MaxReplayLag

    @property
    def Rebalance(self):
        return self._Rebalance

    @Rebalance.setter
    def Rebalance(self, Rebalance):
        self._Rebalance = Rebalance

    @property
    def MinDelayEliminateReserve(self):
        return self._MinDelayEliminateReserve

    @MinDelayEliminateReserve.setter
    def MinDelayEliminateReserve(self, MinDelayEliminateReserve):
        self._MinDelayEliminateReserve = MinDelayEliminateReserve


    def _deserialize(self, params):
        self._ReadOnlyGroupId = params.get("ReadOnlyGroupId")
        self._ReadOnlyGroupName = params.get("ReadOnlyGroupName")
        self._ReplayLagEliminate = params.get("ReplayLagEliminate")
        self._ReplayLatencyEliminate = params.get("ReplayLatencyEliminate")
        self._MaxReplayLatency = params.get("MaxReplayLatency")
        self._MaxReplayLag = params.get("MaxReplayLag")
        self._Rebalance = params.get("Rebalance")
        self._MinDelayEliminateReserve = params.get("MinDelayEliminateReserve")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyReadOnlyGroupConfigResponse(AbstractModel):
    """ModifyReadOnlyGroupConfig response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class ModifySwitchTimePeriodRequest(AbstractModel):
    """ModifySwitchTimePeriod request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: The ID of the instance waiting for a switch
        :type DBInstanceId: str
        :param _SwitchTag: Valid value: `0` (switch immediately)
        :type SwitchTag: int
        """
        self._DBInstanceId = None
        self._SwitchTag = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def SwitchTag(self):
        return self._SwitchTag

    @SwitchTag.setter
    def SwitchTag(self, SwitchTag):
        self._SwitchTag = SwitchTag


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._SwitchTag = params.get("SwitchTag")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifySwitchTimePeriodResponse(AbstractModel):
    """ModifySwitchTimePeriod response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class NetworkAccess(AbstractModel):
    """Network information. (This parameter structure has been deprecated. Please use `DBInstanceNetInfo` to query network information.)

    """

    def __init__(self):
        r"""
        :param _ResourceId: Network resource ID, instance ID, or RO group ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ResourceId: str
        :param _ResourceType: Resource type. Valid values: `1` (instance), `2` (RO group)
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ResourceType: int
        :param _VpcId: VPC ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type VpcId: str
        :param _Vip: IPv4 address
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type Vip: str
        :param _Vip6: IPv6 address
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type Vip6: str
        :param _Vport: Access port
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type Vport: int
        :param _SubnetId: Subnet ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type SubnetId: str
        :param _VpcStatus: Network status. Valid values: `1` (applying), `2` (in use), `3` (deleting), `4` (deleted)
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type VpcStatus: int
        """
        self._ResourceId = None
        self._ResourceType = None
        self._VpcId = None
        self._Vip = None
        self._Vip6 = None
        self._Vport = None
        self._SubnetId = None
        self._VpcStatus = None

    @property
    def ResourceId(self):
        return self._ResourceId

    @ResourceId.setter
    def ResourceId(self, ResourceId):
        self._ResourceId = ResourceId

    @property
    def ResourceType(self):
        return self._ResourceType

    @ResourceType.setter
    def ResourceType(self, ResourceType):
        self._ResourceType = ResourceType

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def Vip(self):
        return self._Vip

    @Vip.setter
    def Vip(self, Vip):
        self._Vip = Vip

    @property
    def Vip6(self):
        return self._Vip6

    @Vip6.setter
    def Vip6(self, Vip6):
        self._Vip6 = Vip6

    @property
    def Vport(self):
        return self._Vport

    @Vport.setter
    def Vport(self, Vport):
        self._Vport = Vport

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def VpcStatus(self):
        return self._VpcStatus

    @VpcStatus.setter
    def VpcStatus(self, VpcStatus):
        self._VpcStatus = VpcStatus


    def _deserialize(self, params):
        self._ResourceId = params.get("ResourceId")
        self._ResourceType = params.get("ResourceType")
        self._VpcId = params.get("VpcId")
        self._Vip = params.get("Vip")
        self._Vip6 = params.get("Vip6")
        self._Vport = params.get("Vport")
        self._SubnetId = params.get("SubnetId")
        self._VpcStatus = params.get("VpcStatus")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class NormalQueryItem(AbstractModel):
    """Information of one SlowQuery

    """

    def __init__(self):
        r"""
        :param _UserName: Username
        :type UserName: str
        :param _Calls: Number of calls
        :type Calls: int
        :param _CallsGrids: Granularity
        :type CallsGrids: list of int
        :param _CostTime: Total time consumed
        :type CostTime: float
        :param _Rows: Number of affected rows
        :type Rows: int
        :param _MinCostTime: Minimum time consumed
        :type MinCostTime: float
        :param _MaxCostTime: Maximum time consumed
        :type MaxCostTime: float
        :param _FirstTime: Time of the earliest slow SQL statement
        :type FirstTime: str
        :param _LastTime: Time of the latest slow SQL statement
        :type LastTime: str
        :param _SharedReadBlks: Shared memory blocks for reads
        :type SharedReadBlks: int
        :param _SharedWriteBlks: Shared memory blocks for writes
        :type SharedWriteBlks: int
        :param _ReadCostTime: Total IO read time
        :type ReadCostTime: int
        :param _WriteCostTime: Total IO write time
        :type WriteCostTime: int
        :param _DatabaseName: Database name
        :type DatabaseName: str
        :param _NormalQuery: Slow SQL statement after desensitization
        :type NormalQuery: str
        """
        self._UserName = None
        self._Calls = None
        self._CallsGrids = None
        self._CostTime = None
        self._Rows = None
        self._MinCostTime = None
        self._MaxCostTime = None
        self._FirstTime = None
        self._LastTime = None
        self._SharedReadBlks = None
        self._SharedWriteBlks = None
        self._ReadCostTime = None
        self._WriteCostTime = None
        self._DatabaseName = None
        self._NormalQuery = None

    @property
    def UserName(self):
        return self._UserName

    @UserName.setter
    def UserName(self, UserName):
        self._UserName = UserName

    @property
    def Calls(self):
        return self._Calls

    @Calls.setter
    def Calls(self, Calls):
        self._Calls = Calls

    @property
    def CallsGrids(self):
        return self._CallsGrids

    @CallsGrids.setter
    def CallsGrids(self, CallsGrids):
        self._CallsGrids = CallsGrids

    @property
    def CostTime(self):
        return self._CostTime

    @CostTime.setter
    def CostTime(self, CostTime):
        self._CostTime = CostTime

    @property
    def Rows(self):
        return self._Rows

    @Rows.setter
    def Rows(self, Rows):
        self._Rows = Rows

    @property
    def MinCostTime(self):
        return self._MinCostTime

    @MinCostTime.setter
    def MinCostTime(self, MinCostTime):
        self._MinCostTime = MinCostTime

    @property
    def MaxCostTime(self):
        return self._MaxCostTime

    @MaxCostTime.setter
    def MaxCostTime(self, MaxCostTime):
        self._MaxCostTime = MaxCostTime

    @property
    def FirstTime(self):
        return self._FirstTime

    @FirstTime.setter
    def FirstTime(self, FirstTime):
        self._FirstTime = FirstTime

    @property
    def LastTime(self):
        return self._LastTime

    @LastTime.setter
    def LastTime(self, LastTime):
        self._LastTime = LastTime

    @property
    def SharedReadBlks(self):
        return self._SharedReadBlks

    @SharedReadBlks.setter
    def SharedReadBlks(self, SharedReadBlks):
        self._SharedReadBlks = SharedReadBlks

    @property
    def SharedWriteBlks(self):
        return self._SharedWriteBlks

    @SharedWriteBlks.setter
    def SharedWriteBlks(self, SharedWriteBlks):
        self._SharedWriteBlks = SharedWriteBlks

    @property
    def ReadCostTime(self):
        return self._ReadCostTime

    @ReadCostTime.setter
    def ReadCostTime(self, ReadCostTime):
        self._ReadCostTime = ReadCostTime

    @property
    def WriteCostTime(self):
        return self._WriteCostTime

    @WriteCostTime.setter
    def WriteCostTime(self, WriteCostTime):
        self._WriteCostTime = WriteCostTime

    @property
    def DatabaseName(self):
        return self._DatabaseName

    @DatabaseName.setter
    def DatabaseName(self, DatabaseName):
        self._DatabaseName = DatabaseName

    @property
    def NormalQuery(self):
        return self._NormalQuery

    @NormalQuery.setter
    def NormalQuery(self, NormalQuery):
        self._NormalQuery = NormalQuery


    def _deserialize(self, params):
        self._UserName = params.get("UserName")
        self._Calls = params.get("Calls")
        self._CallsGrids = params.get("CallsGrids")
        self._CostTime = params.get("CostTime")
        self._Rows = params.get("Rows")
        self._MinCostTime = params.get("MinCostTime")
        self._MaxCostTime = params.get("MaxCostTime")
        self._FirstTime = params.get("FirstTime")
        self._LastTime = params.get("LastTime")
        self._SharedReadBlks = params.get("SharedReadBlks")
        self._SharedWriteBlks = params.get("SharedWriteBlks")
        self._ReadCostTime = params.get("ReadCostTime")
        self._WriteCostTime = params.get("WriteCostTime")
        self._DatabaseName = params.get("DatabaseName")
        self._NormalQuery = params.get("NormalQuery")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class OpenDBExtranetAccessRequest(AbstractModel):
    """OpenDBExtranetAccess request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of postgres-hez4fh0v
        :type DBInstanceId: str
        :param _IsIpv6: Whether to enable public network access over IPv6 address. Valid values: 1 (yes), 0 (no)
        :type IsIpv6: int
        """
        self._DBInstanceId = None
        self._IsIpv6 = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def IsIpv6(self):
        return self._IsIpv6

    @IsIpv6.setter
    def IsIpv6(self, IsIpv6):
        self._IsIpv6 = IsIpv6


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._IsIpv6 = params.get("IsIpv6")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class OpenDBExtranetAccessResponse(AbstractModel):
    """OpenDBExtranetAccess response structure.

    """

    def __init__(self):
        r"""
        :param _FlowId: Async task flow ID
        :type FlowId: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._FlowId = None
        self._RequestId = None

    @property
    def FlowId(self):
        return self._FlowId

    @FlowId.setter
    def FlowId(self, FlowId):
        self._FlowId = FlowId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._FlowId = params.get("FlowId")
        self._RequestId = params.get("RequestId")


class OpenServerlessDBExtranetAccessRequest(AbstractModel):
    """OpenServerlessDBExtranetAccess request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Unique ID of an instance
        :type DBInstanceId: str
        :param _DBInstanceName: Instance name
        :type DBInstanceName: str
        """
        self._DBInstanceId = None
        self._DBInstanceName = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def DBInstanceName(self):
        return self._DBInstanceName

    @DBInstanceName.setter
    def DBInstanceName(self, DBInstanceName):
        self._DBInstanceName = DBInstanceName


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._DBInstanceName = params.get("DBInstanceName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class OpenServerlessDBExtranetAccessResponse(AbstractModel):
    """OpenServerlessDBExtranetAccess response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class ParamEntry(AbstractModel):
    """Parameters to be modified in batches

    """

    def __init__(self):
        r"""
        :param _Name: Parameter name
        :type Name: str
        :param _ExpectedValue: The new value to which the parameter will be modified. When this parameter is used as an input parameter, its value must be a string, such as `0.1` (decimal), `1000` (integer), and `replica` (enum).
        :type ExpectedValue: str
        """
        self._Name = None
        self._ExpectedValue = None

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, Name):
        self._Name = Name

    @property
    def ExpectedValue(self):
        return self._ExpectedValue

    @ExpectedValue.setter
    def ExpectedValue(self, ExpectedValue):
        self._ExpectedValue = ExpectedValue


    def _deserialize(self, params):
        self._Name = params.get("Name")
        self._ExpectedValue = params.get("ExpectedValue")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ParamInfo(AbstractModel):
    """Parameter details

    """

    def __init__(self):
        r"""
        :param _ID: Parameter ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ID: int
        :param _Name: Parameter name
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type Name: str
        :param _ParamValueType: Value type of the parameter. Valid values: `integer`, `real` (floating-point), `bool`, `enum`, `mutil_enum` (this type of parameter can be set to multiple enumerated values).
For an `integer` or `real` parameter, the `Min` field represents the minimum value and the `Max` field the maximum value. 
For a `bool` parameter, the valid values include `true` and `false`; 
For an `enum` or `mutil_enum` parameter, the `EnumValue` field represents the valid values.
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ParamValueType: str
        :param _Unit: Unit of the parameter value. If the parameter has no unit, this field will return null.
Note: This field may return null, indicating that no valid values can be obtained.
        :type Unit: str
        :param _DefaultValue: Default value of the parameter, which is returned as a string
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DefaultValue: str
        :param _CurrentValue: Current value of the parameter, which is returned as a string
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type CurrentValue: str
        :param _Max: The maximum value of the `integer` or `real` parameter
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type Max: float
        :param _EnumValue: Value range of the enum parameter
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type EnumValue: list of str
        :param _Min: The minimum value of the `integer` or `real` parameter
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type Min: float
        :param _ParamDescriptionCH: Parameter description in Chinese
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ParamDescriptionCH: str
        :param _ParamDescriptionEN: Parameter description in English
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ParamDescriptionEN: str
        :param _NeedReboot: Whether to restart the instance for the modified parameter to take effect. Valid values: `true` (yes), `false` (no)
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type NeedReboot: bool
        :param _ClassificationCN: Parameter category in Chinese
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ClassificationCN: str
        :param _ClassificationEN: Parameter category in English
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ClassificationEN: str
        :param _SpecRelated: Whether the parameter is related to specifications. Valid values: `true` (yes), `false` (no)
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type SpecRelated: bool
        :param _Advanced: Whether it is a key parameter. Valid values: `true` (yes, and modifying it may affect instance performance), `false` (no)
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type Advanced: bool
        :param _LastModifyTime: The last modified time of the parameter
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type LastModifyTime: str
        :param _StandbyRelated: Primary-standby constraint. Valid values: `0` (no constraint), `1` (The parameter value of the standby server must be greater than that of the primary server), `2` (The parameter value of the primary server must be greater than that of the standby server.)
Note: This field may return null, indicating that no valid values can be obtained.
        :type StandbyRelated: int
        :param _VersionRelationSet: Associated parameter version information, which refers to the detailed parameter information of the kernel version.
Note: This field may return null, indicating that no valid values can be obtained.
        :type VersionRelationSet: list of ParamVersionRelation
        :param _SpecRelationSet: Associated parameter specification information, which refers to the detailed parameter information of the specifications.
Note: This field may return null, indicating that no valid values can be obtained.
        :type SpecRelationSet: list of ParamSpecRelation
        """
        self._ID = None
        self._Name = None
        self._ParamValueType = None
        self._Unit = None
        self._DefaultValue = None
        self._CurrentValue = None
        self._Max = None
        self._EnumValue = None
        self._Min = None
        self._ParamDescriptionCH = None
        self._ParamDescriptionEN = None
        self._NeedReboot = None
        self._ClassificationCN = None
        self._ClassificationEN = None
        self._SpecRelated = None
        self._Advanced = None
        self._LastModifyTime = None
        self._StandbyRelated = None
        self._VersionRelationSet = None
        self._SpecRelationSet = None

    @property
    def ID(self):
        return self._ID

    @ID.setter
    def ID(self, ID):
        self._ID = ID

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, Name):
        self._Name = Name

    @property
    def ParamValueType(self):
        return self._ParamValueType

    @ParamValueType.setter
    def ParamValueType(self, ParamValueType):
        self._ParamValueType = ParamValueType

    @property
    def Unit(self):
        return self._Unit

    @Unit.setter
    def Unit(self, Unit):
        self._Unit = Unit

    @property
    def DefaultValue(self):
        return self._DefaultValue

    @DefaultValue.setter
    def DefaultValue(self, DefaultValue):
        self._DefaultValue = DefaultValue

    @property
    def CurrentValue(self):
        return self._CurrentValue

    @CurrentValue.setter
    def CurrentValue(self, CurrentValue):
        self._CurrentValue = CurrentValue

    @property
    def Max(self):
        return self._Max

    @Max.setter
    def Max(self, Max):
        self._Max = Max

    @property
    def EnumValue(self):
        return self._EnumValue

    @EnumValue.setter
    def EnumValue(self, EnumValue):
        self._EnumValue = EnumValue

    @property
    def Min(self):
        return self._Min

    @Min.setter
    def Min(self, Min):
        self._Min = Min

    @property
    def ParamDescriptionCH(self):
        return self._ParamDescriptionCH

    @ParamDescriptionCH.setter
    def ParamDescriptionCH(self, ParamDescriptionCH):
        self._ParamDescriptionCH = ParamDescriptionCH

    @property
    def ParamDescriptionEN(self):
        return self._ParamDescriptionEN

    @ParamDescriptionEN.setter
    def ParamDescriptionEN(self, ParamDescriptionEN):
        self._ParamDescriptionEN = ParamDescriptionEN

    @property
    def NeedReboot(self):
        return self._NeedReboot

    @NeedReboot.setter
    def NeedReboot(self, NeedReboot):
        self._NeedReboot = NeedReboot

    @property
    def ClassificationCN(self):
        return self._ClassificationCN

    @ClassificationCN.setter
    def ClassificationCN(self, ClassificationCN):
        self._ClassificationCN = ClassificationCN

    @property
    def ClassificationEN(self):
        return self._ClassificationEN

    @ClassificationEN.setter
    def ClassificationEN(self, ClassificationEN):
        self._ClassificationEN = ClassificationEN

    @property
    def SpecRelated(self):
        return self._SpecRelated

    @SpecRelated.setter
    def SpecRelated(self, SpecRelated):
        self._SpecRelated = SpecRelated

    @property
    def Advanced(self):
        return self._Advanced

    @Advanced.setter
    def Advanced(self, Advanced):
        self._Advanced = Advanced

    @property
    def LastModifyTime(self):
        return self._LastModifyTime

    @LastModifyTime.setter
    def LastModifyTime(self, LastModifyTime):
        self._LastModifyTime = LastModifyTime

    @property
    def StandbyRelated(self):
        return self._StandbyRelated

    @StandbyRelated.setter
    def StandbyRelated(self, StandbyRelated):
        self._StandbyRelated = StandbyRelated

    @property
    def VersionRelationSet(self):
        return self._VersionRelationSet

    @VersionRelationSet.setter
    def VersionRelationSet(self, VersionRelationSet):
        self._VersionRelationSet = VersionRelationSet

    @property
    def SpecRelationSet(self):
        return self._SpecRelationSet

    @SpecRelationSet.setter
    def SpecRelationSet(self, SpecRelationSet):
        self._SpecRelationSet = SpecRelationSet


    def _deserialize(self, params):
        self._ID = params.get("ID")
        self._Name = params.get("Name")
        self._ParamValueType = params.get("ParamValueType")
        self._Unit = params.get("Unit")
        self._DefaultValue = params.get("DefaultValue")
        self._CurrentValue = params.get("CurrentValue")
        self._Max = params.get("Max")
        self._EnumValue = params.get("EnumValue")
        self._Min = params.get("Min")
        self._ParamDescriptionCH = params.get("ParamDescriptionCH")
        self._ParamDescriptionEN = params.get("ParamDescriptionEN")
        self._NeedReboot = params.get("NeedReboot")
        self._ClassificationCN = params.get("ClassificationCN")
        self._ClassificationEN = params.get("ClassificationEN")
        self._SpecRelated = params.get("SpecRelated")
        self._Advanced = params.get("Advanced")
        self._LastModifyTime = params.get("LastModifyTime")
        self._StandbyRelated = params.get("StandbyRelated")
        if params.get("VersionRelationSet") is not None:
            self._VersionRelationSet = []
            for item in params.get("VersionRelationSet"):
                obj = ParamVersionRelation()
                obj._deserialize(item)
                self._VersionRelationSet.append(obj)
        if params.get("SpecRelationSet") is not None:
            self._SpecRelationSet = []
            for item in params.get("SpecRelationSet"):
                obj = ParamSpecRelation()
                obj._deserialize(item)
                self._SpecRelationSet.append(obj)
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ParamSpecRelation(AbstractModel):
    """Parameter information of each specification

    """

    def __init__(self):
        r"""
        :param _Name: Parameter name
Note: This field may return null, indicating that no valid values can be obtained.
        :type Name: str
        :param _Memory: The specification that corresponds to the parameter information
Note: This field may return null, indicating that no valid values can be obtained.
        :type Memory: str
        :param _Value: The default parameter value under this specification
Note: This field may return null, indicating that no valid values can be obtained.
        :type Value: str
        :param _Unit: Unit of the parameter value. If the parameter has no unit, this field will return null.
Note: This field may return null, indicating that no valid values can be obtained.
        :type Unit: str
        :param _Max: The maximum value of the `integer` or `real` parameter
Note: This field may return null, indicating that no valid values can be obtained.
        :type Max: float
        :param _Min: The minimum value of the `integer` or `real` parameter
Note: This field may return null, indicating that no valid values can be obtained.
        :type Min: float
        :param _EnumValue: Value range of the enum parameter
Note: This field may return null, indicating that no valid values can be obtained.
        :type EnumValue: list of str
        """
        self._Name = None
        self._Memory = None
        self._Value = None
        self._Unit = None
        self._Max = None
        self._Min = None
        self._EnumValue = None

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, Name):
        self._Name = Name

    @property
    def Memory(self):
        return self._Memory

    @Memory.setter
    def Memory(self, Memory):
        self._Memory = Memory

    @property
    def Value(self):
        return self._Value

    @Value.setter
    def Value(self, Value):
        self._Value = Value

    @property
    def Unit(self):
        return self._Unit

    @Unit.setter
    def Unit(self, Unit):
        self._Unit = Unit

    @property
    def Max(self):
        return self._Max

    @Max.setter
    def Max(self, Max):
        self._Max = Max

    @property
    def Min(self):
        return self._Min

    @Min.setter
    def Min(self, Min):
        self._Min = Min

    @property
    def EnumValue(self):
        return self._EnumValue

    @EnumValue.setter
    def EnumValue(self, EnumValue):
        self._EnumValue = EnumValue


    def _deserialize(self, params):
        self._Name = params.get("Name")
        self._Memory = params.get("Memory")
        self._Value = params.get("Value")
        self._Unit = params.get("Unit")
        self._Max = params.get("Max")
        self._Min = params.get("Min")
        self._EnumValue = params.get("EnumValue")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ParamVersionRelation(AbstractModel):
    """Parameter information of each version

    """

    def __init__(self):
        r"""
        :param _Name: Parameter name
Note: This field may return null, indicating that no valid values can be obtained.
        :type Name: str
        :param _DBKernelVersion: The kernel version that corresponds to the parameter information
Note: This field may return null, indicating that no valid values can be obtained.
        :type DBKernelVersion: str
        :param _Value: Default parameter value under the kernel version and specification of the instance
Note: This field may return null, indicating that no valid values can be obtained.
        :type Value: str
        :param _Unit: Unit of the parameter value. If the parameter has no unit, this field will return null.
Note: This field may return null, indicating that no valid values can be obtained.
        :type Unit: str
        :param _Max: The maximum value of the `integer` or `real` parameter
Note: This field may return null, indicating that no valid values can be obtained.
        :type Max: float
        :param _Min: The minimum value of the `integer` or `real` parameter
Note: This field may return null, indicating that no valid values can be obtained.
        :type Min: float
        :param _EnumValue: Value range of the enum parameter
Note: This field may return null, indicating that no valid values can be obtained.
        :type EnumValue: list of str
        """
        self._Name = None
        self._DBKernelVersion = None
        self._Value = None
        self._Unit = None
        self._Max = None
        self._Min = None
        self._EnumValue = None

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, Name):
        self._Name = Name

    @property
    def DBKernelVersion(self):
        return self._DBKernelVersion

    @DBKernelVersion.setter
    def DBKernelVersion(self, DBKernelVersion):
        self._DBKernelVersion = DBKernelVersion

    @property
    def Value(self):
        return self._Value

    @Value.setter
    def Value(self, Value):
        self._Value = Value

    @property
    def Unit(self):
        return self._Unit

    @Unit.setter
    def Unit(self, Unit):
        self._Unit = Unit

    @property
    def Max(self):
        return self._Max

    @Max.setter
    def Max(self, Max):
        self._Max = Max

    @property
    def Min(self):
        return self._Min

    @Min.setter
    def Min(self, Min):
        self._Min = Min

    @property
    def EnumValue(self):
        return self._EnumValue

    @EnumValue.setter
    def EnumValue(self, EnumValue):
        self._EnumValue = EnumValue


    def _deserialize(self, params):
        self._Name = params.get("Name")
        self._DBKernelVersion = params.get("DBKernelVersion")
        self._Value = params.get("Value")
        self._Unit = params.get("Unit")
        self._Max = params.get("Max")
        self._Min = params.get("Min")
        self._EnumValue = params.get("EnumValue")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ParameterTemplate(AbstractModel):
    """Basic information of a parameter template

    """

    def __init__(self):
        r"""
        :param _TemplateId: Parameter template ID
        :type TemplateId: str
        :param _TemplateName: Parameter template name
        :type TemplateName: str
        :param _DBMajorVersion: Database version applicable to a parameter template
        :type DBMajorVersion: str
        :param _DBEngine: Database engine applicable to a parameter template
        :type DBEngine: str
        :param _TemplateDescription: Parameter template description
        :type TemplateDescription: str
        """
        self._TemplateId = None
        self._TemplateName = None
        self._DBMajorVersion = None
        self._DBEngine = None
        self._TemplateDescription = None

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId

    @property
    def TemplateName(self):
        return self._TemplateName

    @TemplateName.setter
    def TemplateName(self, TemplateName):
        self._TemplateName = TemplateName

    @property
    def DBMajorVersion(self):
        return self._DBMajorVersion

    @DBMajorVersion.setter
    def DBMajorVersion(self, DBMajorVersion):
        self._DBMajorVersion = DBMajorVersion

    @property
    def DBEngine(self):
        return self._DBEngine

    @DBEngine.setter
    def DBEngine(self, DBEngine):
        self._DBEngine = DBEngine

    @property
    def TemplateDescription(self):
        return self._TemplateDescription

    @TemplateDescription.setter
    def TemplateDescription(self, TemplateDescription):
        self._TemplateDescription = TemplateDescription


    def _deserialize(self, params):
        self._TemplateId = params.get("TemplateId")
        self._TemplateName = params.get("TemplateName")
        self._DBMajorVersion = params.get("DBMajorVersion")
        self._DBEngine = params.get("DBEngine")
        self._TemplateDescription = params.get("TemplateDescription")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class PgDeal(AbstractModel):
    """Order details

    """

    def __init__(self):
        r"""
        :param _DealName: Order name
        :type DealName: str
        :param _OwnerUin: User
        :type OwnerUin: str
        :param _Count: Number of instances involved in order
        :type Count: int
        :param _PayMode: Billing mode. 0: pay-as-you-go
        :type PayMode: int
        :param _FlowId: Async task flow ID
        :type FlowId: int
        :param _DBInstanceIdSet: Instance ID array
        :type DBInstanceIdSet: list of str
        """
        self._DealName = None
        self._OwnerUin = None
        self._Count = None
        self._PayMode = None
        self._FlowId = None
        self._DBInstanceIdSet = None

    @property
    def DealName(self):
        return self._DealName

    @DealName.setter
    def DealName(self, DealName):
        self._DealName = DealName

    @property
    def OwnerUin(self):
        return self._OwnerUin

    @OwnerUin.setter
    def OwnerUin(self, OwnerUin):
        self._OwnerUin = OwnerUin

    @property
    def Count(self):
        return self._Count

    @Count.setter
    def Count(self, Count):
        self._Count = Count

    @property
    def PayMode(self):
        return self._PayMode

    @PayMode.setter
    def PayMode(self, PayMode):
        self._PayMode = PayMode

    @property
    def FlowId(self):
        return self._FlowId

    @FlowId.setter
    def FlowId(self, FlowId):
        self._FlowId = FlowId

    @property
    def DBInstanceIdSet(self):
        return self._DBInstanceIdSet

    @DBInstanceIdSet.setter
    def DBInstanceIdSet(self, DBInstanceIdSet):
        self._DBInstanceIdSet = DBInstanceIdSet


    def _deserialize(self, params):
        self._DealName = params.get("DealName")
        self._OwnerUin = params.get("OwnerUin")
        self._Count = params.get("Count")
        self._PayMode = params.get("PayMode")
        self._FlowId = params.get("FlowId")
        self._DBInstanceIdSet = params.get("DBInstanceIdSet")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class PolicyRule(AbstractModel):
    """Rule information for security group

    """

    def __init__(self):
        r"""
        :param _Action: Policy, Valid values: `ACCEPT`, `DROP`.
        :type Action: str
        :param _CidrIp: Source or destination IP or IP range, such as 172.16.0.0/12.
        :type CidrIp: str
        :param _PortRange: Port
        :type PortRange: str
        :param _IpProtocol: Network protocol. UDP and TCP are supported.
        :type IpProtocol: str
        :param _Description: The rule description
        :type Description: str
        """
        self._Action = None
        self._CidrIp = None
        self._PortRange = None
        self._IpProtocol = None
        self._Description = None

    @property
    def Action(self):
        return self._Action

    @Action.setter
    def Action(self, Action):
        self._Action = Action

    @property
    def CidrIp(self):
        return self._CidrIp

    @CidrIp.setter
    def CidrIp(self, CidrIp):
        self._CidrIp = CidrIp

    @property
    def PortRange(self):
        return self._PortRange

    @PortRange.setter
    def PortRange(self, PortRange):
        self._PortRange = PortRange

    @property
    def IpProtocol(self):
        return self._IpProtocol

    @IpProtocol.setter
    def IpProtocol(self, IpProtocol):
        self._IpProtocol = IpProtocol

    @property
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description


    def _deserialize(self, params):
        self._Action = params.get("Action")
        self._CidrIp = params.get("CidrIp")
        self._PortRange = params.get("PortRange")
        self._IpProtocol = params.get("IpProtocol")
        self._Description = params.get("Description")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class RawSlowQuery(AbstractModel):
    """The list of slow query details returned by the `DescribeSlowQueryList` API

    """

    def __init__(self):
        r"""
        :param _RawQuery: Slow query statement
        :type RawQuery: str
        :param _DatabaseName: The database queried by the slow query statement
        :type DatabaseName: str
        :param _Duration: The execution time of the slow query statement
        :type Duration: float
        :param _ClientAddr: The client that executes the slow query statement
        :type ClientAddr: str
        :param _UserName: The name of the user who executes the slow query statement
        :type UserName: str
        :param _SessionStartTime: The time when the slow query statement starts to execute
        :type SessionStartTime: str
        """
        self._RawQuery = None
        self._DatabaseName = None
        self._Duration = None
        self._ClientAddr = None
        self._UserName = None
        self._SessionStartTime = None

    @property
    def RawQuery(self):
        return self._RawQuery

    @RawQuery.setter
    def RawQuery(self, RawQuery):
        self._RawQuery = RawQuery

    @property
    def DatabaseName(self):
        return self._DatabaseName

    @DatabaseName.setter
    def DatabaseName(self, DatabaseName):
        self._DatabaseName = DatabaseName

    @property
    def Duration(self):
        return self._Duration

    @Duration.setter
    def Duration(self, Duration):
        self._Duration = Duration

    @property
    def ClientAddr(self):
        return self._ClientAddr

    @ClientAddr.setter
    def ClientAddr(self, ClientAddr):
        self._ClientAddr = ClientAddr

    @property
    def UserName(self):
        return self._UserName

    @UserName.setter
    def UserName(self, UserName):
        self._UserName = UserName

    @property
    def SessionStartTime(self):
        return self._SessionStartTime

    @SessionStartTime.setter
    def SessionStartTime(self, SessionStartTime):
        self._SessionStartTime = SessionStartTime


    def _deserialize(self, params):
        self._RawQuery = params.get("RawQuery")
        self._DatabaseName = params.get("DatabaseName")
        self._Duration = params.get("Duration")
        self._ClientAddr = params.get("ClientAddr")
        self._UserName = params.get("UserName")
        self._SessionStartTime = params.get("SessionStartTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ReadOnlyGroup(AbstractModel):
    """RO group information

    """

    def __init__(self):
        r"""
        :param _ReadOnlyGroupId: RO group identifier
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ReadOnlyGroupId: str
        :param _ReadOnlyGroupName: RO group name
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ReadOnlyGroupName: str
        :param _ProjectId: Project ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ProjectId: int
        :param _MasterDBInstanceId: Primary instance ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type MasterDBInstanceId: str
        :param _MinDelayEliminateReserve: The minimum number of read-only replicas that must be retained in an RO group
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type MinDelayEliminateReserve: int
        :param _MaxReplayLatency: Delayed log size threshold
        :type MaxReplayLatency: int
        :param _ReplayLatencyEliminate: Whether to remove a read-only replica from an RO group if the sync log size difference between the read-only replica and the primary instance exceeds the threshold. Valid values: `0` (no), `1` (yes).
        :type ReplayLatencyEliminate: int
        :param _MaxReplayLag: Delay threshold
        :type MaxReplayLag: float
        :param _ReplayLagEliminate: Whether to remove a read-only replica from an RO group if the delay between the read-only replica and the primary instance exceeds the threshold. Valid values: `0` (no), `1` (yes).
        :type ReplayLagEliminate: int
        :param _VpcId: VPC ID
        :type VpcId: str
        :param _SubnetId: Subnet ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type SubnetId: str
        :param _Region: Region ID
        :type Region: str
        :param _Zone: Availability zone ID
        :type Zone: str
        :param _Status: Status
        :type Status: str
        :param _ReadOnlyDBInstanceList: Instance details
        :type ReadOnlyDBInstanceList: list of DBInstance
        :param _Rebalance: Whether to enable automatic load balancing
        :type Rebalance: int
        :param _DBInstanceNetInfo: Network information
        :type DBInstanceNetInfo: list of DBInstanceNetInfo
        :param _NetworkAccessList: Network access list of the RO group (this field has been deprecated)
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type NetworkAccessList: list of NetworkAccess
        """
        self._ReadOnlyGroupId = None
        self._ReadOnlyGroupName = None
        self._ProjectId = None
        self._MasterDBInstanceId = None
        self._MinDelayEliminateReserve = None
        self._MaxReplayLatency = None
        self._ReplayLatencyEliminate = None
        self._MaxReplayLag = None
        self._ReplayLagEliminate = None
        self._VpcId = None
        self._SubnetId = None
        self._Region = None
        self._Zone = None
        self._Status = None
        self._ReadOnlyDBInstanceList = None
        self._Rebalance = None
        self._DBInstanceNetInfo = None
        self._NetworkAccessList = None

    @property
    def ReadOnlyGroupId(self):
        return self._ReadOnlyGroupId

    @ReadOnlyGroupId.setter
    def ReadOnlyGroupId(self, ReadOnlyGroupId):
        self._ReadOnlyGroupId = ReadOnlyGroupId

    @property
    def ReadOnlyGroupName(self):
        return self._ReadOnlyGroupName

    @ReadOnlyGroupName.setter
    def ReadOnlyGroupName(self, ReadOnlyGroupName):
        self._ReadOnlyGroupName = ReadOnlyGroupName

    @property
    def ProjectId(self):
        return self._ProjectId

    @ProjectId.setter
    def ProjectId(self, ProjectId):
        self._ProjectId = ProjectId

    @property
    def MasterDBInstanceId(self):
        return self._MasterDBInstanceId

    @MasterDBInstanceId.setter
    def MasterDBInstanceId(self, MasterDBInstanceId):
        self._MasterDBInstanceId = MasterDBInstanceId

    @property
    def MinDelayEliminateReserve(self):
        return self._MinDelayEliminateReserve

    @MinDelayEliminateReserve.setter
    def MinDelayEliminateReserve(self, MinDelayEliminateReserve):
        self._MinDelayEliminateReserve = MinDelayEliminateReserve

    @property
    def MaxReplayLatency(self):
        return self._MaxReplayLatency

    @MaxReplayLatency.setter
    def MaxReplayLatency(self, MaxReplayLatency):
        self._MaxReplayLatency = MaxReplayLatency

    @property
    def ReplayLatencyEliminate(self):
        return self._ReplayLatencyEliminate

    @ReplayLatencyEliminate.setter
    def ReplayLatencyEliminate(self, ReplayLatencyEliminate):
        self._ReplayLatencyEliminate = ReplayLatencyEliminate

    @property
    def MaxReplayLag(self):
        return self._MaxReplayLag

    @MaxReplayLag.setter
    def MaxReplayLag(self, MaxReplayLag):
        self._MaxReplayLag = MaxReplayLag

    @property
    def ReplayLagEliminate(self):
        return self._ReplayLagEliminate

    @ReplayLagEliminate.setter
    def ReplayLagEliminate(self, ReplayLagEliminate):
        self._ReplayLagEliminate = ReplayLagEliminate

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def Region(self):
        return self._Region

    @Region.setter
    def Region(self, Region):
        self._Region = Region

    @property
    def Zone(self):
        return self._Zone

    @Zone.setter
    def Zone(self, Zone):
        self._Zone = Zone

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status

    @property
    def ReadOnlyDBInstanceList(self):
        return self._ReadOnlyDBInstanceList

    @ReadOnlyDBInstanceList.setter
    def ReadOnlyDBInstanceList(self, ReadOnlyDBInstanceList):
        self._ReadOnlyDBInstanceList = ReadOnlyDBInstanceList

    @property
    def Rebalance(self):
        return self._Rebalance

    @Rebalance.setter
    def Rebalance(self, Rebalance):
        self._Rebalance = Rebalance

    @property
    def DBInstanceNetInfo(self):
        return self._DBInstanceNetInfo

    @DBInstanceNetInfo.setter
    def DBInstanceNetInfo(self, DBInstanceNetInfo):
        self._DBInstanceNetInfo = DBInstanceNetInfo

    @property
    def NetworkAccessList(self):
        return self._NetworkAccessList

    @NetworkAccessList.setter
    def NetworkAccessList(self, NetworkAccessList):
        self._NetworkAccessList = NetworkAccessList


    def _deserialize(self, params):
        self._ReadOnlyGroupId = params.get("ReadOnlyGroupId")
        self._ReadOnlyGroupName = params.get("ReadOnlyGroupName")
        self._ProjectId = params.get("ProjectId")
        self._MasterDBInstanceId = params.get("MasterDBInstanceId")
        self._MinDelayEliminateReserve = params.get("MinDelayEliminateReserve")
        self._MaxReplayLatency = params.get("MaxReplayLatency")
        self._ReplayLatencyEliminate = params.get("ReplayLatencyEliminate")
        self._MaxReplayLag = params.get("MaxReplayLag")
        self._ReplayLagEliminate = params.get("ReplayLagEliminate")
        self._VpcId = params.get("VpcId")
        self._SubnetId = params.get("SubnetId")
        self._Region = params.get("Region")
        self._Zone = params.get("Zone")
        self._Status = params.get("Status")
        if params.get("ReadOnlyDBInstanceList") is not None:
            self._ReadOnlyDBInstanceList = []
            for item in params.get("ReadOnlyDBInstanceList"):
                obj = DBInstance()
                obj._deserialize(item)
                self._ReadOnlyDBInstanceList.append(obj)
        self._Rebalance = params.get("Rebalance")
        if params.get("DBInstanceNetInfo") is not None:
            self._DBInstanceNetInfo = []
            for item in params.get("DBInstanceNetInfo"):
                obj = DBInstanceNetInfo()
                obj._deserialize(item)
                self._DBInstanceNetInfo.append(obj)
        if params.get("NetworkAccessList") is not None:
            self._NetworkAccessList = []
            for item in params.get("NetworkAccessList"):
                obj = NetworkAccess()
                obj._deserialize(item)
                self._NetworkAccessList.append(obj)
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class RebalanceReadOnlyGroupRequest(AbstractModel):
    """RebalanceReadOnlyGroup request structure.

    """

    def __init__(self):
        r"""
        :param _ReadOnlyGroupId: RO group ID
        :type ReadOnlyGroupId: str
        """
        self._ReadOnlyGroupId = None

    @property
    def ReadOnlyGroupId(self):
        return self._ReadOnlyGroupId

    @ReadOnlyGroupId.setter
    def ReadOnlyGroupId(self, ReadOnlyGroupId):
        self._ReadOnlyGroupId = ReadOnlyGroupId


    def _deserialize(self, params):
        self._ReadOnlyGroupId = params.get("ReadOnlyGroupId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class RebalanceReadOnlyGroupResponse(AbstractModel):
    """RebalanceReadOnlyGroup response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class RegionInfo(AbstractModel):
    """Region information such as number and status

    """

    def __init__(self):
        r"""
        :param _Region: Region abbreviation
        :type Region: str
        :param _RegionName: Region name
        :type RegionName: str
        :param _RegionId: Region number
        :type RegionId: int
        :param _RegionState: Availability status. UNAVAILABLE: unavailable, AVAILABLE: available
        :type RegionState: str
        :param _SupportInternational: Whether the resource can be purchased in this region. Valid values: `0` (no), `1` (yes).
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type SupportInternational: int
        """
        self._Region = None
        self._RegionName = None
        self._RegionId = None
        self._RegionState = None
        self._SupportInternational = None

    @property
    def Region(self):
        return self._Region

    @Region.setter
    def Region(self, Region):
        self._Region = Region

    @property
    def RegionName(self):
        return self._RegionName

    @RegionName.setter
    def RegionName(self, RegionName):
        self._RegionName = RegionName

    @property
    def RegionId(self):
        return self._RegionId

    @RegionId.setter
    def RegionId(self, RegionId):
        self._RegionId = RegionId

    @property
    def RegionState(self):
        return self._RegionState

    @RegionState.setter
    def RegionState(self, RegionState):
        self._RegionState = RegionState

    @property
    def SupportInternational(self):
        return self._SupportInternational

    @SupportInternational.setter
    def SupportInternational(self, SupportInternational):
        self._SupportInternational = SupportInternational


    def _deserialize(self, params):
        self._Region = params.get("Region")
        self._RegionName = params.get("RegionName")
        self._RegionId = params.get("RegionId")
        self._RegionState = params.get("RegionState")
        self._SupportInternational = params.get("SupportInternational")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class RemoveDBInstanceFromReadOnlyGroupRequest(AbstractModel):
    """RemoveDBInstanceFromReadOnlyGroup request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _ReadOnlyGroupId: RO group ID
        :type ReadOnlyGroupId: str
        """
        self._DBInstanceId = None
        self._ReadOnlyGroupId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def ReadOnlyGroupId(self):
        return self._ReadOnlyGroupId

    @ReadOnlyGroupId.setter
    def ReadOnlyGroupId(self, ReadOnlyGroupId):
        self._ReadOnlyGroupId = ReadOnlyGroupId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._ReadOnlyGroupId = params.get("ReadOnlyGroupId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class RemoveDBInstanceFromReadOnlyGroupResponse(AbstractModel):
    """RemoveDBInstanceFromReadOnlyGroup response structure.

    """

    def __init__(self):
        r"""
        :param _FlowId: Task ID
        :type FlowId: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._FlowId = None
        self._RequestId = None

    @property
    def FlowId(self):
        return self._FlowId

    @FlowId.setter
    def FlowId(self, FlowId):
        self._FlowId = FlowId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._FlowId = params.get("FlowId")
        self._RequestId = params.get("RequestId")


class RenewInstanceRequest(AbstractModel):
    """RenewInstance request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of `postgres-6fego161`
        :type DBInstanceId: str
        :param _Period: Renewal duration in months
        :type Period: int
        :param _AutoVoucher: Whether to automatically use vouchers. 1: yes, 0: no. Default value: 0
        :type AutoVoucher: int
        :param _VoucherIds: Voucher ID list (only one voucher can be specified currently)
        :type VoucherIds: list of str
        """
        self._DBInstanceId = None
        self._Period = None
        self._AutoVoucher = None
        self._VoucherIds = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def Period(self):
        return self._Period

    @Period.setter
    def Period(self, Period):
        self._Period = Period

    @property
    def AutoVoucher(self):
        return self._AutoVoucher

    @AutoVoucher.setter
    def AutoVoucher(self, AutoVoucher):
        self._AutoVoucher = AutoVoucher

    @property
    def VoucherIds(self):
        return self._VoucherIds

    @VoucherIds.setter
    def VoucherIds(self, VoucherIds):
        self._VoucherIds = VoucherIds


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._Period = params.get("Period")
        self._AutoVoucher = params.get("AutoVoucher")
        self._VoucherIds = params.get("VoucherIds")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class RenewInstanceResponse(AbstractModel):
    """RenewInstance response structure.

    """

    def __init__(self):
        r"""
        :param _DealName: Order name
        :type DealName: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DealName = None
        self._RequestId = None

    @property
    def DealName(self):
        return self._DealName

    @DealName.setter
    def DealName(self, DealName):
        self._DealName = DealName

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._DealName = params.get("DealName")
        self._RequestId = params.get("RequestId")


class ResetAccountPasswordRequest(AbstractModel):
    """ResetAccountPassword request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of postgres-4wdeb0zv
        :type DBInstanceId: str
        :param _UserName: Instance account name
        :type UserName: str
        :param _Password: New password corresponding to `UserName` account
        :type Password: str
        """
        self._DBInstanceId = None
        self._UserName = None
        self._Password = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def UserName(self):
        return self._UserName

    @UserName.setter
    def UserName(self, UserName):
        self._UserName = UserName

    @property
    def Password(self):
        return self._Password

    @Password.setter
    def Password(self, Password):
        self._Password = Password


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._UserName = params.get("UserName")
        self._Password = params.get("Password")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ResetAccountPasswordResponse(AbstractModel):
    """ResetAccountPassword response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class RestartDBInstanceRequest(AbstractModel):
    """RestartDBInstance request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID in the format of postgres-6r233v55
        :type DBInstanceId: str
        """
        self._DBInstanceId = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class RestartDBInstanceResponse(AbstractModel):
    """RestartDBInstance response structure.

    """

    def __init__(self):
        r"""
        :param _FlowId: Async flow ID
        :type FlowId: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._FlowId = None
        self._RequestId = None

    @property
    def FlowId(self):
        return self._FlowId

    @FlowId.setter
    def FlowId(self, FlowId):
        self._FlowId = FlowId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._FlowId = params.get("FlowId")
        self._RequestId = params.get("RequestId")


class SecurityGroup(AbstractModel):
    """Security group information

    """

    def __init__(self):
        r"""
        :param _ProjectId: Project ID
        :type ProjectId: int
        :param _CreateTime: Creation time
        :type CreateTime: str
        :param _Inbound: Inbound rule
        :type Inbound: list of PolicyRule
        :param _Outbound: Outbound rule
        :type Outbound: list of PolicyRule
        :param _SecurityGroupId: Security group ID
        :type SecurityGroupId: str
        :param _SecurityGroupName: Security group name
        :type SecurityGroupName: str
        :param _SecurityGroupDescription: Security group remarks
        :type SecurityGroupDescription: str
        """
        self._ProjectId = None
        self._CreateTime = None
        self._Inbound = None
        self._Outbound = None
        self._SecurityGroupId = None
        self._SecurityGroupName = None
        self._SecurityGroupDescription = None

    @property
    def ProjectId(self):
        return self._ProjectId

    @ProjectId.setter
    def ProjectId(self, ProjectId):
        self._ProjectId = ProjectId

    @property
    def CreateTime(self):
        return self._CreateTime

    @CreateTime.setter
    def CreateTime(self, CreateTime):
        self._CreateTime = CreateTime

    @property
    def Inbound(self):
        return self._Inbound

    @Inbound.setter
    def Inbound(self, Inbound):
        self._Inbound = Inbound

    @property
    def Outbound(self):
        return self._Outbound

    @Outbound.setter
    def Outbound(self, Outbound):
        self._Outbound = Outbound

    @property
    def SecurityGroupId(self):
        return self._SecurityGroupId

    @SecurityGroupId.setter
    def SecurityGroupId(self, SecurityGroupId):
        self._SecurityGroupId = SecurityGroupId

    @property
    def SecurityGroupName(self):
        return self._SecurityGroupName

    @SecurityGroupName.setter
    def SecurityGroupName(self, SecurityGroupName):
        self._SecurityGroupName = SecurityGroupName

    @property
    def SecurityGroupDescription(self):
        return self._SecurityGroupDescription

    @SecurityGroupDescription.setter
    def SecurityGroupDescription(self, SecurityGroupDescription):
        self._SecurityGroupDescription = SecurityGroupDescription


    def _deserialize(self, params):
        self._ProjectId = params.get("ProjectId")
        self._CreateTime = params.get("CreateTime")
        if params.get("Inbound") is not None:
            self._Inbound = []
            for item in params.get("Inbound"):
                obj = PolicyRule()
                obj._deserialize(item)
                self._Inbound.append(obj)
        if params.get("Outbound") is not None:
            self._Outbound = []
            for item in params.get("Outbound"):
                obj = PolicyRule()
                obj._deserialize(item)
                self._Outbound.append(obj)
        self._SecurityGroupId = params.get("SecurityGroupId")
        self._SecurityGroupName = params.get("SecurityGroupName")
        self._SecurityGroupDescription = params.get("SecurityGroupDescription")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ServerlessDBAccount(AbstractModel):
    """PostgreSQL for Serverless instance account description

    """

    def __init__(self):
        r"""
        :param _DBUser: Username
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBUser: str
        :param _DBPassword: Password
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBPassword: str
        :param _DBConnLimit: The maximum number of connections
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBConnLimit: int
        """
        self._DBUser = None
        self._DBPassword = None
        self._DBConnLimit = None

    @property
    def DBUser(self):
        return self._DBUser

    @DBUser.setter
    def DBUser(self, DBUser):
        self._DBUser = DBUser

    @property
    def DBPassword(self):
        return self._DBPassword

    @DBPassword.setter
    def DBPassword(self, DBPassword):
        self._DBPassword = DBPassword

    @property
    def DBConnLimit(self):
        return self._DBConnLimit

    @DBConnLimit.setter
    def DBConnLimit(self, DBConnLimit):
        self._DBConnLimit = DBConnLimit


    def _deserialize(self, params):
        self._DBUser = params.get("DBUser")
        self._DBPassword = params.get("DBPassword")
        self._DBConnLimit = params.get("DBConnLimit")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ServerlessDBInstance(AbstractModel):
    """PostgreSQL for Serverless instance description

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID, which is the unique identifier
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBInstanceId: str
        :param _DBInstanceName: Instance name
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBInstanceName: str
        :param _DBInstanceStatus: Instance status
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBInstanceStatus: str
        :param _Region: Region
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type Region: str
        :param _Zone: Availability zone
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type Zone: str
        :param _ProjectId: Project ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type ProjectId: int
        :param _VpcId: VPC ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type VpcId: str
        :param _SubnetId: Subnet ID
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type SubnetId: str
        :param _DBCharset: Character set
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBCharset: str
        :param _DBVersion: Database version
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBVersion: str
        :param _CreateTime: Creation time
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type CreateTime: str
        :param _DBInstanceNetInfo: Instance network information
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBInstanceNetInfo: list of ServerlessDBInstanceNetInfo
        :param _DBAccountSet: Instance account information
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBAccountSet: list of ServerlessDBAccount
        :param _DBDatabaseList: Information of the databases in an instance
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBDatabaseList: list of str
        :param _TagList: The array of tags bound to an instance
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type TagList: list of Tag
        :param _DBKernelVersion: Database kernel version
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBKernelVersion: str
        :param _DBMajorVersion: Database major version number
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type DBMajorVersion: str
        """
        self._DBInstanceId = None
        self._DBInstanceName = None
        self._DBInstanceStatus = None
        self._Region = None
        self._Zone = None
        self._ProjectId = None
        self._VpcId = None
        self._SubnetId = None
        self._DBCharset = None
        self._DBVersion = None
        self._CreateTime = None
        self._DBInstanceNetInfo = None
        self._DBAccountSet = None
        self._DBDatabaseList = None
        self._TagList = None
        self._DBKernelVersion = None
        self._DBMajorVersion = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def DBInstanceName(self):
        return self._DBInstanceName

    @DBInstanceName.setter
    def DBInstanceName(self, DBInstanceName):
        self._DBInstanceName = DBInstanceName

    @property
    def DBInstanceStatus(self):
        return self._DBInstanceStatus

    @DBInstanceStatus.setter
    def DBInstanceStatus(self, DBInstanceStatus):
        self._DBInstanceStatus = DBInstanceStatus

    @property
    def Region(self):
        return self._Region

    @Region.setter
    def Region(self, Region):
        self._Region = Region

    @property
    def Zone(self):
        return self._Zone

    @Zone.setter
    def Zone(self, Zone):
        self._Zone = Zone

    @property
    def ProjectId(self):
        return self._ProjectId

    @ProjectId.setter
    def ProjectId(self, ProjectId):
        self._ProjectId = ProjectId

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def SubnetId(self):
        return self._SubnetId

    @SubnetId.setter
    def SubnetId(self, SubnetId):
        self._SubnetId = SubnetId

    @property
    def DBCharset(self):
        return self._DBCharset

    @DBCharset.setter
    def DBCharset(self, DBCharset):
        self._DBCharset = DBCharset

    @property
    def DBVersion(self):
        return self._DBVersion

    @DBVersion.setter
    def DBVersion(self, DBVersion):
        self._DBVersion = DBVersion

    @property
    def CreateTime(self):
        return self._CreateTime

    @CreateTime.setter
    def CreateTime(self, CreateTime):
        self._CreateTime = CreateTime

    @property
    def DBInstanceNetInfo(self):
        return self._DBInstanceNetInfo

    @DBInstanceNetInfo.setter
    def DBInstanceNetInfo(self, DBInstanceNetInfo):
        self._DBInstanceNetInfo = DBInstanceNetInfo

    @property
    def DBAccountSet(self):
        return self._DBAccountSet

    @DBAccountSet.setter
    def DBAccountSet(self, DBAccountSet):
        self._DBAccountSet = DBAccountSet

    @property
    def DBDatabaseList(self):
        return self._DBDatabaseList

    @DBDatabaseList.setter
    def DBDatabaseList(self, DBDatabaseList):
        self._DBDatabaseList = DBDatabaseList

    @property
    def TagList(self):
        return self._TagList

    @TagList.setter
    def TagList(self, TagList):
        self._TagList = TagList

    @property
    def DBKernelVersion(self):
        return self._DBKernelVersion

    @DBKernelVersion.setter
    def DBKernelVersion(self, DBKernelVersion):
        self._DBKernelVersion = DBKernelVersion

    @property
    def DBMajorVersion(self):
        return self._DBMajorVersion

    @DBMajorVersion.setter
    def DBMajorVersion(self, DBMajorVersion):
        self._DBMajorVersion = DBMajorVersion


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._DBInstanceName = params.get("DBInstanceName")
        self._DBInstanceStatus = params.get("DBInstanceStatus")
        self._Region = params.get("Region")
        self._Zone = params.get("Zone")
        self._ProjectId = params.get("ProjectId")
        self._VpcId = params.get("VpcId")
        self._SubnetId = params.get("SubnetId")
        self._DBCharset = params.get("DBCharset")
        self._DBVersion = params.get("DBVersion")
        self._CreateTime = params.get("CreateTime")
        if params.get("DBInstanceNetInfo") is not None:
            self._DBInstanceNetInfo = []
            for item in params.get("DBInstanceNetInfo"):
                obj = ServerlessDBInstanceNetInfo()
                obj._deserialize(item)
                self._DBInstanceNetInfo.append(obj)
        if params.get("DBAccountSet") is not None:
            self._DBAccountSet = []
            for item in params.get("DBAccountSet"):
                obj = ServerlessDBAccount()
                obj._deserialize(item)
                self._DBAccountSet.append(obj)
        self._DBDatabaseList = params.get("DBDatabaseList")
        if params.get("TagList") is not None:
            self._TagList = []
            for item in params.get("TagList"):
                obj = Tag()
                obj._deserialize(item)
                self._TagList.append(obj)
        self._DBKernelVersion = params.get("DBKernelVersion")
        self._DBMajorVersion = params.get("DBMajorVersion")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ServerlessDBInstanceNetInfo(AbstractModel):
    """PostgreSQL for Serverless instance network description

    """

    def __init__(self):
        r"""
        :param _Address: Address
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type Address: str
        :param _Ip: IP address
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type Ip: str
        :param _Port: Port number
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type Port: int
        :param _Status: Status
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type Status: str
        :param _NetType: Network type
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type NetType: str
        """
        self._Address = None
        self._Ip = None
        self._Port = None
        self._Status = None
        self._NetType = None

    @property
    def Address(self):
        return self._Address

    @Address.setter
    def Address(self, Address):
        self._Address = Address

    @property
    def Ip(self):
        return self._Ip

    @Ip.setter
    def Ip(self, Ip):
        self._Ip = Ip

    @property
    def Port(self):
        return self._Port

    @Port.setter
    def Port(self, Port):
        self._Port = Port

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status

    @property
    def NetType(self):
        return self._NetType

    @NetType.setter
    def NetType(self, NetType):
        self._NetType = NetType


    def _deserialize(self, params):
        self._Address = params.get("Address")
        self._Ip = params.get("Ip")
        self._Port = params.get("Port")
        self._Status = params.get("Status")
        self._NetType = params.get("NetType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class SetAutoRenewFlagRequest(AbstractModel):
    """SetAutoRenewFlag request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceIdSet: List of instance IDs. Note that currently you cannot manipulate multiple instances at the same time. Only one instance ID can be passed in here.
        :type DBInstanceIdSet: list of str
        :param _AutoRenewFlag: Renewal flag. 0: normal renewal, 1: auto-renewal, 2: no renewal upon expiration
        :type AutoRenewFlag: int
        """
        self._DBInstanceIdSet = None
        self._AutoRenewFlag = None

    @property
    def DBInstanceIdSet(self):
        return self._DBInstanceIdSet

    @DBInstanceIdSet.setter
    def DBInstanceIdSet(self, DBInstanceIdSet):
        self._DBInstanceIdSet = DBInstanceIdSet

    @property
    def AutoRenewFlag(self):
        return self._AutoRenewFlag

    @AutoRenewFlag.setter
    def AutoRenewFlag(self, AutoRenewFlag):
        self._AutoRenewFlag = AutoRenewFlag


    def _deserialize(self, params):
        self._DBInstanceIdSet = params.get("DBInstanceIdSet")
        self._AutoRenewFlag = params.get("AutoRenewFlag")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class SetAutoRenewFlagResponse(AbstractModel):
    """SetAutoRenewFlag response structure.

    """

    def __init__(self):
        r"""
        :param _Count: Number of successfully set instances
        :type Count: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Count = None
        self._RequestId = None

    @property
    def Count(self):
        return self._Count

    @Count.setter
    def Count(self, Count):
        self._Count = Count

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._Count = params.get("Count")
        self._RequestId = params.get("RequestId")


class SlowlogDetail(AbstractModel):
    """Slow query details

    """

    def __init__(self):
        r"""
        :param _TotalTime: Total time consumed
        :type TotalTime: float
        :param _TotalCalls: Total number of calls
        :type TotalCalls: int
        :param _NormalQueries: List of slow SQL statements after desensitization
        :type NormalQueries: list of NormalQueryItem
        """
        self._TotalTime = None
        self._TotalCalls = None
        self._NormalQueries = None

    @property
    def TotalTime(self):
        return self._TotalTime

    @TotalTime.setter
    def TotalTime(self, TotalTime):
        self._TotalTime = TotalTime

    @property
    def TotalCalls(self):
        return self._TotalCalls

    @TotalCalls.setter
    def TotalCalls(self, TotalCalls):
        self._TotalCalls = TotalCalls

    @property
    def NormalQueries(self):
        return self._NormalQueries

    @NormalQueries.setter
    def NormalQueries(self, NormalQueries):
        self._NormalQueries = NormalQueries


    def _deserialize(self, params):
        self._TotalTime = params.get("TotalTime")
        self._TotalCalls = params.get("TotalCalls")
        if params.get("NormalQueries") is not None:
            self._NormalQueries = []
            for item in params.get("NormalQueries"):
                obj = NormalQueryItem()
                obj._deserialize(item)
                self._NormalQueries.append(obj)
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class SpecInfo(AbstractModel):
    """Purchasable specification details in an AZ in a region.

    """

    def __init__(self):
        r"""
        :param _Region: Region abbreviation, which corresponds to the `Region` field of `RegionSet`
        :type Region: str
        :param _Zone: AZ abbreviate, which corresponds to the `Zone` field of `ZoneSet`
        :type Zone: str
        :param _SpecItemInfoList: Specification details list
        :type SpecItemInfoList: list of SpecItemInfo
        :param _SupportKMSRegions: Regions where KMS is supported
Note: This field may return `null`, indicating that no valid value was found.
        :type SupportKMSRegions: list of str
        """
        self._Region = None
        self._Zone = None
        self._SpecItemInfoList = None
        self._SupportKMSRegions = None

    @property
    def Region(self):
        return self._Region

    @Region.setter
    def Region(self, Region):
        self._Region = Region

    @property
    def Zone(self):
        return self._Zone

    @Zone.setter
    def Zone(self, Zone):
        self._Zone = Zone

    @property
    def SpecItemInfoList(self):
        return self._SpecItemInfoList

    @SpecItemInfoList.setter
    def SpecItemInfoList(self, SpecItemInfoList):
        self._SpecItemInfoList = SpecItemInfoList

    @property
    def SupportKMSRegions(self):
        return self._SupportKMSRegions

    @SupportKMSRegions.setter
    def SupportKMSRegions(self, SupportKMSRegions):
        self._SupportKMSRegions = SupportKMSRegions


    def _deserialize(self, params):
        self._Region = params.get("Region")
        self._Zone = params.get("Zone")
        if params.get("SpecItemInfoList") is not None:
            self._SpecItemInfoList = []
            for item in params.get("SpecItemInfoList"):
                obj = SpecItemInfo()
                obj._deserialize(item)
                self._SpecItemInfoList.append(obj)
        self._SupportKMSRegions = params.get("SupportKMSRegions")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class SpecItemInfo(AbstractModel):
    """Specification description

    """

    def __init__(self):
        r"""
        :param _SpecCode: Specification ID
        :type SpecCode: str
        :param _Version: PostgerSQL version number
        :type Version: str
        :param _VersionName: Full version name corresponding to kernel number
        :type VersionName: str
        :param _Cpu: Number of CPU cores
        :type Cpu: int
        :param _Memory: Memory size in MB
        :type Memory: int
        :param _MaxStorage: Maximum storage capacity in GB supported by this specification
        :type MaxStorage: int
        :param _MinStorage: Minimum storage capacity in GB supported by this specification
        :type MinStorage: int
        :param _Qps: Estimated QPS for this specification
        :type Qps: int
        :param _Pid: (Disused)
        :type Pid: int
        :param _Type: Machine type
        :type Type: str
        :param _MajorVersion: PostgreSQL major version number
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type MajorVersion: str
        :param _KernelVersion: PostgreSQL kernel version number
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type KernelVersion: str
        :param _IsSupportTDE: Whether TDE data encryption is supported. Valid values: 0 (no), 1 (yes)
Note: This field may return `null`, indicating that no valid value was found.
        :type IsSupportTDE: int
        """
        self._SpecCode = None
        self._Version = None
        self._VersionName = None
        self._Cpu = None
        self._Memory = None
        self._MaxStorage = None
        self._MinStorage = None
        self._Qps = None
        self._Pid = None
        self._Type = None
        self._MajorVersion = None
        self._KernelVersion = None
        self._IsSupportTDE = None

    @property
    def SpecCode(self):
        return self._SpecCode

    @SpecCode.setter
    def SpecCode(self, SpecCode):
        self._SpecCode = SpecCode

    @property
    def Version(self):
        return self._Version

    @Version.setter
    def Version(self, Version):
        self._Version = Version

    @property
    def VersionName(self):
        return self._VersionName

    @VersionName.setter
    def VersionName(self, VersionName):
        self._VersionName = VersionName

    @property
    def Cpu(self):
        return self._Cpu

    @Cpu.setter
    def Cpu(self, Cpu):
        self._Cpu = Cpu

    @property
    def Memory(self):
        return self._Memory

    @Memory.setter
    def Memory(self, Memory):
        self._Memory = Memory

    @property
    def MaxStorage(self):
        return self._MaxStorage

    @MaxStorage.setter
    def MaxStorage(self, MaxStorage):
        self._MaxStorage = MaxStorage

    @property
    def MinStorage(self):
        return self._MinStorage

    @MinStorage.setter
    def MinStorage(self, MinStorage):
        self._MinStorage = MinStorage

    @property
    def Qps(self):
        return self._Qps

    @Qps.setter
    def Qps(self, Qps):
        self._Qps = Qps

    @property
    def Pid(self):
        return self._Pid

    @Pid.setter
    def Pid(self, Pid):
        self._Pid = Pid

    @property
    def Type(self):
        return self._Type

    @Type.setter
    def Type(self, Type):
        self._Type = Type

    @property
    def MajorVersion(self):
        return self._MajorVersion

    @MajorVersion.setter
    def MajorVersion(self, MajorVersion):
        self._MajorVersion = MajorVersion

    @property
    def KernelVersion(self):
        return self._KernelVersion

    @KernelVersion.setter
    def KernelVersion(self, KernelVersion):
        self._KernelVersion = KernelVersion

    @property
    def IsSupportTDE(self):
        return self._IsSupportTDE

    @IsSupportTDE.setter
    def IsSupportTDE(self, IsSupportTDE):
        self._IsSupportTDE = IsSupportTDE


    def _deserialize(self, params):
        self._SpecCode = params.get("SpecCode")
        self._Version = params.get("Version")
        self._VersionName = params.get("VersionName")
        self._Cpu = params.get("Cpu")
        self._Memory = params.get("Memory")
        self._MaxStorage = params.get("MaxStorage")
        self._MinStorage = params.get("MinStorage")
        self._Qps = params.get("Qps")
        self._Pid = params.get("Pid")
        self._Type = params.get("Type")
        self._MajorVersion = params.get("MajorVersion")
        self._KernelVersion = params.get("KernelVersion")
        self._IsSupportTDE = params.get("IsSupportTDE")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class Tag(AbstractModel):
    """The information of tags associated with instances, including `TagKey` and `TagValue`

    """

    def __init__(self):
        r"""
        :param _TagKey: Tag key
        :type TagKey: str
        :param _TagValue: Tag value
        :type TagValue: str
        """
        self._TagKey = None
        self._TagValue = None

    @property
    def TagKey(self):
        return self._TagKey

    @TagKey.setter
    def TagKey(self, TagKey):
        self._TagKey = TagKey

    @property
    def TagValue(self):
        return self._TagValue

    @TagValue.setter
    def TagValue(self, TagValue):
        self._TagValue = TagValue


    def _deserialize(self, params):
        self._TagKey = params.get("TagKey")
        self._TagValue = params.get("TagValue")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class UpgradeDBInstanceKernelVersionRequest(AbstractModel):
    """UpgradeDBInstanceKernelVersion request structure.

    """

    def __init__(self):
        r"""
        :param _DBInstanceId: Instance ID
        :type DBInstanceId: str
        :param _TargetDBKernelVersion: Target kernel version, which can be obtained in the `AvailableUpgradeTarget` field returned by the `DescribeDBVersions` API.
        :type TargetDBKernelVersion: str
        :param _SwitchTag: Switch time after the kernel version upgrade. Valid values:
`0` (default value): Switch now.
`1`: Switch at the specified time.
`2`: Switch in the maintenance time.
        :type SwitchTag: int
        :param _SwitchStartTime: Switch start time in the format of `HH:MM:SS`, such as 01:00:00. When `SwitchTag` is `0` or `2`, this parameter is invalid.
        :type SwitchStartTime: str
        :param _SwitchEndTime: Switch end time in the format of `HH:MM:SS`, such as 01:30:00. When `SwitchTag` is `0` or `2`, this parameter is invalid. The difference between `SwitchStartTime` and `SwitchEndTime` cannot be less than 30 minutes.
        :type SwitchEndTime: str
        :param _DryRun: Whether to perform a precheck on the current operation of upgrading the instance kernel version. Valid values:
`true`: Performs a precheck without upgrading the kernel version. Check items include request parameters, kernel version compatibility, and instance parameters.
`false` (default value): Sends a normal request and upgrades the kernel version directly after the check is passed.
        :type DryRun: bool
        """
        self._DBInstanceId = None
        self._TargetDBKernelVersion = None
        self._SwitchTag = None
        self._SwitchStartTime = None
        self._SwitchEndTime = None
        self._DryRun = None

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def TargetDBKernelVersion(self):
        return self._TargetDBKernelVersion

    @TargetDBKernelVersion.setter
    def TargetDBKernelVersion(self, TargetDBKernelVersion):
        self._TargetDBKernelVersion = TargetDBKernelVersion

    @property
    def SwitchTag(self):
        return self._SwitchTag

    @SwitchTag.setter
    def SwitchTag(self, SwitchTag):
        self._SwitchTag = SwitchTag

    @property
    def SwitchStartTime(self):
        return self._SwitchStartTime

    @SwitchStartTime.setter
    def SwitchStartTime(self, SwitchStartTime):
        self._SwitchStartTime = SwitchStartTime

    @property
    def SwitchEndTime(self):
        return self._SwitchEndTime

    @SwitchEndTime.setter
    def SwitchEndTime(self, SwitchEndTime):
        self._SwitchEndTime = SwitchEndTime

    @property
    def DryRun(self):
        return self._DryRun

    @DryRun.setter
    def DryRun(self, DryRun):
        self._DryRun = DryRun


    def _deserialize(self, params):
        self._DBInstanceId = params.get("DBInstanceId")
        self._TargetDBKernelVersion = params.get("TargetDBKernelVersion")
        self._SwitchTag = params.get("SwitchTag")
        self._SwitchStartTime = params.get("SwitchStartTime")
        self._SwitchEndTime = params.get("SwitchEndTime")
        self._DryRun = params.get("DryRun")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class UpgradeDBInstanceKernelVersionResponse(AbstractModel):
    """UpgradeDBInstanceKernelVersion response structure.

    """

    def __init__(self):
        r"""
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RequestId = None

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._RequestId = params.get("RequestId")


class UpgradeDBInstanceRequest(AbstractModel):
    """UpgradeDBInstance request structure.

    """

    def __init__(self):
        r"""
        :param _Memory: Instance memory size in GB after upgrade
        :type Memory: int
        :param _Storage: Instance disk size in GB after upgrade
        :type Storage: int
        :param _DBInstanceId: Instance ID in the format of postgres-lnp6j617
        :type DBInstanceId: str
        :param _AutoVoucher: Whether to automatically use vouchers. 1: yes, 0: no. Default value: no
        :type AutoVoucher: int
        :param _VoucherIds: Voucher ID list (only one voucher can be specified currently)
        :type VoucherIds: list of str
        :param _ActivityId: Activity ID
        :type ActivityId: int
        :param _SwitchTag: Switch time after instance configurations are modified. Valid values: `0` (switch immediately), `1` (switch at specified time). Default value: `0`
        :type SwitchTag: int
        :param _SwitchStartTime: The earliest time to start a switch
        :type SwitchStartTime: str
        :param _SwitchEndTime: The latest time to start a switch
        :type SwitchEndTime: str
        """
        self._Memory = None
        self._Storage = None
        self._DBInstanceId = None
        self._AutoVoucher = None
        self._VoucherIds = None
        self._ActivityId = None
        self._SwitchTag = None
        self._SwitchStartTime = None
        self._SwitchEndTime = None

    @property
    def Memory(self):
        return self._Memory

    @Memory.setter
    def Memory(self, Memory):
        self._Memory = Memory

    @property
    def Storage(self):
        return self._Storage

    @Storage.setter
    def Storage(self, Storage):
        self._Storage = Storage

    @property
    def DBInstanceId(self):
        return self._DBInstanceId

    @DBInstanceId.setter
    def DBInstanceId(self, DBInstanceId):
        self._DBInstanceId = DBInstanceId

    @property
    def AutoVoucher(self):
        return self._AutoVoucher

    @AutoVoucher.setter
    def AutoVoucher(self, AutoVoucher):
        self._AutoVoucher = AutoVoucher

    @property
    def VoucherIds(self):
        return self._VoucherIds

    @VoucherIds.setter
    def VoucherIds(self, VoucherIds):
        self._VoucherIds = VoucherIds

    @property
    def ActivityId(self):
        return self._ActivityId

    @ActivityId.setter
    def ActivityId(self, ActivityId):
        self._ActivityId = ActivityId

    @property
    def SwitchTag(self):
        return self._SwitchTag

    @SwitchTag.setter
    def SwitchTag(self, SwitchTag):
        self._SwitchTag = SwitchTag

    @property
    def SwitchStartTime(self):
        return self._SwitchStartTime

    @SwitchStartTime.setter
    def SwitchStartTime(self, SwitchStartTime):
        self._SwitchStartTime = SwitchStartTime

    @property
    def SwitchEndTime(self):
        return self._SwitchEndTime

    @SwitchEndTime.setter
    def SwitchEndTime(self, SwitchEndTime):
        self._SwitchEndTime = SwitchEndTime


    def _deserialize(self, params):
        self._Memory = params.get("Memory")
        self._Storage = params.get("Storage")
        self._DBInstanceId = params.get("DBInstanceId")
        self._AutoVoucher = params.get("AutoVoucher")
        self._VoucherIds = params.get("VoucherIds")
        self._ActivityId = params.get("ActivityId")
        self._SwitchTag = params.get("SwitchTag")
        self._SwitchStartTime = params.get("SwitchStartTime")
        self._SwitchEndTime = params.get("SwitchEndTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class UpgradeDBInstanceResponse(AbstractModel):
    """UpgradeDBInstance response structure.

    """

    def __init__(self):
        r"""
        :param _DealName: Transaction name.
        :type DealName: str
        :param _BillId: Bill ID of frozen fees
        :type BillId: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DealName = None
        self._BillId = None
        self._RequestId = None

    @property
    def DealName(self):
        return self._DealName

    @DealName.setter
    def DealName(self, DealName):
        self._DealName = DealName

    @property
    def BillId(self):
        return self._BillId

    @BillId.setter
    def BillId(self, BillId):
        self._BillId = BillId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._DealName = params.get("DealName")
        self._BillId = params.get("BillId")
        self._RequestId = params.get("RequestId")


class Version(AbstractModel):
    """Database version information

    """

    def __init__(self):
        r"""
        :param _DBEngine: Database engines. Valid values:
1. `postgresql` (TencentDB for PostgreSQL)
2. `mssql_compatible` (MSSQL compatible-TencentDB for PostgreSQL)
        :type DBEngine: str
        :param _DBVersion: Database version, such as 12.4.
        :type DBVersion: str
        :param _DBMajorVersion: Database major version, such as 12.
        :type DBMajorVersion: str
        :param _DBKernelVersion: Database kernel version, such as v12.4_r1.3.
        :type DBKernelVersion: str
        :param _SupportedFeatureNames: List of features supported by the database kernel, such as:
TDE: Supports data encryption.
        :type SupportedFeatureNames: list of str
        :param _Status: Database version status. Valid values:
`AVAILABLE`.
`DEPRECATED`.
        :type Status: str
        :param _AvailableUpgradeTarget: List of versions to which this database version (`DBKernelVersion`) can be upgraded.
        :type AvailableUpgradeTarget: list of str
        """
        self._DBEngine = None
        self._DBVersion = None
        self._DBMajorVersion = None
        self._DBKernelVersion = None
        self._SupportedFeatureNames = None
        self._Status = None
        self._AvailableUpgradeTarget = None

    @property
    def DBEngine(self):
        return self._DBEngine

    @DBEngine.setter
    def DBEngine(self, DBEngine):
        self._DBEngine = DBEngine

    @property
    def DBVersion(self):
        return self._DBVersion

    @DBVersion.setter
    def DBVersion(self, DBVersion):
        self._DBVersion = DBVersion

    @property
    def DBMajorVersion(self):
        return self._DBMajorVersion

    @DBMajorVersion.setter
    def DBMajorVersion(self, DBMajorVersion):
        self._DBMajorVersion = DBMajorVersion

    @property
    def DBKernelVersion(self):
        return self._DBKernelVersion

    @DBKernelVersion.setter
    def DBKernelVersion(self, DBKernelVersion):
        self._DBKernelVersion = DBKernelVersion

    @property
    def SupportedFeatureNames(self):
        return self._SupportedFeatureNames

    @SupportedFeatureNames.setter
    def SupportedFeatureNames(self, SupportedFeatureNames):
        self._SupportedFeatureNames = SupportedFeatureNames

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status

    @property
    def AvailableUpgradeTarget(self):
        return self._AvailableUpgradeTarget

    @AvailableUpgradeTarget.setter
    def AvailableUpgradeTarget(self, AvailableUpgradeTarget):
        self._AvailableUpgradeTarget = AvailableUpgradeTarget


    def _deserialize(self, params):
        self._DBEngine = params.get("DBEngine")
        self._DBVersion = params.get("DBVersion")
        self._DBMajorVersion = params.get("DBMajorVersion")
        self._DBKernelVersion = params.get("DBKernelVersion")
        self._SupportedFeatureNames = params.get("SupportedFeatureNames")
        self._Status = params.get("Status")
        self._AvailableUpgradeTarget = params.get("AvailableUpgradeTarget")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class Xlog(AbstractModel):
    """Database Xlog information

    """

    def __init__(self):
        r"""
        :param _Id: Unique backup file ID
        :type Id: int
        :param _StartTime: File generation start time
        :type StartTime: str
        :param _EndTime: File generation end time
        :type EndTime: str
        :param _InternalAddr: Download address on private network
        :type InternalAddr: str
        :param _ExternalAddr: Download address on public network
        :type ExternalAddr: str
        :param _Size: Backup file size
        :type Size: int
        """
        self._Id = None
        self._StartTime = None
        self._EndTime = None
        self._InternalAddr = None
        self._ExternalAddr = None
        self._Size = None

    @property
    def Id(self):
        return self._Id

    @Id.setter
    def Id(self, Id):
        self._Id = Id

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
    def InternalAddr(self):
        return self._InternalAddr

    @InternalAddr.setter
    def InternalAddr(self, InternalAddr):
        self._InternalAddr = InternalAddr

    @property
    def ExternalAddr(self):
        return self._ExternalAddr

    @ExternalAddr.setter
    def ExternalAddr(self, ExternalAddr):
        self._ExternalAddr = ExternalAddr

    @property
    def Size(self):
        return self._Size

    @Size.setter
    def Size(self, Size):
        self._Size = Size


    def _deserialize(self, params):
        self._Id = params.get("Id")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._InternalAddr = params.get("InternalAddr")
        self._ExternalAddr = params.get("ExternalAddr")
        self._Size = params.get("Size")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ZoneInfo(AbstractModel):
    """AZ information such as number and status

    """

    def __init__(self):
        r"""
        :param _Zone: AZ abbreviation
        :type Zone: str
        :param _ZoneName: AZ name
        :type ZoneName: str
        :param _ZoneId: AZ number
        :type ZoneId: int
        :param _ZoneState: Availability status. Valid values:
`UNAVAILABLE`.
`AVAILABLE`.
`SELLOUT`.
`SUPPORTMODIFYONLY` (supports configuration adjustment).
        :type ZoneState: str
        :param _ZoneSupportIpv6: Whether the AZ supports IPv6 address access
        :type ZoneSupportIpv6: int
        :param _StandbyZoneSet: AZs that can be used as standby when this AZ is primary
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type StandbyZoneSet: list of str
        """
        self._Zone = None
        self._ZoneName = None
        self._ZoneId = None
        self._ZoneState = None
        self._ZoneSupportIpv6 = None
        self._StandbyZoneSet = None

    @property
    def Zone(self):
        return self._Zone

    @Zone.setter
    def Zone(self, Zone):
        self._Zone = Zone

    @property
    def ZoneName(self):
        return self._ZoneName

    @ZoneName.setter
    def ZoneName(self, ZoneName):
        self._ZoneName = ZoneName

    @property
    def ZoneId(self):
        return self._ZoneId

    @ZoneId.setter
    def ZoneId(self, ZoneId):
        self._ZoneId = ZoneId

    @property
    def ZoneState(self):
        return self._ZoneState

    @ZoneState.setter
    def ZoneState(self, ZoneState):
        self._ZoneState = ZoneState

    @property
    def ZoneSupportIpv6(self):
        return self._ZoneSupportIpv6

    @ZoneSupportIpv6.setter
    def ZoneSupportIpv6(self, ZoneSupportIpv6):
        self._ZoneSupportIpv6 = ZoneSupportIpv6

    @property
    def StandbyZoneSet(self):
        return self._StandbyZoneSet

    @StandbyZoneSet.setter
    def StandbyZoneSet(self, StandbyZoneSet):
        self._StandbyZoneSet = StandbyZoneSet


    def _deserialize(self, params):
        self._Zone = params.get("Zone")
        self._ZoneName = params.get("ZoneName")
        self._ZoneId = params.get("ZoneId")
        self._ZoneState = params.get("ZoneState")
        self._ZoneSupportIpv6 = params.get("ZoneSupportIpv6")
        self._StandbyZoneSet = params.get("StandbyZoneSet")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        