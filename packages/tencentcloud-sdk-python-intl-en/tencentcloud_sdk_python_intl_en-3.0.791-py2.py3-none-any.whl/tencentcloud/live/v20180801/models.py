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


class AddDelayLiveStreamRequest(AbstractModel):
    """AddDelayLiveStream request structure.

    """

    def __init__(self):
        r"""
        :param _AppName: Push path, which is the same as the `AppName` in push and playback addresses and is `live` by default.
        :type AppName: str
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _DelayTime: Delay time in seconds, up to 600s.
        :type DelayTime: int
        :param _ExpireTime: Expiration time of the configured delayed playback in UTC format, such as 2018-11-29T19:00:00Z.
Notes:
1. The configuration will expire after 7 days by default and can last up to 7 days.
2. The Beijing time is in UTC+8. This value should be in the format as required by ISO 8601. For more information, please see [ISO Date and Time Format](https://intl.cloud.tencent.com/document/product/266/11732?from_cn_redirect=1#iso-.E6.97.A5.E6.9C.9F.E6.A0.BC.E5.BC.8F).
        :type ExpireTime: str
        """
        self._AppName = None
        self._DomainName = None
        self._StreamName = None
        self._DelayTime = None
        self._ExpireTime = None

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def DelayTime(self):
        return self._DelayTime

    @DelayTime.setter
    def DelayTime(self, DelayTime):
        self._DelayTime = DelayTime

    @property
    def ExpireTime(self):
        return self._ExpireTime

    @ExpireTime.setter
    def ExpireTime(self, ExpireTime):
        self._ExpireTime = ExpireTime


    def _deserialize(self, params):
        self._AppName = params.get("AppName")
        self._DomainName = params.get("DomainName")
        self._StreamName = params.get("StreamName")
        self._DelayTime = params.get("DelayTime")
        self._ExpireTime = params.get("ExpireTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class AddDelayLiveStreamResponse(AbstractModel):
    """AddDelayLiveStream response structure.

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


class AddLiveDomainRequest(AbstractModel):
    """AddLiveDomain request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Domain name.
        :type DomainName: str
        :param _DomainType: Domain name type.
0: push domain name.
1: playback domain name.
        :type DomainType: int
        :param _PlayType: Pull domain name type:
1: Mainland China.
2: global.
3: outside Mainland China.
Default value: 1.
        :type PlayType: int
        :param _IsDelayLive: Whether it is LCB:
0: LVB,
1: LCB.
Default value: 0.
        :type IsDelayLive: int
        :param _IsMiniProgramLive: Whether it is LVB on Mini Program.
0: LVB.
1: LVB on Mini Program.
Default value: 0.
        :type IsMiniProgramLive: int
        :param _VerifyOwnerType: The domain verification type.
Valid values (the value of this parameter must be the same as `VerifyType` of the `AuthenticateDomainOwner` API):
dnsCheck: Check immediately whether the verification DNS record has been added successfully. If so, record this verification result.
fileCheck: Check immediately whether the verification HTML file has been uploaded successfully. If so, record this verification result.
dbCheck: Check whether the domain has already been verified.
If you do not pass a value, `dbCheck` will be used.
        :type VerifyOwnerType: str
        """
        self._DomainName = None
        self._DomainType = None
        self._PlayType = None
        self._IsDelayLive = None
        self._IsMiniProgramLive = None
        self._VerifyOwnerType = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def DomainType(self):
        return self._DomainType

    @DomainType.setter
    def DomainType(self, DomainType):
        self._DomainType = DomainType

    @property
    def PlayType(self):
        return self._PlayType

    @PlayType.setter
    def PlayType(self, PlayType):
        self._PlayType = PlayType

    @property
    def IsDelayLive(self):
        return self._IsDelayLive

    @IsDelayLive.setter
    def IsDelayLive(self, IsDelayLive):
        self._IsDelayLive = IsDelayLive

    @property
    def IsMiniProgramLive(self):
        return self._IsMiniProgramLive

    @IsMiniProgramLive.setter
    def IsMiniProgramLive(self, IsMiniProgramLive):
        self._IsMiniProgramLive = IsMiniProgramLive

    @property
    def VerifyOwnerType(self):
        return self._VerifyOwnerType

    @VerifyOwnerType.setter
    def VerifyOwnerType(self, VerifyOwnerType):
        self._VerifyOwnerType = VerifyOwnerType


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._DomainType = params.get("DomainType")
        self._PlayType = params.get("PlayType")
        self._IsDelayLive = params.get("IsDelayLive")
        self._IsMiniProgramLive = params.get("IsMiniProgramLive")
        self._VerifyOwnerType = params.get("VerifyOwnerType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class AddLiveDomainResponse(AbstractModel):
    """AddLiveDomain response structure.

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


class AddLiveWatermarkRequest(AbstractModel):
    """AddLiveWatermark request structure.

    """

    def __init__(self):
        r"""
        :param _PictureUrl: Watermark image URL.
Unallowed characters in the URL:
 ;(){}$>`#"\'|
        :type PictureUrl: str
        :param _WatermarkName: Watermark name.
Up to 16 bytes.
        :type WatermarkName: str
        :param _XPosition: Display position: X-axis offset in %. Default value: 0.
        :type XPosition: int
        :param _YPosition: Display position: Y-axis offset in %. Default value: 0.
        :type YPosition: int
        :param _Width: Watermark width or its percentage of the live streaming video width. It is recommended to just specify either height or width as the other will be scaled proportionally to avoid distortions. The original width is used by default.
        :type Width: int
        :param _Height: Watermark height, which is set by entering a percentage of the live stream image’s original height. You are advised to set either the height or width as the other will be scaled proportionally to avoid distortions. Default value: original height.
        :type Height: int
        """
        self._PictureUrl = None
        self._WatermarkName = None
        self._XPosition = None
        self._YPosition = None
        self._Width = None
        self._Height = None

    @property
    def PictureUrl(self):
        return self._PictureUrl

    @PictureUrl.setter
    def PictureUrl(self, PictureUrl):
        self._PictureUrl = PictureUrl

    @property
    def WatermarkName(self):
        return self._WatermarkName

    @WatermarkName.setter
    def WatermarkName(self, WatermarkName):
        self._WatermarkName = WatermarkName

    @property
    def XPosition(self):
        return self._XPosition

    @XPosition.setter
    def XPosition(self, XPosition):
        self._XPosition = XPosition

    @property
    def YPosition(self):
        return self._YPosition

    @YPosition.setter
    def YPosition(self, YPosition):
        self._YPosition = YPosition

    @property
    def Width(self):
        return self._Width

    @Width.setter
    def Width(self, Width):
        self._Width = Width

    @property
    def Height(self):
        return self._Height

    @Height.setter
    def Height(self, Height):
        self._Height = Height


    def _deserialize(self, params):
        self._PictureUrl = params.get("PictureUrl")
        self._WatermarkName = params.get("WatermarkName")
        self._XPosition = params.get("XPosition")
        self._YPosition = params.get("YPosition")
        self._Width = params.get("Width")
        self._Height = params.get("Height")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class AddLiveWatermarkResponse(AbstractModel):
    """AddLiveWatermark response structure.

    """

    def __init__(self):
        r"""
        :param _WatermarkId: Watermark ID.
        :type WatermarkId: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._WatermarkId = None
        self._RequestId = None

    @property
    def WatermarkId(self):
        return self._WatermarkId

    @WatermarkId.setter
    def WatermarkId(self, WatermarkId):
        self._WatermarkId = WatermarkId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._WatermarkId = params.get("WatermarkId")
        self._RequestId = params.get("RequestId")


class AuthenticateDomainOwnerRequest(AbstractModel):
    """AuthenticateDomainOwner request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: The domain to verify.
        :type DomainName: str
        :param _VerifyType: The verification type. Valid values:
dnsCheck: Check immediately whether the verification DNS record has been added successfully. If so, record this verification result.
fileCheck: Check immediately whether the verification HTML file has been uploaded successfully. If so, record this verification result.
dbCheck: Check whether the domain has already been successfully verified.
        :type VerifyType: str
        """
        self._DomainName = None
        self._VerifyType = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def VerifyType(self):
        return self._VerifyType

    @VerifyType.setter
    def VerifyType(self, VerifyType):
        self._VerifyType = VerifyType


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._VerifyType = params.get("VerifyType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class AuthenticateDomainOwnerResponse(AbstractModel):
    """AuthenticateDomainOwner response structure.

    """

    def __init__(self):
        r"""
        :param _Content: The content verified.
If `VerifyType` is `dnsCheck`, this is the TXT record that should be added for verification.
If `VerifyType` is `fileCheck`, this is the file that should be uploaded for verification.
        :type Content: str
        :param _Status: The verification status.
If the value of this parameter is 0 or greater, the domain has been verified.
If the value of this parameter is smaller than 0, the domain has not been verified.
        :type Status: int
        :param _MainDomain: The primary domain of the domain verified.
Verification is not required if another domain under the same primary domain has been successfully verified.
        :type MainDomain: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Content = None
        self._Status = None
        self._MainDomain = None
        self._RequestId = None

    @property
    def Content(self):
        return self._Content

    @Content.setter
    def Content(self, Content):
        self._Content = Content

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status

    @property
    def MainDomain(self):
        return self._MainDomain

    @MainDomain.setter
    def MainDomain(self, MainDomain):
        self._MainDomain = MainDomain

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._Content = params.get("Content")
        self._Status = params.get("Status")
        self._MainDomain = params.get("MainDomain")
        self._RequestId = params.get("RequestId")


class BandwidthInfo(AbstractModel):
    """Bandwidth information

    """

    def __init__(self):
        r"""
        :param _Time: Format of return value:
yyyy-mm-dd HH:MM:SS
The time accuracy matches with the query granularity.
        :type Time: str
        :param _Bandwidth: Bandwidth.
        :type Bandwidth: float
        """
        self._Time = None
        self._Bandwidth = None

    @property
    def Time(self):
        return self._Time

    @Time.setter
    def Time(self, Time):
        self._Time = Time

    @property
    def Bandwidth(self):
        return self._Bandwidth

    @Bandwidth.setter
    def Bandwidth(self, Bandwidth):
        self._Bandwidth = Bandwidth


    def _deserialize(self, params):
        self._Time = params.get("Time")
        self._Bandwidth = params.get("Bandwidth")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class BatchDomainOperateErrors(AbstractModel):
    """Error information for domains that a batch domain operation API fails to operate.

    """

    def __init__(self):
        r"""
        :param _DomainName: The domain that the API failed to operate.
        :type DomainName: str
        :param _Code: The API 3.0 error code.
        :type Code: str
        :param _Message: The API 3.0 error message.
        :type Message: str
        """
        self._DomainName = None
        self._Code = None
        self._Message = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def Code(self):
        return self._Code

    @Code.setter
    def Code(self, Code):
        self._Code = Code

    @property
    def Message(self):
        return self._Message

    @Message.setter
    def Message(self, Message):
        self._Message = Message


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._Code = params.get("Code")
        self._Message = params.get("Message")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class BillDataInfo(AbstractModel):
    """Bandwidth and traffic information.

    """

    def __init__(self):
        r"""
        :param _Time: Time point in the format of `yyyy-mm-dd HH:MM:SS`.
        :type Time: str
        :param _Bandwidth: Bandwidth in Mbps.
        :type Bandwidth: float
        :param _Flux: Traffic in MB.
        :type Flux: float
        :param _PeakTime: Time point of peak value in the format of `yyyy-mm-dd HH:MM:SS`. As raw data is at a 5-minute granularity, if data at a 1-hour or 1-day granularity is queried, the time point of peak bandwidth value at the corresponding granularity will be returned.
        :type PeakTime: str
        """
        self._Time = None
        self._Bandwidth = None
        self._Flux = None
        self._PeakTime = None

    @property
    def Time(self):
        return self._Time

    @Time.setter
    def Time(self, Time):
        self._Time = Time

    @property
    def Bandwidth(self):
        return self._Bandwidth

    @Bandwidth.setter
    def Bandwidth(self, Bandwidth):
        self._Bandwidth = Bandwidth

    @property
    def Flux(self):
        return self._Flux

    @Flux.setter
    def Flux(self, Flux):
        self._Flux = Flux

    @property
    def PeakTime(self):
        return self._PeakTime

    @PeakTime.setter
    def PeakTime(self, PeakTime):
        self._PeakTime = PeakTime


    def _deserialize(self, params):
        self._Time = params.get("Time")
        self._Bandwidth = params.get("Bandwidth")
        self._Flux = params.get("Flux")
        self._PeakTime = params.get("PeakTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CallBackRuleInfo(AbstractModel):
    """Rule information

    """

    def __init__(self):
        r"""
        :param _CreateTime: The rule creation time.
Note: Beijing time (UTC+8) is used.
        :type CreateTime: str
        :param _UpdateTime: The rule update time.
Note: Beijing time (UTC+8) is used.
        :type UpdateTime: str
        :param _TemplateId: Template ID.
        :type TemplateId: int
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _AppName: Push path.
        :type AppName: str
        """
        self._CreateTime = None
        self._UpdateTime = None
        self._TemplateId = None
        self._DomainName = None
        self._AppName = None

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
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName


    def _deserialize(self, params):
        self._CreateTime = params.get("CreateTime")
        self._UpdateTime = params.get("UpdateTime")
        self._TemplateId = params.get("TemplateId")
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CallBackTemplateInfo(AbstractModel):
    """Callback template information.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
        :type TemplateId: int
        :param _TemplateName: Template name.
        :type TemplateName: str
        :param _Description: Description.
        :type Description: str
        :param _StreamBeginNotifyUrl: Stream starting callback URL.
        :type StreamBeginNotifyUrl: str
        :param _StreamMixNotifyUrl: Stream mixing callback URL (disused)
        :type StreamMixNotifyUrl: str
        :param _StreamEndNotifyUrl: Interruption callback URL.
        :type StreamEndNotifyUrl: str
        :param _RecordNotifyUrl: Recording callback URL.
        :type RecordNotifyUrl: str
        :param _SnapshotNotifyUrl: Screencapturing callback URL.
        :type SnapshotNotifyUrl: str
        :param _PornCensorshipNotifyUrl: Porn detection callback URL.
        :type PornCensorshipNotifyUrl: str
        :param _CallbackKey: Callback authentication key.
        :type CallbackKey: str
        :param _PushExceptionNotifyUrl: The push error callback URL.
Note: This field may return null, indicating that no valid values can be obtained.
        :type PushExceptionNotifyUrl: str
        :param _AudioAuditNotifyUrl: The audio/video moderation callback URL.
Note: This field may return null, indicating that no valid values can be obtained.
        :type AudioAuditNotifyUrl: str
        """
        self._TemplateId = None
        self._TemplateName = None
        self._Description = None
        self._StreamBeginNotifyUrl = None
        self._StreamMixNotifyUrl = None
        self._StreamEndNotifyUrl = None
        self._RecordNotifyUrl = None
        self._SnapshotNotifyUrl = None
        self._PornCensorshipNotifyUrl = None
        self._CallbackKey = None
        self._PushExceptionNotifyUrl = None
        self._AudioAuditNotifyUrl = None

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
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def StreamBeginNotifyUrl(self):
        return self._StreamBeginNotifyUrl

    @StreamBeginNotifyUrl.setter
    def StreamBeginNotifyUrl(self, StreamBeginNotifyUrl):
        self._StreamBeginNotifyUrl = StreamBeginNotifyUrl

    @property
    def StreamMixNotifyUrl(self):
        return self._StreamMixNotifyUrl

    @StreamMixNotifyUrl.setter
    def StreamMixNotifyUrl(self, StreamMixNotifyUrl):
        self._StreamMixNotifyUrl = StreamMixNotifyUrl

    @property
    def StreamEndNotifyUrl(self):
        return self._StreamEndNotifyUrl

    @StreamEndNotifyUrl.setter
    def StreamEndNotifyUrl(self, StreamEndNotifyUrl):
        self._StreamEndNotifyUrl = StreamEndNotifyUrl

    @property
    def RecordNotifyUrl(self):
        return self._RecordNotifyUrl

    @RecordNotifyUrl.setter
    def RecordNotifyUrl(self, RecordNotifyUrl):
        self._RecordNotifyUrl = RecordNotifyUrl

    @property
    def SnapshotNotifyUrl(self):
        return self._SnapshotNotifyUrl

    @SnapshotNotifyUrl.setter
    def SnapshotNotifyUrl(self, SnapshotNotifyUrl):
        self._SnapshotNotifyUrl = SnapshotNotifyUrl

    @property
    def PornCensorshipNotifyUrl(self):
        return self._PornCensorshipNotifyUrl

    @PornCensorshipNotifyUrl.setter
    def PornCensorshipNotifyUrl(self, PornCensorshipNotifyUrl):
        self._PornCensorshipNotifyUrl = PornCensorshipNotifyUrl

    @property
    def CallbackKey(self):
        return self._CallbackKey

    @CallbackKey.setter
    def CallbackKey(self, CallbackKey):
        self._CallbackKey = CallbackKey

    @property
    def PushExceptionNotifyUrl(self):
        return self._PushExceptionNotifyUrl

    @PushExceptionNotifyUrl.setter
    def PushExceptionNotifyUrl(self, PushExceptionNotifyUrl):
        self._PushExceptionNotifyUrl = PushExceptionNotifyUrl

    @property
    def AudioAuditNotifyUrl(self):
        return self._AudioAuditNotifyUrl

    @AudioAuditNotifyUrl.setter
    def AudioAuditNotifyUrl(self, AudioAuditNotifyUrl):
        self._AudioAuditNotifyUrl = AudioAuditNotifyUrl


    def _deserialize(self, params):
        self._TemplateId = params.get("TemplateId")
        self._TemplateName = params.get("TemplateName")
        self._Description = params.get("Description")
        self._StreamBeginNotifyUrl = params.get("StreamBeginNotifyUrl")
        self._StreamMixNotifyUrl = params.get("StreamMixNotifyUrl")
        self._StreamEndNotifyUrl = params.get("StreamEndNotifyUrl")
        self._RecordNotifyUrl = params.get("RecordNotifyUrl")
        self._SnapshotNotifyUrl = params.get("SnapshotNotifyUrl")
        self._PornCensorshipNotifyUrl = params.get("PornCensorshipNotifyUrl")
        self._CallbackKey = params.get("CallbackKey")
        self._PushExceptionNotifyUrl = params.get("PushExceptionNotifyUrl")
        self._AudioAuditNotifyUrl = params.get("AudioAuditNotifyUrl")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CancelCommonMixStreamRequest(AbstractModel):
    """CancelCommonMixStream request structure.

    """

    def __init__(self):
        r"""
        :param _MixStreamSessionId: ID of stream mix session (from applying for stream mix to canceling stream mix).
This value is the same as the `MixStreamSessionId` in `CreateCommonMixStream`.
        :type MixStreamSessionId: str
        """
        self._MixStreamSessionId = None

    @property
    def MixStreamSessionId(self):
        return self._MixStreamSessionId

    @MixStreamSessionId.setter
    def MixStreamSessionId(self, MixStreamSessionId):
        self._MixStreamSessionId = MixStreamSessionId


    def _deserialize(self, params):
        self._MixStreamSessionId = params.get("MixStreamSessionId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CancelCommonMixStreamResponse(AbstractModel):
    """CancelCommonMixStream response structure.

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


class CdnPlayStatData(AbstractModel):
    """Downstream playback statistical metrics

    """

    def __init__(self):
        r"""
        :param _Time: Time point in the format of `yyyy-mm-dd HH:MM:SS`.
        :type Time: str
        :param _Bandwidth: Bandwidth in Mbps.
        :type Bandwidth: float
        :param _Flux: Traffic in MB.
        :type Flux: float
        :param _Request: Number of new requests.
        :type Request: int
        :param _Online: Number of concurrent connections.
        :type Online: int
        """
        self._Time = None
        self._Bandwidth = None
        self._Flux = None
        self._Request = None
        self._Online = None

    @property
    def Time(self):
        return self._Time

    @Time.setter
    def Time(self, Time):
        self._Time = Time

    @property
    def Bandwidth(self):
        return self._Bandwidth

    @Bandwidth.setter
    def Bandwidth(self, Bandwidth):
        self._Bandwidth = Bandwidth

    @property
    def Flux(self):
        return self._Flux

    @Flux.setter
    def Flux(self, Flux):
        self._Flux = Flux

    @property
    def Request(self):
        return self._Request

    @Request.setter
    def Request(self, Request):
        self._Request = Request

    @property
    def Online(self):
        return self._Online

    @Online.setter
    def Online(self, Online):
        self._Online = Online


    def _deserialize(self, params):
        self._Time = params.get("Time")
        self._Bandwidth = params.get("Bandwidth")
        self._Flux = params.get("Flux")
        self._Request = params.get("Request")
        self._Online = params.get("Online")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CertInfo(AbstractModel):
    """Certificate information.

    """

    def __init__(self):
        r"""
        :param _CertId: Certificate ID.
        :type CertId: int
        :param _CertName: Certificate name.
        :type CertName: str
        :param _Description: Description.
        :type Description: str
        :param _CreateTime: The creation time in UTC format.
Note: Beijing time (UTC+8) is used.
        :type CreateTime: str
        :param _HttpsCrt: Certificate content.
        :type HttpsCrt: str
        :param _CertType: Certificate type.
0: user-added certificate
1: Tencent Cloud-hosted certificate
        :type CertType: int
        :param _CertExpireTime: The certificate expiration time in UTC format.
Note: Beijing time (UTC+8) is used.
        :type CertExpireTime: str
        :param _DomainList: List of domain names that use this certificate.
        :type DomainList: list of str
        """
        self._CertId = None
        self._CertName = None
        self._Description = None
        self._CreateTime = None
        self._HttpsCrt = None
        self._CertType = None
        self._CertExpireTime = None
        self._DomainList = None

    @property
    def CertId(self):
        return self._CertId

    @CertId.setter
    def CertId(self, CertId):
        self._CertId = CertId

    @property
    def CertName(self):
        return self._CertName

    @CertName.setter
    def CertName(self, CertName):
        self._CertName = CertName

    @property
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def CreateTime(self):
        return self._CreateTime

    @CreateTime.setter
    def CreateTime(self, CreateTime):
        self._CreateTime = CreateTime

    @property
    def HttpsCrt(self):
        return self._HttpsCrt

    @HttpsCrt.setter
    def HttpsCrt(self, HttpsCrt):
        self._HttpsCrt = HttpsCrt

    @property
    def CertType(self):
        return self._CertType

    @CertType.setter
    def CertType(self, CertType):
        self._CertType = CertType

    @property
    def CertExpireTime(self):
        return self._CertExpireTime

    @CertExpireTime.setter
    def CertExpireTime(self, CertExpireTime):
        self._CertExpireTime = CertExpireTime

    @property
    def DomainList(self):
        return self._DomainList

    @DomainList.setter
    def DomainList(self, DomainList):
        self._DomainList = DomainList


    def _deserialize(self, params):
        self._CertId = params.get("CertId")
        self._CertName = params.get("CertName")
        self._Description = params.get("Description")
        self._CreateTime = params.get("CreateTime")
        self._HttpsCrt = params.get("HttpsCrt")
        self._CertType = params.get("CertType")
        self._CertExpireTime = params.get("CertExpireTime")
        self._DomainList = params.get("DomainList")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ClientIpPlaySumInfo(AbstractModel):
    """Aggregated playback information of client IP.

    """

    def __init__(self):
        r"""
        :param _ClientIp: Client IP in dotted-decimal notation.
        :type ClientIp: str
        :param _Province: District where the client is located.
        :type Province: str
        :param _TotalFlux: Total traffic.
        :type TotalFlux: float
        :param _TotalRequest: Total number of requests.
        :type TotalRequest: int
        :param _TotalFailedRequest: Total number of failed requests.
        :type TotalFailedRequest: int
        :param _CountryArea: Country/region where the client is located.
        :type CountryArea: str
        """
        self._ClientIp = None
        self._Province = None
        self._TotalFlux = None
        self._TotalRequest = None
        self._TotalFailedRequest = None
        self._CountryArea = None

    @property
    def ClientIp(self):
        return self._ClientIp

    @ClientIp.setter
    def ClientIp(self, ClientIp):
        self._ClientIp = ClientIp

    @property
    def Province(self):
        return self._Province

    @Province.setter
    def Province(self, Province):
        self._Province = Province

    @property
    def TotalFlux(self):
        return self._TotalFlux

    @TotalFlux.setter
    def TotalFlux(self, TotalFlux):
        self._TotalFlux = TotalFlux

    @property
    def TotalRequest(self):
        return self._TotalRequest

    @TotalRequest.setter
    def TotalRequest(self, TotalRequest):
        self._TotalRequest = TotalRequest

    @property
    def TotalFailedRequest(self):
        return self._TotalFailedRequest

    @TotalFailedRequest.setter
    def TotalFailedRequest(self, TotalFailedRequest):
        self._TotalFailedRequest = TotalFailedRequest

    @property
    def CountryArea(self):
        return self._CountryArea

    @CountryArea.setter
    def CountryArea(self, CountryArea):
        self._CountryArea = CountryArea


    def _deserialize(self, params):
        self._ClientIp = params.get("ClientIp")
        self._Province = params.get("Province")
        self._TotalFlux = params.get("TotalFlux")
        self._TotalRequest = params.get("TotalRequest")
        self._TotalFailedRequest = params.get("TotalFailedRequest")
        self._CountryArea = params.get("CountryArea")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CommonMixControlParams(AbstractModel):
    """General stream mix control parameter

    """

    def __init__(self):
        r"""
        :param _UseMixCropCenter: Value range: [0,1]. 
If 1 is entered, when the layer resolution in the parameter is different from the actual video resolution, the video will be automatically cropped according to the resolution set by the layer.
        :type UseMixCropCenter: int
        :param _AllowCopy: Value range: [0,1].
If this parameter is set to 1, when both `InputStreamList` and `OutputParams.OutputStreamType` are set to 1, you can copy a stream instead of canceling it.
        :type AllowCopy: int
        :param _PassInputSei: Valid values: 0, 1
If you set this parameter to 1, SEI (Supplemental Enhanced Information) of the input streams will be passed through.
        :type PassInputSei: int
        """
        self._UseMixCropCenter = None
        self._AllowCopy = None
        self._PassInputSei = None

    @property
    def UseMixCropCenter(self):
        return self._UseMixCropCenter

    @UseMixCropCenter.setter
    def UseMixCropCenter(self, UseMixCropCenter):
        self._UseMixCropCenter = UseMixCropCenter

    @property
    def AllowCopy(self):
        return self._AllowCopy

    @AllowCopy.setter
    def AllowCopy(self, AllowCopy):
        self._AllowCopy = AllowCopy

    @property
    def PassInputSei(self):
        return self._PassInputSei

    @PassInputSei.setter
    def PassInputSei(self, PassInputSei):
        self._PassInputSei = PassInputSei


    def _deserialize(self, params):
        self._UseMixCropCenter = params.get("UseMixCropCenter")
        self._AllowCopy = params.get("AllowCopy")
        self._PassInputSei = params.get("PassInputSei")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CommonMixCropParams(AbstractModel):
    """General stream mix input crop parameter.

    """

    def __init__(self):
        r"""
        :param _CropWidth: Crop width. Value range: [0,2000].
        :type CropWidth: float
        :param _CropHeight: Crop height. Value range: [0,2000].
        :type CropHeight: float
        :param _CropStartLocationX: Starting crop X coordinate. Value range: [0,2000].
        :type CropStartLocationX: float
        :param _CropStartLocationY: Starting crop Y coordinate. Value range: [0,2000].
        :type CropStartLocationY: float
        """
        self._CropWidth = None
        self._CropHeight = None
        self._CropStartLocationX = None
        self._CropStartLocationY = None

    @property
    def CropWidth(self):
        return self._CropWidth

    @CropWidth.setter
    def CropWidth(self, CropWidth):
        self._CropWidth = CropWidth

    @property
    def CropHeight(self):
        return self._CropHeight

    @CropHeight.setter
    def CropHeight(self, CropHeight):
        self._CropHeight = CropHeight

    @property
    def CropStartLocationX(self):
        return self._CropStartLocationX

    @CropStartLocationX.setter
    def CropStartLocationX(self, CropStartLocationX):
        self._CropStartLocationX = CropStartLocationX

    @property
    def CropStartLocationY(self):
        return self._CropStartLocationY

    @CropStartLocationY.setter
    def CropStartLocationY(self, CropStartLocationY):
        self._CropStartLocationY = CropStartLocationY


    def _deserialize(self, params):
        self._CropWidth = params.get("CropWidth")
        self._CropHeight = params.get("CropHeight")
        self._CropStartLocationX = params.get("CropStartLocationX")
        self._CropStartLocationY = params.get("CropStartLocationY")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CommonMixInputParam(AbstractModel):
    """General stream mix input parameter.

    """

    def __init__(self):
        r"""
        :param _InputStreamName: Input stream name, which can contain up to 80 bytes of letters, digits, and underscores.
The value should be the name of an input stream for stream mix when `LayoutParams.InputType` is set to `0` (audio and video), `4` (pure audio), or `5` (pure video).
The value can be a random name for identification, such as `Canvas1` or `Picture1`, when `LayoutParams.InputType` is set to `2` (image) or `3` (canvas).
        :type InputStreamName: str
        :param _LayoutParams: Input stream layout parameter.
        :type LayoutParams: :class:`tencentcloud.live.v20180801.models.CommonMixLayoutParams`
        :param _CropParams: Input stream crop parameter.
        :type CropParams: :class:`tencentcloud.live.v20180801.models.CommonMixCropParams`
        """
        self._InputStreamName = None
        self._LayoutParams = None
        self._CropParams = None

    @property
    def InputStreamName(self):
        return self._InputStreamName

    @InputStreamName.setter
    def InputStreamName(self, InputStreamName):
        self._InputStreamName = InputStreamName

    @property
    def LayoutParams(self):
        return self._LayoutParams

    @LayoutParams.setter
    def LayoutParams(self, LayoutParams):
        self._LayoutParams = LayoutParams

    @property
    def CropParams(self):
        return self._CropParams

    @CropParams.setter
    def CropParams(self, CropParams):
        self._CropParams = CropParams


    def _deserialize(self, params):
        self._InputStreamName = params.get("InputStreamName")
        if params.get("LayoutParams") is not None:
            self._LayoutParams = CommonMixLayoutParams()
            self._LayoutParams._deserialize(params.get("LayoutParams"))
        if params.get("CropParams") is not None:
            self._CropParams = CommonMixCropParams()
            self._CropParams._deserialize(params.get("CropParams"))
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CommonMixLayoutParams(AbstractModel):
    """General stream mix layout parameter.

    """

    def __init__(self):
        r"""
        :param _ImageLayer: Input layer. Value range: [1,16]
(1) For the background stream, i.e., the room owner’s image or the canvas, set this parameter to `1`.
(2) This parameter is required for audio-only stream mixing as well.
Note that two inputs cannot have the same `ImageLayer` value.
        :type ImageLayer: int
        :param _InputType: Input type. Value range: [0,5].
If this parameter is left empty, 0 will be used by default.
0: the input stream is audio/video.
2: the input stream is image.
3: the input stream is canvas. 
4: the input stream is audio.
5: the input stream is pure video.
        :type InputType: int
        :param _ImageHeight: Output height of input video image. Value range:
Pixel: [0,2000]
Percentage: [0.01,0.99]
If this parameter is left empty, the input stream height will be used by default.
If percentage is used, the expected output is (percentage * background height).
        :type ImageHeight: float
        :param _ImageWidth: Output width of input video image. Value range:
Pixel: [0,2000]
Percentage: [0.01,0.99]
If this parameter is left empty, the input stream width will be used by default.
If percentage is used, the expected output is (percentage * background width).
        :type ImageWidth: float
        :param _LocationX: X-axis offset of input in output video image. Value range:
Pixel: [0,2000]
Percentage: [0.01,0.99]
If this parameter is left empty, 0 will be used by default.
Horizontal offset from the top-left corner of main host background video image. 
If percentage is used, the expected output is (percentage * background width).
        :type LocationX: float
        :param _LocationY: Y-axis offset of input in output video image. Value range:
Pixel: [0,2000]
Percentage: [0.01,0.99]
If this parameter is left empty, 0 will be used by default.
Vertical offset from the top-left corner of main host background video image. 
If percentage is used, the expected output is (percentage * background width)
        :type LocationY: float
        :param _Color: When `InputType` is 3 (canvas), this value indicates the canvas color.
Commonly used colors include:
Red: 0xcc0033.
Yellow: 0xcc9900.
Green: 0xcccc33.
Blue: 0x99CCFF.
Black: 0x000000.
White: 0xFFFFFF.
Gray: 0x999999
        :type Color: str
        :param _WatermarkId: When `InputType` is 2 (image), this value is the watermark ID.
        :type WatermarkId: int
        """
        self._ImageLayer = None
        self._InputType = None
        self._ImageHeight = None
        self._ImageWidth = None
        self._LocationX = None
        self._LocationY = None
        self._Color = None
        self._WatermarkId = None

    @property
    def ImageLayer(self):
        return self._ImageLayer

    @ImageLayer.setter
    def ImageLayer(self, ImageLayer):
        self._ImageLayer = ImageLayer

    @property
    def InputType(self):
        return self._InputType

    @InputType.setter
    def InputType(self, InputType):
        self._InputType = InputType

    @property
    def ImageHeight(self):
        return self._ImageHeight

    @ImageHeight.setter
    def ImageHeight(self, ImageHeight):
        self._ImageHeight = ImageHeight

    @property
    def ImageWidth(self):
        return self._ImageWidth

    @ImageWidth.setter
    def ImageWidth(self, ImageWidth):
        self._ImageWidth = ImageWidth

    @property
    def LocationX(self):
        return self._LocationX

    @LocationX.setter
    def LocationX(self, LocationX):
        self._LocationX = LocationX

    @property
    def LocationY(self):
        return self._LocationY

    @LocationY.setter
    def LocationY(self, LocationY):
        self._LocationY = LocationY

    @property
    def Color(self):
        return self._Color

    @Color.setter
    def Color(self, Color):
        self._Color = Color

    @property
    def WatermarkId(self):
        return self._WatermarkId

    @WatermarkId.setter
    def WatermarkId(self, WatermarkId):
        self._WatermarkId = WatermarkId


    def _deserialize(self, params):
        self._ImageLayer = params.get("ImageLayer")
        self._InputType = params.get("InputType")
        self._ImageHeight = params.get("ImageHeight")
        self._ImageWidth = params.get("ImageWidth")
        self._LocationX = params.get("LocationX")
        self._LocationY = params.get("LocationY")
        self._Color = params.get("Color")
        self._WatermarkId = params.get("WatermarkId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CommonMixOutputParams(AbstractModel):
    """General stream mix output parameter.

    """

    def __init__(self):
        r"""
        :param _OutputStreamName: Output stream name.
        :type OutputStreamName: str
        :param _OutputStreamType: Output stream type. Valid values: [0,1].
If this parameter is left empty, 0 will be used by default.
If the output stream is a stream in the input stream list, enter 0.
If you want the stream mix result to be a new stream, enter 1.
If this value is 1, `output_stream_id` cannot appear in `input_stram_list`, and there cannot be a stream with the same ID on the LVB backend.
        :type OutputStreamType: int
        :param _OutputStreamBitRate: The output bitrate. Value range: 1-10000.
If you do not specify this, the system will select a bitrate automatically.
        :type OutputStreamBitRate: int
        :param _OutputStreamGop: Output stream GOP size. Value range: [1,10].
If this parameter is left empty, the system will automatically determine.
        :type OutputStreamGop: int
        :param _OutputStreamFrameRate: Output stream frame rate. Value range: [1,60].
If this parameter is left empty, the system will automatically determine.
        :type OutputStreamFrameRate: int
        :param _OutputAudioBitRate: Output stream audio bitrate. Value range: [1,500]
If this parameter is left empty, the system will automatically determine.
        :type OutputAudioBitRate: int
        :param _OutputAudioSampleRate: Output stream audio sample rate. Valid values: [96000, 88200, 64000, 48000, 44100, 32000,24000, 22050, 16000, 12000, 11025, 8000].
If this parameter is left empty, the system will automatically determine.
        :type OutputAudioSampleRate: int
        :param _OutputAudioChannels: Output stream audio sound channel. Valid values: [1,2].
If this parameter is left empty, the system will automatically determine.
        :type OutputAudioChannels: int
        :param _MixSei: SEI information in output stream. If there are no special needs, leave it empty.
        :type MixSei: str
        """
        self._OutputStreamName = None
        self._OutputStreamType = None
        self._OutputStreamBitRate = None
        self._OutputStreamGop = None
        self._OutputStreamFrameRate = None
        self._OutputAudioBitRate = None
        self._OutputAudioSampleRate = None
        self._OutputAudioChannels = None
        self._MixSei = None

    @property
    def OutputStreamName(self):
        return self._OutputStreamName

    @OutputStreamName.setter
    def OutputStreamName(self, OutputStreamName):
        self._OutputStreamName = OutputStreamName

    @property
    def OutputStreamType(self):
        return self._OutputStreamType

    @OutputStreamType.setter
    def OutputStreamType(self, OutputStreamType):
        self._OutputStreamType = OutputStreamType

    @property
    def OutputStreamBitRate(self):
        return self._OutputStreamBitRate

    @OutputStreamBitRate.setter
    def OutputStreamBitRate(self, OutputStreamBitRate):
        self._OutputStreamBitRate = OutputStreamBitRate

    @property
    def OutputStreamGop(self):
        return self._OutputStreamGop

    @OutputStreamGop.setter
    def OutputStreamGop(self, OutputStreamGop):
        self._OutputStreamGop = OutputStreamGop

    @property
    def OutputStreamFrameRate(self):
        return self._OutputStreamFrameRate

    @OutputStreamFrameRate.setter
    def OutputStreamFrameRate(self, OutputStreamFrameRate):
        self._OutputStreamFrameRate = OutputStreamFrameRate

    @property
    def OutputAudioBitRate(self):
        return self._OutputAudioBitRate

    @OutputAudioBitRate.setter
    def OutputAudioBitRate(self, OutputAudioBitRate):
        self._OutputAudioBitRate = OutputAudioBitRate

    @property
    def OutputAudioSampleRate(self):
        return self._OutputAudioSampleRate

    @OutputAudioSampleRate.setter
    def OutputAudioSampleRate(self, OutputAudioSampleRate):
        self._OutputAudioSampleRate = OutputAudioSampleRate

    @property
    def OutputAudioChannels(self):
        return self._OutputAudioChannels

    @OutputAudioChannels.setter
    def OutputAudioChannels(self, OutputAudioChannels):
        self._OutputAudioChannels = OutputAudioChannels

    @property
    def MixSei(self):
        return self._MixSei

    @MixSei.setter
    def MixSei(self, MixSei):
        self._MixSei = MixSei


    def _deserialize(self, params):
        self._OutputStreamName = params.get("OutputStreamName")
        self._OutputStreamType = params.get("OutputStreamType")
        self._OutputStreamBitRate = params.get("OutputStreamBitRate")
        self._OutputStreamGop = params.get("OutputStreamGop")
        self._OutputStreamFrameRate = params.get("OutputStreamFrameRate")
        self._OutputAudioBitRate = params.get("OutputAudioBitRate")
        self._OutputAudioSampleRate = params.get("OutputAudioSampleRate")
        self._OutputAudioChannels = params.get("OutputAudioChannels")
        self._MixSei = params.get("MixSei")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ConcurrentRecordStreamNum(AbstractModel):
    """Number of concurrent recording channels

    """

    def __init__(self):
        r"""
        :param _Time: Time point.
        :type Time: str
        :param _Num: Number of channels.
        :type Num: int
        """
        self._Time = None
        self._Num = None

    @property
    def Time(self):
        return self._Time

    @Time.setter
    def Time(self, Time):
        self._Time = Time

    @property
    def Num(self):
        return self._Num

    @Num.setter
    def Num(self, Num):
        self._Num = Num


    def _deserialize(self, params):
        self._Time = params.get("Time")
        self._Num = params.get("Num")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateCommonMixStreamRequest(AbstractModel):
    """CreateCommonMixStream request structure.

    """

    def __init__(self):
        r"""
        :param _MixStreamSessionId: ID of a stream mix session (from applying for the stream mix to cancelling it). This parameter can contain up to 80 bytes of letters, digits, and underscores.
        :type MixStreamSessionId: str
        :param _InputStreamList: Input stream list for stream mix.
        :type InputStreamList: list of CommonMixInputParam
        :param _OutputParams: Output stream parameter for stream mix.
        :type OutputParams: :class:`tencentcloud.live.v20180801.models.CommonMixOutputParams`
        :param _MixStreamTemplateId: Input template ID. If this parameter is set, the output will be generated according to the default template layout, and there is no need to enter the custom position parameters.
If this parameter is left empty, 0 will be used by default.
For two input sources, 10, 20, 30, 40, and 50 are supported.
For three input sources, 310, 390, and 391 are supported.
For four input sources, 410 is supported.
For five input sources, 510 and 590 are supported.
For six input sources, 610 is supported.
        :type MixStreamTemplateId: int
        :param _ControlParams: Special control parameter for stream mix. If there are no special needs, leave it empty.
        :type ControlParams: :class:`tencentcloud.live.v20180801.models.CommonMixControlParams`
        """
        self._MixStreamSessionId = None
        self._InputStreamList = None
        self._OutputParams = None
        self._MixStreamTemplateId = None
        self._ControlParams = None

    @property
    def MixStreamSessionId(self):
        return self._MixStreamSessionId

    @MixStreamSessionId.setter
    def MixStreamSessionId(self, MixStreamSessionId):
        self._MixStreamSessionId = MixStreamSessionId

    @property
    def InputStreamList(self):
        return self._InputStreamList

    @InputStreamList.setter
    def InputStreamList(self, InputStreamList):
        self._InputStreamList = InputStreamList

    @property
    def OutputParams(self):
        return self._OutputParams

    @OutputParams.setter
    def OutputParams(self, OutputParams):
        self._OutputParams = OutputParams

    @property
    def MixStreamTemplateId(self):
        return self._MixStreamTemplateId

    @MixStreamTemplateId.setter
    def MixStreamTemplateId(self, MixStreamTemplateId):
        self._MixStreamTemplateId = MixStreamTemplateId

    @property
    def ControlParams(self):
        return self._ControlParams

    @ControlParams.setter
    def ControlParams(self, ControlParams):
        self._ControlParams = ControlParams


    def _deserialize(self, params):
        self._MixStreamSessionId = params.get("MixStreamSessionId")
        if params.get("InputStreamList") is not None:
            self._InputStreamList = []
            for item in params.get("InputStreamList"):
                obj = CommonMixInputParam()
                obj._deserialize(item)
                self._InputStreamList.append(obj)
        if params.get("OutputParams") is not None:
            self._OutputParams = CommonMixOutputParams()
            self._OutputParams._deserialize(params.get("OutputParams"))
        self._MixStreamTemplateId = params.get("MixStreamTemplateId")
        if params.get("ControlParams") is not None:
            self._ControlParams = CommonMixControlParams()
            self._ControlParams._deserialize(params.get("ControlParams"))
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateCommonMixStreamResponse(AbstractModel):
    """CreateCommonMixStream response structure.

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


class CreateLiveCallbackRuleRequest(AbstractModel):
    """CreateLiveCallbackRule request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _AppName: Push path, which is the same as the `AppName` in push and playback addresses and is `live` by default.
        :type AppName: str
        :param _TemplateId: Template ID.
        :type TemplateId: int
        """
        self._DomainName = None
        self._AppName = None
        self._TemplateId = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._TemplateId = params.get("TemplateId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateLiveCallbackRuleResponse(AbstractModel):
    """CreateLiveCallbackRule response structure.

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


class CreateLiveCallbackTemplateRequest(AbstractModel):
    """CreateLiveCallbackTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateName: Template name.
Maximum length: 255 bytes.
Only letters, digits, underscores, and hyphens can be contained.
        :type TemplateName: str
        :param _Description: Description.
Maximum length: 1,024 bytes.
Only letters, digits, underscores, and hyphens can be contained.
        :type Description: str
        :param _StreamBeginNotifyUrl: Stream starting callback URL,
Protocol document: [Event Message Notification](https://intl.cloud.tencent.com/document/product/267/32744?from_cn_redirect=1).
        :type StreamBeginNotifyUrl: str
        :param _StreamEndNotifyUrl: Interruption callback URL,
Protocol document: [Event Message Notification](https://intl.cloud.tencent.com/document/product/267/32744?from_cn_redirect=1).
        :type StreamEndNotifyUrl: str
        :param _RecordNotifyUrl: Recording callback URL,
Protocol document: [Event Message Notification](https://intl.cloud.tencent.com/document/product/267/32744?from_cn_redirect=1).
        :type RecordNotifyUrl: str
        :param _SnapshotNotifyUrl: Screencapturing callback URL,
Protocol document: [Event Message Notification](https://intl.cloud.tencent.com/document/product/267/32744?from_cn_redirect=1).
        :type SnapshotNotifyUrl: str
        :param _PornCensorshipNotifyUrl: Porn detection callback URL,
Protocol document: [Event Message Notification](https://intl.cloud.tencent.com/document/product/267/32741?from_cn_redirect=1).
        :type PornCensorshipNotifyUrl: str
        :param _CallbackKey: Callback key. The callback URL is public. For the callback signature, please see the event message notification document.
[Event Message Notification](https://intl.cloud.tencent.com/document/product/267/32744?from_cn_redirect=1).
        :type CallbackKey: str
        :param _StreamMixNotifyUrl: Disused
        :type StreamMixNotifyUrl: str
        :param _PushExceptionNotifyUrl: The push error callback URL.
        :type PushExceptionNotifyUrl: str
        """
        self._TemplateName = None
        self._Description = None
        self._StreamBeginNotifyUrl = None
        self._StreamEndNotifyUrl = None
        self._RecordNotifyUrl = None
        self._SnapshotNotifyUrl = None
        self._PornCensorshipNotifyUrl = None
        self._CallbackKey = None
        self._StreamMixNotifyUrl = None
        self._PushExceptionNotifyUrl = None

    @property
    def TemplateName(self):
        return self._TemplateName

    @TemplateName.setter
    def TemplateName(self, TemplateName):
        self._TemplateName = TemplateName

    @property
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def StreamBeginNotifyUrl(self):
        return self._StreamBeginNotifyUrl

    @StreamBeginNotifyUrl.setter
    def StreamBeginNotifyUrl(self, StreamBeginNotifyUrl):
        self._StreamBeginNotifyUrl = StreamBeginNotifyUrl

    @property
    def StreamEndNotifyUrl(self):
        return self._StreamEndNotifyUrl

    @StreamEndNotifyUrl.setter
    def StreamEndNotifyUrl(self, StreamEndNotifyUrl):
        self._StreamEndNotifyUrl = StreamEndNotifyUrl

    @property
    def RecordNotifyUrl(self):
        return self._RecordNotifyUrl

    @RecordNotifyUrl.setter
    def RecordNotifyUrl(self, RecordNotifyUrl):
        self._RecordNotifyUrl = RecordNotifyUrl

    @property
    def SnapshotNotifyUrl(self):
        return self._SnapshotNotifyUrl

    @SnapshotNotifyUrl.setter
    def SnapshotNotifyUrl(self, SnapshotNotifyUrl):
        self._SnapshotNotifyUrl = SnapshotNotifyUrl

    @property
    def PornCensorshipNotifyUrl(self):
        return self._PornCensorshipNotifyUrl

    @PornCensorshipNotifyUrl.setter
    def PornCensorshipNotifyUrl(self, PornCensorshipNotifyUrl):
        self._PornCensorshipNotifyUrl = PornCensorshipNotifyUrl

    @property
    def CallbackKey(self):
        return self._CallbackKey

    @CallbackKey.setter
    def CallbackKey(self, CallbackKey):
        self._CallbackKey = CallbackKey

    @property
    def StreamMixNotifyUrl(self):
        return self._StreamMixNotifyUrl

    @StreamMixNotifyUrl.setter
    def StreamMixNotifyUrl(self, StreamMixNotifyUrl):
        self._StreamMixNotifyUrl = StreamMixNotifyUrl

    @property
    def PushExceptionNotifyUrl(self):
        return self._PushExceptionNotifyUrl

    @PushExceptionNotifyUrl.setter
    def PushExceptionNotifyUrl(self, PushExceptionNotifyUrl):
        self._PushExceptionNotifyUrl = PushExceptionNotifyUrl


    def _deserialize(self, params):
        self._TemplateName = params.get("TemplateName")
        self._Description = params.get("Description")
        self._StreamBeginNotifyUrl = params.get("StreamBeginNotifyUrl")
        self._StreamEndNotifyUrl = params.get("StreamEndNotifyUrl")
        self._RecordNotifyUrl = params.get("RecordNotifyUrl")
        self._SnapshotNotifyUrl = params.get("SnapshotNotifyUrl")
        self._PornCensorshipNotifyUrl = params.get("PornCensorshipNotifyUrl")
        self._CallbackKey = params.get("CallbackKey")
        self._StreamMixNotifyUrl = params.get("StreamMixNotifyUrl")
        self._PushExceptionNotifyUrl = params.get("PushExceptionNotifyUrl")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateLiveCallbackTemplateResponse(AbstractModel):
    """CreateLiveCallbackTemplate response structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
        :type TemplateId: int
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


class CreateLivePullStreamTaskRequest(AbstractModel):
    """CreateLivePullStreamTask request structure.

    """

    def __init__(self):
        r"""
        :param _SourceType: The source type. Valid values:
PullLivePushLive: Live streaming
PullVodPushLive: Video files
PullPicPushLive: Images
        :type SourceType: str
        :param _SourceUrls: The source URL(s).
If `SourceType` is `PullLivePushLive`, you can specify only one source URL.
If `SourceType` is `PullVodPushLive`, you can specify at most 30 source URLs.
Supported file formats: FLV, MP4, HLS.
Supported protocols: HTTP, HTTPS, RTMP, RTMPS, RTSP, SRT.
Notes:
1. We recommend you use FLV files as the source. Poorly interleaved MP4 files may result in playback stuttering. You can also re-interleave your MP4 files before adding them as the source.
2. Do not use private network domains or malicious URLs. CSS will block accounts that do.
3. To avoid push and playback issues, make sure the source files are properly interleaved.
4. Supported video coding formats: H.264, H.265.
5. Supported audio coding format: AAC.
6. Use small video files, preferably not longer than one hour. Large files may take a long time to load or resume after pause. Relay may fail if the time consumed exceeds 15 seconds.
        :type SourceUrls: list of str
        :param _DomainName: The push domain name.
The pulled stream is pushed to this domain.
Note: If the destination is not a CSS address and its format is different from that of CSS addresses, pass the full address to `ToUrl`. For details, see the description of the `ToUrl` parameter.
        :type DomainName: str
        :param _AppName: The application to push to.
The pulled stream is pushed to this application.
        :type AppName: str
        :param _StreamName: The stream name.
The pulled stream is pushed under this name.
        :type StreamName: str
        :param _StartTime: The start time.
It must be in UTC format.
Example: 2019-01-08T10:00:00Z.
Note: Beijing time is 8 hours ahead of UTC. The [ISO 8601 format](https://intl.cloud.tencent.com/document/product/266/11732#iso-date-format) is used.
        :type StartTime: str
        :param _EndTime: The end time. Notes:
1. The end time must be later than the start time.
2. The end time and start time must be later than the current time.
3. The end time and start time must be less than seven days apart.
It must be in UTC format.
Example: 2019-01-08T10:00:00Z.
Note: Beijing time is 8 hours ahead of UTC. The [ISO 8601 format](https://intl.cloud.tencent.com/document/product/266/11732#iso-date-format) is used.
        :type EndTime: str
        :param _Operator: The operator.
        :type Operator: str
        :param _PushArgs: The push parameter.
This is a custom parameter carried during push.
Example:
bak=1&test=2
        :type PushArgs: str
        :param _CallbackEvents: The events to listen for. If you do not pass this parameter, all events will be listened for.
TaskStart: Callback for starting a task
TaskExit: Callback for ending a task
VodSourceFileStart: Callback for starting to pull from video files
VodSourceFileFinish: Callback for stopping pulling from video files
ResetTaskConfig: Callback for modifying a task

`TaskAlarm` indicates a warning event. `AlarmType` examples:
PullFileUnstable: Pull from video files is unstable.
PushStreamUnstable: Push is unstable.
PullFileFailed: Error pulling from video files.
PushStreamFailed: Push error.
FileEndEarly: The video file ended prematurely.
        :type CallbackEvents: list of str
        :param _VodLoopTimes: The number of times to loop video files. Default value: -1.
-1: Loop indefinitely
0: Do not loop
> 0: The number of loop times. A task will end either when the videos are looped for the specified number of times or at the specified task end time, whichever is earlier.
This parameter is valid only when the source is video files.
        :type VodLoopTimes: str
        :param _VodRefreshType: The behavior after the source video files (`SourceUrls`) are changed.
ImmediateNewSource: Play the new videos immediately
ContinueBreakPoint: Play the new videos after the current video is finished playing (the remaining videos in the old playlist will not be played).

This parameter is valid only if the source before the change is video files.
        :type VodRefreshType: str
        :param _CallbackUrl: A custom callback URL.
Callbacks about pull and relay events will be sent to this URL.
        :type CallbackUrl: str
        :param _ExtraCmd: Other parameters.
For example, you can use `ignore_region` to ignore the region passed in and assign a region based on load distribution.
        :type ExtraCmd: str
        :param _Comment: The remarks for a task, not longer than 512 bytes.
        :type Comment: str
        :param _ToUrl: The complete destination URL.
If you specify this parameter, make sure you pass in an empty string for `DomainName`, `AppName`, and `StreamName`.

Note: Make sure that the expiration time of the signature is later than the task end time.
        :type ToUrl: str
        :param _BackupSourceType: The backup source type.
PullLivePushLive: Live streaming
PullVodPushLive: Video files
Notes:
1. Backup sources are supported only if the primary source type is live streaming.
2. When pull from the primary source is interrupted, the system will pull from the backup source.
3. If the backup source is a video file, each time the video is finished, the system will check if the primary source is recovered and will switch back if it is.
        :type BackupSourceType: str
        :param _BackupSourceUrl: The URL of the backup source.
You can specify only one backup source URL.
        :type BackupSourceUrl: str
        :param _WatermarkList: The information of watermarks to add.
Notes:
1. You can add up to four watermarks to different locations of the video.
2. Make sure you use publicly accessible URLs for the watermark images.
3. Supported image formats include PNG, JPG, and GIF.
        :type WatermarkList: list of PullPushWatermarkInfo
        :param _VodLocalMode: Whether to use local mode when the source type is video files. The default is `0`.
0: Do not use local mode
1: Use local mode
Note: If you enable local mode, MP4 files will be downloaded to local storage, and the local files will be used for push. This ensures more reliable push. Pushing a local file will incur additional fees.
        :type VodLocalMode: int
        """
        self._SourceType = None
        self._SourceUrls = None
        self._DomainName = None
        self._AppName = None
        self._StreamName = None
        self._StartTime = None
        self._EndTime = None
        self._Operator = None
        self._PushArgs = None
        self._CallbackEvents = None
        self._VodLoopTimes = None
        self._VodRefreshType = None
        self._CallbackUrl = None
        self._ExtraCmd = None
        self._Comment = None
        self._ToUrl = None
        self._BackupSourceType = None
        self._BackupSourceUrl = None
        self._WatermarkList = None
        self._VodLocalMode = None

    @property
    def SourceType(self):
        return self._SourceType

    @SourceType.setter
    def SourceType(self, SourceType):
        self._SourceType = SourceType

    @property
    def SourceUrls(self):
        return self._SourceUrls

    @SourceUrls.setter
    def SourceUrls(self, SourceUrls):
        self._SourceUrls = SourceUrls

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

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
    def Operator(self):
        return self._Operator

    @Operator.setter
    def Operator(self, Operator):
        self._Operator = Operator

    @property
    def PushArgs(self):
        return self._PushArgs

    @PushArgs.setter
    def PushArgs(self, PushArgs):
        self._PushArgs = PushArgs

    @property
    def CallbackEvents(self):
        return self._CallbackEvents

    @CallbackEvents.setter
    def CallbackEvents(self, CallbackEvents):
        self._CallbackEvents = CallbackEvents

    @property
    def VodLoopTimes(self):
        return self._VodLoopTimes

    @VodLoopTimes.setter
    def VodLoopTimes(self, VodLoopTimes):
        self._VodLoopTimes = VodLoopTimes

    @property
    def VodRefreshType(self):
        return self._VodRefreshType

    @VodRefreshType.setter
    def VodRefreshType(self, VodRefreshType):
        self._VodRefreshType = VodRefreshType

    @property
    def CallbackUrl(self):
        return self._CallbackUrl

    @CallbackUrl.setter
    def CallbackUrl(self, CallbackUrl):
        self._CallbackUrl = CallbackUrl

    @property
    def ExtraCmd(self):
        return self._ExtraCmd

    @ExtraCmd.setter
    def ExtraCmd(self, ExtraCmd):
        self._ExtraCmd = ExtraCmd

    @property
    def Comment(self):
        return self._Comment

    @Comment.setter
    def Comment(self, Comment):
        self._Comment = Comment

    @property
    def ToUrl(self):
        return self._ToUrl

    @ToUrl.setter
    def ToUrl(self, ToUrl):
        self._ToUrl = ToUrl

    @property
    def BackupSourceType(self):
        return self._BackupSourceType

    @BackupSourceType.setter
    def BackupSourceType(self, BackupSourceType):
        self._BackupSourceType = BackupSourceType

    @property
    def BackupSourceUrl(self):
        return self._BackupSourceUrl

    @BackupSourceUrl.setter
    def BackupSourceUrl(self, BackupSourceUrl):
        self._BackupSourceUrl = BackupSourceUrl

    @property
    def WatermarkList(self):
        return self._WatermarkList

    @WatermarkList.setter
    def WatermarkList(self, WatermarkList):
        self._WatermarkList = WatermarkList

    @property
    def VodLocalMode(self):
        return self._VodLocalMode

    @VodLocalMode.setter
    def VodLocalMode(self, VodLocalMode):
        self._VodLocalMode = VodLocalMode


    def _deserialize(self, params):
        self._SourceType = params.get("SourceType")
        self._SourceUrls = params.get("SourceUrls")
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._Operator = params.get("Operator")
        self._PushArgs = params.get("PushArgs")
        self._CallbackEvents = params.get("CallbackEvents")
        self._VodLoopTimes = params.get("VodLoopTimes")
        self._VodRefreshType = params.get("VodRefreshType")
        self._CallbackUrl = params.get("CallbackUrl")
        self._ExtraCmd = params.get("ExtraCmd")
        self._Comment = params.get("Comment")
        self._ToUrl = params.get("ToUrl")
        self._BackupSourceType = params.get("BackupSourceType")
        self._BackupSourceUrl = params.get("BackupSourceUrl")
        if params.get("WatermarkList") is not None:
            self._WatermarkList = []
            for item in params.get("WatermarkList"):
                obj = PullPushWatermarkInfo()
                obj._deserialize(item)
                self._WatermarkList.append(obj)
        self._VodLocalMode = params.get("VodLocalMode")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateLivePullStreamTaskResponse(AbstractModel):
    """CreateLivePullStreamTask response structure.

    """

    def __init__(self):
        r"""
        :param _TaskId: The task ID.
        :type TaskId: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TaskId = None
        self._RequestId = None

    @property
    def TaskId(self):
        return self._TaskId

    @TaskId.setter
    def TaskId(self, TaskId):
        self._TaskId = TaskId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TaskId = params.get("TaskId")
        self._RequestId = params.get("RequestId")


class CreateLiveRecordRequest(AbstractModel):
    """CreateLiveRecord request structure.

    """

    def __init__(self):
        r"""
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _AppName: Push path, which is the same as the `AppName` in push and playback addresses and is `live` by default.
        :type AppName: str
        :param _DomainName: Push domain name. This parameter must be set for multi-domain name push.
        :type DomainName: str
        :param _StartTime: Recording start time, which is China standard time and should be URL-encoded (RFC3986). For example, the encoding of 2017-01-01 10:10:01 is 2017-01-01+10%3a10%3a01.
In scheduled recording mode, this field must be set; in real-time video recording mode, this field is ignored.
        :type StartTime: str
        :param _EndTime: Recording end time, which is China standard time and should be URL-encoded (RFC3986). For example, the encoding of 2017-01-01 10:30:01 is 2017-01-01+10%3a30%3a01.
In scheduled recording mode, this field must be set; in real-time video recording mode, this field is optional. If the recording is set to real-time video recording mode through the `Highlight` parameter, the set end time should not be more than 30 minutes after the current time. If the set end time is more than 30 minutes after the current time, earlier than the current time, or left empty, the actual end time will be 30 minutes after the current time.
        :type EndTime: str
        :param _RecordType: Recording type.
"video": Audio-video recording **(default)**.
"audio": audio recording.
In both scheduled and real-time video recording modes, this parameter is valid and is not case sensitive.
        :type RecordType: str
        :param _FileFormat: Recording file format. Valid values:
"flv" **(default)**, "hls", "mp4", "aac", "mp3".
In both scheduled and real-time video recording modes, this parameter is valid and is not case sensitive.
        :type FileFormat: str
        :param _Highlight: Mark for enabling real-time video recording mode.
0: Real-time video recording mode is not enabled, i.e., the scheduled recording mode is used **(default)**. See [Sample 1](#.E7.A4.BA.E4.BE.8B1-.E5.88.9B.E5.BB.BA.E5.AE.9A.E6.97.B6.E5.BD.95.E5.88.B6.E4.BB.BB.E5.8A.A1).
1: Real-time video recording mode is enabled. See [Sample 2](#.E7.A4.BA.E4.BE.8B2-.E5.88.9B.E5.BB.BA.E5.AE.9E.E6.97.B6.E5.BD.95.E5.88.B6.E4.BB.BB.E5.8A.A1).
        :type Highlight: int
        :param _MixStream: Flag for enabling A+B=C mixed stream recording.
0: A+B=C mixed stream recording is not enabled **(default)**.
1: A+B=C mixed stream recording is enabled.
In both scheduled and real-time video recording modes, this parameter is valid.
        :type MixStream: int
        :param _StreamParam: Recording stream parameter. The following parameters are supported currently:
record_interval: recording interval in seconds. Value range: 1800-7200.
storage_time: recording file storage duration in seconds.
Example: record_interval=3600&storage_time=2592000.
Note: the parameter needs to be URL-encoded.
In both scheduled and real-time video recording modes, this parameter is valid.
        :type StreamParam: str
        """
        self._StreamName = None
        self._AppName = None
        self._DomainName = None
        self._StartTime = None
        self._EndTime = None
        self._RecordType = None
        self._FileFormat = None
        self._Highlight = None
        self._MixStream = None
        self._StreamParam = None

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

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
    def RecordType(self):
        return self._RecordType

    @RecordType.setter
    def RecordType(self, RecordType):
        self._RecordType = RecordType

    @property
    def FileFormat(self):
        return self._FileFormat

    @FileFormat.setter
    def FileFormat(self, FileFormat):
        self._FileFormat = FileFormat

    @property
    def Highlight(self):
        return self._Highlight

    @Highlight.setter
    def Highlight(self, Highlight):
        self._Highlight = Highlight

    @property
    def MixStream(self):
        return self._MixStream

    @MixStream.setter
    def MixStream(self, MixStream):
        self._MixStream = MixStream

    @property
    def StreamParam(self):
        return self._StreamParam

    @StreamParam.setter
    def StreamParam(self, StreamParam):
        self._StreamParam = StreamParam


    def _deserialize(self, params):
        self._StreamName = params.get("StreamName")
        self._AppName = params.get("AppName")
        self._DomainName = params.get("DomainName")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._RecordType = params.get("RecordType")
        self._FileFormat = params.get("FileFormat")
        self._Highlight = params.get("Highlight")
        self._MixStream = params.get("MixStream")
        self._StreamParam = params.get("StreamParam")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateLiveRecordResponse(AbstractModel):
    """CreateLiveRecord response structure.

    """

    def __init__(self):
        r"""
        :param _TaskId: Task ID, which uniquely identifies a recording task globally.
        :type TaskId: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TaskId = None
        self._RequestId = None

    @property
    def TaskId(self):
        return self._TaskId

    @TaskId.setter
    def TaskId(self, TaskId):
        self._TaskId = TaskId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TaskId = params.get("TaskId")
        self._RequestId = params.get("RequestId")


class CreateLiveRecordRuleRequest(AbstractModel):
    """CreateLiveRecordRule request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _TemplateId: Template ID.
        :type TemplateId: int
        :param _AppName: Push path, which is the same as the AppName in push and playback addresses and is "live" by default.
        :type AppName: str
        :param _StreamName: Stream name.
Note: If the parameter is a non-empty string, the rule will be only applicable to the particular stream.
        :type StreamName: str
        """
        self._DomainName = None
        self._TemplateId = None
        self._AppName = None
        self._StreamName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._TemplateId = params.get("TemplateId")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateLiveRecordRuleResponse(AbstractModel):
    """CreateLiveRecordRule response structure.

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


class CreateLiveRecordTemplateRequest(AbstractModel):
    """CreateLiveRecordTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateName: Template name. Only letters, digits, underscores, and hyphens can be contained.
        :type TemplateName: str
        :param _Description: Message description
        :type Description: str
        :param _FlvParam: FLV recording parameter, which is set when FLV recording is enabled.
        :type FlvParam: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _HlsParam: HLS recording parameter, which is set when HLS recording is enabled.
        :type HlsParam: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _Mp4Param: Mp4 recording parameter, which is set when Mp4 recording is enabled.
        :type Mp4Param: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _AacParam: AAC recording parameter, which is set when AAC recording is enabled.
        :type AacParam: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _IsDelayLive: LVB type. Default value: 0.
0: LVB.
1: LCB.
        :type IsDelayLive: int
        :param _HlsSpecialParam: HLS-specific recording parameter.
        :type HlsSpecialParam: :class:`tencentcloud.live.v20180801.models.HlsSpecialParam`
        :param _Mp3Param: Mp3 recording parameter, which is set when Mp3 recording is enabled.
        :type Mp3Param: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _RemoveWatermark: Whether to remove the watermark. This parameter is invalid if `IsDelayLive` is `1`.
        :type RemoveWatermark: bool
        :param _FlvSpecialParam: A special parameter for FLV recording.
        :type FlvSpecialParam: :class:`tencentcloud.live.v20180801.models.FlvSpecialParam`
        """
        self._TemplateName = None
        self._Description = None
        self._FlvParam = None
        self._HlsParam = None
        self._Mp4Param = None
        self._AacParam = None
        self._IsDelayLive = None
        self._HlsSpecialParam = None
        self._Mp3Param = None
        self._RemoveWatermark = None
        self._FlvSpecialParam = None

    @property
    def TemplateName(self):
        return self._TemplateName

    @TemplateName.setter
    def TemplateName(self, TemplateName):
        self._TemplateName = TemplateName

    @property
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def FlvParam(self):
        return self._FlvParam

    @FlvParam.setter
    def FlvParam(self, FlvParam):
        self._FlvParam = FlvParam

    @property
    def HlsParam(self):
        return self._HlsParam

    @HlsParam.setter
    def HlsParam(self, HlsParam):
        self._HlsParam = HlsParam

    @property
    def Mp4Param(self):
        return self._Mp4Param

    @Mp4Param.setter
    def Mp4Param(self, Mp4Param):
        self._Mp4Param = Mp4Param

    @property
    def AacParam(self):
        return self._AacParam

    @AacParam.setter
    def AacParam(self, AacParam):
        self._AacParam = AacParam

    @property
    def IsDelayLive(self):
        return self._IsDelayLive

    @IsDelayLive.setter
    def IsDelayLive(self, IsDelayLive):
        self._IsDelayLive = IsDelayLive

    @property
    def HlsSpecialParam(self):
        return self._HlsSpecialParam

    @HlsSpecialParam.setter
    def HlsSpecialParam(self, HlsSpecialParam):
        self._HlsSpecialParam = HlsSpecialParam

    @property
    def Mp3Param(self):
        return self._Mp3Param

    @Mp3Param.setter
    def Mp3Param(self, Mp3Param):
        self._Mp3Param = Mp3Param

    @property
    def RemoveWatermark(self):
        return self._RemoveWatermark

    @RemoveWatermark.setter
    def RemoveWatermark(self, RemoveWatermark):
        self._RemoveWatermark = RemoveWatermark

    @property
    def FlvSpecialParam(self):
        return self._FlvSpecialParam

    @FlvSpecialParam.setter
    def FlvSpecialParam(self, FlvSpecialParam):
        self._FlvSpecialParam = FlvSpecialParam


    def _deserialize(self, params):
        self._TemplateName = params.get("TemplateName")
        self._Description = params.get("Description")
        if params.get("FlvParam") is not None:
            self._FlvParam = RecordParam()
            self._FlvParam._deserialize(params.get("FlvParam"))
        if params.get("HlsParam") is not None:
            self._HlsParam = RecordParam()
            self._HlsParam._deserialize(params.get("HlsParam"))
        if params.get("Mp4Param") is not None:
            self._Mp4Param = RecordParam()
            self._Mp4Param._deserialize(params.get("Mp4Param"))
        if params.get("AacParam") is not None:
            self._AacParam = RecordParam()
            self._AacParam._deserialize(params.get("AacParam"))
        self._IsDelayLive = params.get("IsDelayLive")
        if params.get("HlsSpecialParam") is not None:
            self._HlsSpecialParam = HlsSpecialParam()
            self._HlsSpecialParam._deserialize(params.get("HlsSpecialParam"))
        if params.get("Mp3Param") is not None:
            self._Mp3Param = RecordParam()
            self._Mp3Param._deserialize(params.get("Mp3Param"))
        self._RemoveWatermark = params.get("RemoveWatermark")
        if params.get("FlvSpecialParam") is not None:
            self._FlvSpecialParam = FlvSpecialParam()
            self._FlvSpecialParam._deserialize(params.get("FlvSpecialParam"))
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateLiveRecordTemplateResponse(AbstractModel):
    """CreateLiveRecordTemplate response structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
        :type TemplateId: int
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


class CreateLiveSnapshotRuleRequest(AbstractModel):
    """CreateLiveSnapshotRule request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _TemplateId: Template ID.
        :type TemplateId: int
        :param _AppName: Push path, which is the same as the `AppName` in push and playback addresses and is `live` by default.
        :type AppName: str
        :param _StreamName: Stream name.
Note: if this parameter is a non-empty string, the rule will take effect only for the particular stream.
        :type StreamName: str
        """
        self._DomainName = None
        self._TemplateId = None
        self._AppName = None
        self._StreamName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._TemplateId = params.get("TemplateId")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateLiveSnapshotRuleResponse(AbstractModel):
    """CreateLiveSnapshotRule response structure.

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


class CreateLiveSnapshotTemplateRequest(AbstractModel):
    """CreateLiveSnapshotTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateName: Template name.
Maximum length: 255 bytes.
Only letters, digits, underscores, and hyphens can be contained.
        :type TemplateName: str
        :param _CosAppId: COS application ID.
        :type CosAppId: int
        :param _CosBucket: COS bucket name.
Note: the value of `CosBucket` cannot contain `-[appid]`.
        :type CosBucket: str
        :param _CosRegion: COS region.
        :type CosRegion: str
        :param _Description: Description.
Maximum length: 1,024 bytes.
Only letters, digits, underscores, and hyphens can be contained.
        :type Description: str
        :param _SnapshotInterval: Screencapturing interval (s). Default value: 10
Value range: 2-300
        :type SnapshotInterval: int
        :param _Width: Screenshot width. Default value: `0` (original width)
Value range: 0-3000
        :type Width: int
        :param _Height: Screenshot height. Default value: `0` (original height)
Value range: 0-2000
        :type Height: int
        :param _PornFlag: Whether to enable porn detection. 0: no, 1: yes. Default value: 0
        :type PornFlag: int
        :param _CosPrefix: COS Bucket folder prefix.
If no value is entered, the default value
`/{Year}-{Month}-{Day}`
will be used.
        :type CosPrefix: str
        :param _CosFileName: COS filename.
If no value is entered, the default value 
`{StreamID}-screenshot-{Hour}-{Minute}-{Second}-{Width}x{Height}{Ext}`
will be used.
        :type CosFileName: str
        """
        self._TemplateName = None
        self._CosAppId = None
        self._CosBucket = None
        self._CosRegion = None
        self._Description = None
        self._SnapshotInterval = None
        self._Width = None
        self._Height = None
        self._PornFlag = None
        self._CosPrefix = None
        self._CosFileName = None

    @property
    def TemplateName(self):
        return self._TemplateName

    @TemplateName.setter
    def TemplateName(self, TemplateName):
        self._TemplateName = TemplateName

    @property
    def CosAppId(self):
        return self._CosAppId

    @CosAppId.setter
    def CosAppId(self, CosAppId):
        self._CosAppId = CosAppId

    @property
    def CosBucket(self):
        return self._CosBucket

    @CosBucket.setter
    def CosBucket(self, CosBucket):
        self._CosBucket = CosBucket

    @property
    def CosRegion(self):
        return self._CosRegion

    @CosRegion.setter
    def CosRegion(self, CosRegion):
        self._CosRegion = CosRegion

    @property
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def SnapshotInterval(self):
        return self._SnapshotInterval

    @SnapshotInterval.setter
    def SnapshotInterval(self, SnapshotInterval):
        self._SnapshotInterval = SnapshotInterval

    @property
    def Width(self):
        return self._Width

    @Width.setter
    def Width(self, Width):
        self._Width = Width

    @property
    def Height(self):
        return self._Height

    @Height.setter
    def Height(self, Height):
        self._Height = Height

    @property
    def PornFlag(self):
        return self._PornFlag

    @PornFlag.setter
    def PornFlag(self, PornFlag):
        self._PornFlag = PornFlag

    @property
    def CosPrefix(self):
        return self._CosPrefix

    @CosPrefix.setter
    def CosPrefix(self, CosPrefix):
        self._CosPrefix = CosPrefix

    @property
    def CosFileName(self):
        return self._CosFileName

    @CosFileName.setter
    def CosFileName(self, CosFileName):
        self._CosFileName = CosFileName


    def _deserialize(self, params):
        self._TemplateName = params.get("TemplateName")
        self._CosAppId = params.get("CosAppId")
        self._CosBucket = params.get("CosBucket")
        self._CosRegion = params.get("CosRegion")
        self._Description = params.get("Description")
        self._SnapshotInterval = params.get("SnapshotInterval")
        self._Width = params.get("Width")
        self._Height = params.get("Height")
        self._PornFlag = params.get("PornFlag")
        self._CosPrefix = params.get("CosPrefix")
        self._CosFileName = params.get("CosFileName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateLiveSnapshotTemplateResponse(AbstractModel):
    """CreateLiveSnapshotTemplate response structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
        :type TemplateId: int
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


class CreateLiveTimeShiftRuleRequest(AbstractModel):
    """CreateLiveTimeShiftRule request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: The push domain.
        :type DomainName: str
        :param _AppName: The push path, which should be the same as `AppName` in the push and playback URLs. The default value is `live`.
        :type AppName: str
        :param _StreamName: The stream name.
Note: If you pass in a non-empty string, the rule will only be applied to the specified stream.
        :type StreamName: str
        :param _TemplateId: The template ID.
        :type TemplateId: int
        """
        self._DomainName = None
        self._AppName = None
        self._StreamName = None
        self._TemplateId = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        self._TemplateId = params.get("TemplateId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateLiveTimeShiftRuleResponse(AbstractModel):
    """CreateLiveTimeShiftRule response structure.

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


class CreateLiveTimeShiftTemplateRequest(AbstractModel):
    """CreateLiveTimeShiftTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateName: The template name.
Maximum length: 255 bytes.
Only letters, numbers, underscores, and hyphens are supported.
        :type TemplateName: str
        :param _Duration: The time shifting duration.
Unit: Second.
        :type Duration: int
        :param _Description: The template description.
Only letters, numbers, underscores, and hyphens are supported.
        :type Description: str
        :param _Area: The region.
`Mainland`: The Chinese mainland.
`Overseas`: Outside the Chinese mainland.
Default value: `Mainland`.
        :type Area: str
        :param _ItemDuration: The segment size.
Value range: 3-10.
Unit: Second.
Default value: 5
        :type ItemDuration: int
        :param _RemoveWatermark: Whether to remove watermarks.
If you pass in `true`, the original stream will be recorded.
Default value: `false`.
        :type RemoveWatermark: bool
        :param _TranscodeTemplateIds: The transcoding template IDs.
This API works only if `RemoveWatermark` is `false`.
        :type TranscodeTemplateIds: list of int
        """
        self._TemplateName = None
        self._Duration = None
        self._Description = None
        self._Area = None
        self._ItemDuration = None
        self._RemoveWatermark = None
        self._TranscodeTemplateIds = None

    @property
    def TemplateName(self):
        return self._TemplateName

    @TemplateName.setter
    def TemplateName(self, TemplateName):
        self._TemplateName = TemplateName

    @property
    def Duration(self):
        return self._Duration

    @Duration.setter
    def Duration(self, Duration):
        self._Duration = Duration

    @property
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def Area(self):
        return self._Area

    @Area.setter
    def Area(self, Area):
        self._Area = Area

    @property
    def ItemDuration(self):
        return self._ItemDuration

    @ItemDuration.setter
    def ItemDuration(self, ItemDuration):
        self._ItemDuration = ItemDuration

    @property
    def RemoveWatermark(self):
        return self._RemoveWatermark

    @RemoveWatermark.setter
    def RemoveWatermark(self, RemoveWatermark):
        self._RemoveWatermark = RemoveWatermark

    @property
    def TranscodeTemplateIds(self):
        return self._TranscodeTemplateIds

    @TranscodeTemplateIds.setter
    def TranscodeTemplateIds(self, TranscodeTemplateIds):
        self._TranscodeTemplateIds = TranscodeTemplateIds


    def _deserialize(self, params):
        self._TemplateName = params.get("TemplateName")
        self._Duration = params.get("Duration")
        self._Description = params.get("Description")
        self._Area = params.get("Area")
        self._ItemDuration = params.get("ItemDuration")
        self._RemoveWatermark = params.get("RemoveWatermark")
        self._TranscodeTemplateIds = params.get("TranscodeTemplateIds")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateLiveTimeShiftTemplateResponse(AbstractModel):
    """CreateLiveTimeShiftTemplate response structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: The template ID.
        :type TemplateId: int
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


class CreateLiveTranscodeRuleRequest(AbstractModel):
    """CreateLiveTranscodeRule request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Playback domain name.
        :type DomainName: str
        :param _AppName: The push path, which is the same as `AppName` in the push and playback addresses and is `live` by default. If you only want to bind the template to a domain, pass in an empty string.
        :type AppName: str
        :param _StreamName: Stream name. If only the domain name or path is bound, leave this parameter blank.
        :type StreamName: str
        :param _TemplateId: Designates an existing template ID.
        :type TemplateId: int
        """
        self._DomainName = None
        self._AppName = None
        self._StreamName = None
        self._TemplateId = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        self._TemplateId = params.get("TemplateId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateLiveTranscodeRuleResponse(AbstractModel):
    """CreateLiveTranscodeRule response structure.

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


class CreateLiveTranscodeTemplateRequest(AbstractModel):
    """CreateLiveTranscodeTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateName: Template name, such as “900p”. This can be only a combination of letters and digits.
Length limit:
  Standard transcoding: 1-10 characters
  Top speed codec transcoding: 3-10 characters
        :type TemplateName: str
        :param _VideoBitrate: Video bitrate in Kbps. Value range: 100-8000.
Note: the transcoding template requires that the bitrate be unique. Therefore, the final saved bitrate may be different from the input bitrate.
        :type VideoBitrate: int
        :param _Acodec: Audio codec. Default value: aac.
Note: this parameter is unsupported now.
        :type Acodec: str
        :param _AudioBitrate: Audio bitrate. Default value: 0.
Value range: 0-500.
        :type AudioBitrate: int
        :param _Vcodec: Video codec. Valid values: h264, h265, origin (default)

origin: original codec as the output codec
        :type Vcodec: str
        :param _Description: Template description.
        :type Description: str
        :param _NeedVideo: Whether to keep the video. 0: no; 1: yes. Default value: 1.
        :type NeedVideo: int
        :param _Width: Width. Default value: 0.
Value range: 0-3000
It must be a multiple of 2. The original width is 0.
        :type Width: int
        :param _NeedAudio: Whether to keep the audio. 0: no; 1: yes. Default value: 1.
        :type NeedAudio: int
        :param _Height: Height. Default value: 0
Value range: 0-3000
The value must be a multiple of 2. The original height is `0`.
This parameter is required for a top speed codec template (when `AiTransCode` is `1`).
        :type Height: int
        :param _Fps: Frame rate. Default value: 0.
Value range: 0-60
        :type Fps: int
        :param _Gop: Keyframe interval in seconds. Default value: original interval
Value range: 2-6
        :type Gop: int
        :param _Rotate: Rotation angle. Default value: 0.
Valid values: 0, 90, 180, 270
        :type Rotate: int
        :param _Profile: Encoding quality:
baseline/main/high. Default value: baseline.
        :type Profile: str
        :param _BitrateToOrig: Whether to use the original bitrate when the set bitrate is larger than the original bitrate.
0: no, 1: yes
Default value: 0.
        :type BitrateToOrig: int
        :param _HeightToOrig: Whether to use the original height when the set height is higher than the original height.
0: no, 1: yes
Default value: 0.
        :type HeightToOrig: int
        :param _FpsToOrig: Whether to use the original frame rate when the set frame rate is larger than the original frame rate.
0: no, 1: yes
Default value: 0.
        :type FpsToOrig: int
        :param _AiTransCode: Whether it is a top speed codec template. 0: no, 1: yes. Default value: 0.
        :type AiTransCode: int
        :param _AdaptBitratePercent: Bitrate compression ratio of top speed codec video.
Target bitrate of top speed code = VideoBitrate * (1-AdaptBitratePercent)

Value range: 0.0-0.5.
        :type AdaptBitratePercent: float
        :param _ShortEdgeAsHeight: Whether to use the short side as the video height. 0: no, 1: yes. Default value: 0.
        :type ShortEdgeAsHeight: int
        :param _DRMType: The DRM encryption type. Valid values: fairplay, normalaes, widevine.
If you do not pass this parameter or pass in an empty string, the existing configuration will be reset.
        :type DRMType: str
        :param _DRMTracks: The tracks to encrypt. Valid values: AUDIO, SD, HD, UHD1, UHD2. You can choose only one video track (SD, HD, UHD1, or UHD2).
If you do not pass this parameter or pass in an empty string, the existing configuration will be reset.
        :type DRMTracks: str
        """
        self._TemplateName = None
        self._VideoBitrate = None
        self._Acodec = None
        self._AudioBitrate = None
        self._Vcodec = None
        self._Description = None
        self._NeedVideo = None
        self._Width = None
        self._NeedAudio = None
        self._Height = None
        self._Fps = None
        self._Gop = None
        self._Rotate = None
        self._Profile = None
        self._BitrateToOrig = None
        self._HeightToOrig = None
        self._FpsToOrig = None
        self._AiTransCode = None
        self._AdaptBitratePercent = None
        self._ShortEdgeAsHeight = None
        self._DRMType = None
        self._DRMTracks = None

    @property
    def TemplateName(self):
        return self._TemplateName

    @TemplateName.setter
    def TemplateName(self, TemplateName):
        self._TemplateName = TemplateName

    @property
    def VideoBitrate(self):
        return self._VideoBitrate

    @VideoBitrate.setter
    def VideoBitrate(self, VideoBitrate):
        self._VideoBitrate = VideoBitrate

    @property
    def Acodec(self):
        return self._Acodec

    @Acodec.setter
    def Acodec(self, Acodec):
        self._Acodec = Acodec

    @property
    def AudioBitrate(self):
        return self._AudioBitrate

    @AudioBitrate.setter
    def AudioBitrate(self, AudioBitrate):
        self._AudioBitrate = AudioBitrate

    @property
    def Vcodec(self):
        return self._Vcodec

    @Vcodec.setter
    def Vcodec(self, Vcodec):
        self._Vcodec = Vcodec

    @property
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def NeedVideo(self):
        return self._NeedVideo

    @NeedVideo.setter
    def NeedVideo(self, NeedVideo):
        self._NeedVideo = NeedVideo

    @property
    def Width(self):
        return self._Width

    @Width.setter
    def Width(self, Width):
        self._Width = Width

    @property
    def NeedAudio(self):
        return self._NeedAudio

    @NeedAudio.setter
    def NeedAudio(self, NeedAudio):
        self._NeedAudio = NeedAudio

    @property
    def Height(self):
        return self._Height

    @Height.setter
    def Height(self, Height):
        self._Height = Height

    @property
    def Fps(self):
        return self._Fps

    @Fps.setter
    def Fps(self, Fps):
        self._Fps = Fps

    @property
    def Gop(self):
        return self._Gop

    @Gop.setter
    def Gop(self, Gop):
        self._Gop = Gop

    @property
    def Rotate(self):
        return self._Rotate

    @Rotate.setter
    def Rotate(self, Rotate):
        self._Rotate = Rotate

    @property
    def Profile(self):
        return self._Profile

    @Profile.setter
    def Profile(self, Profile):
        self._Profile = Profile

    @property
    def BitrateToOrig(self):
        return self._BitrateToOrig

    @BitrateToOrig.setter
    def BitrateToOrig(self, BitrateToOrig):
        self._BitrateToOrig = BitrateToOrig

    @property
    def HeightToOrig(self):
        return self._HeightToOrig

    @HeightToOrig.setter
    def HeightToOrig(self, HeightToOrig):
        self._HeightToOrig = HeightToOrig

    @property
    def FpsToOrig(self):
        return self._FpsToOrig

    @FpsToOrig.setter
    def FpsToOrig(self, FpsToOrig):
        self._FpsToOrig = FpsToOrig

    @property
    def AiTransCode(self):
        return self._AiTransCode

    @AiTransCode.setter
    def AiTransCode(self, AiTransCode):
        self._AiTransCode = AiTransCode

    @property
    def AdaptBitratePercent(self):
        return self._AdaptBitratePercent

    @AdaptBitratePercent.setter
    def AdaptBitratePercent(self, AdaptBitratePercent):
        self._AdaptBitratePercent = AdaptBitratePercent

    @property
    def ShortEdgeAsHeight(self):
        return self._ShortEdgeAsHeight

    @ShortEdgeAsHeight.setter
    def ShortEdgeAsHeight(self, ShortEdgeAsHeight):
        self._ShortEdgeAsHeight = ShortEdgeAsHeight

    @property
    def DRMType(self):
        return self._DRMType

    @DRMType.setter
    def DRMType(self, DRMType):
        self._DRMType = DRMType

    @property
    def DRMTracks(self):
        return self._DRMTracks

    @DRMTracks.setter
    def DRMTracks(self, DRMTracks):
        self._DRMTracks = DRMTracks


    def _deserialize(self, params):
        self._TemplateName = params.get("TemplateName")
        self._VideoBitrate = params.get("VideoBitrate")
        self._Acodec = params.get("Acodec")
        self._AudioBitrate = params.get("AudioBitrate")
        self._Vcodec = params.get("Vcodec")
        self._Description = params.get("Description")
        self._NeedVideo = params.get("NeedVideo")
        self._Width = params.get("Width")
        self._NeedAudio = params.get("NeedAudio")
        self._Height = params.get("Height")
        self._Fps = params.get("Fps")
        self._Gop = params.get("Gop")
        self._Rotate = params.get("Rotate")
        self._Profile = params.get("Profile")
        self._BitrateToOrig = params.get("BitrateToOrig")
        self._HeightToOrig = params.get("HeightToOrig")
        self._FpsToOrig = params.get("FpsToOrig")
        self._AiTransCode = params.get("AiTransCode")
        self._AdaptBitratePercent = params.get("AdaptBitratePercent")
        self._ShortEdgeAsHeight = params.get("ShortEdgeAsHeight")
        self._DRMType = params.get("DRMType")
        self._DRMTracks = params.get("DRMTracks")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateLiveTranscodeTemplateResponse(AbstractModel):
    """CreateLiveTranscodeTemplate response structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
        :type TemplateId: int
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


class CreateLiveWatermarkRuleRequest(AbstractModel):
    """CreateLiveWatermarkRule request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _AppName: Push path, which is the same as the `AppName` in push and playback addresses and is `live` by default.
        :type AppName: str
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _TemplateId: Watermark ID, which is the `WatermarkId` returned by the [AddLiveWatermark](https://intl.cloud.tencent.com/document/product/267/30154?from_cn_redirect=1) API.
        :type TemplateId: int
        """
        self._DomainName = None
        self._AppName = None
        self._StreamName = None
        self._TemplateId = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        self._TemplateId = params.get("TemplateId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateLiveWatermarkRuleResponse(AbstractModel):
    """CreateLiveWatermarkRule response structure.

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


class CreateRecordTaskRequest(AbstractModel):
    """CreateRecordTask request structure.

    """

    def __init__(self):
        r"""
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _AppName: Push path.
        :type AppName: str
        :param _EndTime: Recording end time in UNIX timestamp format. `EndTime` should be later than `StartTime` and the current time, and the duration between `EndTime` and `StartTime` is up to 24 hours.
        :type EndTime: int
        :param _StartTime: Recording start time in UNIX timestamp format. Leaving this parameter empty means starting recording now. `StartTime` cannot be later than the current time plus 6 days.
        :type StartTime: int
        :param _StreamType: Push type. Default value: 0. Valid values:
0: LVB push.
1: mixed stream, i.e., A + B = C mixed stream.
        :type StreamType: int
        :param _TemplateId: Recording template ID, which is the returned value of `CreateLiveRecordTemplate`. If this parameter is left empty or incorrect, the stream will be recorded in HLS format and retained permanently by default.
        :type TemplateId: int
        :param _Extension: Extension field which is not defined now. It is empty by default.
        :type Extension: str
        """
        self._StreamName = None
        self._DomainName = None
        self._AppName = None
        self._EndTime = None
        self._StartTime = None
        self._StreamType = None
        self._TemplateId = None
        self._Extension = None

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def EndTime(self):
        return self._EndTime

    @EndTime.setter
    def EndTime(self, EndTime):
        self._EndTime = EndTime

    @property
    def StartTime(self):
        return self._StartTime

    @StartTime.setter
    def StartTime(self, StartTime):
        self._StartTime = StartTime

    @property
    def StreamType(self):
        return self._StreamType

    @StreamType.setter
    def StreamType(self, StreamType):
        self._StreamType = StreamType

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId

    @property
    def Extension(self):
        return self._Extension

    @Extension.setter
    def Extension(self, Extension):
        self._Extension = Extension


    def _deserialize(self, params):
        self._StreamName = params.get("StreamName")
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._EndTime = params.get("EndTime")
        self._StartTime = params.get("StartTime")
        self._StreamType = params.get("StreamType")
        self._TemplateId = params.get("TemplateId")
        self._Extension = params.get("Extension")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateRecordTaskResponse(AbstractModel):
    """CreateRecordTask response structure.

    """

    def __init__(self):
        r"""
        :param _TaskId: A globally unique task ID. If `TaskId` is returned, the recording task has been successfully created.
        :type TaskId: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TaskId = None
        self._RequestId = None

    @property
    def TaskId(self):
        return self._TaskId

    @TaskId.setter
    def TaskId(self, TaskId):
        self._TaskId = TaskId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TaskId = params.get("TaskId")
        self._RequestId = params.get("RequestId")


class CreateScreenshotTaskRequest(AbstractModel):
    """CreateScreenshotTask request structure.

    """

    def __init__(self):
        r"""
        :param _StreamName: The stream name.
        :type StreamName: str
        :param _DomainName: The push domain.
        :type DomainName: str
        :param _AppName: The push path.
        :type AppName: str
        :param _EndTime: The task end time, which must be a Unix timestamp and later than `StartTime` and the current time. The end time and start time cannot be more than 24 hours apart.
        :type EndTime: int
        :param _TemplateId: The ID of the screencapturing template, which is returned by `CreateLiveSnapshotTemplate`. If an incorrect template ID is passed in, the screencapturing task will fail.
        :type TemplateId: int
        :param _StartTime: The task start time, which must be a Unix timestamp and cannot be later than six days from the current time. If you do not specify this parameter, the task will start immediately.
        :type StartTime: int
        :param _StreamType: The publishing type. Valid values:
`0` (default): Live stream
`1`: Mixed stream
        :type StreamType: int
        :param _Extension: An extension field, which is not defined currently and is empty by default.
        :type Extension: str
        """
        self._StreamName = None
        self._DomainName = None
        self._AppName = None
        self._EndTime = None
        self._TemplateId = None
        self._StartTime = None
        self._StreamType = None
        self._Extension = None

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def EndTime(self):
        return self._EndTime

    @EndTime.setter
    def EndTime(self, EndTime):
        self._EndTime = EndTime

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId

    @property
    def StartTime(self):
        return self._StartTime

    @StartTime.setter
    def StartTime(self, StartTime):
        self._StartTime = StartTime

    @property
    def StreamType(self):
        return self._StreamType

    @StreamType.setter
    def StreamType(self, StreamType):
        self._StreamType = StreamType

    @property
    def Extension(self):
        return self._Extension

    @Extension.setter
    def Extension(self, Extension):
        self._Extension = Extension


    def _deserialize(self, params):
        self._StreamName = params.get("StreamName")
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._EndTime = params.get("EndTime")
        self._TemplateId = params.get("TemplateId")
        self._StartTime = params.get("StartTime")
        self._StreamType = params.get("StreamType")
        self._Extension = params.get("Extension")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateScreenshotTaskResponse(AbstractModel):
    """CreateScreenshotTask response structure.

    """

    def __init__(self):
        r"""
        :param _TaskId: A unique task ID. If this parameter is returned, the screencapturing task is created successfully.
        :type TaskId: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TaskId = None
        self._RequestId = None

    @property
    def TaskId(self):
        return self._TaskId

    @TaskId.setter
    def TaskId(self, TaskId):
        self._TaskId = TaskId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TaskId = params.get("TaskId")
        self._RequestId = params.get("RequestId")


class DayStreamPlayInfo(AbstractModel):
    """Stream playback information

    """

    def __init__(self):
        r"""
        :param _Time: Data point in time in the format of `yyyy-mm-dd HH:MM:SS`.
        :type Time: str
        :param _Bandwidth: Bandwidth in Mbps.
        :type Bandwidth: float
        :param _Flux: Traffic in MB.
        :type Flux: float
        :param _Request: Number of requests.
        :type Request: int
        :param _Online: Number of online viewers.
        :type Online: int
        """
        self._Time = None
        self._Bandwidth = None
        self._Flux = None
        self._Request = None
        self._Online = None

    @property
    def Time(self):
        return self._Time

    @Time.setter
    def Time(self, Time):
        self._Time = Time

    @property
    def Bandwidth(self):
        return self._Bandwidth

    @Bandwidth.setter
    def Bandwidth(self, Bandwidth):
        self._Bandwidth = Bandwidth

    @property
    def Flux(self):
        return self._Flux

    @Flux.setter
    def Flux(self, Flux):
        self._Flux = Flux

    @property
    def Request(self):
        return self._Request

    @Request.setter
    def Request(self, Request):
        self._Request = Request

    @property
    def Online(self):
        return self._Online

    @Online.setter
    def Online(self, Online):
        self._Online = Online


    def _deserialize(self, params):
        self._Time = params.get("Time")
        self._Bandwidth = params.get("Bandwidth")
        self._Flux = params.get("Flux")
        self._Request = params.get("Request")
        self._Online = params.get("Online")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DelayInfo(AbstractModel):
    """Delayed playback information.

    """

    def __init__(self):
        r"""
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _AppName: Push path, which is the same as the 
 `AppName` in push and playback addresses and is `live` by default.
        :type AppName: str
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _DelayInterval: Delay time in seconds.
        :type DelayInterval: int
        :param _CreateTime: Creation time in UTC time.
Note: the difference between UTC time and Beijing time is 8 hours.
Example: 2019-06-18T12:00:00Z (i.e., June 18, 2019 20:00:00 Beijing time).
        :type CreateTime: str
        :param _ExpireTime: Expiration time in UTC time.
Note: the difference between UTC time and Beijing time is 8 hours.
Example: 2019-06-18T12:00:00Z (i.e., June 18, 2019 20:00:00 Beijing time).
        :type ExpireTime: str
        :param _Status: Current status:
-1: expired.
1: in effect.
        :type Status: int
        """
        self._DomainName = None
        self._AppName = None
        self._StreamName = None
        self._DelayInterval = None
        self._CreateTime = None
        self._ExpireTime = None
        self._Status = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def DelayInterval(self):
        return self._DelayInterval

    @DelayInterval.setter
    def DelayInterval(self, DelayInterval):
        self._DelayInterval = DelayInterval

    @property
    def CreateTime(self):
        return self._CreateTime

    @CreateTime.setter
    def CreateTime(self, CreateTime):
        self._CreateTime = CreateTime

    @property
    def ExpireTime(self):
        return self._ExpireTime

    @ExpireTime.setter
    def ExpireTime(self, ExpireTime):
        self._ExpireTime = ExpireTime

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        self._DelayInterval = params.get("DelayInterval")
        self._CreateTime = params.get("CreateTime")
        self._ExpireTime = params.get("ExpireTime")
        self._Status = params.get("Status")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteLiveCallbackRuleRequest(AbstractModel):
    """DeleteLiveCallbackRule request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _AppName: Push path, which is the same as the `AppName` in push and playback addresses and is `live` by default.
        :type AppName: str
        """
        self._DomainName = None
        self._AppName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteLiveCallbackRuleResponse(AbstractModel):
    """DeleteLiveCallbackRule response structure.

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


class DeleteLiveCallbackTemplateRequest(AbstractModel):
    """DeleteLiveCallbackTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
1. Get the template ID in the returned value of the [CreateLiveCallbackTemplate](https://intl.cloud.tencent.com/document/product/267/32637?from_cn_redirect=1) API call.
2. You can query the list of created templates through the [DescribeLiveCallbackTemplates](https://intl.cloud.tencent.com/document/product/267/32632?from_cn_redirect=1) API.
        :type TemplateId: int
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
        


class DeleteLiveCallbackTemplateResponse(AbstractModel):
    """DeleteLiveCallbackTemplate response structure.

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


class DeleteLiveDomainRequest(AbstractModel):
    """DeleteLiveDomain request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Domain name to be deleted.
        :type DomainName: str
        :param _DomainType: Type. 0: push, 1: playback.
        :type DomainType: int
        """
        self._DomainName = None
        self._DomainType = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def DomainType(self):
        return self._DomainType

    @DomainType.setter
    def DomainType(self, DomainType):
        self._DomainType = DomainType


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._DomainType = params.get("DomainType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteLiveDomainResponse(AbstractModel):
    """DeleteLiveDomain response structure.

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


class DeleteLivePullStreamTaskRequest(AbstractModel):
    """DeleteLivePullStreamTask request structure.

    """

    def __init__(self):
        r"""
        :param _TaskId: The task ID.
        :type TaskId: str
        :param _Operator: The operator.
        :type Operator: str
        """
        self._TaskId = None
        self._Operator = None

    @property
    def TaskId(self):
        return self._TaskId

    @TaskId.setter
    def TaskId(self, TaskId):
        self._TaskId = TaskId

    @property
    def Operator(self):
        return self._Operator

    @Operator.setter
    def Operator(self, Operator):
        self._Operator = Operator


    def _deserialize(self, params):
        self._TaskId = params.get("TaskId")
        self._Operator = params.get("Operator")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteLivePullStreamTaskResponse(AbstractModel):
    """DeleteLivePullStreamTask response structure.

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


class DeleteLiveRecordRequest(AbstractModel):
    """DeleteLiveRecord request structure.

    """

    def __init__(self):
        r"""
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _TaskId: Task ID returned by the `CreateLiveRecord` API.
        :type TaskId: int
        """
        self._StreamName = None
        self._TaskId = None

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def TaskId(self):
        return self._TaskId

    @TaskId.setter
    def TaskId(self, TaskId):
        self._TaskId = TaskId


    def _deserialize(self, params):
        self._StreamName = params.get("StreamName")
        self._TaskId = params.get("TaskId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteLiveRecordResponse(AbstractModel):
    """DeleteLiveRecord response structure.

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


class DeleteLiveRecordRuleRequest(AbstractModel):
    """DeleteLiveRecordRule request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Push domain name.
Domain name+AppName+StreamName uniquely identifies a single transcoding rule. If you need to delete it, strong match is required. For example, even if AppName is blank, you need to pass in a blank string to make a strong match.
        :type DomainName: str
        :param _AppName: Push path, which is the same as the AppName in push and playback addresses and is "live" by default.
Domain name+AppName+StreamName uniquely identifies a single transcoding rule. If you need to delete it, strong match is required. For example, even if AppName is blank, you need to pass in a blank string to make a strong match.
        :type AppName: str
        :param _StreamName: Stream name.
Domain name+AppName+StreamName uniquely identifies a single transcoding rule. If you need to delete it, strong match is required. For example, even if AppName is blank, you need to pass in a blank string to make a strong match.
        :type StreamName: str
        """
        self._DomainName = None
        self._AppName = None
        self._StreamName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteLiveRecordRuleResponse(AbstractModel):
    """DeleteLiveRecordRule response structure.

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


class DeleteLiveRecordTemplateRequest(AbstractModel):
    """DeleteLiveRecordTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID obtained through the `DescribeRecordTemplates` API.
        :type TemplateId: int
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
        


class DeleteLiveRecordTemplateResponse(AbstractModel):
    """DeleteLiveRecordTemplate response structure.

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


class DeleteLiveSnapshotRuleRequest(AbstractModel):
    """DeleteLiveSnapshotRule request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _AppName: Push path, which is the same as the `AppName` in push and playback addresses and is `live` by default.
        :type AppName: str
        :param _StreamName: Stream name.
        :type StreamName: str
        """
        self._DomainName = None
        self._AppName = None
        self._StreamName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteLiveSnapshotRuleResponse(AbstractModel):
    """DeleteLiveSnapshotRule response structure.

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


class DeleteLiveSnapshotTemplateRequest(AbstractModel):
    """DeleteLiveSnapshotTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
1. Get from the returned value of the [CreateLiveSnapshotTemplate](https://intl.cloud.tencent.com/document/product/267/32624?from_cn_redirect=1) API call.
2. You can query the list of created screencapturing templates through the [DescribeLiveSnapshotTemplates](https://intl.cloud.tencent.com/document/product/267/32619?from_cn_redirect=1) API.
        :type TemplateId: int
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
        


class DeleteLiveSnapshotTemplateResponse(AbstractModel):
    """DeleteLiveSnapshotTemplate response structure.

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


class DeleteLiveTimeShiftRuleRequest(AbstractModel):
    """DeleteLiveTimeShiftRule request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: The push domain.
`Domain name+AppName+StreamName` uniquely identifies a time shifting rule. To delete a time shifting rule, exact match is required. This means if the `AppName` of a time shifting rule is empty, to delete the rule, you need to pass in an empty string for `AppName`.
        :type DomainName: str
        :param _AppName: The push path, which should be the same as `AppName` in the push and playback URLs. The default value is `live`.
`Domain name+AppName+StreamName` uniquely identifies a time shifting rule. To delete a time shifting rule, exact match is required. This means if the `AppName` of a time shifting rule is empty, to delete the rule, you need to pass in an empty string for `AppName`.
        :type AppName: str
        :param _StreamName: The stream name.
`Domain name+AppName+StreamName` uniquely identifies a time shifting rule. To delete a time shifting rule, exact match is required. This means if the `AppName` of a time shifting rule is empty, to delete the rule, you need to pass in an empty string for `AppName`.
        :type StreamName: str
        """
        self._DomainName = None
        self._AppName = None
        self._StreamName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteLiveTimeShiftRuleResponse(AbstractModel):
    """DeleteLiveTimeShiftRule response structure.

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


class DeleteLiveTimeShiftTemplateRequest(AbstractModel):
    """DeleteLiveTimeShiftTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: The template ID.
        :type TemplateId: int
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
        


class DeleteLiveTimeShiftTemplateResponse(AbstractModel):
    """DeleteLiveTimeShiftTemplate response structure.

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


class DeleteLiveTranscodeRuleRequest(AbstractModel):
    """DeleteLiveTranscodeRule request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Playback domain name.
        :type DomainName: str
        :param _AppName: Push path, which is the same as the `AppName` in push and playback addresses and is `live` by default.
        :type AppName: str
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _TemplateId: Template ID.
        :type TemplateId: int
        """
        self._DomainName = None
        self._AppName = None
        self._StreamName = None
        self._TemplateId = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        self._TemplateId = params.get("TemplateId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteLiveTranscodeRuleResponse(AbstractModel):
    """DeleteLiveTranscodeRule response structure.

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


class DeleteLiveTranscodeTemplateRequest(AbstractModel):
    """DeleteLiveTranscodeTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
1. Get the template ID in the returned value of the [CreateLiveTranscodeTemplate](https://intl.cloud.tencent.com/document/product/267/32646?from_cn_redirect=1) API call.
2. You can query the list of created templates through the [DescribeLiveTranscodeTemplates](https://intl.cloud.tencent.com/document/product/267/32641?from_cn_redirect=1) API.
        :type TemplateId: int
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
        


class DeleteLiveTranscodeTemplateResponse(AbstractModel):
    """DeleteLiveTranscodeTemplate response structure.

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


class DeleteLiveWatermarkRequest(AbstractModel):
    """DeleteLiveWatermark request structure.

    """

    def __init__(self):
        r"""
        :param _WatermarkId: Watermark ID.
Watermark ID obtained in the returned value of the [AddLiveWatermark](https://intl.cloud.tencent.com/document/product/267/30154?from_cn_redirect=1) API call.
Watermark ID returned by the `DescribeLiveWatermarks` API.
        :type WatermarkId: int
        """
        self._WatermarkId = None

    @property
    def WatermarkId(self):
        return self._WatermarkId

    @WatermarkId.setter
    def WatermarkId(self, WatermarkId):
        self._WatermarkId = WatermarkId


    def _deserialize(self, params):
        self._WatermarkId = params.get("WatermarkId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteLiveWatermarkResponse(AbstractModel):
    """DeleteLiveWatermark response structure.

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


class DeleteLiveWatermarkRuleRequest(AbstractModel):
    """DeleteLiveWatermarkRule request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _AppName: Push path, which is the same as the `AppName` in push and playback addresses and is `live` by default.
        :type AppName: str
        :param _StreamName: Stream name.
        :type StreamName: str
        """
        self._DomainName = None
        self._AppName = None
        self._StreamName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteLiveWatermarkRuleResponse(AbstractModel):
    """DeleteLiveWatermarkRule response structure.

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


class DeleteRecordTaskRequest(AbstractModel):
    """DeleteRecordTask request structure.

    """

    def __init__(self):
        r"""
        :param _TaskId: Task ID returned by `CreateRecordTask`. The recording task specified by `TaskId` will be deleted.
        :type TaskId: str
        """
        self._TaskId = None

    @property
    def TaskId(self):
        return self._TaskId

    @TaskId.setter
    def TaskId(self, TaskId):
        self._TaskId = TaskId


    def _deserialize(self, params):
        self._TaskId = params.get("TaskId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteRecordTaskResponse(AbstractModel):
    """DeleteRecordTask response structure.

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


class DescribeAllStreamPlayInfoListRequest(AbstractModel):
    """DescribeAllStreamPlayInfoList request structure.

    """

    def __init__(self):
        r"""
        :param _QueryTime: The query time of the request, supports data query for the last one month. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format, for details, see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type QueryTime: str
        :param _PlayDomains: The playback domains to query. If you leave this empty, all playback domains will be queried.
        :type PlayDomains: list of str
        """
        self._QueryTime = None
        self._PlayDomains = None

    @property
    def QueryTime(self):
        return self._QueryTime

    @QueryTime.setter
    def QueryTime(self, QueryTime):
        self._QueryTime = QueryTime

    @property
    def PlayDomains(self):
        return self._PlayDomains

    @PlayDomains.setter
    def PlayDomains(self, PlayDomains):
        self._PlayDomains = PlayDomains


    def _deserialize(self, params):
        self._QueryTime = params.get("QueryTime")
        self._PlayDomains = params.get("PlayDomains")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeAllStreamPlayInfoListResponse(AbstractModel):
    """DescribeAllStreamPlayInfoList response structure.

    """

    def __init__(self):
        r"""
        :param _QueryTime: The time point queried, whose format is the same as that of the corresponding request parameter.
        :type QueryTime: str
        :param _DataInfoList: The playback data.
        :type DataInfoList: list of MonitorStreamPlayInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._QueryTime = None
        self._DataInfoList = None
        self._RequestId = None

    @property
    def QueryTime(self):
        return self._QueryTime

    @QueryTime.setter
    def QueryTime(self, QueryTime):
        self._QueryTime = QueryTime

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._QueryTime = params.get("QueryTime")
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = MonitorStreamPlayInfo()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeBillBandwidthAndFluxListRequest(AbstractModel):
    """DescribeBillBandwidthAndFluxList request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time of the request, supports data query for the last three years, the gap between the start time and the end time cannot exceed one month. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format, for details, see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type StartTime: str
        :param _EndTime: The end time of the request, supports data query for the last three years, the gap between the start time and the end time cannot exceed one month. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format,for details,see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type EndTime: str
        :param _PlayDomains: LVB playback domain name. If this parameter is left empty, full data will be queried.
        :type PlayDomains: list of str
        :param _MainlandOrOversea: Valid values:
Mainland: query data for Mainland China,
Oversea: query data for regions outside Mainland China,
Default: query data for all regions.
Note: LEB only supports querying data for all regions.
        :type MainlandOrOversea: str
        :param _Granularity: Data granularity. Valid values:
5: 5-minute granularity (the query time span should be within 1 day),
60: 1-hour granularity (the query time span should be within one month),
1440: 1-day granularity (the query time span should be within one month).
Default value: 5.
        :type Granularity: int
        :param _ServiceName: Service name. Valid values: LVB, LEB. The sum of LVB and LEB usage will be returned if this parameter is left empty.
        :type ServiceName: str
        :param _RegionNames: Region. Valid values:
China Mainland
Asia Pacific I
Asia Pacific II
Asia Pacific III
Europe
North America
South America
Middle East
Africa
        :type RegionNames: list of str
        """
        self._StartTime = None
        self._EndTime = None
        self._PlayDomains = None
        self._MainlandOrOversea = None
        self._Granularity = None
        self._ServiceName = None
        self._RegionNames = None

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
    def PlayDomains(self):
        return self._PlayDomains

    @PlayDomains.setter
    def PlayDomains(self, PlayDomains):
        self._PlayDomains = PlayDomains

    @property
    def MainlandOrOversea(self):
        return self._MainlandOrOversea

    @MainlandOrOversea.setter
    def MainlandOrOversea(self, MainlandOrOversea):
        self._MainlandOrOversea = MainlandOrOversea

    @property
    def Granularity(self):
        return self._Granularity

    @Granularity.setter
    def Granularity(self, Granularity):
        self._Granularity = Granularity

    @property
    def ServiceName(self):
        return self._ServiceName

    @ServiceName.setter
    def ServiceName(self, ServiceName):
        self._ServiceName = ServiceName

    @property
    def RegionNames(self):
        return self._RegionNames

    @RegionNames.setter
    def RegionNames(self, RegionNames):
        self._RegionNames = RegionNames


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._PlayDomains = params.get("PlayDomains")
        self._MainlandOrOversea = params.get("MainlandOrOversea")
        self._Granularity = params.get("Granularity")
        self._ServiceName = params.get("ServiceName")
        self._RegionNames = params.get("RegionNames")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeBillBandwidthAndFluxListResponse(AbstractModel):
    """DescribeBillBandwidthAndFluxList response structure.

    """

    def __init__(self):
        r"""
        :param _PeakBandwidthTime: Time point of peak bandwidth value in the format of `yyyy-mm-dd HH:MM:SS`.
        :type PeakBandwidthTime: str
        :param _PeakBandwidth: Peak bandwidth in Mbps.
        :type PeakBandwidth: float
        :param _P95PeakBandwidthTime: Time point of 95th percentile bandwidth value in the format of `yyyy-mm-dd HH:MM:SS`.
        :type P95PeakBandwidthTime: str
        :param _P95PeakBandwidth: 95th percentile bandwidth in Mbps.
        :type P95PeakBandwidth: float
        :param _SumFlux: Total traffic in MB.
        :type SumFlux: float
        :param _DataInfoList: Detailed data information.
        :type DataInfoList: list of BillDataInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._PeakBandwidthTime = None
        self._PeakBandwidth = None
        self._P95PeakBandwidthTime = None
        self._P95PeakBandwidth = None
        self._SumFlux = None
        self._DataInfoList = None
        self._RequestId = None

    @property
    def PeakBandwidthTime(self):
        return self._PeakBandwidthTime

    @PeakBandwidthTime.setter
    def PeakBandwidthTime(self, PeakBandwidthTime):
        self._PeakBandwidthTime = PeakBandwidthTime

    @property
    def PeakBandwidth(self):
        return self._PeakBandwidth

    @PeakBandwidth.setter
    def PeakBandwidth(self, PeakBandwidth):
        self._PeakBandwidth = PeakBandwidth

    @property
    def P95PeakBandwidthTime(self):
        return self._P95PeakBandwidthTime

    @P95PeakBandwidthTime.setter
    def P95PeakBandwidthTime(self, P95PeakBandwidthTime):
        self._P95PeakBandwidthTime = P95PeakBandwidthTime

    @property
    def P95PeakBandwidth(self):
        return self._P95PeakBandwidth

    @P95PeakBandwidth.setter
    def P95PeakBandwidth(self, P95PeakBandwidth):
        self._P95PeakBandwidth = P95PeakBandwidth

    @property
    def SumFlux(self):
        return self._SumFlux

    @SumFlux.setter
    def SumFlux(self, SumFlux):
        self._SumFlux = SumFlux

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._PeakBandwidthTime = params.get("PeakBandwidthTime")
        self._PeakBandwidth = params.get("PeakBandwidth")
        self._P95PeakBandwidthTime = params.get("P95PeakBandwidthTime")
        self._P95PeakBandwidth = params.get("P95PeakBandwidth")
        self._SumFlux = params.get("SumFlux")
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = BillDataInfo()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeConcurrentRecordStreamNumRequest(AbstractModel):
    """DescribeConcurrentRecordStreamNum request structure.

    """

    def __init__(self):
        r"""
        :param _LiveType: Live streaming type. SlowLive: LCB.
NormalLive: LVB.
        :type LiveType: str
        :param _StartTime: The start time of the request, supports data query for the last six months, the gap between the start time and the end time cannot exceed one month. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format, for details, see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type StartTime: str
        :param _EndTime: The end time of the request, supports data query for the last six months, the gap between the start time and the end time cannot exceed one month. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format,for details,see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type EndTime: str
        :param _MainlandOrOversea: Valid values: Mainland (data for Mainland China), Oversea (data for regions outside Mainland China). If this parameter is left empty, data for all regions will be queried.
        :type MainlandOrOversea: str
        :param _PushDomains: Playback domain name list. If this parameter is left empty, full data will be queried.
        :type PushDomains: list of str
        """
        self._LiveType = None
        self._StartTime = None
        self._EndTime = None
        self._MainlandOrOversea = None
        self._PushDomains = None

    @property
    def LiveType(self):
        return self._LiveType

    @LiveType.setter
    def LiveType(self, LiveType):
        self._LiveType = LiveType

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
    def MainlandOrOversea(self):
        return self._MainlandOrOversea

    @MainlandOrOversea.setter
    def MainlandOrOversea(self, MainlandOrOversea):
        self._MainlandOrOversea = MainlandOrOversea

    @property
    def PushDomains(self):
        return self._PushDomains

    @PushDomains.setter
    def PushDomains(self, PushDomains):
        self._PushDomains = PushDomains


    def _deserialize(self, params):
        self._LiveType = params.get("LiveType")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._MainlandOrOversea = params.get("MainlandOrOversea")
        self._PushDomains = params.get("PushDomains")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeConcurrentRecordStreamNumResponse(AbstractModel):
    """DescribeConcurrentRecordStreamNum response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: Statistics list.
        :type DataInfoList: list of ConcurrentRecordStreamNum
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = ConcurrentRecordStreamNum()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeDeliverBandwidthListRequest(AbstractModel):
    """DescribeDeliverBandwidthList request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time of the request, supports data query for the last three months, the gap between the start time and the end time cannot exceed a month. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format, for details, see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type StartTime: str
        :param _EndTime: The end time of the request, supports data query for the last three months, the gap between the start time and the end time cannot exceed a month. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format,for details,see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type EndTime: str
        """
        self._StartTime = None
        self._EndTime = None

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


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeDeliverBandwidthListResponse(AbstractModel):
    """DescribeDeliverBandwidthList response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: Billable bandwidth of live stream relaying.
        :type DataInfoList: list of BandwidthInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = BandwidthInfo()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeGroupProIspPlayInfoListRequest(AbstractModel):
    """DescribeGroupProIspPlayInfoList request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time of the request, supports data query for the last one month, the gap between the start time and the end time cannot exceed one month. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format, for details, see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type StartTime: str
        :param _EndTime: The end time of the request, supports data query for the last one month, the gap between the start time and the end time cannot exceed one month. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format,for details,see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type EndTime: str
        :param _PlayDomains: Playback domain name. If this parameter is left empty, full data will be queried.
        :type PlayDomains: list of str
        :param _ProvinceNames: District list. If this parameter is left empty, data for all districts will be returned.
        :type ProvinceNames: list of str
        :param _IspNames: ISP list. If this parameter is left empty, data of all ISPs will be returned.
        :type IspNames: list of str
        :param _MainlandOrOversea: Within or outside Mainland China. Valid values: Mainland (data for Mainland China), Oversea (data for regions outside Mainland China). If this parameter is left empty, data for all regions will be queried.
        :type MainlandOrOversea: str
        """
        self._StartTime = None
        self._EndTime = None
        self._PlayDomains = None
        self._ProvinceNames = None
        self._IspNames = None
        self._MainlandOrOversea = None

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
    def PlayDomains(self):
        return self._PlayDomains

    @PlayDomains.setter
    def PlayDomains(self, PlayDomains):
        self._PlayDomains = PlayDomains

    @property
    def ProvinceNames(self):
        return self._ProvinceNames

    @ProvinceNames.setter
    def ProvinceNames(self, ProvinceNames):
        self._ProvinceNames = ProvinceNames

    @property
    def IspNames(self):
        return self._IspNames

    @IspNames.setter
    def IspNames(self, IspNames):
        self._IspNames = IspNames

    @property
    def MainlandOrOversea(self):
        return self._MainlandOrOversea

    @MainlandOrOversea.setter
    def MainlandOrOversea(self, MainlandOrOversea):
        self._MainlandOrOversea = MainlandOrOversea


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._PlayDomains = params.get("PlayDomains")
        self._ProvinceNames = params.get("ProvinceNames")
        self._IspNames = params.get("IspNames")
        self._MainlandOrOversea = params.get("MainlandOrOversea")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeGroupProIspPlayInfoListResponse(AbstractModel):
    """DescribeGroupProIspPlayInfoList response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: Data content.
        :type DataInfoList: list of GroupProIspDataInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = GroupProIspDataInfo()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeHttpStatusInfoListRequest(AbstractModel):
    """DescribeHttpStatusInfoList request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time of the request, supports data query for the last three months, the gap between the start time and the end time cannot exceed one day. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format, for details, see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type StartTime: str
        :param _EndTime: The end time of the request, supports data query for the last three months, the gap between the start time and the end time cannot exceed one day. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format,for details,see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type EndTime: str
        :param _PlayDomains: Playback domain name list.
        :type PlayDomains: list of str
        """
        self._StartTime = None
        self._EndTime = None
        self._PlayDomains = None

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
    def PlayDomains(self):
        return self._PlayDomains

    @PlayDomains.setter
    def PlayDomains(self, PlayDomains):
        self._PlayDomains = PlayDomains


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._PlayDomains = params.get("PlayDomains")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeHttpStatusInfoListResponse(AbstractModel):
    """DescribeHttpStatusInfoList response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: Playback status code list.
        :type DataInfoList: list of HttpStatusData
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = HttpStatusData()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveCallbackRulesRequest(AbstractModel):
    """DescribeLiveCallbackRules request structure.

    """


class DescribeLiveCallbackRulesResponse(AbstractModel):
    """DescribeLiveCallbackRules response structure.

    """

    def __init__(self):
        r"""
        :param _Rules: Rule information list.
        :type Rules: list of CallBackRuleInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Rules = None
        self._RequestId = None

    @property
    def Rules(self):
        return self._Rules

    @Rules.setter
    def Rules(self, Rules):
        self._Rules = Rules

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Rules") is not None:
            self._Rules = []
            for item in params.get("Rules"):
                obj = CallBackRuleInfo()
                obj._deserialize(item)
                self._Rules.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveCallbackTemplateRequest(AbstractModel):
    """DescribeLiveCallbackTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
1. Get the template ID in the returned value of the [CreateLiveCallbackTemplate](https://intl.cloud.tencent.com/document/product/267/32637?from_cn_redirect=1) API call.
2. You can query the list of created templates through the [DescribeLiveCallbackTemplates](https://intl.cloud.tencent.com/document/product/267/32632?from_cn_redirect=1) API.
        :type TemplateId: int
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
        


class DescribeLiveCallbackTemplateResponse(AbstractModel):
    """DescribeLiveCallbackTemplate response structure.

    """

    def __init__(self):
        r"""
        :param _Template: Callback template information.
        :type Template: :class:`tencentcloud.live.v20180801.models.CallBackTemplateInfo`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Template = None
        self._RequestId = None

    @property
    def Template(self):
        return self._Template

    @Template.setter
    def Template(self, Template):
        self._Template = Template

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Template") is not None:
            self._Template = CallBackTemplateInfo()
            self._Template._deserialize(params.get("Template"))
        self._RequestId = params.get("RequestId")


class DescribeLiveCallbackTemplatesRequest(AbstractModel):
    """DescribeLiveCallbackTemplates request structure.

    """


class DescribeLiveCallbackTemplatesResponse(AbstractModel):
    """DescribeLiveCallbackTemplates response structure.

    """

    def __init__(self):
        r"""
        :param _Templates: Template information list.
        :type Templates: list of CallBackTemplateInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Templates = None
        self._RequestId = None

    @property
    def Templates(self):
        return self._Templates

    @Templates.setter
    def Templates(self, Templates):
        self._Templates = Templates

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Templates") is not None:
            self._Templates = []
            for item in params.get("Templates"):
                obj = CallBackTemplateInfo()
                obj._deserialize(item)
                self._Templates.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveCertRequest(AbstractModel):
    """DescribeLiveCert request structure.

    """

    def __init__(self):
        r"""
        :param _CertId: Certificate ID obtained through the `DescribeLiveCerts` API.
        :type CertId: int
        """
        self._CertId = None

    @property
    def CertId(self):
        return self._CertId

    @CertId.setter
    def CertId(self, CertId):
        self._CertId = CertId


    def _deserialize(self, params):
        self._CertId = params.get("CertId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveCertResponse(AbstractModel):
    """DescribeLiveCert response structure.

    """

    def __init__(self):
        r"""
        :param _CertInfo: Certificate information.
        :type CertInfo: :class:`tencentcloud.live.v20180801.models.CertInfo`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._CertInfo = None
        self._RequestId = None

    @property
    def CertInfo(self):
        return self._CertInfo

    @CertInfo.setter
    def CertInfo(self, CertInfo):
        self._CertInfo = CertInfo

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("CertInfo") is not None:
            self._CertInfo = CertInfo()
            self._CertInfo._deserialize(params.get("CertInfo"))
        self._RequestId = params.get("RequestId")


class DescribeLiveCertsRequest(AbstractModel):
    """DescribeLiveCerts request structure.

    """


class DescribeLiveCertsResponse(AbstractModel):
    """DescribeLiveCerts response structure.

    """

    def __init__(self):
        r"""
        :param _CertInfoSet: Certificate information list.
        :type CertInfoSet: list of CertInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._CertInfoSet = None
        self._RequestId = None

    @property
    def CertInfoSet(self):
        return self._CertInfoSet

    @CertInfoSet.setter
    def CertInfoSet(self, CertInfoSet):
        self._CertInfoSet = CertInfoSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("CertInfoSet") is not None:
            self._CertInfoSet = []
            for item in params.get("CertInfoSet"):
                obj = CertInfo()
                obj._deserialize(item)
                self._CertInfoSet.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveDelayInfoListRequest(AbstractModel):
    """DescribeLiveDelayInfoList request structure.

    """


class DescribeLiveDelayInfoListResponse(AbstractModel):
    """DescribeLiveDelayInfoList response structure.

    """

    def __init__(self):
        r"""
        :param _DelayInfoList: Delayed playback information list.
        :type DelayInfoList: list of DelayInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DelayInfoList = None
        self._RequestId = None

    @property
    def DelayInfoList(self):
        return self._DelayInfoList

    @DelayInfoList.setter
    def DelayInfoList(self, DelayInfoList):
        self._DelayInfoList = DelayInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DelayInfoList") is not None:
            self._DelayInfoList = []
            for item in params.get("DelayInfoList"):
                obj = DelayInfo()
                obj._deserialize(item)
                self._DelayInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveDomainCertBindingsRequest(AbstractModel):
    """DescribeLiveDomainCertBindings request structure.

    """

    def __init__(self):
        r"""
        :param _DomainSearch: The keyword to use to search for domains.
        :type DomainSearch: str
        :param _Offset: The number of records to skip before starting to return any results. 0 means to start from the first record and is the default.
        :type Offset: int
        :param _Length: The maximum number of records to return. The default is 50.
If this parameter is not specified, up to 50 records will be returned.
        :type Length: int
        :param _DomainName: The name of a particular domain to query.
        :type DomainName: str
        :param _OrderBy: Valid values:
ExpireTimeAsc: Sort the records by certificate expiration time in ascending order.
ExpireTimeDesc: Sort the records by certificate expiration time in descending order.
        :type OrderBy: str
        """
        self._DomainSearch = None
        self._Offset = None
        self._Length = None
        self._DomainName = None
        self._OrderBy = None

    @property
    def DomainSearch(self):
        return self._DomainSearch

    @DomainSearch.setter
    def DomainSearch(self, DomainSearch):
        self._DomainSearch = DomainSearch

    @property
    def Offset(self):
        return self._Offset

    @Offset.setter
    def Offset(self, Offset):
        self._Offset = Offset

    @property
    def Length(self):
        return self._Length

    @Length.setter
    def Length(self, Length):
        self._Length = Length

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def OrderBy(self):
        return self._OrderBy

    @OrderBy.setter
    def OrderBy(self, OrderBy):
        self._OrderBy = OrderBy


    def _deserialize(self, params):
        self._DomainSearch = params.get("DomainSearch")
        self._Offset = params.get("Offset")
        self._Length = params.get("Length")
        self._DomainName = params.get("DomainName")
        self._OrderBy = params.get("OrderBy")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveDomainCertBindingsResponse(AbstractModel):
    """DescribeLiveDomainCertBindings response structure.

    """

    def __init__(self):
        r"""
        :param _LiveDomainCertBindings: The information of domains that meet the query criteria.
        :type LiveDomainCertBindings: list of LiveDomainCertBindings
        :param _TotalNum: The number of records returned, which is needed for pagination.
        :type TotalNum: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._LiveDomainCertBindings = None
        self._TotalNum = None
        self._RequestId = None

    @property
    def LiveDomainCertBindings(self):
        return self._LiveDomainCertBindings

    @LiveDomainCertBindings.setter
    def LiveDomainCertBindings(self, LiveDomainCertBindings):
        self._LiveDomainCertBindings = LiveDomainCertBindings

    @property
    def TotalNum(self):
        return self._TotalNum

    @TotalNum.setter
    def TotalNum(self, TotalNum):
        self._TotalNum = TotalNum

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("LiveDomainCertBindings") is not None:
            self._LiveDomainCertBindings = []
            for item in params.get("LiveDomainCertBindings"):
                obj = LiveDomainCertBindings()
                obj._deserialize(item)
                self._LiveDomainCertBindings.append(obj)
        self._TotalNum = params.get("TotalNum")
        self._RequestId = params.get("RequestId")


class DescribeLiveDomainCertRequest(AbstractModel):
    """DescribeLiveDomainCert request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Playback domain name.
        :type DomainName: str
        """
        self._DomainName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveDomainCertResponse(AbstractModel):
    """DescribeLiveDomainCert response structure.

    """

    def __init__(self):
        r"""
        :param _DomainCertInfo: Certificate information.
        :type DomainCertInfo: :class:`tencentcloud.live.v20180801.models.DomainCertInfo`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DomainCertInfo = None
        self._RequestId = None

    @property
    def DomainCertInfo(self):
        return self._DomainCertInfo

    @DomainCertInfo.setter
    def DomainCertInfo(self, DomainCertInfo):
        self._DomainCertInfo = DomainCertInfo

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DomainCertInfo") is not None:
            self._DomainCertInfo = DomainCertInfo()
            self._DomainCertInfo._deserialize(params.get("DomainCertInfo"))
        self._RequestId = params.get("RequestId")


class DescribeLiveDomainRefererRequest(AbstractModel):
    """DescribeLiveDomainReferer request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Playback domain name
        :type DomainName: str
        """
        self._DomainName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveDomainRefererResponse(AbstractModel):
    """DescribeLiveDomainReferer response structure.

    """

    def __init__(self):
        r"""
        :param _RefererAuthConfig: Referer allowlist/blocklist configuration of a domain name
        :type RefererAuthConfig: :class:`tencentcloud.live.v20180801.models.RefererAuthConfig`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RefererAuthConfig = None
        self._RequestId = None

    @property
    def RefererAuthConfig(self):
        return self._RefererAuthConfig

    @RefererAuthConfig.setter
    def RefererAuthConfig(self, RefererAuthConfig):
        self._RefererAuthConfig = RefererAuthConfig

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("RefererAuthConfig") is not None:
            self._RefererAuthConfig = RefererAuthConfig()
            self._RefererAuthConfig._deserialize(params.get("RefererAuthConfig"))
        self._RequestId = params.get("RequestId")


class DescribeLiveDomainRequest(AbstractModel):
    """DescribeLiveDomain request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Domain name.
        :type DomainName: str
        """
        self._DomainName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveDomainResponse(AbstractModel):
    """DescribeLiveDomain response structure.

    """

    def __init__(self):
        r"""
        :param _DomainInfo: Domain name information.
Note: this field may return `null`, indicating that no valid value is obtained.
        :type DomainInfo: :class:`tencentcloud.live.v20180801.models.DomainInfo`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DomainInfo = None
        self._RequestId = None

    @property
    def DomainInfo(self):
        return self._DomainInfo

    @DomainInfo.setter
    def DomainInfo(self, DomainInfo):
        self._DomainInfo = DomainInfo

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DomainInfo") is not None:
            self._DomainInfo = DomainInfo()
            self._DomainInfo._deserialize(params.get("DomainInfo"))
        self._RequestId = params.get("RequestId")


class DescribeLiveDomainsRequest(AbstractModel):
    """DescribeLiveDomains request structure.

    """

    def __init__(self):
        r"""
        :param _DomainStatus: Filter by domain name status. 0: disabled, 1: enabled.
        :type DomainStatus: int
        :param _DomainType: Filter by domain name type. 0: push. 1: playback
        :type DomainType: int
        :param _PageSize: Number of entries per page. Value range: 10-100. Default value: 10.
        :type PageSize: int
        :param _PageNum: Page number to get. Value range: 1-100000. Default value: 1.
        :type PageNum: int
        :param _IsDelayLive: 0: LVB, 1: LCB. Default value: 0.
        :type IsDelayLive: int
        :param _DomainPrefix: Domain name prefix.
        :type DomainPrefix: str
        :param _PlayType: Playback region. This parameter is valid only when `DomainType` is set to `1`.
`1`: Chinese mainland
`2`: global
`3`: outside Chinese mainland
        :type PlayType: int
        """
        self._DomainStatus = None
        self._DomainType = None
        self._PageSize = None
        self._PageNum = None
        self._IsDelayLive = None
        self._DomainPrefix = None
        self._PlayType = None

    @property
    def DomainStatus(self):
        return self._DomainStatus

    @DomainStatus.setter
    def DomainStatus(self, DomainStatus):
        self._DomainStatus = DomainStatus

    @property
    def DomainType(self):
        return self._DomainType

    @DomainType.setter
    def DomainType(self, DomainType):
        self._DomainType = DomainType

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def IsDelayLive(self):
        return self._IsDelayLive

    @IsDelayLive.setter
    def IsDelayLive(self, IsDelayLive):
        self._IsDelayLive = IsDelayLive

    @property
    def DomainPrefix(self):
        return self._DomainPrefix

    @DomainPrefix.setter
    def DomainPrefix(self, DomainPrefix):
        self._DomainPrefix = DomainPrefix

    @property
    def PlayType(self):
        return self._PlayType

    @PlayType.setter
    def PlayType(self, PlayType):
        self._PlayType = PlayType


    def _deserialize(self, params):
        self._DomainStatus = params.get("DomainStatus")
        self._DomainType = params.get("DomainType")
        self._PageSize = params.get("PageSize")
        self._PageNum = params.get("PageNum")
        self._IsDelayLive = params.get("IsDelayLive")
        self._DomainPrefix = params.get("DomainPrefix")
        self._PlayType = params.get("PlayType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveDomainsResponse(AbstractModel):
    """DescribeLiveDomains response structure.

    """

    def __init__(self):
        r"""
        :param _AllCount: Total number of results.
        :type AllCount: int
        :param _DomainList: List of domain name details.
        :type DomainList: list of DomainInfo
        :param _CreateLimitCount: The number of domain names that can be added
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type CreateLimitCount: int
        :param _PlayTypeCount: The number of domains accelerated in the Chinese mainland, globally, and outside the Chinese mainland respectively.
Note: This field may return null, indicating that no valid values can be obtained.
        :type PlayTypeCount: list of int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._AllCount = None
        self._DomainList = None
        self._CreateLimitCount = None
        self._PlayTypeCount = None
        self._RequestId = None

    @property
    def AllCount(self):
        return self._AllCount

    @AllCount.setter
    def AllCount(self, AllCount):
        self._AllCount = AllCount

    @property
    def DomainList(self):
        return self._DomainList

    @DomainList.setter
    def DomainList(self, DomainList):
        self._DomainList = DomainList

    @property
    def CreateLimitCount(self):
        return self._CreateLimitCount

    @CreateLimitCount.setter
    def CreateLimitCount(self, CreateLimitCount):
        self._CreateLimitCount = CreateLimitCount

    @property
    def PlayTypeCount(self):
        return self._PlayTypeCount

    @PlayTypeCount.setter
    def PlayTypeCount(self, PlayTypeCount):
        self._PlayTypeCount = PlayTypeCount

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._AllCount = params.get("AllCount")
        if params.get("DomainList") is not None:
            self._DomainList = []
            for item in params.get("DomainList"):
                obj = DomainInfo()
                obj._deserialize(item)
                self._DomainList.append(obj)
        self._CreateLimitCount = params.get("CreateLimitCount")
        self._PlayTypeCount = params.get("PlayTypeCount")
        self._RequestId = params.get("RequestId")


class DescribeLiveForbidStreamListRequest(AbstractModel):
    """DescribeLiveForbidStreamList request structure.

    """

    def __init__(self):
        r"""
        :param _PageNum: Page number to get. Default value: 1.
        :type PageNum: int
        :param _PageSize: Number of entries per page. Maximum value: 100. 
Value: any integer between 1 and 100.
Default value: 10.
        :type PageSize: int
        :param _StreamName: Stream name for query
        :type StreamName: str
        """
        self._PageNum = None
        self._PageSize = None
        self._StreamName = None

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName


    def _deserialize(self, params):
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._StreamName = params.get("StreamName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveForbidStreamListResponse(AbstractModel):
    """DescribeLiveForbidStreamList response structure.

    """

    def __init__(self):
        r"""
        :param _TotalNum: Total number of eligible ones.
        :type TotalNum: int
        :param _TotalPage: Total number of pages.
        :type TotalPage: int
        :param _PageNum: Page number.
        :type PageNum: int
        :param _PageSize: Number of entries displayed per page.
        :type PageSize: int
        :param _ForbidStreamList: List of forbidden streams.
        :type ForbidStreamList: list of ForbidStreamInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalNum = None
        self._TotalPage = None
        self._PageNum = None
        self._PageSize = None
        self._ForbidStreamList = None
        self._RequestId = None

    @property
    def TotalNum(self):
        return self._TotalNum

    @TotalNum.setter
    def TotalNum(self, TotalNum):
        self._TotalNum = TotalNum

    @property
    def TotalPage(self):
        return self._TotalPage

    @TotalPage.setter
    def TotalPage(self, TotalPage):
        self._TotalPage = TotalPage

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def ForbidStreamList(self):
        return self._ForbidStreamList

    @ForbidStreamList.setter
    def ForbidStreamList(self, ForbidStreamList):
        self._ForbidStreamList = ForbidStreamList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalNum = params.get("TotalNum")
        self._TotalPage = params.get("TotalPage")
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        if params.get("ForbidStreamList") is not None:
            self._ForbidStreamList = []
            for item in params.get("ForbidStreamList"):
                obj = ForbidStreamInfo()
                obj._deserialize(item)
                self._ForbidStreamList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLivePlayAuthKeyRequest(AbstractModel):
    """DescribeLivePlayAuthKey request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Domain name.
        :type DomainName: str
        """
        self._DomainName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLivePlayAuthKeyResponse(AbstractModel):
    """DescribeLivePlayAuthKey response structure.

    """

    def __init__(self):
        r"""
        :param _PlayAuthKeyInfo: Playback authentication key information.
        :type PlayAuthKeyInfo: :class:`tencentcloud.live.v20180801.models.PlayAuthKeyInfo`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._PlayAuthKeyInfo = None
        self._RequestId = None

    @property
    def PlayAuthKeyInfo(self):
        return self._PlayAuthKeyInfo

    @PlayAuthKeyInfo.setter
    def PlayAuthKeyInfo(self, PlayAuthKeyInfo):
        self._PlayAuthKeyInfo = PlayAuthKeyInfo

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("PlayAuthKeyInfo") is not None:
            self._PlayAuthKeyInfo = PlayAuthKeyInfo()
            self._PlayAuthKeyInfo._deserialize(params.get("PlayAuthKeyInfo"))
        self._RequestId = params.get("RequestId")


class DescribeLivePullStreamTasksRequest(AbstractModel):
    """DescribeLivePullStreamTasks request structure.

    """

    def __init__(self):
        r"""
        :param _TaskId: The task ID. 
A task ID is returned by the `CreateLivePullStreamTask` API.
If you do not pass this parameter, all tasks will be returned, sorted by last updated time in descending order.
        :type TaskId: str
        :param _PageNum: The number of page to start from. Default value: 1.
        :type PageNum: int
        :param _PageSize: The maximum number of records per page. Default value: 10.
Valid values: Any integer between 1 and 20.
        :type PageSize: int
        """
        self._TaskId = None
        self._PageNum = None
        self._PageSize = None

    @property
    def TaskId(self):
        return self._TaskId

    @TaskId.setter
    def TaskId(self, TaskId):
        self._TaskId = TaskId

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize


    def _deserialize(self, params):
        self._TaskId = params.get("TaskId")
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLivePullStreamTasksResponse(AbstractModel):
    """DescribeLivePullStreamTasks response structure.

    """

    def __init__(self):
        r"""
        :param _TaskInfos: The information of stream pulling tasks.
        :type TaskInfos: list of PullStreamTaskInfo
        :param _PageNum: The page number.
        :type PageNum: int
        :param _PageSize: The number of records per page.
        :type PageSize: int
        :param _TotalNum: The total number of records.
        :type TotalNum: int
        :param _TotalPage: The total number of pages.
        :type TotalPage: int
        :param _LimitTaskNum: The maximum number of tasks allowed.
        :type LimitTaskNum: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TaskInfos = None
        self._PageNum = None
        self._PageSize = None
        self._TotalNum = None
        self._TotalPage = None
        self._LimitTaskNum = None
        self._RequestId = None

    @property
    def TaskInfos(self):
        return self._TaskInfos

    @TaskInfos.setter
    def TaskInfos(self, TaskInfos):
        self._TaskInfos = TaskInfos

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def TotalNum(self):
        return self._TotalNum

    @TotalNum.setter
    def TotalNum(self, TotalNum):
        self._TotalNum = TotalNum

    @property
    def TotalPage(self):
        return self._TotalPage

    @TotalPage.setter
    def TotalPage(self, TotalPage):
        self._TotalPage = TotalPage

    @property
    def LimitTaskNum(self):
        return self._LimitTaskNum

    @LimitTaskNum.setter
    def LimitTaskNum(self, LimitTaskNum):
        self._LimitTaskNum = LimitTaskNum

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("TaskInfos") is not None:
            self._TaskInfos = []
            for item in params.get("TaskInfos"):
                obj = PullStreamTaskInfo()
                obj._deserialize(item)
                self._TaskInfos.append(obj)
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._TotalNum = params.get("TotalNum")
        self._TotalPage = params.get("TotalPage")
        self._LimitTaskNum = params.get("LimitTaskNum")
        self._RequestId = params.get("RequestId")


class DescribeLivePushAuthKeyRequest(AbstractModel):
    """DescribeLivePushAuthKey request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Push domain name.
        :type DomainName: str
        """
        self._DomainName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLivePushAuthKeyResponse(AbstractModel):
    """DescribeLivePushAuthKey response structure.

    """

    def __init__(self):
        r"""
        :param _PushAuthKeyInfo: Push authentication key information.
        :type PushAuthKeyInfo: :class:`tencentcloud.live.v20180801.models.PushAuthKeyInfo`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._PushAuthKeyInfo = None
        self._RequestId = None

    @property
    def PushAuthKeyInfo(self):
        return self._PushAuthKeyInfo

    @PushAuthKeyInfo.setter
    def PushAuthKeyInfo(self, PushAuthKeyInfo):
        self._PushAuthKeyInfo = PushAuthKeyInfo

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("PushAuthKeyInfo") is not None:
            self._PushAuthKeyInfo = PushAuthKeyInfo()
            self._PushAuthKeyInfo._deserialize(params.get("PushAuthKeyInfo"))
        self._RequestId = params.get("RequestId")


class DescribeLiveRecordRulesRequest(AbstractModel):
    """DescribeLiveRecordRules request structure.

    """


class DescribeLiveRecordRulesResponse(AbstractModel):
    """DescribeLiveRecordRules response structure.

    """

    def __init__(self):
        r"""
        :param _Rules: List of rules.
        :type Rules: list of RuleInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Rules = None
        self._RequestId = None

    @property
    def Rules(self):
        return self._Rules

    @Rules.setter
    def Rules(self, Rules):
        self._Rules = Rules

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Rules") is not None:
            self._Rules = []
            for item in params.get("Rules"):
                obj = RuleInfo()
                obj._deserialize(item)
                self._Rules.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveRecordTemplateRequest(AbstractModel):
    """DescribeLiveRecordTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID obtained by [DescribeLiveRecordTemplates](https://intl.cloud.tencent.com/document/product/267/32609?from_cn_redirect=1).
        :type TemplateId: int
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
        


class DescribeLiveRecordTemplateResponse(AbstractModel):
    """DescribeLiveRecordTemplate response structure.

    """

    def __init__(self):
        r"""
        :param _Template: Recording template information.
        :type Template: :class:`tencentcloud.live.v20180801.models.RecordTemplateInfo`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Template = None
        self._RequestId = None

    @property
    def Template(self):
        return self._Template

    @Template.setter
    def Template(self, Template):
        self._Template = Template

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Template") is not None:
            self._Template = RecordTemplateInfo()
            self._Template._deserialize(params.get("Template"))
        self._RequestId = params.get("RequestId")


class DescribeLiveRecordTemplatesRequest(AbstractModel):
    """DescribeLiveRecordTemplates request structure.

    """

    def __init__(self):
        r"""
        :param _IsDelayLive: Whether it is an LCB template. Default value: 0.
0: LVB.
1: LCB.
        :type IsDelayLive: int
        """
        self._IsDelayLive = None

    @property
    def IsDelayLive(self):
        return self._IsDelayLive

    @IsDelayLive.setter
    def IsDelayLive(self, IsDelayLive):
        self._IsDelayLive = IsDelayLive


    def _deserialize(self, params):
        self._IsDelayLive = params.get("IsDelayLive")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveRecordTemplatesResponse(AbstractModel):
    """DescribeLiveRecordTemplates response structure.

    """

    def __init__(self):
        r"""
        :param _Templates: Recording template information list.
        :type Templates: list of RecordTemplateInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Templates = None
        self._RequestId = None

    @property
    def Templates(self):
        return self._Templates

    @Templates.setter
    def Templates(self, Templates):
        self._Templates = Templates

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Templates") is not None:
            self._Templates = []
            for item in params.get("Templates"):
                obj = RecordTemplateInfo()
                obj._deserialize(item)
                self._Templates.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveSnapshotRulesRequest(AbstractModel):
    """DescribeLiveSnapshotRules request structure.

    """


class DescribeLiveSnapshotRulesResponse(AbstractModel):
    """DescribeLiveSnapshotRules response structure.

    """

    def __init__(self):
        r"""
        :param _Rules: Rule list.
        :type Rules: list of RuleInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Rules = None
        self._RequestId = None

    @property
    def Rules(self):
        return self._Rules

    @Rules.setter
    def Rules(self, Rules):
        self._Rules = Rules

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Rules") is not None:
            self._Rules = []
            for item in params.get("Rules"):
                obj = RuleInfo()
                obj._deserialize(item)
                self._Rules.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveSnapshotTemplateRequest(AbstractModel):
    """DescribeLiveSnapshotTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
Template ID returned by the [CreateLiveSnapshotTemplate](https://intl.cloud.tencent.com/document/product/267/32624?from_cn_redirect=1) API call.
        :type TemplateId: int
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
        


class DescribeLiveSnapshotTemplateResponse(AbstractModel):
    """DescribeLiveSnapshotTemplate response structure.

    """

    def __init__(self):
        r"""
        :param _Template: Screencapturing template information.
        :type Template: :class:`tencentcloud.live.v20180801.models.SnapshotTemplateInfo`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Template = None
        self._RequestId = None

    @property
    def Template(self):
        return self._Template

    @Template.setter
    def Template(self, Template):
        self._Template = Template

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Template") is not None:
            self._Template = SnapshotTemplateInfo()
            self._Template._deserialize(params.get("Template"))
        self._RequestId = params.get("RequestId")


class DescribeLiveSnapshotTemplatesRequest(AbstractModel):
    """DescribeLiveSnapshotTemplates request structure.

    """


class DescribeLiveSnapshotTemplatesResponse(AbstractModel):
    """DescribeLiveSnapshotTemplates response structure.

    """

    def __init__(self):
        r"""
        :param _Templates: Screencapturing template list.
        :type Templates: list of SnapshotTemplateInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Templates = None
        self._RequestId = None

    @property
    def Templates(self):
        return self._Templates

    @Templates.setter
    def Templates(self, Templates):
        self._Templates = Templates

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Templates") is not None:
            self._Templates = []
            for item in params.get("Templates"):
                obj = SnapshotTemplateInfo()
                obj._deserialize(item)
                self._Templates.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveStreamEventListRequest(AbstractModel):
    """DescribeLiveStreamEventList request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: Start time. 
In UTC format, such as 2018-12-29T19:00:00Z.
This supports querying the history of 60 days.
        :type StartTime: str
        :param _EndTime: End time.
In UTC format, such as 2018-12-29T20:00:00Z.
This cannot be after the current time and cannot be more than 30 days after the start time.
        :type EndTime: str
        :param _AppName: Push path, which is the same as the AppName in push and playback addresses and is "live" by default.
        :type AppName: str
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _StreamName: Stream name; query with wildcard (*) is not supported; fuzzy match by default.
The IsStrict field can be used to change to exact query.
        :type StreamName: str
        :param _PageNum: Page number to get.
Default value: 1.
Note: Currently, query for up to 10,000 entries is supported.
        :type PageNum: int
        :param _PageSize: Number of entries per page.
Maximum value: 100.
Value range: any integer between 1 and 100.
Default value: 10.
Note: currently, query for up to 10,000 entries is supported.
        :type PageSize: int
        :param _IsFilter: Whether to filter. No filtering by default.
0: No filtering at all.
1: Filter out the failing streams and return only the successful ones.
        :type IsFilter: int
        :param _IsStrict: Whether to query exactly. Fuzzy match by default.
0: Fuzzy match.
1: Exact query.
Note: This parameter takes effect when StreamName is used.
        :type IsStrict: int
        :param _IsAsc: Whether to display in ascending order by end time. Descending order by default.
0: Descending.
1: Ascending.
        :type IsAsc: int
        """
        self._StartTime = None
        self._EndTime = None
        self._AppName = None
        self._DomainName = None
        self._StreamName = None
        self._PageNum = None
        self._PageSize = None
        self._IsFilter = None
        self._IsStrict = None
        self._IsAsc = None

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
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def IsFilter(self):
        return self._IsFilter

    @IsFilter.setter
    def IsFilter(self, IsFilter):
        self._IsFilter = IsFilter

    @property
    def IsStrict(self):
        return self._IsStrict

    @IsStrict.setter
    def IsStrict(self, IsStrict):
        self._IsStrict = IsStrict

    @property
    def IsAsc(self):
        return self._IsAsc

    @IsAsc.setter
    def IsAsc(self, IsAsc):
        self._IsAsc = IsAsc


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._AppName = params.get("AppName")
        self._DomainName = params.get("DomainName")
        self._StreamName = params.get("StreamName")
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._IsFilter = params.get("IsFilter")
        self._IsStrict = params.get("IsStrict")
        self._IsAsc = params.get("IsAsc")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveStreamEventListResponse(AbstractModel):
    """DescribeLiveStreamEventList response structure.

    """

    def __init__(self):
        r"""
        :param _EventList: List of streaming events.
        :type EventList: list of StreamEventInfo
        :param _PageNum: Page number.
        :type PageNum: int
        :param _PageSize: Number of entries per page.
        :type PageSize: int
        :param _TotalNum: Total number of eligible ones.
        :type TotalNum: int
        :param _TotalPage: Total number of pages.
        :type TotalPage: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._EventList = None
        self._PageNum = None
        self._PageSize = None
        self._TotalNum = None
        self._TotalPage = None
        self._RequestId = None

    @property
    def EventList(self):
        return self._EventList

    @EventList.setter
    def EventList(self, EventList):
        self._EventList = EventList

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def TotalNum(self):
        return self._TotalNum

    @TotalNum.setter
    def TotalNum(self, TotalNum):
        self._TotalNum = TotalNum

    @property
    def TotalPage(self):
        return self._TotalPage

    @TotalPage.setter
    def TotalPage(self, TotalPage):
        self._TotalPage = TotalPage

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("EventList") is not None:
            self._EventList = []
            for item in params.get("EventList"):
                obj = StreamEventInfo()
                obj._deserialize(item)
                self._EventList.append(obj)
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._TotalNum = params.get("TotalNum")
        self._TotalPage = params.get("TotalPage")
        self._RequestId = params.get("RequestId")


class DescribeLiveStreamOnlineListRequest(AbstractModel):
    """DescribeLiveStreamOnlineList request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Push domain name. If you use multiple paths, enter the `DomainName`.
        :type DomainName: str
        :param _AppName: Push path, which is the same as the `AppName` in push and playback addresses and is `live` by default. If you use multiple paths, enter the `AppName`.
        :type AppName: str
        :param _PageNum: Page number to get. Default value: 1.
        :type PageNum: int
        :param _PageSize: Number of entries per page. Maximum value: 100. 
Value: any integer between 10 and 100.
Default value: 10.
        :type PageSize: int
        :param _StreamName: Stream name, which is used for exact query.
        :type StreamName: str
        """
        self._DomainName = None
        self._AppName = None
        self._PageNum = None
        self._PageSize = None
        self._StreamName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._StreamName = params.get("StreamName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveStreamOnlineListResponse(AbstractModel):
    """DescribeLiveStreamOnlineList response structure.

    """

    def __init__(self):
        r"""
        :param _TotalNum: Total number of eligible ones.
        :type TotalNum: int
        :param _TotalPage: Total number of pages.
        :type TotalPage: int
        :param _PageNum: Page number.
        :type PageNum: int
        :param _PageSize: Number of entries displayed per page.
        :type PageSize: int
        :param _OnlineInfo: Active push information list.
        :type OnlineInfo: list of StreamOnlineInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalNum = None
        self._TotalPage = None
        self._PageNum = None
        self._PageSize = None
        self._OnlineInfo = None
        self._RequestId = None

    @property
    def TotalNum(self):
        return self._TotalNum

    @TotalNum.setter
    def TotalNum(self, TotalNum):
        self._TotalNum = TotalNum

    @property
    def TotalPage(self):
        return self._TotalPage

    @TotalPage.setter
    def TotalPage(self, TotalPage):
        self._TotalPage = TotalPage

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def OnlineInfo(self):
        return self._OnlineInfo

    @OnlineInfo.setter
    def OnlineInfo(self, OnlineInfo):
        self._OnlineInfo = OnlineInfo

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalNum = params.get("TotalNum")
        self._TotalPage = params.get("TotalPage")
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        if params.get("OnlineInfo") is not None:
            self._OnlineInfo = []
            for item in params.get("OnlineInfo"):
                obj = StreamOnlineInfo()
                obj._deserialize(item)
                self._OnlineInfo.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveStreamPublishedListRequest(AbstractModel):
    """DescribeLiveStreamPublishedList request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Your push domain name.
        :type DomainName: str
        :param _EndTime: End time.
In UTC format, such as 2016-06-30T19:00:00Z.
This cannot be after the current time.
Note: The difference between EndTime and StartTime cannot be greater than 30 days.
        :type EndTime: str
        :param _StartTime: Start time. 
In UTC format, such as 2016-06-29T19:00:00Z.
This supports querying data in the past 60 days.
        :type StartTime: str
        :param _AppName: Push path, which is the same as the `AppName` in push and playback addresses and is `live` by default. Fuzzy match is not supported.
        :type AppName: str
        :param _PageNum: Page number to get.
Default value: 1.
        :type PageNum: int
        :param _PageSize: Number of entries per page.
Maximum value: 100
Valid values: integers between 10 and 100
Default value: 10
        :type PageSize: int
        :param _StreamName: Stream name, which supports fuzzy match.
        :type StreamName: str
        """
        self._DomainName = None
        self._EndTime = None
        self._StartTime = None
        self._AppName = None
        self._PageNum = None
        self._PageSize = None
        self._StreamName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def EndTime(self):
        return self._EndTime

    @EndTime.setter
    def EndTime(self, EndTime):
        self._EndTime = EndTime

    @property
    def StartTime(self):
        return self._StartTime

    @StartTime.setter
    def StartTime(self, StartTime):
        self._StartTime = StartTime

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._EndTime = params.get("EndTime")
        self._StartTime = params.get("StartTime")
        self._AppName = params.get("AppName")
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._StreamName = params.get("StreamName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveStreamPublishedListResponse(AbstractModel):
    """DescribeLiveStreamPublishedList response structure.

    """

    def __init__(self):
        r"""
        :param _PublishInfo: Push record information.
        :type PublishInfo: list of StreamName
        :param _PageNum: Page number.
        :type PageNum: int
        :param _PageSize: Number of entries per page
        :type PageSize: int
        :param _TotalNum: Total number of eligible ones.
        :type TotalNum: int
        :param _TotalPage: Total number of pages.
        :type TotalPage: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._PublishInfo = None
        self._PageNum = None
        self._PageSize = None
        self._TotalNum = None
        self._TotalPage = None
        self._RequestId = None

    @property
    def PublishInfo(self):
        return self._PublishInfo

    @PublishInfo.setter
    def PublishInfo(self, PublishInfo):
        self._PublishInfo = PublishInfo

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def TotalNum(self):
        return self._TotalNum

    @TotalNum.setter
    def TotalNum(self, TotalNum):
        self._TotalNum = TotalNum

    @property
    def TotalPage(self):
        return self._TotalPage

    @TotalPage.setter
    def TotalPage(self, TotalPage):
        self._TotalPage = TotalPage

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("PublishInfo") is not None:
            self._PublishInfo = []
            for item in params.get("PublishInfo"):
                obj = StreamName()
                obj._deserialize(item)
                self._PublishInfo.append(obj)
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._TotalNum = params.get("TotalNum")
        self._TotalPage = params.get("TotalPage")
        self._RequestId = params.get("RequestId")


class DescribeLiveStreamPushInfoListRequest(AbstractModel):
    """DescribeLiveStreamPushInfoList request structure.

    """

    def __init__(self):
        r"""
        :param _PushDomain: Push domain name.
        :type PushDomain: str
        :param _AppName: Push path, which is the same as the `AppName` in push and playback addresses and is `live` by default.
        :type AppName: str
        :param _PageNum: Number of pages,
Value range: [1,10000],
Default value: 1.
        :type PageNum: int
        :param _PageSize: Number of entries per page,
Value range: [1,1000],
Default value: 200.
        :type PageSize: int
        """
        self._PushDomain = None
        self._AppName = None
        self._PageNum = None
        self._PageSize = None

    @property
    def PushDomain(self):
        return self._PushDomain

    @PushDomain.setter
    def PushDomain(self, PushDomain):
        self._PushDomain = PushDomain

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize


    def _deserialize(self, params):
        self._PushDomain = params.get("PushDomain")
        self._AppName = params.get("AppName")
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveStreamPushInfoListResponse(AbstractModel):
    """DescribeLiveStreamPushInfoList response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: Live stream statistics list.
        :type DataInfoList: list of PushDataInfo
        :param _TotalNum: Total number of live streams.
        :type TotalNum: int
        :param _TotalPage: Total number of pages.
        :type TotalPage: int
        :param _PageNum: Page number where the current data resides.
        :type PageNum: int
        :param _PageSize: Number of live streams per page.
        :type PageSize: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._TotalNum = None
        self._TotalPage = None
        self._PageNum = None
        self._PageSize = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def TotalNum(self):
        return self._TotalNum

    @TotalNum.setter
    def TotalNum(self, TotalNum):
        self._TotalNum = TotalNum

    @property
    def TotalPage(self):
        return self._TotalPage

    @TotalPage.setter
    def TotalPage(self, TotalPage):
        self._TotalPage = TotalPage

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = PushDataInfo()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._TotalNum = params.get("TotalNum")
        self._TotalPage = params.get("TotalPage")
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._RequestId = params.get("RequestId")


class DescribeLiveStreamStateRequest(AbstractModel):
    """DescribeLiveStreamState request structure.

    """

    def __init__(self):
        r"""
        :param _AppName: Push path, which is the same as the AppName in push and playback addresses and is "live" by default.
        :type AppName: str
        :param _DomainName: Your push domain name.
        :type DomainName: str
        :param _StreamName: Stream name.
        :type StreamName: str
        """
        self._AppName = None
        self._DomainName = None
        self._StreamName = None

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName


    def _deserialize(self, params):
        self._AppName = params.get("AppName")
        self._DomainName = params.get("DomainName")
        self._StreamName = params.get("StreamName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveStreamStateResponse(AbstractModel):
    """DescribeLiveStreamState response structure.

    """

    def __init__(self):
        r"""
        :param _StreamState: Stream status,
active: active
inactive: Inactive
forbid: forbidden.
        :type StreamState: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._StreamState = None
        self._RequestId = None

    @property
    def StreamState(self):
        return self._StreamState

    @StreamState.setter
    def StreamState(self, StreamState):
        self._StreamState = StreamState

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._StreamState = params.get("StreamState")
        self._RequestId = params.get("RequestId")


class DescribeLiveTimeShiftBillInfoListRequest(AbstractModel):
    """DescribeLiveTimeShiftBillInfoList request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time for query. You can query data from the past three months. The longest time period that can be queried is one month.

It must be in UTC format.
Example: 2019-01-08T10:00:00Z.
Note: Beijing time is 8 hours ahead of UTC. The [ISO 8601 format](https://intl.cloud.tencent.com/document/product/266/11732#iso-date-format) is used.
        :type StartTime: str
        :param _EndTime: The end time for query. You can query data from the past three months. The longest time period that can be queried is one month.

It must be in UTC format.
Example: 2019-01-08T10:00:00Z.
Note: Beijing time is 8 hours ahead of UTC. The [ISO 8601 format](https://intl.cloud.tencent.com/document/product/266/11732#iso-date-format) is used.
        :type EndTime: str
        :param _PushDomains: The push domains to query. If you leave this empty, the time shifting billing data of all push domains will be returned.
        :type PushDomains: list of str
        """
        self._StartTime = None
        self._EndTime = None
        self._PushDomains = None

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
    def PushDomains(self):
        return self._PushDomains

    @PushDomains.setter
    def PushDomains(self, PushDomains):
        self._PushDomains = PushDomains


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._PushDomains = params.get("PushDomains")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveTimeShiftBillInfoListResponse(AbstractModel):
    """DescribeLiveTimeShiftBillInfoList response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: The time shifting billing data.
        :type DataInfoList: list of TimeShiftBillData
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = TimeShiftBillData()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveTimeShiftRulesRequest(AbstractModel):
    """DescribeLiveTimeShiftRules request structure.

    """


class DescribeLiveTimeShiftRulesResponse(AbstractModel):
    """DescribeLiveTimeShiftRules response structure.

    """

    def __init__(self):
        r"""
        :param _Rules: The information of the rules.
        :type Rules: list of RuleInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Rules = None
        self._RequestId = None

    @property
    def Rules(self):
        return self._Rules

    @Rules.setter
    def Rules(self, Rules):
        self._Rules = Rules

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Rules") is not None:
            self._Rules = []
            for item in params.get("Rules"):
                obj = RuleInfo()
                obj._deserialize(item)
                self._Rules.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveTimeShiftTemplatesRequest(AbstractModel):
    """DescribeLiveTimeShiftTemplates request structure.

    """


class DescribeLiveTimeShiftTemplatesResponse(AbstractModel):
    """DescribeLiveTimeShiftTemplates response structure.

    """

    def __init__(self):
        r"""
        :param _Templates: The information of the templates.
        :type Templates: list of TimeShiftTemplate
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Templates = None
        self._RequestId = None

    @property
    def Templates(self):
        return self._Templates

    @Templates.setter
    def Templates(self, Templates):
        self._Templates = Templates

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Templates") is not None:
            self._Templates = []
            for item in params.get("Templates"):
                obj = TimeShiftTemplate()
                obj._deserialize(item)
                self._Templates.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveTranscodeDetailInfoRequest(AbstractModel):
    """DescribeLiveTranscodeDetailInfo request structure.

    """

    def __init__(self):
        r"""
        :param _PushDomain: Push domain name.
        :type PushDomain: str
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _DayTime: Query date (UTC+8)
Format: yyyymmdd
Note: you can query the statistics for a day in the past three months, with yesterday as the latest date allowed.
        :type DayTime: str
        :param _PageNum: Number of pages. Default value: 1.
Up to 100 pages.
        :type PageNum: int
        :param _PageSize: Number of entries per page. Default value: 20,
Value range: [10,1000].
        :type PageSize: int
        :param _StartDayTime: Start date (UTC+8)
Format: yyyymmdd
Note: details for the last three months can be queried.
        :type StartDayTime: str
        :param _EndDayTime: End date (UTC+8)
Format: yyyymmdd
Note: you can query the statistics for a period in the past three months, with yesterday as the latest date allowed. You must specify either `DayTime`, or `StartDayTime` and `EndDayTime`. If you specify all three parameters, only `DayTime` will be applied.
        :type EndDayTime: str
        """
        self._PushDomain = None
        self._StreamName = None
        self._DayTime = None
        self._PageNum = None
        self._PageSize = None
        self._StartDayTime = None
        self._EndDayTime = None

    @property
    def PushDomain(self):
        return self._PushDomain

    @PushDomain.setter
    def PushDomain(self, PushDomain):
        self._PushDomain = PushDomain

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def DayTime(self):
        return self._DayTime

    @DayTime.setter
    def DayTime(self, DayTime):
        self._DayTime = DayTime

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def StartDayTime(self):
        return self._StartDayTime

    @StartDayTime.setter
    def StartDayTime(self, StartDayTime):
        self._StartDayTime = StartDayTime

    @property
    def EndDayTime(self):
        return self._EndDayTime

    @EndDayTime.setter
    def EndDayTime(self, EndDayTime):
        self._EndDayTime = EndDayTime


    def _deserialize(self, params):
        self._PushDomain = params.get("PushDomain")
        self._StreamName = params.get("StreamName")
        self._DayTime = params.get("DayTime")
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._StartDayTime = params.get("StartDayTime")
        self._EndDayTime = params.get("EndDayTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveTranscodeDetailInfoResponse(AbstractModel):
    """DescribeLiveTranscodeDetailInfo response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: Statistics list.
        :type DataInfoList: list of TranscodeDetailInfo
        :param _PageNum: Page number.
        :type PageNum: int
        :param _PageSize: Number of entries per page.
        :type PageSize: int
        :param _TotalNum: Total number.
        :type TotalNum: int
        :param _TotalPage: Total number of pages.
        :type TotalPage: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._PageNum = None
        self._PageSize = None
        self._TotalNum = None
        self._TotalPage = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def TotalNum(self):
        return self._TotalNum

    @TotalNum.setter
    def TotalNum(self, TotalNum):
        self._TotalNum = TotalNum

    @property
    def TotalPage(self):
        return self._TotalPage

    @TotalPage.setter
    def TotalPage(self, TotalPage):
        self._TotalPage = TotalPage

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = TranscodeDetailInfo()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._TotalNum = params.get("TotalNum")
        self._TotalPage = params.get("TotalPage")
        self._RequestId = params.get("RequestId")


class DescribeLiveTranscodeRulesRequest(AbstractModel):
    """DescribeLiveTranscodeRules request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateIds: An array of template IDs to be filtered.
        :type TemplateIds: list of int
        :param _DomainNames: An array of domain names to be filtered.
        :type DomainNames: list of str
        """
        self._TemplateIds = None
        self._DomainNames = None

    @property
    def TemplateIds(self):
        return self._TemplateIds

    @TemplateIds.setter
    def TemplateIds(self, TemplateIds):
        self._TemplateIds = TemplateIds

    @property
    def DomainNames(self):
        return self._DomainNames

    @DomainNames.setter
    def DomainNames(self, DomainNames):
        self._DomainNames = DomainNames


    def _deserialize(self, params):
        self._TemplateIds = params.get("TemplateIds")
        self._DomainNames = params.get("DomainNames")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveTranscodeRulesResponse(AbstractModel):
    """DescribeLiveTranscodeRules response structure.

    """

    def __init__(self):
        r"""
        :param _Rules: List of transcoding rules.
        :type Rules: list of RuleInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Rules = None
        self._RequestId = None

    @property
    def Rules(self):
        return self._Rules

    @Rules.setter
    def Rules(self, Rules):
        self._Rules = Rules

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Rules") is not None:
            self._Rules = []
            for item in params.get("Rules"):
                obj = RuleInfo()
                obj._deserialize(item)
                self._Rules.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveTranscodeTemplateRequest(AbstractModel):
    """DescribeLiveTranscodeTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
Note: get the template ID in the returned value of the [CreateLiveTranscodeTemplate](https://intl.cloud.tencent.com/document/product/267/32646?from_cn_redirect=1) API call.
        :type TemplateId: int
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
        


class DescribeLiveTranscodeTemplateResponse(AbstractModel):
    """DescribeLiveTranscodeTemplate response structure.

    """

    def __init__(self):
        r"""
        :param _Template: Template information.
        :type Template: :class:`tencentcloud.live.v20180801.models.TemplateInfo`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Template = None
        self._RequestId = None

    @property
    def Template(self):
        return self._Template

    @Template.setter
    def Template(self, Template):
        self._Template = Template

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Template") is not None:
            self._Template = TemplateInfo()
            self._Template._deserialize(params.get("Template"))
        self._RequestId = params.get("RequestId")


class DescribeLiveTranscodeTemplatesRequest(AbstractModel):
    """DescribeLiveTranscodeTemplates request structure.

    """


class DescribeLiveTranscodeTemplatesResponse(AbstractModel):
    """DescribeLiveTranscodeTemplates response structure.

    """

    def __init__(self):
        r"""
        :param _Templates: List of transcoding templates.
        :type Templates: list of TemplateInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Templates = None
        self._RequestId = None

    @property
    def Templates(self):
        return self._Templates

    @Templates.setter
    def Templates(self, Templates):
        self._Templates = Templates

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Templates") is not None:
            self._Templates = []
            for item in params.get("Templates"):
                obj = TemplateInfo()
                obj._deserialize(item)
                self._Templates.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveTranscodeTotalInfoRequest(AbstractModel):
    """DescribeLiveTranscodeTotalInfo request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time of the request, supports data query for the last three months, the gap between the start time and the end time cannot exceed three months. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format, for details, see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type StartTime: str
        :param _EndTime: The end time of the request, supports data query for the last three months, the gap between the start time and the end time cannot exceed three months. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format,for details,see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type EndTime: str
        :param _PushDomains: List of push domains to query. If this parameter is left empty, the data of all domains is queried.
If this parameter is specified, the data returned will be on an hourly basis.
        :type PushDomains: list of str
        :param _MainlandOrOversea: Valid values:
`Mainland`: queries transcoding data in the Chinese mainland
`Oversea`: queries transcoding data outside the Chinese mainland
By default, the data both in and outside the Chinese mainland is queried.
        :type MainlandOrOversea: str
        """
        self._StartTime = None
        self._EndTime = None
        self._PushDomains = None
        self._MainlandOrOversea = None

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
    def PushDomains(self):
        return self._PushDomains

    @PushDomains.setter
    def PushDomains(self, PushDomains):
        self._PushDomains = PushDomains

    @property
    def MainlandOrOversea(self):
        return self._MainlandOrOversea

    @MainlandOrOversea.setter
    def MainlandOrOversea(self, MainlandOrOversea):
        self._MainlandOrOversea = MainlandOrOversea


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._PushDomains = params.get("PushDomains")
        self._MainlandOrOversea = params.get("MainlandOrOversea")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveTranscodeTotalInfoResponse(AbstractModel):
    """DescribeLiveTranscodeTotalInfo response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: List of transcoding data
Note: This field may return `null`, indicating that no valid value can be found.
        :type DataInfoList: list of TranscodeTotalInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = TranscodeTotalInfo()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveWatermarkRequest(AbstractModel):
    """DescribeLiveWatermark request structure.

    """

    def __init__(self):
        r"""
        :param _WatermarkId: Watermark ID returned by the `DescribeLiveWatermarks` API.
        :type WatermarkId: int
        """
        self._WatermarkId = None

    @property
    def WatermarkId(self):
        return self._WatermarkId

    @WatermarkId.setter
    def WatermarkId(self, WatermarkId):
        self._WatermarkId = WatermarkId


    def _deserialize(self, params):
        self._WatermarkId = params.get("WatermarkId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeLiveWatermarkResponse(AbstractModel):
    """DescribeLiveWatermark response structure.

    """

    def __init__(self):
        r"""
        :param _Watermark: Watermark information.
        :type Watermark: :class:`tencentcloud.live.v20180801.models.WatermarkInfo`
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Watermark = None
        self._RequestId = None

    @property
    def Watermark(self):
        return self._Watermark

    @Watermark.setter
    def Watermark(self, Watermark):
        self._Watermark = Watermark

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Watermark") is not None:
            self._Watermark = WatermarkInfo()
            self._Watermark._deserialize(params.get("Watermark"))
        self._RequestId = params.get("RequestId")


class DescribeLiveWatermarkRulesRequest(AbstractModel):
    """DescribeLiveWatermarkRules request structure.

    """


class DescribeLiveWatermarkRulesResponse(AbstractModel):
    """DescribeLiveWatermarkRules response structure.

    """

    def __init__(self):
        r"""
        :param _Rules: Watermarking rule list.
        :type Rules: list of RuleInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._Rules = None
        self._RequestId = None

    @property
    def Rules(self):
        return self._Rules

    @Rules.setter
    def Rules(self, Rules):
        self._Rules = Rules

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("Rules") is not None:
            self._Rules = []
            for item in params.get("Rules"):
                obj = RuleInfo()
                obj._deserialize(item)
                self._Rules.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeLiveWatermarksRequest(AbstractModel):
    """DescribeLiveWatermarks request structure.

    """


class DescribeLiveWatermarksResponse(AbstractModel):
    """DescribeLiveWatermarks response structure.

    """

    def __init__(self):
        r"""
        :param _TotalNum: Total number of watermarks.
        :type TotalNum: int
        :param _WatermarkList: Watermark information list.
        :type WatermarkList: list of WatermarkInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalNum = None
        self._WatermarkList = None
        self._RequestId = None

    @property
    def TotalNum(self):
        return self._TotalNum

    @TotalNum.setter
    def TotalNum(self, TotalNum):
        self._TotalNum = TotalNum

    @property
    def WatermarkList(self):
        return self._WatermarkList

    @WatermarkList.setter
    def WatermarkList(self, WatermarkList):
        self._WatermarkList = WatermarkList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalNum = params.get("TotalNum")
        if params.get("WatermarkList") is not None:
            self._WatermarkList = []
            for item in params.get("WatermarkList"):
                obj = WatermarkInfo()
                obj._deserialize(item)
                self._WatermarkList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribePlayErrorCodeDetailInfoListRequest(AbstractModel):
    """DescribePlayErrorCodeDetailInfoList request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time of the request, supports data query for the last one day, the gap between the start time and the end time cannot exceed one day. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format, for details, see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type StartTime: str
        :param _EndTime: The end time of the request, supports data query for the last one day, the gap between the start time and the end time cannot exceed one day. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format,for details,see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type EndTime: str
        :param _Granularity: Query granularity:
1: 1-minute granularity.
        :type Granularity: int
        :param _StatType: Yes. Valid values: "4xx", "5xx". Mixed codes in the format of `4xx,5xx` are also supported.
        :type StatType: str
        :param _PlayDomains: Playback domain name list.
        :type PlayDomains: list of str
        :param _MainlandOrOversea: Region. Valid values: Mainland (data for Mainland China), Oversea (data for regions outside Mainland China), China (data for China, including Hong Kong, Macao, and Taiwan), Foreign (data for regions outside China, excluding Hong Kong, Macao, and Taiwan), Global (default). If this parameter is left empty, data for all regions will be queried.
        :type MainlandOrOversea: str
        """
        self._StartTime = None
        self._EndTime = None
        self._Granularity = None
        self._StatType = None
        self._PlayDomains = None
        self._MainlandOrOversea = None

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
    def Granularity(self):
        return self._Granularity

    @Granularity.setter
    def Granularity(self, Granularity):
        self._Granularity = Granularity

    @property
    def StatType(self):
        return self._StatType

    @StatType.setter
    def StatType(self, StatType):
        self._StatType = StatType

    @property
    def PlayDomains(self):
        return self._PlayDomains

    @PlayDomains.setter
    def PlayDomains(self, PlayDomains):
        self._PlayDomains = PlayDomains

    @property
    def MainlandOrOversea(self):
        return self._MainlandOrOversea

    @MainlandOrOversea.setter
    def MainlandOrOversea(self, MainlandOrOversea):
        self._MainlandOrOversea = MainlandOrOversea


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._Granularity = params.get("Granularity")
        self._StatType = params.get("StatType")
        self._PlayDomains = params.get("PlayDomains")
        self._MainlandOrOversea = params.get("MainlandOrOversea")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribePlayErrorCodeDetailInfoListResponse(AbstractModel):
    """DescribePlayErrorCodeDetailInfoList response structure.

    """

    def __init__(self):
        r"""
        :param _HttpCodeList: Statistics list.
        :type HttpCodeList: list of HttpCodeInfo
        :param _StatType: Statistics type.
        :type StatType: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._HttpCodeList = None
        self._StatType = None
        self._RequestId = None

    @property
    def HttpCodeList(self):
        return self._HttpCodeList

    @HttpCodeList.setter
    def HttpCodeList(self, HttpCodeList):
        self._HttpCodeList = HttpCodeList

    @property
    def StatType(self):
        return self._StatType

    @StatType.setter
    def StatType(self, StatType):
        self._StatType = StatType

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("HttpCodeList") is not None:
            self._HttpCodeList = []
            for item in params.get("HttpCodeList"):
                obj = HttpCodeInfo()
                obj._deserialize(item)
                self._HttpCodeList.append(obj)
        self._StatType = params.get("StatType")
        self._RequestId = params.get("RequestId")


class DescribePlayErrorCodeSumInfoListRequest(AbstractModel):
    """DescribePlayErrorCodeSumInfoList request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time of the request, supports data query for the last one day, the gap between the start time and the end time cannot exceed one day. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format, for details, see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type StartTime: str
        :param _EndTime: The end time of the request, supports data query for the last one day, the gap between the start time and the end time cannot exceed one day. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format,for details,see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type EndTime: str
        :param _PlayDomains: Playback domain name list. If this parameter is left empty, full data will be queried.
        :type PlayDomains: list of str
        :param _PageNum: Number of pages. Value range: [1,1000]. Default value: 1.
        :type PageNum: int
        :param _PageSize: Number of entries per page. Value range: [1,1000]. Default value: 20.
        :type PageSize: int
        :param _MainlandOrOversea: Region. Valid values: Mainland (data for Mainland China), Oversea (data for regions outside Mainland China), China (data for China, including Hong Kong, Macao, and Taiwan), Foreign (data for regions outside China, excluding Hong Kong, Macao, and Taiwan), Global (default). If this parameter is left empty, data for all regions will be queried.
        :type MainlandOrOversea: str
        :param _GroupType: Grouping parameter. Valid values: CountryProIsp (default value), Country (country/region). Grouping is made by country/region + district + ISP by default. Currently, districts and ISPs outside Mainland China cannot be recognized.
        :type GroupType: str
        :param _OutLanguage: Language used in the output field. Valid values: Chinese (default), English. Currently, country/region, district, and ISP parameters support multiple languages.
        :type OutLanguage: str
        """
        self._StartTime = None
        self._EndTime = None
        self._PlayDomains = None
        self._PageNum = None
        self._PageSize = None
        self._MainlandOrOversea = None
        self._GroupType = None
        self._OutLanguage = None

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
    def PlayDomains(self):
        return self._PlayDomains

    @PlayDomains.setter
    def PlayDomains(self, PlayDomains):
        self._PlayDomains = PlayDomains

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def MainlandOrOversea(self):
        return self._MainlandOrOversea

    @MainlandOrOversea.setter
    def MainlandOrOversea(self, MainlandOrOversea):
        self._MainlandOrOversea = MainlandOrOversea

    @property
    def GroupType(self):
        return self._GroupType

    @GroupType.setter
    def GroupType(self, GroupType):
        self._GroupType = GroupType

    @property
    def OutLanguage(self):
        return self._OutLanguage

    @OutLanguage.setter
    def OutLanguage(self, OutLanguage):
        self._OutLanguage = OutLanguage


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._PlayDomains = params.get("PlayDomains")
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._MainlandOrOversea = params.get("MainlandOrOversea")
        self._GroupType = params.get("GroupType")
        self._OutLanguage = params.get("OutLanguage")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribePlayErrorCodeSumInfoListResponse(AbstractModel):
    """DescribePlayErrorCodeSumInfoList response structure.

    """

    def __init__(self):
        r"""
        :param _ProIspInfoList: Information of error codes starting with 2, 3, 4, or 5 by district and ISP.
        :type ProIspInfoList: list of ProIspPlayCodeDataInfo
        :param _TotalCodeAll: Total occurrences of all status codes.
        :type TotalCodeAll: int
        :param _TotalCode4xx: Occurrences of 4xx status codes.
        :type TotalCode4xx: int
        :param _TotalCode5xx: Occurrences of 5xx status codes.
        :type TotalCode5xx: int
        :param _TotalCodeList: Total occurrences of each status code.
        :type TotalCodeList: list of PlayCodeTotalInfo
        :param _PageNum: Page number.
        :type PageNum: int
        :param _PageSize: Number of entries per page.
        :type PageSize: int
        :param _TotalPage: Total number of pages.
        :type TotalPage: int
        :param _TotalNum: Total number of results.
        :type TotalNum: int
        :param _TotalCode2xx: Occurrences of 2xx status codes.
        :type TotalCode2xx: int
        :param _TotalCode3xx: Occurrences of 3xx status codes.
        :type TotalCode3xx: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._ProIspInfoList = None
        self._TotalCodeAll = None
        self._TotalCode4xx = None
        self._TotalCode5xx = None
        self._TotalCodeList = None
        self._PageNum = None
        self._PageSize = None
        self._TotalPage = None
        self._TotalNum = None
        self._TotalCode2xx = None
        self._TotalCode3xx = None
        self._RequestId = None

    @property
    def ProIspInfoList(self):
        return self._ProIspInfoList

    @ProIspInfoList.setter
    def ProIspInfoList(self, ProIspInfoList):
        self._ProIspInfoList = ProIspInfoList

    @property
    def TotalCodeAll(self):
        return self._TotalCodeAll

    @TotalCodeAll.setter
    def TotalCodeAll(self, TotalCodeAll):
        self._TotalCodeAll = TotalCodeAll

    @property
    def TotalCode4xx(self):
        return self._TotalCode4xx

    @TotalCode4xx.setter
    def TotalCode4xx(self, TotalCode4xx):
        self._TotalCode4xx = TotalCode4xx

    @property
    def TotalCode5xx(self):
        return self._TotalCode5xx

    @TotalCode5xx.setter
    def TotalCode5xx(self, TotalCode5xx):
        self._TotalCode5xx = TotalCode5xx

    @property
    def TotalCodeList(self):
        return self._TotalCodeList

    @TotalCodeList.setter
    def TotalCodeList(self, TotalCodeList):
        self._TotalCodeList = TotalCodeList

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def TotalPage(self):
        return self._TotalPage

    @TotalPage.setter
    def TotalPage(self, TotalPage):
        self._TotalPage = TotalPage

    @property
    def TotalNum(self):
        return self._TotalNum

    @TotalNum.setter
    def TotalNum(self, TotalNum):
        self._TotalNum = TotalNum

    @property
    def TotalCode2xx(self):
        return self._TotalCode2xx

    @TotalCode2xx.setter
    def TotalCode2xx(self, TotalCode2xx):
        self._TotalCode2xx = TotalCode2xx

    @property
    def TotalCode3xx(self):
        return self._TotalCode3xx

    @TotalCode3xx.setter
    def TotalCode3xx(self, TotalCode3xx):
        self._TotalCode3xx = TotalCode3xx

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("ProIspInfoList") is not None:
            self._ProIspInfoList = []
            for item in params.get("ProIspInfoList"):
                obj = ProIspPlayCodeDataInfo()
                obj._deserialize(item)
                self._ProIspInfoList.append(obj)
        self._TotalCodeAll = params.get("TotalCodeAll")
        self._TotalCode4xx = params.get("TotalCode4xx")
        self._TotalCode5xx = params.get("TotalCode5xx")
        if params.get("TotalCodeList") is not None:
            self._TotalCodeList = []
            for item in params.get("TotalCodeList"):
                obj = PlayCodeTotalInfo()
                obj._deserialize(item)
                self._TotalCodeList.append(obj)
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._TotalPage = params.get("TotalPage")
        self._TotalNum = params.get("TotalNum")
        self._TotalCode2xx = params.get("TotalCode2xx")
        self._TotalCode3xx = params.get("TotalCode3xx")
        self._RequestId = params.get("RequestId")


class DescribeProvinceIspPlayInfoListRequest(AbstractModel):
    """DescribeProvinceIspPlayInfoList request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time of the request, supports data query for the last one day, the gap between the start time and the end time cannot exceed one day. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format, for details, see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type StartTime: str
        :param _EndTime: The end time of the request, supports data query for the last one day, the gap between the start time and the end time cannot exceed one day. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format,for details,see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type EndTime: str
        :param _Granularity: Supported granularities:
1: 1-minute granularity (the query interval should be within 1 day)
        :type Granularity: int
        :param _StatType: Statistical metric type:
"Bandwidth": bandwidth
"FluxPerSecond": average traffic
"Flux": traffic
"Request": number of requests
"Online": number of concurrent connections
        :type StatType: str
        :param _PlayDomains: Playback domain name list.
        :type PlayDomains: list of str
        :param _ProvinceNames: List of the districts to be queried, such as Beijing.
        :type ProvinceNames: list of str
        :param _IspNames: List of the ISPs to be queried, such as China Mobile. If this parameter is left empty, the data of all ISPs will be queried.
        :type IspNames: list of str
        :param _MainlandOrOversea: Region. Valid values: Mainland (data for Mainland China), Oversea (data for regions outside Mainland China), China (data for China, including Hong Kong, Macao, and Taiwan), Foreign (data for regions outside China, excluding Hong Kong, Macao, and Taiwan), Global (default). If this parameter is left empty, data for all regions will be queried.
        :type MainlandOrOversea: str
        :param _IpType: IP type:
"Ipv6": IPv6 data
Data of all IPs will be returned if this parameter is left empty.
        :type IpType: str
        """
        self._StartTime = None
        self._EndTime = None
        self._Granularity = None
        self._StatType = None
        self._PlayDomains = None
        self._ProvinceNames = None
        self._IspNames = None
        self._MainlandOrOversea = None
        self._IpType = None

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
    def Granularity(self):
        return self._Granularity

    @Granularity.setter
    def Granularity(self, Granularity):
        self._Granularity = Granularity

    @property
    def StatType(self):
        return self._StatType

    @StatType.setter
    def StatType(self, StatType):
        self._StatType = StatType

    @property
    def PlayDomains(self):
        return self._PlayDomains

    @PlayDomains.setter
    def PlayDomains(self, PlayDomains):
        self._PlayDomains = PlayDomains

    @property
    def ProvinceNames(self):
        return self._ProvinceNames

    @ProvinceNames.setter
    def ProvinceNames(self, ProvinceNames):
        self._ProvinceNames = ProvinceNames

    @property
    def IspNames(self):
        return self._IspNames

    @IspNames.setter
    def IspNames(self, IspNames):
        self._IspNames = IspNames

    @property
    def MainlandOrOversea(self):
        return self._MainlandOrOversea

    @MainlandOrOversea.setter
    def MainlandOrOversea(self, MainlandOrOversea):
        self._MainlandOrOversea = MainlandOrOversea

    @property
    def IpType(self):
        return self._IpType

    @IpType.setter
    def IpType(self, IpType):
        self._IpType = IpType


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._Granularity = params.get("Granularity")
        self._StatType = params.get("StatType")
        self._PlayDomains = params.get("PlayDomains")
        self._ProvinceNames = params.get("ProvinceNames")
        self._IspNames = params.get("IspNames")
        self._MainlandOrOversea = params.get("MainlandOrOversea")
        self._IpType = params.get("IpType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeProvinceIspPlayInfoListResponse(AbstractModel):
    """DescribeProvinceIspPlayInfoList response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: Playback information list.
        :type DataInfoList: list of PlayStatInfo
        :param _StatType: Statistics type, which is the same as the input parameter.
        :type StatType: str
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._StatType = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def StatType(self):
        return self._StatType

    @StatType.setter
    def StatType(self, StatType):
        self._StatType = StatType

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = PlayStatInfo()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._StatType = params.get("StatType")
        self._RequestId = params.get("RequestId")


class DescribeRecordTaskRequest(AbstractModel):
    """DescribeRecordTask request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time of the tasks to retrieve in Unix timestamp. The time range should not be earlier than 90 days before the current time, and the query span should not exceed one week.
        :type StartTime: int
        :param _EndTime: The end time of the tasks to retrieve in Unix timestamp. The EndTime must be greater than the StartTime. The time range should not be earlier than 90 days before the current time, and the query span should not exceed one week. (Note: the start and end times of the task must be within the query time range).
        :type EndTime: int
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _AppName: Push path.
        :type AppName: str
        :param _ScrollToken: Page token used for batch retrieval: If a single request cannot retrieve all data, the interface will return a ScrollToken. The next request carrying this token will start retrieving from the next record.
        :type ScrollToken: str
        """
        self._StartTime = None
        self._EndTime = None
        self._StreamName = None
        self._DomainName = None
        self._AppName = None
        self._ScrollToken = None

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
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def ScrollToken(self):
        return self._ScrollToken

    @ScrollToken.setter
    def ScrollToken(self, ScrollToken):
        self._ScrollToken = ScrollToken


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._StreamName = params.get("StreamName")
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._ScrollToken = params.get("ScrollToken")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeRecordTaskResponse(AbstractModel):
    """DescribeRecordTask response structure.

    """

    def __init__(self):
        r"""
        :param _ScrollToken: Page token: When the request does not return all data, this field indicates the token of the next record. When this field is empty, it means there is no more data.
        :type ScrollToken: str
        :param _TaskList: List of recording tasks. When this field is empty, it means all data has been returned.
        :type TaskList: list of RecordTask
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._ScrollToken = None
        self._TaskList = None
        self._RequestId = None

    @property
    def ScrollToken(self):
        return self._ScrollToken

    @ScrollToken.setter
    def ScrollToken(self, ScrollToken):
        self._ScrollToken = ScrollToken

    @property
    def TaskList(self):
        return self._TaskList

    @TaskList.setter
    def TaskList(self, TaskList):
        self._TaskList = TaskList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._ScrollToken = params.get("ScrollToken")
        if params.get("TaskList") is not None:
            self._TaskList = []
            for item in params.get("TaskList"):
                obj = RecordTask()
                obj._deserialize(item)
                self._TaskList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeScreenShotSheetNumListRequest(AbstractModel):
    """DescribeScreenShotSheetNumList request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: Start time in UTC time in the format of `yyyy-mm-ddTHH:MM:SSZ`.
        :type StartTime: str
        :param _EndTime: End time in UTC time in the format of `yyyy-mm-ddTHH:MM:SSZ`. Data for the last year can be queried.
        :type EndTime: str
        :param _Zone: Region information. Valid values: Mainland, Oversea. The former is to query data within Mainland China, while the latter outside Mainland China. If this parameter is left empty, data of all regions will be queried.
        :type Zone: str
        :param _PushDomains: Push domain name (data at the domain name level after November 1, 2019 can be queried).
        :type PushDomains: list of str
        :param _Granularity: Data granularity. There is a 1.5-hour delay in data reporting. Valid values: `Minute` (5-minute granularity; query period of up to 31 days); `Day` (1-day granularity based on UTC+8:00; query period of up to 186 days)
        :type Granularity: str
        """
        self._StartTime = None
        self._EndTime = None
        self._Zone = None
        self._PushDomains = None
        self._Granularity = None

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
    def Zone(self):
        return self._Zone

    @Zone.setter
    def Zone(self, Zone):
        self._Zone = Zone

    @property
    def PushDomains(self):
        return self._PushDomains

    @PushDomains.setter
    def PushDomains(self, PushDomains):
        self._PushDomains = PushDomains

    @property
    def Granularity(self):
        return self._Granularity

    @Granularity.setter
    def Granularity(self, Granularity):
        self._Granularity = Granularity


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._Zone = params.get("Zone")
        self._PushDomains = params.get("PushDomains")
        self._Granularity = params.get("Granularity")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeScreenShotSheetNumListResponse(AbstractModel):
    """DescribeScreenShotSheetNumList response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: Data information list.
        :type DataInfoList: list of TimeValue
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = TimeValue()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeStreamDayPlayInfoListRequest(AbstractModel):
    """DescribeStreamDayPlayInfoList request structure.

    """

    def __init__(self):
        r"""
        :param _DayTime: Date in the format of YYYY-mm-dd
Data is available at 3am Beijing Time the next day. You are recommended to query the latest data after this time point. Data in the last 3 months can be queried.
        :type DayTime: str
        :param _PlayDomain: Playback domain name.
        :type PlayDomain: str
        :param _PageNum: Page number. Value range: [1,1000]. Default value: 1.
        :type PageNum: int
        :param _PageSize: Number of entries per page. Value range: [100,1000]. Default value: 1,000.
        :type PageSize: int
        :param _MainlandOrOversea: Valid values:
Mainland: query data for Mainland China,
Oversea: query data for regions outside Mainland China,
Default: query data for all regions.
        :type MainlandOrOversea: str
        :param _ServiceName: Service name. Valid values: LVB, LEB. If this parameter is left empty, all data of LVB and LEB will be queried.
        :type ServiceName: str
        """
        self._DayTime = None
        self._PlayDomain = None
        self._PageNum = None
        self._PageSize = None
        self._MainlandOrOversea = None
        self._ServiceName = None

    @property
    def DayTime(self):
        return self._DayTime

    @DayTime.setter
    def DayTime(self, DayTime):
        self._DayTime = DayTime

    @property
    def PlayDomain(self):
        return self._PlayDomain

    @PlayDomain.setter
    def PlayDomain(self, PlayDomain):
        self._PlayDomain = PlayDomain

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def MainlandOrOversea(self):
        return self._MainlandOrOversea

    @MainlandOrOversea.setter
    def MainlandOrOversea(self, MainlandOrOversea):
        self._MainlandOrOversea = MainlandOrOversea

    @property
    def ServiceName(self):
        return self._ServiceName

    @ServiceName.setter
    def ServiceName(self, ServiceName):
        self._ServiceName = ServiceName


    def _deserialize(self, params):
        self._DayTime = params.get("DayTime")
        self._PlayDomain = params.get("PlayDomain")
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._MainlandOrOversea = params.get("MainlandOrOversea")
        self._ServiceName = params.get("ServiceName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeStreamDayPlayInfoListResponse(AbstractModel):
    """DescribeStreamDayPlayInfoList response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: Playback data information list.
        :type DataInfoList: list of PlayDataInfoByStream
        :param _TotalNum: Total number.
        :type TotalNum: int
        :param _TotalPage: Total number of pages.
        :type TotalPage: int
        :param _PageNum: Page number where the current data resides.
        :type PageNum: int
        :param _PageSize: Number of entries per page.
        :type PageSize: int
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._TotalNum = None
        self._TotalPage = None
        self._PageNum = None
        self._PageSize = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def TotalNum(self):
        return self._TotalNum

    @TotalNum.setter
    def TotalNum(self, TotalNum):
        self._TotalNum = TotalNum

    @property
    def TotalPage(self):
        return self._TotalPage

    @TotalPage.setter
    def TotalPage(self, TotalPage):
        self._TotalPage = TotalPage

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = PlayDataInfoByStream()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._TotalNum = params.get("TotalNum")
        self._TotalPage = params.get("TotalPage")
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._RequestId = params.get("RequestId")


class DescribeStreamPlayInfoListRequest(AbstractModel):
    """DescribeStreamPlayInfoList request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time of the request, supports data query for the last one month, the gap between the start time and the end time cannot exceed twenty-four hours. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format, for details, see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type StartTime: str
        :param _EndTime: The end time of the request, supports data query for the last one month, the gap between the start time and the end time cannot exceed twenty-four hours. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format,for details,see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type EndTime: str
        :param _PlayDomain: Playback domain name,
If this parameter is left empty, data of live streams of all playback domain names will be queried.
        :type PlayDomain: str
        :param _StreamName: Stream name (exact match).
If this parameter is left empty, full playback data will be queried.
        :type StreamName: str
        :param _AppName: Push address. Its value is the same as the `AppName` in playback address. It supports exact match, and takes effect only when `StreamName` is passed at the same time.
If it is left empty, the full playback data will be queried.
Note: to query by `AppName`, you need to submit a ticket first. After your application succeeds, it will take about 5 business days (subject to the time in the reply) for the configuration to take effect.
        :type AppName: str
        :param _ServiceName: Service name. Valid values: LVB, LEB. If this parameter is left empty, all data of LVB and LEB will be queried.
        :type ServiceName: str
        """
        self._StartTime = None
        self._EndTime = None
        self._PlayDomain = None
        self._StreamName = None
        self._AppName = None
        self._ServiceName = None

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
    def PlayDomain(self):
        return self._PlayDomain

    @PlayDomain.setter
    def PlayDomain(self, PlayDomain):
        self._PlayDomain = PlayDomain

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def ServiceName(self):
        return self._ServiceName

    @ServiceName.setter
    def ServiceName(self, ServiceName):
        self._ServiceName = ServiceName


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._PlayDomain = params.get("PlayDomain")
        self._StreamName = params.get("StreamName")
        self._AppName = params.get("AppName")
        self._ServiceName = params.get("ServiceName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeStreamPlayInfoListResponse(AbstractModel):
    """DescribeStreamPlayInfoList response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: Statistics list at a 1-minute granularity.
        :type DataInfoList: list of DayStreamPlayInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = DayStreamPlayInfo()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeStreamPushInfoListRequest(AbstractModel):
    """DescribeStreamPushInfoList request structure.

    """

    def __init__(self):
        r"""
        :param _StreamName: The stream name.
        :type StreamName: str
        :param _StartTime: The start time (UTC+8) in the format of “yyyy-mm-dd HH:MM:SS”.
        :type StartTime: str
        :param _EndTime: The end time (UTC+8) in the format of “yyyy-mm-dd HH:MM:SS”. You can query data from the past seven days for a period of preferably not longer than three hours.
        :type EndTime: str
        :param _PushDomain: The push domain.
        :type PushDomain: str
        :param _AppName: The push path, which should be the same as `AppName` in the push and playback URL. The default value is `live`.
        :type AppName: str
        """
        self._StreamName = None
        self._StartTime = None
        self._EndTime = None
        self._PushDomain = None
        self._AppName = None

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

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
    def PushDomain(self):
        return self._PushDomain

    @PushDomain.setter
    def PushDomain(self, PushDomain):
        self._PushDomain = PushDomain

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName


    def _deserialize(self, params):
        self._StreamName = params.get("StreamName")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._PushDomain = params.get("PushDomain")
        self._AppName = params.get("AppName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeStreamPushInfoListResponse(AbstractModel):
    """DescribeStreamPushInfoList response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: Returned data list.
        :type DataInfoList: list of PushQualityData
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = PushQualityData()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeTimeShiftRecordDetailRequest(AbstractModel):
    """DescribeTimeShiftRecordDetail request structure.

    """

    def __init__(self):
        r"""
        :param _Domain: The push domain.
        :type Domain: str
        :param _AppName: The push path.
        :type AppName: str
        :param _StreamName: The stream name.
        :type StreamName: str
        :param _StartTime: The start time, which must be a Unix timestamp.
        :type StartTime: int
        :param _EndTime: The end time, which must be a Unix timestamp. 
        :type EndTime: int
        :param _DomainGroup: The group the push domain belongs to. You don’t need to specify this parameter if the domain doesn’t belong to any group or the group name is an empty string.
        :type DomainGroup: str
        :param _TransCodeId: The transcoding template ID. You don’t need to specify this parameter if the transcoding template ID is `0`.
        :type TransCodeId: int
        """
        self._Domain = None
        self._AppName = None
        self._StreamName = None
        self._StartTime = None
        self._EndTime = None
        self._DomainGroup = None
        self._TransCodeId = None

    @property
    def Domain(self):
        return self._Domain

    @Domain.setter
    def Domain(self, Domain):
        self._Domain = Domain

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

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
    def DomainGroup(self):
        return self._DomainGroup

    @DomainGroup.setter
    def DomainGroup(self, DomainGroup):
        self._DomainGroup = DomainGroup

    @property
    def TransCodeId(self):
        return self._TransCodeId

    @TransCodeId.setter
    def TransCodeId(self, TransCodeId):
        self._TransCodeId = TransCodeId


    def _deserialize(self, params):
        self._Domain = params.get("Domain")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._DomainGroup = params.get("DomainGroup")
        self._TransCodeId = params.get("TransCodeId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeTimeShiftRecordDetailResponse(AbstractModel):
    """DescribeTimeShiftRecordDetail response structure.

    """

    def __init__(self):
        r"""
        :param _RecordList: The number of sessions recorded.
Note: This field may return null, indicating that no valid values can be obtained.
        :type RecordList: list of TimeShiftRecord
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._RecordList = None
        self._RequestId = None

    @property
    def RecordList(self):
        return self._RecordList

    @RecordList.setter
    def RecordList(self, RecordList):
        self._RecordList = RecordList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("RecordList") is not None:
            self._RecordList = []
            for item in params.get("RecordList"):
                obj = TimeShiftRecord()
                obj._deserialize(item)
                self._RecordList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeTimeShiftStreamListRequest(AbstractModel):
    """DescribeTimeShiftStreamList request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time, which must be a Unix timestamp.
        :type StartTime: int
        :param _EndTime: The end time, which must be a Unix timestamp.
        :type EndTime: int
        :param _StreamName: The stream name.
        :type StreamName: str
        :param _Domain: The push domain.
        :type Domain: str
        :param _DomainGroup: The group the push domain belongs to.
        :type DomainGroup: str
        :param _PageSize: The maximum number of records to return. Value range: 0-100. If you do not specify this parameter or pass in `0`, 
the default value `100` will be used. If you pass in a negative number or a value greater than 100, an error will be returned.
        :type PageSize: int
        :param _PageNum: The number of page to pull records from. If you do not specify this parameter, the default value `1` will be used.
        :type PageNum: int
        """
        self._StartTime = None
        self._EndTime = None
        self._StreamName = None
        self._Domain = None
        self._DomainGroup = None
        self._PageSize = None
        self._PageNum = None

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
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def Domain(self):
        return self._Domain

    @Domain.setter
    def Domain(self, Domain):
        self._Domain = Domain

    @property
    def DomainGroup(self):
        return self._DomainGroup

    @DomainGroup.setter
    def DomainGroup(self, DomainGroup):
        self._DomainGroup = DomainGroup

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._StreamName = params.get("StreamName")
        self._Domain = params.get("Domain")
        self._DomainGroup = params.get("DomainGroup")
        self._PageSize = params.get("PageSize")
        self._PageNum = params.get("PageNum")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeTimeShiftStreamListResponse(AbstractModel):
    """DescribeTimeShiftStreamList response structure.

    """

    def __init__(self):
        r"""
        :param _TotalSize: The total number of records in the specified time period.
        :type TotalSize: int
        :param _StreamList: The information of the streams.
Note: This field may return null, indicating that no valid values can be obtained.
        :type StreamList: list of TimeShiftStreamInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._TotalSize = None
        self._StreamList = None
        self._RequestId = None

    @property
    def TotalSize(self):
        return self._TotalSize

    @TotalSize.setter
    def TotalSize(self, TotalSize):
        self._TotalSize = TotalSize

    @property
    def StreamList(self):
        return self._StreamList

    @StreamList.setter
    def StreamList(self, StreamList):
        self._StreamList = StreamList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalSize = params.get("TotalSize")
        if params.get("StreamList") is not None:
            self._StreamList = []
            for item in params.get("StreamList"):
                obj = TimeShiftStreamInfo()
                obj._deserialize(item)
                self._StreamList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeTopClientIpSumInfoListRequest(AbstractModel):
    """DescribeTopClientIpSumInfoList request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time of the request, supports data query for the last one day, the gap between the start time and the end time cannot exceed four hours. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format, for details, see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type StartTime: str
        :param _EndTime: The end time of the request, supports data query for the last one day, the gap between the start time and the end time cannot exceed four hours. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format,for details,see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type EndTime: str
        :param _PlayDomains: Playback domain name. If this parameter is left empty, full data will be queried by default.
        :type PlayDomains: list of str
        :param _PageNum: Page number. Value range: [1,1000]. Default value: 1.
        :type PageNum: int
        :param _PageSize: Number of entries per page. Value range: [1,1000]. Default value: 20.
        :type PageSize: int
        :param _OrderParam: Sorting metric. Valid values: TotalRequest (default value), FailedRequest, TotalFlux.
        :type OrderParam: str
        :param _MainlandOrOversea: Region. Valid values: Mainland (data for Mainland China), Oversea (data for regions outside Mainland China), China (data for China, including Hong Kong, Macao, and Taiwan), Foreign (data for regions outside China, excluding Hong Kong, Macao, and Taiwan), Global (default). If this parameter is left empty, data for all regions will be queried.
        :type MainlandOrOversea: str
        :param _OutLanguage: Language used in the output field. Valid values: Chinese (default), English. Currently, country/region, district, and ISP parameters support multiple languages.
        :type OutLanguage: str
        """
        self._StartTime = None
        self._EndTime = None
        self._PlayDomains = None
        self._PageNum = None
        self._PageSize = None
        self._OrderParam = None
        self._MainlandOrOversea = None
        self._OutLanguage = None

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
    def PlayDomains(self):
        return self._PlayDomains

    @PlayDomains.setter
    def PlayDomains(self, PlayDomains):
        self._PlayDomains = PlayDomains

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def OrderParam(self):
        return self._OrderParam

    @OrderParam.setter
    def OrderParam(self, OrderParam):
        self._OrderParam = OrderParam

    @property
    def MainlandOrOversea(self):
        return self._MainlandOrOversea

    @MainlandOrOversea.setter
    def MainlandOrOversea(self, MainlandOrOversea):
        self._MainlandOrOversea = MainlandOrOversea

    @property
    def OutLanguage(self):
        return self._OutLanguage

    @OutLanguage.setter
    def OutLanguage(self, OutLanguage):
        self._OutLanguage = OutLanguage


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._PlayDomains = params.get("PlayDomains")
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._OrderParam = params.get("OrderParam")
        self._MainlandOrOversea = params.get("MainlandOrOversea")
        self._OutLanguage = params.get("OutLanguage")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeTopClientIpSumInfoListResponse(AbstractModel):
    """DescribeTopClientIpSumInfoList response structure.

    """

    def __init__(self):
        r"""
        :param _PageNum: Page number. Value range: [1,1000]. Default value: 1.
        :type PageNum: int
        :param _PageSize: Number of entries per page. Value range: [1,1000]. Default value: 20.
        :type PageSize: int
        :param _OrderParam: Sorting metric. Valid values: "TotalRequest", "FailedRequest", "TotalFlux".
        :type OrderParam: str
        :param _TotalNum: Total number of results.
        :type TotalNum: int
        :param _TotalPage: Total number of result pages.
        :type TotalPage: int
        :param _DataInfoList: Data content.
        :type DataInfoList: list of ClientIpPlaySumInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._PageNum = None
        self._PageSize = None
        self._OrderParam = None
        self._TotalNum = None
        self._TotalPage = None
        self._DataInfoList = None
        self._RequestId = None

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def OrderParam(self):
        return self._OrderParam

    @OrderParam.setter
    def OrderParam(self, OrderParam):
        self._OrderParam = OrderParam

    @property
    def TotalNum(self):
        return self._TotalNum

    @TotalNum.setter
    def TotalNum(self, TotalNum):
        self._TotalNum = TotalNum

    @property
    def TotalPage(self):
        return self._TotalPage

    @TotalPage.setter
    def TotalPage(self, TotalPage):
        self._TotalPage = TotalPage

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._OrderParam = params.get("OrderParam")
        self._TotalNum = params.get("TotalNum")
        self._TotalPage = params.get("TotalPage")
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = ClientIpPlaySumInfo()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeTranscodeTaskNumRequest(AbstractModel):
    """DescribeTranscodeTaskNum request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time of the request, supports data query for the last forty days, the gap between the start time and the end time cannot exceed one day. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format, for details, see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type StartTime: str
        :param _EndTime: The end time of the request, supports data query for the last forty days, the gap between the start time and the end time cannot exceed one day. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format,for details,see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type EndTime: str
        :param _PushDomains: The push domains to query. If you do not pass a value, all push domains will be queried.
        :type PushDomains: list of str
        """
        self._StartTime = None
        self._EndTime = None
        self._PushDomains = None

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
    def PushDomains(self):
        return self._PushDomains

    @PushDomains.setter
    def PushDomains(self, PushDomains):
        self._PushDomains = PushDomains


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._PushDomains = params.get("PushDomains")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeTranscodeTaskNumResponse(AbstractModel):
    """DescribeTranscodeTaskNum response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: The number of tasks.
        :type DataInfoList: list of TranscodeTaskNum
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = TranscodeTaskNum()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeUploadStreamNumsRequest(AbstractModel):
    """DescribeUploadStreamNums request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: The start time of the request, supports data query for the last one month, the gap between the start time and the end time cannot exceed one month. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format, for details, see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type StartTime: str
        :param _EndTime: The end time of the request, supports data query for the last one month, the gap between the start time and the end time cannot exceed one month. Interface request supports two time formats:
1) YYYY-MM-DDThh:mm:ssZ: ISO time format,for details,see [ISO Date Format Description](https://cloud.tencent.com/document/product/267/38543#:~:text=I- ,ISO,-%E6%97%A5%E6%9C%9F%E6%A0%BC%E5%BC%8F)
2) YYYY-MM-DD hh:mm:ss: When using this format, it represents Beijing time by default.
        :type EndTime: str
        :param _Domains: LVB domain names. If this parameter is left empty, data of all domain names will be queried.
        :type Domains: list of str
        :param _Granularity: Time granularity of the data. Valid values:
5: 5-minute granularity (the query period is up to 1 day)
1440: 1-day granularity (the query period is up to 1 month)
Default value: 5
        :type Granularity: int
        """
        self._StartTime = None
        self._EndTime = None
        self._Domains = None
        self._Granularity = None

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
    def Domains(self):
        return self._Domains

    @Domains.setter
    def Domains(self, Domains):
        self._Domains = Domains

    @property
    def Granularity(self):
        return self._Granularity

    @Granularity.setter
    def Granularity(self, Granularity):
        self._Granularity = Granularity


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._Domains = params.get("Domains")
        self._Granularity = params.get("Granularity")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeUploadStreamNumsResponse(AbstractModel):
    """DescribeUploadStreamNums response structure.

    """

    def __init__(self):
        r"""
        :param _DataInfoList: Detailed data.
        :type DataInfoList: list of ConcurrentRecordStreamNum
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._DataInfoList = None
        self._RequestId = None

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = ConcurrentRecordStreamNum()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeVisitTopSumInfoListRequest(AbstractModel):
    """DescribeVisitTopSumInfoList request structure.

    """

    def __init__(self):
        r"""
        :param _StartTime: Start point in time in the format of `yyyy-mm-dd HH:MM:SS`.
        :type StartTime: str
        :param _EndTime: End point in time in the format of `yyyy-mm-dd HH:MM:SS`
The time span is (0,4 hours]. Data for the last day can be queried.
        :type EndTime: str
        :param _TopIndex: Bandwidth metric. Valid values: "Domain", "StreamId".
        :type TopIndex: str
        :param _PlayDomains: Playback domain name. If this parameter is left empty, full data will be queried by default.
        :type PlayDomains: list of str
        :param _PageNum: Page number,
Value range: [1,1000],
Default value: 1.
        :type PageNum: int
        :param _PageSize: Number of entries per page. Value range: [1,1000].
Default value: 20.
        :type PageSize: int
        :param _OrderParam: Sorting metric. Valid values: "AvgFluxPerSecond", "TotalRequest" (default), "TotalFlux".
        :type OrderParam: str
        """
        self._StartTime = None
        self._EndTime = None
        self._TopIndex = None
        self._PlayDomains = None
        self._PageNum = None
        self._PageSize = None
        self._OrderParam = None

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
    def TopIndex(self):
        return self._TopIndex

    @TopIndex.setter
    def TopIndex(self, TopIndex):
        self._TopIndex = TopIndex

    @property
    def PlayDomains(self):
        return self._PlayDomains

    @PlayDomains.setter
    def PlayDomains(self, PlayDomains):
        self._PlayDomains = PlayDomains

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def OrderParam(self):
        return self._OrderParam

    @OrderParam.setter
    def OrderParam(self, OrderParam):
        self._OrderParam = OrderParam


    def _deserialize(self, params):
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._TopIndex = params.get("TopIndex")
        self._PlayDomains = params.get("PlayDomains")
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._OrderParam = params.get("OrderParam")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeVisitTopSumInfoListResponse(AbstractModel):
    """DescribeVisitTopSumInfoList response structure.

    """

    def __init__(self):
        r"""
        :param _PageNum: Page number,
Value range: [1,1000],
Default value: 1.
        :type PageNum: int
        :param _PageSize: Number of entries per page. Value range: [1,1000].
Default value: 20.
        :type PageSize: int
        :param _TopIndex: Bandwidth metric. Valid values: "Domain", "StreamId".
        :type TopIndex: str
        :param _OrderParam: Sorting metric. Valid values: AvgFluxPerSecond (sort by average traffic per second), TotalRequest (sort by total requests), TotalFlux (sort by total traffic). Default value: TotalRequest.
        :type OrderParam: str
        :param _TotalNum: Total number of results.
        :type TotalNum: int
        :param _TotalPage: Total number of result pages.
        :type TotalPage: int
        :param _DataInfoList: Data content.
        :type DataInfoList: list of PlaySumStatInfo
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._PageNum = None
        self._PageSize = None
        self._TopIndex = None
        self._OrderParam = None
        self._TotalNum = None
        self._TotalPage = None
        self._DataInfoList = None
        self._RequestId = None

    @property
    def PageNum(self):
        return self._PageNum

    @PageNum.setter
    def PageNum(self, PageNum):
        self._PageNum = PageNum

    @property
    def PageSize(self):
        return self._PageSize

    @PageSize.setter
    def PageSize(self, PageSize):
        self._PageSize = PageSize

    @property
    def TopIndex(self):
        return self._TopIndex

    @TopIndex.setter
    def TopIndex(self, TopIndex):
        self._TopIndex = TopIndex

    @property
    def OrderParam(self):
        return self._OrderParam

    @OrderParam.setter
    def OrderParam(self, OrderParam):
        self._OrderParam = OrderParam

    @property
    def TotalNum(self):
        return self._TotalNum

    @TotalNum.setter
    def TotalNum(self, TotalNum):
        self._TotalNum = TotalNum

    @property
    def TotalPage(self):
        return self._TotalPage

    @TotalPage.setter
    def TotalPage(self, TotalPage):
        self._TotalPage = TotalPage

    @property
    def DataInfoList(self):
        return self._DataInfoList

    @DataInfoList.setter
    def DataInfoList(self, DataInfoList):
        self._DataInfoList = DataInfoList

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._PageNum = params.get("PageNum")
        self._PageSize = params.get("PageSize")
        self._TopIndex = params.get("TopIndex")
        self._OrderParam = params.get("OrderParam")
        self._TotalNum = params.get("TotalNum")
        self._TotalPage = params.get("TotalPage")
        if params.get("DataInfoList") is not None:
            self._DataInfoList = []
            for item in params.get("DataInfoList"):
                obj = PlaySumStatInfo()
                obj._deserialize(item)
                self._DataInfoList.append(obj)
        self._RequestId = params.get("RequestId")


class DomainCertInfo(AbstractModel):
    """Domain name certificate information

    """

    def __init__(self):
        r"""
        :param _CertId: Certificate ID.
        :type CertId: int
        :param _CertName: Certificate name.
        :type CertName: str
        :param _Description: Description.
        :type Description: str
        :param _CreateTime: The creation time in UTC format.
Note: Beijing time (UTC+8) is used.
        :type CreateTime: str
        :param _HttpsCrt: Certificate content.
        :type HttpsCrt: str
        :param _CertType: Certificate type.
0: user-added certificate
1: Tencent Cloud-hosted certificate.
        :type CertType: int
        :param _CertExpireTime: The certificate expiration time in UTC format.
Note: Beijing time (UTC+8) is used.
        :type CertExpireTime: str
        :param _DomainName: Domain name that uses this certificate.
        :type DomainName: str
        :param _Status: Certificate status.
        :type Status: int
        :param _CertDomains: List of domain names in the certificate.
["*.x.com"] for example.
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type CertDomains: list of str
        :param _CloudCertId: Tencent Cloud SSL certificate ID.
Note: this field may return `null`, indicating that no valid values can be obtained.
        :type CloudCertId: str
        """
        self._CertId = None
        self._CertName = None
        self._Description = None
        self._CreateTime = None
        self._HttpsCrt = None
        self._CertType = None
        self._CertExpireTime = None
        self._DomainName = None
        self._Status = None
        self._CertDomains = None
        self._CloudCertId = None

    @property
    def CertId(self):
        return self._CertId

    @CertId.setter
    def CertId(self, CertId):
        self._CertId = CertId

    @property
    def CertName(self):
        return self._CertName

    @CertName.setter
    def CertName(self, CertName):
        self._CertName = CertName

    @property
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def CreateTime(self):
        return self._CreateTime

    @CreateTime.setter
    def CreateTime(self, CreateTime):
        self._CreateTime = CreateTime

    @property
    def HttpsCrt(self):
        return self._HttpsCrt

    @HttpsCrt.setter
    def HttpsCrt(self, HttpsCrt):
        self._HttpsCrt = HttpsCrt

    @property
    def CertType(self):
        return self._CertType

    @CertType.setter
    def CertType(self, CertType):
        self._CertType = CertType

    @property
    def CertExpireTime(self):
        return self._CertExpireTime

    @CertExpireTime.setter
    def CertExpireTime(self, CertExpireTime):
        self._CertExpireTime = CertExpireTime

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status

    @property
    def CertDomains(self):
        return self._CertDomains

    @CertDomains.setter
    def CertDomains(self, CertDomains):
        self._CertDomains = CertDomains

    @property
    def CloudCertId(self):
        return self._CloudCertId

    @CloudCertId.setter
    def CloudCertId(self, CloudCertId):
        self._CloudCertId = CloudCertId


    def _deserialize(self, params):
        self._CertId = params.get("CertId")
        self._CertName = params.get("CertName")
        self._Description = params.get("Description")
        self._CreateTime = params.get("CreateTime")
        self._HttpsCrt = params.get("HttpsCrt")
        self._CertType = params.get("CertType")
        self._CertExpireTime = params.get("CertExpireTime")
        self._DomainName = params.get("DomainName")
        self._Status = params.get("Status")
        self._CertDomains = params.get("CertDomains")
        self._CloudCertId = params.get("CloudCertId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DomainInfo(AbstractModel):
    """LVB domain name information

    """

    def __init__(self):
        r"""
        :param _Name: LVB domain name.
        :type Name: str
        :param _Type: Domain name type:
0: push.
1: playback.
        :type Type: int
        :param _Status: Domain name status:
0: deactivated.
1: activated.
        :type Status: int
        :param _CreateTime: The time when the domain was added.
Note: Beijing time (UTC+8) is used.
        :type CreateTime: str
        :param _BCName: Whether there is a CNAME record pointing to a fixed rule domain name:
0: no.
1: yes.
        :type BCName: int
        :param _TargetDomain: Domain name corresponding to CNAME record.
        :type TargetDomain: str
        :param _PlayType: Playback region. This parameter is valid only if `Type` is 1.
1: in Mainland China.
2: global.
3: outside Mainland China.
        :type PlayType: int
        :param _IsDelayLive: Whether it is LCB:
0: LVB.
1: LCB.
        :type IsDelayLive: int
        :param _CurrentCName: Information of currently used CNAME record.
        :type CurrentCName: str
        :param _RentTag: Disused parameter, which can be ignored.
        :type RentTag: int
        :param _RentExpireTime: A disused parameter.
Note: Beijing time (UTC+8) is used.
        :type RentExpireTime: str
        :param _IsMiniProgramLive: 0: LVB.
1: LVB on Mini Program.
Note: this field may return null, indicating that no valid values can be obtained.
        :type IsMiniProgramLive: int
        """
        self._Name = None
        self._Type = None
        self._Status = None
        self._CreateTime = None
        self._BCName = None
        self._TargetDomain = None
        self._PlayType = None
        self._IsDelayLive = None
        self._CurrentCName = None
        self._RentTag = None
        self._RentExpireTime = None
        self._IsMiniProgramLive = None

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, Name):
        self._Name = Name

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
    def CreateTime(self):
        return self._CreateTime

    @CreateTime.setter
    def CreateTime(self, CreateTime):
        self._CreateTime = CreateTime

    @property
    def BCName(self):
        return self._BCName

    @BCName.setter
    def BCName(self, BCName):
        self._BCName = BCName

    @property
    def TargetDomain(self):
        return self._TargetDomain

    @TargetDomain.setter
    def TargetDomain(self, TargetDomain):
        self._TargetDomain = TargetDomain

    @property
    def PlayType(self):
        return self._PlayType

    @PlayType.setter
    def PlayType(self, PlayType):
        self._PlayType = PlayType

    @property
    def IsDelayLive(self):
        return self._IsDelayLive

    @IsDelayLive.setter
    def IsDelayLive(self, IsDelayLive):
        self._IsDelayLive = IsDelayLive

    @property
    def CurrentCName(self):
        return self._CurrentCName

    @CurrentCName.setter
    def CurrentCName(self, CurrentCName):
        self._CurrentCName = CurrentCName

    @property
    def RentTag(self):
        return self._RentTag

    @RentTag.setter
    def RentTag(self, RentTag):
        self._RentTag = RentTag

    @property
    def RentExpireTime(self):
        return self._RentExpireTime

    @RentExpireTime.setter
    def RentExpireTime(self, RentExpireTime):
        self._RentExpireTime = RentExpireTime

    @property
    def IsMiniProgramLive(self):
        return self._IsMiniProgramLive

    @IsMiniProgramLive.setter
    def IsMiniProgramLive(self, IsMiniProgramLive):
        self._IsMiniProgramLive = IsMiniProgramLive


    def _deserialize(self, params):
        self._Name = params.get("Name")
        self._Type = params.get("Type")
        self._Status = params.get("Status")
        self._CreateTime = params.get("CreateTime")
        self._BCName = params.get("BCName")
        self._TargetDomain = params.get("TargetDomain")
        self._PlayType = params.get("PlayType")
        self._IsDelayLive = params.get("IsDelayLive")
        self._CurrentCName = params.get("CurrentCName")
        self._RentTag = params.get("RentTag")
        self._RentExpireTime = params.get("RentExpireTime")
        self._IsMiniProgramLive = params.get("IsMiniProgramLive")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DropLiveStreamRequest(AbstractModel):
    """DropLiveStream request structure.

    """

    def __init__(self):
        r"""
        :param _StreamName: The stream name.
        :type StreamName: str
        :param _DomainName: Your push domain.
        :type DomainName: str
        :param _AppName: The push path, which should be the same as `AppName` in the push and playback URL. The default value is `live`.
        :type AppName: str
        """
        self._StreamName = None
        self._DomainName = None
        self._AppName = None

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName


    def _deserialize(self, params):
        self._StreamName = params.get("StreamName")
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DropLiveStreamResponse(AbstractModel):
    """DropLiveStream response structure.

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


class EnableLiveDomainRequest(AbstractModel):
    """EnableLiveDomain request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: LVB domain name to be enabled.
        :type DomainName: str
        """
        self._DomainName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class EnableLiveDomainResponse(AbstractModel):
    """EnableLiveDomain response structure.

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


class FlvSpecialParam(AbstractModel):
    """Special FLV recording setting.

    """

    def __init__(self):
        r"""
        :param _UploadInRecording: Whether to enable upload while recording. This parameter is only valid for FLV recording.
        :type UploadInRecording: bool
        """
        self._UploadInRecording = None

    @property
    def UploadInRecording(self):
        return self._UploadInRecording

    @UploadInRecording.setter
    def UploadInRecording(self, UploadInRecording):
        self._UploadInRecording = UploadInRecording


    def _deserialize(self, params):
        self._UploadInRecording = params.get("UploadInRecording")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ForbidLiveDomainRequest(AbstractModel):
    """ForbidLiveDomain request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: LVB domain name to be disabled.
        :type DomainName: str
        """
        self._DomainName = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ForbidLiveDomainResponse(AbstractModel):
    """ForbidLiveDomain response structure.

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


class ForbidLiveStreamRequest(AbstractModel):
    """ForbidLiveStream request structure.

    """

    def __init__(self):
        r"""
        :param _AppName: Push path, which is the same as the AppName in push and playback addresses and is "live" by default.
        :type AppName: str
        :param _DomainName: Your push domain name.
        :type DomainName: str
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _ResumeTime: The time (in UTC format) to resume the stream, such as 2018-11-29T19:00:00Z.
Notes:
1. The default stream disabling period is seven days. A stream can be disabled for up to 90 days.
2. Beijing time is 8 hours ahead of UTC. The [ISO 8601 format](https://intl.cloud.tencent.com/document/product/266/11732#iso-date-format) is used.
        :type ResumeTime: str
        :param _Reason: Reason for forbidding.
Note: Be sure to enter the reason for forbidding to avoid any faulty operations.
Length limit: 2,048 bytes.
        :type Reason: str
        """
        self._AppName = None
        self._DomainName = None
        self._StreamName = None
        self._ResumeTime = None
        self._Reason = None

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def ResumeTime(self):
        return self._ResumeTime

    @ResumeTime.setter
    def ResumeTime(self, ResumeTime):
        self._ResumeTime = ResumeTime

    @property
    def Reason(self):
        return self._Reason

    @Reason.setter
    def Reason(self, Reason):
        self._Reason = Reason


    def _deserialize(self, params):
        self._AppName = params.get("AppName")
        self._DomainName = params.get("DomainName")
        self._StreamName = params.get("StreamName")
        self._ResumeTime = params.get("ResumeTime")
        self._Reason = params.get("Reason")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ForbidLiveStreamResponse(AbstractModel):
    """ForbidLiveStream response structure.

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


class ForbidStreamInfo(AbstractModel):
    """List of forbidden streams

    """

    def __init__(self):
        r"""
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _CreateTime: The creation time.
Note: Beijing time (UTC+8) is used.
        :type CreateTime: str
        :param _ExpireTime: The end time.
Note: Beijing time (UTC+8) is used.
        :type ExpireTime: str
        :param _AppName: The push path.
Note: This field may return null, indicating that no valid values can be obtained.
        :type AppName: str
        :param _DomainName: The push domain name.
Note: This field may return null, indicating that no valid values can be obtained.
        :type DomainName: str
        """
        self._StreamName = None
        self._CreateTime = None
        self._ExpireTime = None
        self._AppName = None
        self._DomainName = None

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def CreateTime(self):
        return self._CreateTime

    @CreateTime.setter
    def CreateTime(self, CreateTime):
        self._CreateTime = CreateTime

    @property
    def ExpireTime(self):
        return self._ExpireTime

    @ExpireTime.setter
    def ExpireTime(self, ExpireTime):
        self._ExpireTime = ExpireTime

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName


    def _deserialize(self, params):
        self._StreamName = params.get("StreamName")
        self._CreateTime = params.get("CreateTime")
        self._ExpireTime = params.get("ExpireTime")
        self._AppName = params.get("AppName")
        self._DomainName = params.get("DomainName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class GroupProIspDataInfo(AbstractModel):
    """Bandwidth, traffic, number of requests, and number of concurrent connections of an ISP in a district.

    """

    def __init__(self):
        r"""
        :param _ProvinceName: District.
        :type ProvinceName: str
        :param _IspName: ISP.
        :type IspName: str
        :param _DetailInfoList: Detailed data at the minute level.
        :type DetailInfoList: list of CdnPlayStatData
        """
        self._ProvinceName = None
        self._IspName = None
        self._DetailInfoList = None

    @property
    def ProvinceName(self):
        return self._ProvinceName

    @ProvinceName.setter
    def ProvinceName(self, ProvinceName):
        self._ProvinceName = ProvinceName

    @property
    def IspName(self):
        return self._IspName

    @IspName.setter
    def IspName(self, IspName):
        self._IspName = IspName

    @property
    def DetailInfoList(self):
        return self._DetailInfoList

    @DetailInfoList.setter
    def DetailInfoList(self, DetailInfoList):
        self._DetailInfoList = DetailInfoList


    def _deserialize(self, params):
        self._ProvinceName = params.get("ProvinceName")
        self._IspName = params.get("IspName")
        if params.get("DetailInfoList") is not None:
            self._DetailInfoList = []
            for item in params.get("DetailInfoList"):
                obj = CdnPlayStatData()
                obj._deserialize(item)
                self._DetailInfoList.append(obj)
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class HlsSpecialParam(AbstractModel):
    """HLS-specific recording parameter

    """

    def __init__(self):
        r"""
        :param _FlowContinueDuration: Timeout period for restarting an interrupted HLS push.
Value range: [0, 1,800].
        :type FlowContinueDuration: int
        """
        self._FlowContinueDuration = None

    @property
    def FlowContinueDuration(self):
        return self._FlowContinueDuration

    @FlowContinueDuration.setter
    def FlowContinueDuration(self, FlowContinueDuration):
        self._FlowContinueDuration = FlowContinueDuration


    def _deserialize(self, params):
        self._FlowContinueDuration = params.get("FlowContinueDuration")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class HttpCodeInfo(AbstractModel):
    """HTTP return code and statistics

    """

    def __init__(self):
        r"""
        :param _HttpCode: HTTP return code.
Example: "2xx", "3xx", "4xx", "5xx".
        :type HttpCode: str
        :param _ValueList: Statistics. 0 will be added for points in time when there is no data.
        :type ValueList: list of HttpCodeValue
        """
        self._HttpCode = None
        self._ValueList = None

    @property
    def HttpCode(self):
        return self._HttpCode

    @HttpCode.setter
    def HttpCode(self, HttpCode):
        self._HttpCode = HttpCode

    @property
    def ValueList(self):
        return self._ValueList

    @ValueList.setter
    def ValueList(self, ValueList):
        self._ValueList = ValueList


    def _deserialize(self, params):
        self._HttpCode = params.get("HttpCode")
        if params.get("ValueList") is not None:
            self._ValueList = []
            for item in params.get("ValueList"):
                obj = HttpCodeValue()
                obj._deserialize(item)
                self._ValueList.append(obj)
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class HttpCodeValue(AbstractModel):
    """HTTP return code data

    """

    def __init__(self):
        r"""
        :param _Time: Time in the format of `yyyy-mm-dd HH:MM:SS`.
        :type Time: str
        :param _Numbers: Occurrences.
        :type Numbers: int
        :param _Percentage: Proportion.
        :type Percentage: float
        """
        self._Time = None
        self._Numbers = None
        self._Percentage = None

    @property
    def Time(self):
        return self._Time

    @Time.setter
    def Time(self, Time):
        self._Time = Time

    @property
    def Numbers(self):
        return self._Numbers

    @Numbers.setter
    def Numbers(self, Numbers):
        self._Numbers = Numbers

    @property
    def Percentage(self):
        return self._Percentage

    @Percentage.setter
    def Percentage(self, Percentage):
        self._Percentage = Percentage


    def _deserialize(self, params):
        self._Time = params.get("Time")
        self._Numbers = params.get("Numbers")
        self._Percentage = params.get("Percentage")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class HttpStatusData(AbstractModel):
    """Playback error code information

    """

    def __init__(self):
        r"""
        :param _Time: Data point in time,
In the format of `yyyy-mm-dd HH:MM:SS`.
        :type Time: str
        :param _HttpStatusInfoList: Playback status code details.
        :type HttpStatusInfoList: list of HttpStatusInfo
        """
        self._Time = None
        self._HttpStatusInfoList = None

    @property
    def Time(self):
        return self._Time

    @Time.setter
    def Time(self, Time):
        self._Time = Time

    @property
    def HttpStatusInfoList(self):
        return self._HttpStatusInfoList

    @HttpStatusInfoList.setter
    def HttpStatusInfoList(self, HttpStatusInfoList):
        self._HttpStatusInfoList = HttpStatusInfoList


    def _deserialize(self, params):
        self._Time = params.get("Time")
        if params.get("HttpStatusInfoList") is not None:
            self._HttpStatusInfoList = []
            for item in params.get("HttpStatusInfoList"):
                obj = HttpStatusInfo()
                obj._deserialize(item)
                self._HttpStatusInfoList.append(obj)
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class HttpStatusInfo(AbstractModel):
    """Playback error code information

    """

    def __init__(self):
        r"""
        :param _HttpStatus: Playback HTTP status code.
        :type HttpStatus: str
        :param _Num: Quantity.
        :type Num: int
        """
        self._HttpStatus = None
        self._Num = None

    @property
    def HttpStatus(self):
        return self._HttpStatus

    @HttpStatus.setter
    def HttpStatus(self, HttpStatus):
        self._HttpStatus = HttpStatus

    @property
    def Num(self):
        return self._Num

    @Num.setter
    def Num(self, Num):
        self._Num = Num


    def _deserialize(self, params):
        self._HttpStatus = params.get("HttpStatus")
        self._Num = params.get("Num")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class LiveCertDomainInfo(AbstractModel):
    """The domains to bind to a certificate.

    """

    def __init__(self):
        r"""
        :param _DomainName: The domain name.
        :type DomainName: str
        :param _Status: Whether to enable HTTPS for the domain.
1: Enable
0: Disable
-1: Keep the current configuration
        :type Status: int
        """
        self._DomainName = None
        self._Status = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._Status = params.get("Status")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class LiveDomainCertBindings(AbstractModel):
    """The domain and certificate information returned by `DescribeLiveDomainCertBindings` and `DescribeLiveDomainCertBindingsGray`.

    """

    def __init__(self):
        r"""
        :param _DomainName: The domain name.
        :type DomainName: str
        :param _CertificateAlias: The remarks for the certificate. This parameter is the same as `CertName`.
        :type CertificateAlias: str
        :param _CertType: The certificate type.
0: Self-owned certificate
1: Tencent Cloud-hosted certificate
        :type CertType: int
        :param _Status: Whether HTTPS is enabled.
1: Enabled
0: Disabled
        :type Status: int
        :param _CertExpireTime: The certificate expiration time.
Note: Beijing time (UTC+8) is used.
        :type CertExpireTime: str
        :param _CertId: The certificate ID.
        :type CertId: int
        :param _CloudCertId: The SSL certificate ID assigned by Tencent Cloud.
        :type CloudCertId: str
        :param _UpdateTime: The last updated time.
Note: Beijing time (UTC+8) is used.
Note: This field may return null, indicating that no valid values can be obtained.
        :type UpdateTime: str
        """
        self._DomainName = None
        self._CertificateAlias = None
        self._CertType = None
        self._Status = None
        self._CertExpireTime = None
        self._CertId = None
        self._CloudCertId = None
        self._UpdateTime = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def CertificateAlias(self):
        return self._CertificateAlias

    @CertificateAlias.setter
    def CertificateAlias(self, CertificateAlias):
        self._CertificateAlias = CertificateAlias

    @property
    def CertType(self):
        return self._CertType

    @CertType.setter
    def CertType(self, CertType):
        self._CertType = CertType

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status

    @property
    def CertExpireTime(self):
        return self._CertExpireTime

    @CertExpireTime.setter
    def CertExpireTime(self, CertExpireTime):
        self._CertExpireTime = CertExpireTime

    @property
    def CertId(self):
        return self._CertId

    @CertId.setter
    def CertId(self, CertId):
        self._CertId = CertId

    @property
    def CloudCertId(self):
        return self._CloudCertId

    @CloudCertId.setter
    def CloudCertId(self, CloudCertId):
        self._CloudCertId = CloudCertId

    @property
    def UpdateTime(self):
        return self._UpdateTime

    @UpdateTime.setter
    def UpdateTime(self, UpdateTime):
        self._UpdateTime = UpdateTime


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._CertificateAlias = params.get("CertificateAlias")
        self._CertType = params.get("CertType")
        self._Status = params.get("Status")
        self._CertExpireTime = params.get("CertExpireTime")
        self._CertId = params.get("CertId")
        self._CloudCertId = params.get("CloudCertId")
        self._UpdateTime = params.get("UpdateTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyLiveCallbackTemplateRequest(AbstractModel):
    """ModifyLiveCallbackTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID returned by the `DescribeLiveCallbackTemplates` API.
        :type TemplateId: int
        :param _TemplateName: Template name.
        :type TemplateName: str
        :param _Description: Description.
        :type Description: str
        :param _StreamBeginNotifyUrl: Stream starting callback URL.
        :type StreamBeginNotifyUrl: str
        :param _StreamEndNotifyUrl: Interruption callback URL.
        :type StreamEndNotifyUrl: str
        :param _RecordNotifyUrl: Recording callback URL.
        :type RecordNotifyUrl: str
        :param _SnapshotNotifyUrl: Screencapturing callback URL.
        :type SnapshotNotifyUrl: str
        :param _PornCensorshipNotifyUrl: Porn detection callback URL.
        :type PornCensorshipNotifyUrl: str
        :param _CallbackKey: Callback key. The callback URL is public. For the callback signature, please see the event message notification document.
[Event Message Notification](https://intl.cloud.tencent.com/document/product/267/32744?from_cn_redirect=1).
        :type CallbackKey: str
        :param _PushExceptionNotifyUrl: The push error callback URL.
        :type PushExceptionNotifyUrl: str
        """
        self._TemplateId = None
        self._TemplateName = None
        self._Description = None
        self._StreamBeginNotifyUrl = None
        self._StreamEndNotifyUrl = None
        self._RecordNotifyUrl = None
        self._SnapshotNotifyUrl = None
        self._PornCensorshipNotifyUrl = None
        self._CallbackKey = None
        self._PushExceptionNotifyUrl = None

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
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def StreamBeginNotifyUrl(self):
        return self._StreamBeginNotifyUrl

    @StreamBeginNotifyUrl.setter
    def StreamBeginNotifyUrl(self, StreamBeginNotifyUrl):
        self._StreamBeginNotifyUrl = StreamBeginNotifyUrl

    @property
    def StreamEndNotifyUrl(self):
        return self._StreamEndNotifyUrl

    @StreamEndNotifyUrl.setter
    def StreamEndNotifyUrl(self, StreamEndNotifyUrl):
        self._StreamEndNotifyUrl = StreamEndNotifyUrl

    @property
    def RecordNotifyUrl(self):
        return self._RecordNotifyUrl

    @RecordNotifyUrl.setter
    def RecordNotifyUrl(self, RecordNotifyUrl):
        self._RecordNotifyUrl = RecordNotifyUrl

    @property
    def SnapshotNotifyUrl(self):
        return self._SnapshotNotifyUrl

    @SnapshotNotifyUrl.setter
    def SnapshotNotifyUrl(self, SnapshotNotifyUrl):
        self._SnapshotNotifyUrl = SnapshotNotifyUrl

    @property
    def PornCensorshipNotifyUrl(self):
        return self._PornCensorshipNotifyUrl

    @PornCensorshipNotifyUrl.setter
    def PornCensorshipNotifyUrl(self, PornCensorshipNotifyUrl):
        self._PornCensorshipNotifyUrl = PornCensorshipNotifyUrl

    @property
    def CallbackKey(self):
        return self._CallbackKey

    @CallbackKey.setter
    def CallbackKey(self, CallbackKey):
        self._CallbackKey = CallbackKey

    @property
    def PushExceptionNotifyUrl(self):
        return self._PushExceptionNotifyUrl

    @PushExceptionNotifyUrl.setter
    def PushExceptionNotifyUrl(self, PushExceptionNotifyUrl):
        self._PushExceptionNotifyUrl = PushExceptionNotifyUrl


    def _deserialize(self, params):
        self._TemplateId = params.get("TemplateId")
        self._TemplateName = params.get("TemplateName")
        self._Description = params.get("Description")
        self._StreamBeginNotifyUrl = params.get("StreamBeginNotifyUrl")
        self._StreamEndNotifyUrl = params.get("StreamEndNotifyUrl")
        self._RecordNotifyUrl = params.get("RecordNotifyUrl")
        self._SnapshotNotifyUrl = params.get("SnapshotNotifyUrl")
        self._PornCensorshipNotifyUrl = params.get("PornCensorshipNotifyUrl")
        self._CallbackKey = params.get("CallbackKey")
        self._PushExceptionNotifyUrl = params.get("PushExceptionNotifyUrl")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyLiveCallbackTemplateResponse(AbstractModel):
    """ModifyLiveCallbackTemplate response structure.

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


class ModifyLiveDomainCertBindingsRequest(AbstractModel):
    """ModifyLiveDomainCertBindings request structure.

    """

    def __init__(self):
        r"""
        :param _DomainInfos: The playback domains to bind and whether to enable HTTPS for them.
If neither `CloudCertId` nor the public/private key is specified, and a domain is already bound with a certificate, this API will only update the HTTPS configuration of the domain and, if the certificate is a self-owned certificate, upload it to Tencent Cloud.
        :type DomainInfos: list of LiveCertDomainInfo
        :param _CloudCertId: The SSL certificate ID assigned by Tencent Cloud.
For details, see https://intl.cloud.tencent.com/document/api/400/41665?from_cn_redirect=1
        :type CloudCertId: str
        :param _CertificatePublicKey: The public key of the certificate.
You can specify either `CloudCertId` or the public/private key. If both are specified, the private and public key parameters will be ignored. If you pass in only the public and private keys, the corresponding certificate will be uploaded to Tencent Cloud SSL Certificate Service, which will generate a `CloudCertId` for the certificate.
        :type CertificatePublicKey: str
        :param _CertificatePrivateKey: The private key of the certificate.
You can specify either `CloudCertId` or the public/private key. If both are specified, the private and public key parameters will be ignored. If you pass in only the public and private keys, the corresponding certificate will be uploaded to Tencent Cloud SSL Certificate Service, which will generate a `CloudCertId` for the certificate.
        :type CertificatePrivateKey: str
        :param _CertificateAlias: The remarks for the certificate in Tencent Cloud SSL Certificate Service. This parameter will be ignored if `CloudCertId` is specified.
        :type CertificateAlias: str
        """
        self._DomainInfos = None
        self._CloudCertId = None
        self._CertificatePublicKey = None
        self._CertificatePrivateKey = None
        self._CertificateAlias = None

    @property
    def DomainInfos(self):
        return self._DomainInfos

    @DomainInfos.setter
    def DomainInfos(self, DomainInfos):
        self._DomainInfos = DomainInfos

    @property
    def CloudCertId(self):
        return self._CloudCertId

    @CloudCertId.setter
    def CloudCertId(self, CloudCertId):
        self._CloudCertId = CloudCertId

    @property
    def CertificatePublicKey(self):
        return self._CertificatePublicKey

    @CertificatePublicKey.setter
    def CertificatePublicKey(self, CertificatePublicKey):
        self._CertificatePublicKey = CertificatePublicKey

    @property
    def CertificatePrivateKey(self):
        return self._CertificatePrivateKey

    @CertificatePrivateKey.setter
    def CertificatePrivateKey(self, CertificatePrivateKey):
        self._CertificatePrivateKey = CertificatePrivateKey

    @property
    def CertificateAlias(self):
        return self._CertificateAlias

    @CertificateAlias.setter
    def CertificateAlias(self, CertificateAlias):
        self._CertificateAlias = CertificateAlias


    def _deserialize(self, params):
        if params.get("DomainInfos") is not None:
            self._DomainInfos = []
            for item in params.get("DomainInfos"):
                obj = LiveCertDomainInfo()
                obj._deserialize(item)
                self._DomainInfos.append(obj)
        self._CloudCertId = params.get("CloudCertId")
        self._CertificatePublicKey = params.get("CertificatePublicKey")
        self._CertificatePrivateKey = params.get("CertificatePrivateKey")
        self._CertificateAlias = params.get("CertificateAlias")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyLiveDomainCertBindingsResponse(AbstractModel):
    """ModifyLiveDomainCertBindings response structure.

    """

    def __init__(self):
        r"""
        :param _MismatchedDomainNames: The domains skipped due to certificate mismatch.
        :type MismatchedDomainNames: list of str
        :param _Errors: The domains that the API failed to bind, including those in `MismatchedDomainNames`, and the error information.
Note: This field may return null, indicating that no valid values can be obtained.
        :type Errors: list of BatchDomainOperateErrors
        :param _RequestId: The unique request ID, which is returned for each request. RequestId is required for locating a problem.
        :type RequestId: str
        """
        self._MismatchedDomainNames = None
        self._Errors = None
        self._RequestId = None

    @property
    def MismatchedDomainNames(self):
        return self._MismatchedDomainNames

    @MismatchedDomainNames.setter
    def MismatchedDomainNames(self, MismatchedDomainNames):
        self._MismatchedDomainNames = MismatchedDomainNames

    @property
    def Errors(self):
        return self._Errors

    @Errors.setter
    def Errors(self, Errors):
        self._Errors = Errors

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._MismatchedDomainNames = params.get("MismatchedDomainNames")
        if params.get("Errors") is not None:
            self._Errors = []
            for item in params.get("Errors"):
                obj = BatchDomainOperateErrors()
                obj._deserialize(item)
                self._Errors.append(obj)
        self._RequestId = params.get("RequestId")


class ModifyLiveDomainRefererRequest(AbstractModel):
    """ModifyLiveDomainReferer request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Playback domain name
        :type DomainName: str
        :param _Enable: Whether to enable referer allowlist/blocklist authentication for the current domain name
        :type Enable: int
        :param _Type: List type. Valid values: `0` (blocklist), `1` (allowlist)
        :type Type: int
        :param _AllowEmpty: Whether to allow empty referer. Valid values: `0` (no), `1` (yes)
        :type AllowEmpty: int
        :param _Rules: Referer list. Separate items in it with semicolons (;).
        :type Rules: str
        """
        self._DomainName = None
        self._Enable = None
        self._Type = None
        self._AllowEmpty = None
        self._Rules = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def Enable(self):
        return self._Enable

    @Enable.setter
    def Enable(self, Enable):
        self._Enable = Enable

    @property
    def Type(self):
        return self._Type

    @Type.setter
    def Type(self, Type):
        self._Type = Type

    @property
    def AllowEmpty(self):
        return self._AllowEmpty

    @AllowEmpty.setter
    def AllowEmpty(self, AllowEmpty):
        self._AllowEmpty = AllowEmpty

    @property
    def Rules(self):
        return self._Rules

    @Rules.setter
    def Rules(self, Rules):
        self._Rules = Rules


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._Enable = params.get("Enable")
        self._Type = params.get("Type")
        self._AllowEmpty = params.get("AllowEmpty")
        self._Rules = params.get("Rules")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyLiveDomainRefererResponse(AbstractModel):
    """ModifyLiveDomainReferer response structure.

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


class ModifyLivePlayAuthKeyRequest(AbstractModel):
    """ModifyLivePlayAuthKey request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Playback domain name.
        :type DomainName: str
        :param _Enable: Whether to enable. 0: disabled; 1: enabled.
If this parameter is left empty, the current value will not be modified.
        :type Enable: int
        :param _AuthKey: Authentication key.
If this parameter is left empty, the current value will not be modified.
        :type AuthKey: str
        :param _AuthDelta: Validity period in seconds.
If this parameter is left empty, the current value will not be modified.
        :type AuthDelta: int
        :param _AuthBackKey: Backup authentication key.
If this parameter is left empty, the current value will not be modified.
        :type AuthBackKey: str
        """
        self._DomainName = None
        self._Enable = None
        self._AuthKey = None
        self._AuthDelta = None
        self._AuthBackKey = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def Enable(self):
        return self._Enable

    @Enable.setter
    def Enable(self, Enable):
        self._Enable = Enable

    @property
    def AuthKey(self):
        return self._AuthKey

    @AuthKey.setter
    def AuthKey(self, AuthKey):
        self._AuthKey = AuthKey

    @property
    def AuthDelta(self):
        return self._AuthDelta

    @AuthDelta.setter
    def AuthDelta(self, AuthDelta):
        self._AuthDelta = AuthDelta

    @property
    def AuthBackKey(self):
        return self._AuthBackKey

    @AuthBackKey.setter
    def AuthBackKey(self, AuthBackKey):
        self._AuthBackKey = AuthBackKey


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._Enable = params.get("Enable")
        self._AuthKey = params.get("AuthKey")
        self._AuthDelta = params.get("AuthDelta")
        self._AuthBackKey = params.get("AuthBackKey")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyLivePlayAuthKeyResponse(AbstractModel):
    """ModifyLivePlayAuthKey response structure.

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


class ModifyLivePlayDomainRequest(AbstractModel):
    """ModifyLivePlayDomain request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Playback domain name.
        :type DomainName: str
        :param _PlayType: Pull domain name type. 1: Mainland China. 2: global, 3: outside Mainland China
        :type PlayType: int
        """
        self._DomainName = None
        self._PlayType = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def PlayType(self):
        return self._PlayType

    @PlayType.setter
    def PlayType(self, PlayType):
        self._PlayType = PlayType


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._PlayType = params.get("PlayType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyLivePlayDomainResponse(AbstractModel):
    """ModifyLivePlayDomain response structure.

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


class ModifyLivePullStreamTaskRequest(AbstractModel):
    """ModifyLivePullStreamTask request structure.

    """

    def __init__(self):
        r"""
        :param _TaskId: The task ID.
        :type TaskId: str
        :param _Operator: The operator.
        :type Operator: str
        :param _SourceUrls: The source URL(s).
If `SourceType` is `PullLivePushLive`, you can specify only one source URL.
If `SourceType` is `PullVodPushLive`, you can specify at most 30 source URLs.
        :type SourceUrls: list of str
        :param _StartTime: The start time.
It must be in UTC format.
Example: 2019-01-08T10:00:00Z.
Note: Beijing time is 8 hours ahead of UTC. The [ISO 8601 format](https://intl.cloud.tencent.com/document/product/266/11732#iso-date-format) is used.
        :type StartTime: str
        :param _EndTime: The end time. Notes:
1. The end time must be later than the start time.
2. The end time and start time must be later than the current time.
3. The end time and start time must be less than seven days apart.
It must be in UTC format.
Example: 2019-01-08T10:00:00Z.
Note: Beijing time is 8 hours ahead of UTC. The [ISO 8601 format](https://intl.cloud.tencent.com/document/product/266/11732#iso-date-format) is used.
        :type EndTime: str
        :param _VodLoopTimes: The number of times to loop video files.
-1: Loop indefinitely
0: Do not loop
> 0: The number of loop times. A task will end either when the videos are looped for the specified number of times or at the specified task end time, whichever is earlier.
This parameter is valid only if the source is video files.
        :type VodLoopTimes: int
        :param _VodRefreshType: The behavior after the source video files (`SourceUrls`) are changed.
ImmediateNewSource: Play the new videos immediately
ContinueBreakPoint: Finish the current video first and then pull from the new source.
This parameter is valid only if the source is video files.
        :type VodRefreshType: str
        :param _Status: Whether to enable or pause the task. Valid values:
enable
pause
        :type Status: str
        :param _CallbackEvents: The events to listen for. If you do not pass this parameter, all events will be listened for.
TaskStart: Callback for starting a task
TaskExit: Callback for ending a task
VodSourceFileStart: Callback for starting to pull from video files
VodSourceFileFinish: Callback for stopping pulling from video files
ResetTaskConfig: Callback for modifying a task
        :type CallbackEvents: list of str
        :param _CallbackUrl: A custom callback URL.
Callbacks will be sent to this URL.
        :type CallbackUrl: str
        :param _FileIndex: The index of the video to start from.
The value of this parameter cannot be smaller than 1 or larger than the number of elements in `SourceUrls`.
        :type FileIndex: int
        :param _OffsetTime: The playback offset (seconds).
Notes:
1. This parameter should be used together with `FileIndex`.
        :type OffsetTime: int
        :param _Comment: The remarks for the task.
        :type Comment: str
        :param _BackupSourceType: The backup source type.
PullLivePushLive: Live streaming
PullVodPushLive: Video files
Notes:
1. Backup sources are supported only if the primary source type is live streaming.
2. Leaving this parameter empty will reset the backup source.
3. When pull from the primary source is interrupted, the system will pull from the backup source.
4. If the backup source is a video file, each time the video is finished, the system will check if the primary source is recovered and will switch back if it is.
        :type BackupSourceType: str
        :param _BackupSourceUrl: The URL of the backup source.
You can specify only one backup source URL.
        :type BackupSourceUrl: str
        :param _WatermarkList: The information of watermarks to add.
Notes:
1. You can add up to four watermarks to different locations of the video.
2. Make sure you use publicly accessible URLs for the watermark images.
3. Supported image formats include PNG and JPG.
4. If you change the watermark configuration of a task whose source is a list of video files, the new configuration will take effect for the next file in the list.
5. If you change the watermark configuration of a task whose source is a live stream, the new configuration will take effect immediately.
6. If you want to stop using watermarks, pass in an empty array.
7. Currently, animated watermarks are not supported.
        :type WatermarkList: list of PullPushWatermarkInfo
        :param _VodLocalMode: Whether to use local mode when the source type is video files. The default is `0`.
0: Do not use local mode
1: Use local mode
Note: If you enable local mode, MP4 files will be downloaded to local storage, and the local files will be used for push. This ensures more reliable push. Pushing a local file will incur additional fees.
        :type VodLocalMode: int
        """
        self._TaskId = None
        self._Operator = None
        self._SourceUrls = None
        self._StartTime = None
        self._EndTime = None
        self._VodLoopTimes = None
        self._VodRefreshType = None
        self._Status = None
        self._CallbackEvents = None
        self._CallbackUrl = None
        self._FileIndex = None
        self._OffsetTime = None
        self._Comment = None
        self._BackupSourceType = None
        self._BackupSourceUrl = None
        self._WatermarkList = None
        self._VodLocalMode = None

    @property
    def TaskId(self):
        return self._TaskId

    @TaskId.setter
    def TaskId(self, TaskId):
        self._TaskId = TaskId

    @property
    def Operator(self):
        return self._Operator

    @Operator.setter
    def Operator(self, Operator):
        self._Operator = Operator

    @property
    def SourceUrls(self):
        return self._SourceUrls

    @SourceUrls.setter
    def SourceUrls(self, SourceUrls):
        self._SourceUrls = SourceUrls

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
    def VodLoopTimes(self):
        return self._VodLoopTimes

    @VodLoopTimes.setter
    def VodLoopTimes(self, VodLoopTimes):
        self._VodLoopTimes = VodLoopTimes

    @property
    def VodRefreshType(self):
        return self._VodRefreshType

    @VodRefreshType.setter
    def VodRefreshType(self, VodRefreshType):
        self._VodRefreshType = VodRefreshType

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status

    @property
    def CallbackEvents(self):
        return self._CallbackEvents

    @CallbackEvents.setter
    def CallbackEvents(self, CallbackEvents):
        self._CallbackEvents = CallbackEvents

    @property
    def CallbackUrl(self):
        return self._CallbackUrl

    @CallbackUrl.setter
    def CallbackUrl(self, CallbackUrl):
        self._CallbackUrl = CallbackUrl

    @property
    def FileIndex(self):
        return self._FileIndex

    @FileIndex.setter
    def FileIndex(self, FileIndex):
        self._FileIndex = FileIndex

    @property
    def OffsetTime(self):
        return self._OffsetTime

    @OffsetTime.setter
    def OffsetTime(self, OffsetTime):
        self._OffsetTime = OffsetTime

    @property
    def Comment(self):
        return self._Comment

    @Comment.setter
    def Comment(self, Comment):
        self._Comment = Comment

    @property
    def BackupSourceType(self):
        return self._BackupSourceType

    @BackupSourceType.setter
    def BackupSourceType(self, BackupSourceType):
        self._BackupSourceType = BackupSourceType

    @property
    def BackupSourceUrl(self):
        return self._BackupSourceUrl

    @BackupSourceUrl.setter
    def BackupSourceUrl(self, BackupSourceUrl):
        self._BackupSourceUrl = BackupSourceUrl

    @property
    def WatermarkList(self):
        return self._WatermarkList

    @WatermarkList.setter
    def WatermarkList(self, WatermarkList):
        self._WatermarkList = WatermarkList

    @property
    def VodLocalMode(self):
        return self._VodLocalMode

    @VodLocalMode.setter
    def VodLocalMode(self, VodLocalMode):
        self._VodLocalMode = VodLocalMode


    def _deserialize(self, params):
        self._TaskId = params.get("TaskId")
        self._Operator = params.get("Operator")
        self._SourceUrls = params.get("SourceUrls")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._VodLoopTimes = params.get("VodLoopTimes")
        self._VodRefreshType = params.get("VodRefreshType")
        self._Status = params.get("Status")
        self._CallbackEvents = params.get("CallbackEvents")
        self._CallbackUrl = params.get("CallbackUrl")
        self._FileIndex = params.get("FileIndex")
        self._OffsetTime = params.get("OffsetTime")
        self._Comment = params.get("Comment")
        self._BackupSourceType = params.get("BackupSourceType")
        self._BackupSourceUrl = params.get("BackupSourceUrl")
        if params.get("WatermarkList") is not None:
            self._WatermarkList = []
            for item in params.get("WatermarkList"):
                obj = PullPushWatermarkInfo()
                obj._deserialize(item)
                self._WatermarkList.append(obj)
        self._VodLocalMode = params.get("VodLocalMode")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyLivePullStreamTaskResponse(AbstractModel):
    """ModifyLivePullStreamTask response structure.

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


class ModifyLivePushAuthKeyRequest(AbstractModel):
    """ModifyLivePushAuthKey request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _Enable: Whether to enable. 0: disabled; 1: enabled.
If this parameter is left empty, the current value will not be modified.
        :type Enable: int
        :param _MasterAuthKey: Master authentication key.
If this parameter is left empty, the current value will not be modified.
        :type MasterAuthKey: str
        :param _BackupAuthKey: Backup authentication key.
If this parameter is left empty, the current value will not be modified.
        :type BackupAuthKey: str
        :param _AuthDelta: Validity period in seconds.
        :type AuthDelta: int
        """
        self._DomainName = None
        self._Enable = None
        self._MasterAuthKey = None
        self._BackupAuthKey = None
        self._AuthDelta = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def Enable(self):
        return self._Enable

    @Enable.setter
    def Enable(self, Enable):
        self._Enable = Enable

    @property
    def MasterAuthKey(self):
        return self._MasterAuthKey

    @MasterAuthKey.setter
    def MasterAuthKey(self, MasterAuthKey):
        self._MasterAuthKey = MasterAuthKey

    @property
    def BackupAuthKey(self):
        return self._BackupAuthKey

    @BackupAuthKey.setter
    def BackupAuthKey(self, BackupAuthKey):
        self._BackupAuthKey = BackupAuthKey

    @property
    def AuthDelta(self):
        return self._AuthDelta

    @AuthDelta.setter
    def AuthDelta(self, AuthDelta):
        self._AuthDelta = AuthDelta


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._Enable = params.get("Enable")
        self._MasterAuthKey = params.get("MasterAuthKey")
        self._BackupAuthKey = params.get("BackupAuthKey")
        self._AuthDelta = params.get("AuthDelta")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyLivePushAuthKeyResponse(AbstractModel):
    """ModifyLivePushAuthKey response structure.

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


class ModifyLiveRecordTemplateRequest(AbstractModel):
    """ModifyLiveRecordTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID obtained through the `DescribeRecordTemplates` API.
        :type TemplateId: int
        :param _TemplateName: Template name.
        :type TemplateName: str
        :param _Description: Message description
        :type Description: str
        :param _FlvParam: FLV recording parameter, which is set when FLV recording is enabled.
        :type FlvParam: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _HlsParam: HLS recording parameter, which is set when HLS recording is enabled.
        :type HlsParam: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _Mp4Param: MP4 recording parameter, which is set when MP4 recording is enabled.
        :type Mp4Param: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _AacParam: AAC recording parameter, which is set when AAC recording is enabled.
        :type AacParam: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _HlsSpecialParam: Custom HLS recording parameter.
        :type HlsSpecialParam: :class:`tencentcloud.live.v20180801.models.HlsSpecialParam`
        :param _Mp3Param: MP3 recording parameter, which is set when MP3 recording is enabled.
        :type Mp3Param: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _RemoveWatermark: Whether to remove the watermark. This parameter is invalid if `IsDelayLive` is `1`.
        :type RemoveWatermark: bool
        :param _FlvSpecialParam: A special parameter for FLV recording.
        :type FlvSpecialParam: :class:`tencentcloud.live.v20180801.models.FlvSpecialParam`
        """
        self._TemplateId = None
        self._TemplateName = None
        self._Description = None
        self._FlvParam = None
        self._HlsParam = None
        self._Mp4Param = None
        self._AacParam = None
        self._HlsSpecialParam = None
        self._Mp3Param = None
        self._RemoveWatermark = None
        self._FlvSpecialParam = None

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
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def FlvParam(self):
        return self._FlvParam

    @FlvParam.setter
    def FlvParam(self, FlvParam):
        self._FlvParam = FlvParam

    @property
    def HlsParam(self):
        return self._HlsParam

    @HlsParam.setter
    def HlsParam(self, HlsParam):
        self._HlsParam = HlsParam

    @property
    def Mp4Param(self):
        return self._Mp4Param

    @Mp4Param.setter
    def Mp4Param(self, Mp4Param):
        self._Mp4Param = Mp4Param

    @property
    def AacParam(self):
        return self._AacParam

    @AacParam.setter
    def AacParam(self, AacParam):
        self._AacParam = AacParam

    @property
    def HlsSpecialParam(self):
        return self._HlsSpecialParam

    @HlsSpecialParam.setter
    def HlsSpecialParam(self, HlsSpecialParam):
        self._HlsSpecialParam = HlsSpecialParam

    @property
    def Mp3Param(self):
        return self._Mp3Param

    @Mp3Param.setter
    def Mp3Param(self, Mp3Param):
        self._Mp3Param = Mp3Param

    @property
    def RemoveWatermark(self):
        return self._RemoveWatermark

    @RemoveWatermark.setter
    def RemoveWatermark(self, RemoveWatermark):
        self._RemoveWatermark = RemoveWatermark

    @property
    def FlvSpecialParam(self):
        return self._FlvSpecialParam

    @FlvSpecialParam.setter
    def FlvSpecialParam(self, FlvSpecialParam):
        self._FlvSpecialParam = FlvSpecialParam


    def _deserialize(self, params):
        self._TemplateId = params.get("TemplateId")
        self._TemplateName = params.get("TemplateName")
        self._Description = params.get("Description")
        if params.get("FlvParam") is not None:
            self._FlvParam = RecordParam()
            self._FlvParam._deserialize(params.get("FlvParam"))
        if params.get("HlsParam") is not None:
            self._HlsParam = RecordParam()
            self._HlsParam._deserialize(params.get("HlsParam"))
        if params.get("Mp4Param") is not None:
            self._Mp4Param = RecordParam()
            self._Mp4Param._deserialize(params.get("Mp4Param"))
        if params.get("AacParam") is not None:
            self._AacParam = RecordParam()
            self._AacParam._deserialize(params.get("AacParam"))
        if params.get("HlsSpecialParam") is not None:
            self._HlsSpecialParam = HlsSpecialParam()
            self._HlsSpecialParam._deserialize(params.get("HlsSpecialParam"))
        if params.get("Mp3Param") is not None:
            self._Mp3Param = RecordParam()
            self._Mp3Param._deserialize(params.get("Mp3Param"))
        self._RemoveWatermark = params.get("RemoveWatermark")
        if params.get("FlvSpecialParam") is not None:
            self._FlvSpecialParam = FlvSpecialParam()
            self._FlvSpecialParam._deserialize(params.get("FlvSpecialParam"))
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyLiveRecordTemplateResponse(AbstractModel):
    """ModifyLiveRecordTemplate response structure.

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


class ModifyLiveSnapshotTemplateRequest(AbstractModel):
    """ModifyLiveSnapshotTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
        :type TemplateId: int
        :param _CosAppId: The COS application ID.
**Please note that this parameter is required now**.
        :type CosAppId: int
        :param _CosBucket: The COS bucket name.
Note: Do not include the `-[appid]` part in the value of `CosBucket`.
**Please note that this parameter is required now**.
        :type CosBucket: str
        :param _CosRegion: The COS region.
**Please note that this parameter is required now**.
        :type CosRegion: str
        :param _TemplateName: Template name.
Maximum length: 255 bytes.
        :type TemplateName: str
        :param _Description: Description.
Maximum length: 1,024 bytes.
        :type Description: str
        :param _SnapshotInterval: Screencapturing interval in seconds. Default value: 10s.
Value range: 5-300s.
        :type SnapshotInterval: int
        :param _Width: Screenshot width. Default value: 0 (original width).
        :type Width: int
        :param _Height: Screenshot height. Default value: 0 (original height).
        :type Height: int
        :param _PornFlag: Whether to enable porn detection. Default value: 0.
0: do not enable.
1: enable.
        :type PornFlag: int
        :param _CosPrefix: COS bucket folder prefix.
        :type CosPrefix: str
        :param _CosFileName: COS filename.
        :type CosFileName: str
        """
        self._TemplateId = None
        self._CosAppId = None
        self._CosBucket = None
        self._CosRegion = None
        self._TemplateName = None
        self._Description = None
        self._SnapshotInterval = None
        self._Width = None
        self._Height = None
        self._PornFlag = None
        self._CosPrefix = None
        self._CosFileName = None

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId

    @property
    def CosAppId(self):
        return self._CosAppId

    @CosAppId.setter
    def CosAppId(self, CosAppId):
        self._CosAppId = CosAppId

    @property
    def CosBucket(self):
        return self._CosBucket

    @CosBucket.setter
    def CosBucket(self, CosBucket):
        self._CosBucket = CosBucket

    @property
    def CosRegion(self):
        return self._CosRegion

    @CosRegion.setter
    def CosRegion(self, CosRegion):
        self._CosRegion = CosRegion

    @property
    def TemplateName(self):
        return self._TemplateName

    @TemplateName.setter
    def TemplateName(self, TemplateName):
        self._TemplateName = TemplateName

    @property
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def SnapshotInterval(self):
        return self._SnapshotInterval

    @SnapshotInterval.setter
    def SnapshotInterval(self, SnapshotInterval):
        self._SnapshotInterval = SnapshotInterval

    @property
    def Width(self):
        return self._Width

    @Width.setter
    def Width(self, Width):
        self._Width = Width

    @property
    def Height(self):
        return self._Height

    @Height.setter
    def Height(self, Height):
        self._Height = Height

    @property
    def PornFlag(self):
        return self._PornFlag

    @PornFlag.setter
    def PornFlag(self, PornFlag):
        self._PornFlag = PornFlag

    @property
    def CosPrefix(self):
        return self._CosPrefix

    @CosPrefix.setter
    def CosPrefix(self, CosPrefix):
        self._CosPrefix = CosPrefix

    @property
    def CosFileName(self):
        return self._CosFileName

    @CosFileName.setter
    def CosFileName(self, CosFileName):
        self._CosFileName = CosFileName


    def _deserialize(self, params):
        self._TemplateId = params.get("TemplateId")
        self._CosAppId = params.get("CosAppId")
        self._CosBucket = params.get("CosBucket")
        self._CosRegion = params.get("CosRegion")
        self._TemplateName = params.get("TemplateName")
        self._Description = params.get("Description")
        self._SnapshotInterval = params.get("SnapshotInterval")
        self._Width = params.get("Width")
        self._Height = params.get("Height")
        self._PornFlag = params.get("PornFlag")
        self._CosPrefix = params.get("CosPrefix")
        self._CosFileName = params.get("CosFileName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyLiveSnapshotTemplateResponse(AbstractModel):
    """ModifyLiveSnapshotTemplate response structure.

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


class ModifyLiveTimeShiftTemplateRequest(AbstractModel):
    """ModifyLiveTimeShiftTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: The time shifting template ID.
        :type TemplateId: int
        :param _TemplateName: The template name.
Only letters, numbers, underscores, and hyphens are supported.
        :type TemplateName: str
        :param _Description: The template description.
Maximum length: 1,024 bytes.
Only letters, numbers, underscores, and hyphens are supported.
        :type Description: str
        :param _Duration: The time shifting duration.
Unit: Second.
        :type Duration: int
        :param _ItemDuration: The segment size.
Value range: 3-10.
Unit: Second.
Default value: 5
        :type ItemDuration: int
        :param _RemoveWatermark: Whether to remove watermarks.
If you pass in `true`, the original stream will be recorded.
Default value: `false`.
        :type RemoveWatermark: bool
        :param _TranscodeTemplateIds: The transcoding template IDs.
This API works only if `RemoveWatermark` is `false`.
        :type TranscodeTemplateIds: list of int
        :param _Area: The region.
`Mainland`: The Chinese mainland.
`Overseas`: Outside the Chinese mainland.
Default value: `Mainland`.
        :type Area: str
        """
        self._TemplateId = None
        self._TemplateName = None
        self._Description = None
        self._Duration = None
        self._ItemDuration = None
        self._RemoveWatermark = None
        self._TranscodeTemplateIds = None
        self._Area = None

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
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def Duration(self):
        return self._Duration

    @Duration.setter
    def Duration(self, Duration):
        self._Duration = Duration

    @property
    def ItemDuration(self):
        return self._ItemDuration

    @ItemDuration.setter
    def ItemDuration(self, ItemDuration):
        self._ItemDuration = ItemDuration

    @property
    def RemoveWatermark(self):
        return self._RemoveWatermark

    @RemoveWatermark.setter
    def RemoveWatermark(self, RemoveWatermark):
        self._RemoveWatermark = RemoveWatermark

    @property
    def TranscodeTemplateIds(self):
        return self._TranscodeTemplateIds

    @TranscodeTemplateIds.setter
    def TranscodeTemplateIds(self, TranscodeTemplateIds):
        self._TranscodeTemplateIds = TranscodeTemplateIds

    @property
    def Area(self):
        return self._Area

    @Area.setter
    def Area(self, Area):
        self._Area = Area


    def _deserialize(self, params):
        self._TemplateId = params.get("TemplateId")
        self._TemplateName = params.get("TemplateName")
        self._Description = params.get("Description")
        self._Duration = params.get("Duration")
        self._ItemDuration = params.get("ItemDuration")
        self._RemoveWatermark = params.get("RemoveWatermark")
        self._TranscodeTemplateIds = params.get("TranscodeTemplateIds")
        self._Area = params.get("Area")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyLiveTimeShiftTemplateResponse(AbstractModel):
    """ModifyLiveTimeShiftTemplate response structure.

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


class ModifyLiveTranscodeTemplateRequest(AbstractModel):
    """ModifyLiveTranscodeTemplate request structure.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
        :type TemplateId: int
        :param _Vcodec: Video codec. Valid values: h264, h265, origin (default)

origin: original codec as the output codec
        :type Vcodec: str
        :param _Acodec: Audio codec. Defaut value: aac.
Note: this parameter is unsupported now.
        :type Acodec: str
        :param _AudioBitrate: Audio bitrate. Default value: 0.
Value range: 0-500.
        :type AudioBitrate: int
        :param _Description: Template description.
        :type Description: str
        :param _VideoBitrate: Video bitrate in Kbps. Value range: 100-8000.
Note: the transcoding template requires that the bitrate be unique. Therefore, the final saved bitrate may be different from the input bitrate.
        :type VideoBitrate: int
        :param _Width: Width in pixels. Value range: 0-3000.
It must be a multiple of 2. The original width is 0.
        :type Width: int
        :param _NeedVideo: Whether to keep the video. 0: no; 1: yes. Default value: 1.
        :type NeedVideo: int
        :param _NeedAudio: Whether to keep the audio. 0: no; 1: yes. Default value: 1.
        :type NeedAudio: int
        :param _Height: Height in pixels. Value range: 0-3000.
It must be a multiple of 2. The original height is 0.
        :type Height: int
        :param _Fps: Frame rate in fps. Default value: 0.
Value range: 0-60
        :type Fps: int
        :param _Gop: Keyframe interval in seconds.
Value range: 2-6
        :type Gop: int
        :param _Rotate: Rotation angle. Default value: 0.
Valid values: 0, 90, 180, 270
        :type Rotate: int
        :param _Profile: Encoding quality:
baseline/main/high.
        :type Profile: str
        :param _BitrateToOrig: Whether to use the original bitrate when the set bitrate is larger than the original bitrate.
0: no, 1: yes
Default value: 0.
        :type BitrateToOrig: int
        :param _HeightToOrig: Whether to use the original height when the set height is higher than the original height.
0: no, 1: yes
Default value: 0.
        :type HeightToOrig: int
        :param _FpsToOrig: Whether to use the original frame rate when the set frame rate is larger than the original frame rate.
0: no, 1: yes
Default value: 0.
        :type FpsToOrig: int
        :param _AdaptBitratePercent: Bitrate compression ratio of top speed codec video.
Target bitrate of top speed code = VideoBitrate * (1-AdaptBitratePercent)

Value range: 0.0-0.5.
        :type AdaptBitratePercent: float
        :param _ShortEdgeAsHeight: Whether to use the short side as the video height. 0: no, 1: yes. Default value: 0.
        :type ShortEdgeAsHeight: int
        :param _DRMType: The DRM encryption type. Valid values: fairplay, normalaes, widevine.
If you do not pass this parameter or pass in an empty string, the existing configuration will be reset.
        :type DRMType: str
        :param _DRMTracks: The tracks to encrypt. Valid values: AUDIO, SD, HD, UHD1, UHD2. You can choose only one video track (SD, HD, UHD1, or UHD2).
If you do not pass this parameter or pass in an empty string, the existing configuration will be reset.
        :type DRMTracks: str
        """
        self._TemplateId = None
        self._Vcodec = None
        self._Acodec = None
        self._AudioBitrate = None
        self._Description = None
        self._VideoBitrate = None
        self._Width = None
        self._NeedVideo = None
        self._NeedAudio = None
        self._Height = None
        self._Fps = None
        self._Gop = None
        self._Rotate = None
        self._Profile = None
        self._BitrateToOrig = None
        self._HeightToOrig = None
        self._FpsToOrig = None
        self._AdaptBitratePercent = None
        self._ShortEdgeAsHeight = None
        self._DRMType = None
        self._DRMTracks = None

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId

    @property
    def Vcodec(self):
        return self._Vcodec

    @Vcodec.setter
    def Vcodec(self, Vcodec):
        self._Vcodec = Vcodec

    @property
    def Acodec(self):
        return self._Acodec

    @Acodec.setter
    def Acodec(self, Acodec):
        self._Acodec = Acodec

    @property
    def AudioBitrate(self):
        return self._AudioBitrate

    @AudioBitrate.setter
    def AudioBitrate(self, AudioBitrate):
        self._AudioBitrate = AudioBitrate

    @property
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def VideoBitrate(self):
        return self._VideoBitrate

    @VideoBitrate.setter
    def VideoBitrate(self, VideoBitrate):
        self._VideoBitrate = VideoBitrate

    @property
    def Width(self):
        return self._Width

    @Width.setter
    def Width(self, Width):
        self._Width = Width

    @property
    def NeedVideo(self):
        return self._NeedVideo

    @NeedVideo.setter
    def NeedVideo(self, NeedVideo):
        self._NeedVideo = NeedVideo

    @property
    def NeedAudio(self):
        return self._NeedAudio

    @NeedAudio.setter
    def NeedAudio(self, NeedAudio):
        self._NeedAudio = NeedAudio

    @property
    def Height(self):
        return self._Height

    @Height.setter
    def Height(self, Height):
        self._Height = Height

    @property
    def Fps(self):
        return self._Fps

    @Fps.setter
    def Fps(self, Fps):
        self._Fps = Fps

    @property
    def Gop(self):
        return self._Gop

    @Gop.setter
    def Gop(self, Gop):
        self._Gop = Gop

    @property
    def Rotate(self):
        return self._Rotate

    @Rotate.setter
    def Rotate(self, Rotate):
        self._Rotate = Rotate

    @property
    def Profile(self):
        return self._Profile

    @Profile.setter
    def Profile(self, Profile):
        self._Profile = Profile

    @property
    def BitrateToOrig(self):
        return self._BitrateToOrig

    @BitrateToOrig.setter
    def BitrateToOrig(self, BitrateToOrig):
        self._BitrateToOrig = BitrateToOrig

    @property
    def HeightToOrig(self):
        return self._HeightToOrig

    @HeightToOrig.setter
    def HeightToOrig(self, HeightToOrig):
        self._HeightToOrig = HeightToOrig

    @property
    def FpsToOrig(self):
        return self._FpsToOrig

    @FpsToOrig.setter
    def FpsToOrig(self, FpsToOrig):
        self._FpsToOrig = FpsToOrig

    @property
    def AdaptBitratePercent(self):
        return self._AdaptBitratePercent

    @AdaptBitratePercent.setter
    def AdaptBitratePercent(self, AdaptBitratePercent):
        self._AdaptBitratePercent = AdaptBitratePercent

    @property
    def ShortEdgeAsHeight(self):
        return self._ShortEdgeAsHeight

    @ShortEdgeAsHeight.setter
    def ShortEdgeAsHeight(self, ShortEdgeAsHeight):
        self._ShortEdgeAsHeight = ShortEdgeAsHeight

    @property
    def DRMType(self):
        return self._DRMType

    @DRMType.setter
    def DRMType(self, DRMType):
        self._DRMType = DRMType

    @property
    def DRMTracks(self):
        return self._DRMTracks

    @DRMTracks.setter
    def DRMTracks(self, DRMTracks):
        self._DRMTracks = DRMTracks


    def _deserialize(self, params):
        self._TemplateId = params.get("TemplateId")
        self._Vcodec = params.get("Vcodec")
        self._Acodec = params.get("Acodec")
        self._AudioBitrate = params.get("AudioBitrate")
        self._Description = params.get("Description")
        self._VideoBitrate = params.get("VideoBitrate")
        self._Width = params.get("Width")
        self._NeedVideo = params.get("NeedVideo")
        self._NeedAudio = params.get("NeedAudio")
        self._Height = params.get("Height")
        self._Fps = params.get("Fps")
        self._Gop = params.get("Gop")
        self._Rotate = params.get("Rotate")
        self._Profile = params.get("Profile")
        self._BitrateToOrig = params.get("BitrateToOrig")
        self._HeightToOrig = params.get("HeightToOrig")
        self._FpsToOrig = params.get("FpsToOrig")
        self._AdaptBitratePercent = params.get("AdaptBitratePercent")
        self._ShortEdgeAsHeight = params.get("ShortEdgeAsHeight")
        self._DRMType = params.get("DRMType")
        self._DRMTracks = params.get("DRMTracks")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyLiveTranscodeTemplateResponse(AbstractModel):
    """ModifyLiveTranscodeTemplate response structure.

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


class MonitorStreamPlayInfo(AbstractModel):
    """The playback data.

    """

    def __init__(self):
        r"""
        :param _PlayDomain: The playback domain.
        :type PlayDomain: str
        :param _StreamName: The stream ID.
        :type StreamName: str
        :param _Rate: The playback bitrate. `0` indicates the original bitrate.
        :type Rate: int
        :param _Protocol: The playback protocol. Valid values: `Unknown`, `Flv`, `Hls`, `Rtmp`, `Huyap2p`.
        :type Protocol: str
        :param _Bandwidth: The bandwidth (Mbps).
        :type Bandwidth: float
        :param _Online: The number of online users, which is represented by the number of TCP connections (data collected every minute).
        :type Online: int
        :param _Request: The number of requests.
        :type Request: int
        """
        self._PlayDomain = None
        self._StreamName = None
        self._Rate = None
        self._Protocol = None
        self._Bandwidth = None
        self._Online = None
        self._Request = None

    @property
    def PlayDomain(self):
        return self._PlayDomain

    @PlayDomain.setter
    def PlayDomain(self, PlayDomain):
        self._PlayDomain = PlayDomain

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def Rate(self):
        return self._Rate

    @Rate.setter
    def Rate(self, Rate):
        self._Rate = Rate

    @property
    def Protocol(self):
        return self._Protocol

    @Protocol.setter
    def Protocol(self, Protocol):
        self._Protocol = Protocol

    @property
    def Bandwidth(self):
        return self._Bandwidth

    @Bandwidth.setter
    def Bandwidth(self, Bandwidth):
        self._Bandwidth = Bandwidth

    @property
    def Online(self):
        return self._Online

    @Online.setter
    def Online(self, Online):
        self._Online = Online

    @property
    def Request(self):
        return self._Request

    @Request.setter
    def Request(self, Request):
        self._Request = Request


    def _deserialize(self, params):
        self._PlayDomain = params.get("PlayDomain")
        self._StreamName = params.get("StreamName")
        self._Rate = params.get("Rate")
        self._Protocol = params.get("Protocol")
        self._Bandwidth = params.get("Bandwidth")
        self._Online = params.get("Online")
        self._Request = params.get("Request")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class PlayAuthKeyInfo(AbstractModel):
    """Playback authentication key information.

    """

    def __init__(self):
        r"""
        :param _DomainName: Domain name.
        :type DomainName: str
        :param _Enable: Whether to enable:
0: disable.
1: enable.
        :type Enable: int
        :param _AuthKey: Authentication key.
        :type AuthKey: str
        :param _AuthDelta: Validity period in seconds.
        :type AuthDelta: int
        :param _AuthBackKey: Authentication `BackKey`.
        :type AuthBackKey: str
        """
        self._DomainName = None
        self._Enable = None
        self._AuthKey = None
        self._AuthDelta = None
        self._AuthBackKey = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def Enable(self):
        return self._Enable

    @Enable.setter
    def Enable(self, Enable):
        self._Enable = Enable

    @property
    def AuthKey(self):
        return self._AuthKey

    @AuthKey.setter
    def AuthKey(self, AuthKey):
        self._AuthKey = AuthKey

    @property
    def AuthDelta(self):
        return self._AuthDelta

    @AuthDelta.setter
    def AuthDelta(self, AuthDelta):
        self._AuthDelta = AuthDelta

    @property
    def AuthBackKey(self):
        return self._AuthBackKey

    @AuthBackKey.setter
    def AuthBackKey(self, AuthBackKey):
        self._AuthBackKey = AuthBackKey


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._Enable = params.get("Enable")
        self._AuthKey = params.get("AuthKey")
        self._AuthDelta = params.get("AuthDelta")
        self._AuthBackKey = params.get("AuthBackKey")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class PlayCodeTotalInfo(AbstractModel):
    """Total occurrences of each status code. Most HTTP return codes are supported.

    """

    def __init__(self):
        r"""
        :param _Code: HTTP code. Valid values:
400, 403, 404, 500, 502, 503, 504.
        :type Code: str
        :param _Num: Total occurrences.
        :type Num: int
        """
        self._Code = None
        self._Num = None

    @property
    def Code(self):
        return self._Code

    @Code.setter
    def Code(self, Code):
        self._Code = Code

    @property
    def Num(self):
        return self._Num

    @Num.setter
    def Num(self, Num):
        self._Num = Num


    def _deserialize(self, params):
        self._Code = params.get("Code")
        self._Num = params.get("Num")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class PlayDataInfoByStream(AbstractModel):
    """Playback information at the stream level.

    """

    def __init__(self):
        r"""
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _TotalFlux: Total traffic in MB.
        :type TotalFlux: float
        """
        self._StreamName = None
        self._TotalFlux = None

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def TotalFlux(self):
        return self._TotalFlux

    @TotalFlux.setter
    def TotalFlux(self, TotalFlux):
        self._TotalFlux = TotalFlux


    def _deserialize(self, params):
        self._StreamName = params.get("StreamName")
        self._TotalFlux = params.get("TotalFlux")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class PlayStatInfo(AbstractModel):
    """Queries the playback information by ISP and district.

    """

    def __init__(self):
        r"""
        :param _Time: Data point in time.
        :type Time: str
        :param _Value: Value of bandwidth/traffic/number of requests/number of concurrent connections/download speed. If there is no data returned, the value is 0.
Note: this field may return null, indicating that no valid values can be obtained.
        :type Value: float
        """
        self._Time = None
        self._Value = None

    @property
    def Time(self):
        return self._Time

    @Time.setter
    def Time(self, Time):
        self._Time = Time

    @property
    def Value(self):
        return self._Value

    @Value.setter
    def Value(self, Value):
        self._Value = Value


    def _deserialize(self, params):
        self._Time = params.get("Time")
        self._Value = params.get("Value")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class PlaySumStatInfo(AbstractModel):
    """Aggregated playback statistics.

    """

    def __init__(self):
        r"""
        :param _Name: Domain name or stream ID.
        :type Name: str
        :param _AvgFluxPerSecond: Average download speed,
In MB/s.
Calculation formula: average download speed per minute.
        :type AvgFluxPerSecond: float
        :param _TotalFlux: Total traffic in MB.
        :type TotalFlux: float
        :param _TotalRequest: Total number of requests.
        :type TotalRequest: int
        """
        self._Name = None
        self._AvgFluxPerSecond = None
        self._TotalFlux = None
        self._TotalRequest = None

    @property
    def Name(self):
        return self._Name

    @Name.setter
    def Name(self, Name):
        self._Name = Name

    @property
    def AvgFluxPerSecond(self):
        return self._AvgFluxPerSecond

    @AvgFluxPerSecond.setter
    def AvgFluxPerSecond(self, AvgFluxPerSecond):
        self._AvgFluxPerSecond = AvgFluxPerSecond

    @property
    def TotalFlux(self):
        return self._TotalFlux

    @TotalFlux.setter
    def TotalFlux(self, TotalFlux):
        self._TotalFlux = TotalFlux

    @property
    def TotalRequest(self):
        return self._TotalRequest

    @TotalRequest.setter
    def TotalRequest(self, TotalRequest):
        self._TotalRequest = TotalRequest


    def _deserialize(self, params):
        self._Name = params.get("Name")
        self._AvgFluxPerSecond = params.get("AvgFluxPerSecond")
        self._TotalFlux = params.get("TotalFlux")
        self._TotalRequest = params.get("TotalRequest")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ProIspPlayCodeDataInfo(AbstractModel):
    """Playback error code information

    """

    def __init__(self):
        r"""
        :param _CountryAreaName: Country or region.
        :type CountryAreaName: str
        :param _ProvinceName: District.
        :type ProvinceName: str
        :param _IspName: ISP.
        :type IspName: str
        :param _Code2xx: Occurrences of 2xx error codes.
        :type Code2xx: int
        :param _Code3xx: Occurrences of 3xx error codes.
        :type Code3xx: int
        :param _Code4xx: Occurrences of 4xx error codes.
        :type Code4xx: int
        :param _Code5xx: Occurrences of 5xx error codes.
        :type Code5xx: int
        """
        self._CountryAreaName = None
        self._ProvinceName = None
        self._IspName = None
        self._Code2xx = None
        self._Code3xx = None
        self._Code4xx = None
        self._Code5xx = None

    @property
    def CountryAreaName(self):
        return self._CountryAreaName

    @CountryAreaName.setter
    def CountryAreaName(self, CountryAreaName):
        self._CountryAreaName = CountryAreaName

    @property
    def ProvinceName(self):
        return self._ProvinceName

    @ProvinceName.setter
    def ProvinceName(self, ProvinceName):
        self._ProvinceName = ProvinceName

    @property
    def IspName(self):
        return self._IspName

    @IspName.setter
    def IspName(self, IspName):
        self._IspName = IspName

    @property
    def Code2xx(self):
        return self._Code2xx

    @Code2xx.setter
    def Code2xx(self, Code2xx):
        self._Code2xx = Code2xx

    @property
    def Code3xx(self):
        return self._Code3xx

    @Code3xx.setter
    def Code3xx(self, Code3xx):
        self._Code3xx = Code3xx

    @property
    def Code4xx(self):
        return self._Code4xx

    @Code4xx.setter
    def Code4xx(self, Code4xx):
        self._Code4xx = Code4xx

    @property
    def Code5xx(self):
        return self._Code5xx

    @Code5xx.setter
    def Code5xx(self, Code5xx):
        self._Code5xx = Code5xx


    def _deserialize(self, params):
        self._CountryAreaName = params.get("CountryAreaName")
        self._ProvinceName = params.get("ProvinceName")
        self._IspName = params.get("IspName")
        self._Code2xx = params.get("Code2xx")
        self._Code3xx = params.get("Code3xx")
        self._Code4xx = params.get("Code4xx")
        self._Code5xx = params.get("Code5xx")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class PublishTime(AbstractModel):
    """Push time.

    """

    def __init__(self):
        r"""
        :param _PublishTime: Push time.
In UTC format, such as 2018-06-29T19:00:00Z.
        :type PublishTime: str
        """
        self._PublishTime = None

    @property
    def PublishTime(self):
        return self._PublishTime

    @PublishTime.setter
    def PublishTime(self, PublishTime):
        self._PublishTime = PublishTime


    def _deserialize(self, params):
        self._PublishTime = params.get("PublishTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class PullPushWatermarkInfo(AbstractModel):
    """The watermark configuration for a relay task.

    """

    def __init__(self):
        r"""
        :param _PictureUrl: The watermark image URL.
Characters not allowed:
;(){}$>`#"'|
        :type PictureUrl: str
        :param _XPosition: The horizontal offset (%) of the watermark. The default value is 0.
        :type XPosition: int
        :param _YPosition: The vertical offset (%) of the watermark. The default value is 0.
        :type YPosition: int
        :param _Width: The watermark width as a percentage of the video width. To avoid distorted images, we recommend you specify only the width or height so that the other side can be scaled proportionally. By default, the original width of the watermark image is used.
        :type Width: int
        :param _Height: The watermark height as a percentage of the video height. To avoid distorted images, we recommend you specify only the width or height so that the other side can be scaled proportionally. By default, the original height of the watermark image is used.
        :type Height: int
        :param _Location: The origin. The default value is 0.
0: Top left corner
1: Top right corner
2: Bottom right corner
3: Bottom left corner
        :type Location: int
        """
        self._PictureUrl = None
        self._XPosition = None
        self._YPosition = None
        self._Width = None
        self._Height = None
        self._Location = None

    @property
    def PictureUrl(self):
        return self._PictureUrl

    @PictureUrl.setter
    def PictureUrl(self, PictureUrl):
        self._PictureUrl = PictureUrl

    @property
    def XPosition(self):
        return self._XPosition

    @XPosition.setter
    def XPosition(self, XPosition):
        self._XPosition = XPosition

    @property
    def YPosition(self):
        return self._YPosition

    @YPosition.setter
    def YPosition(self, YPosition):
        self._YPosition = YPosition

    @property
    def Width(self):
        return self._Width

    @Width.setter
    def Width(self, Width):
        self._Width = Width

    @property
    def Height(self):
        return self._Height

    @Height.setter
    def Height(self, Height):
        self._Height = Height

    @property
    def Location(self):
        return self._Location

    @Location.setter
    def Location(self, Location):
        self._Location = Location


    def _deserialize(self, params):
        self._PictureUrl = params.get("PictureUrl")
        self._XPosition = params.get("XPosition")
        self._YPosition = params.get("YPosition")
        self._Width = params.get("Width")
        self._Height = params.get("Height")
        self._Location = params.get("Location")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class PullStreamTaskInfo(AbstractModel):
    """The information of a stream pulling task.

    """

    def __init__(self):
        r"""
        :param _TaskId: The task ID.
        :type TaskId: str
        :param _SourceType: The source type. Valid values:
PullLivePushLive: Live streaming
PullVodPushLive: Video files
PullPicPushLive: Images
        :type SourceType: str
        :param _SourceUrls: The source URL(s).
If `SourceType` is `PullLiveToLive`, there can be only one source URL.
If `SourceType` is `PullVodToLive`, there can be at most 10 source URLs.
        :type SourceUrls: list of str
        :param _DomainName: The push domain name.
The pulled stream is pushed to this domain.
        :type DomainName: str
        :param _AppName: The application to push to.
The pulled stream is pushed to this application.
        :type AppName: str
        :param _StreamName: The stream name.
The pulled stream is pushed under this name.
        :type StreamName: str
        :param _PushArgs: The push parameter.
A custom push parameter.
        :type PushArgs: str
        :param _StartTime: The start time.
It must be in UTC format.
Example: 2019-01-08T10:00:00Z.
Note: Beijing time is 8 hours ahead of UTC. The [ISO 8601 format](https://intl.cloud.tencent.com/document/product/266/11732#iso-date-format) is used.
        :type StartTime: str
        :param _EndTime: The end time. Notes:
1. The end time must be later than the start time.
2. The end time and start time must be later than the current time.
3. The end time and start time must be less than seven days apart.
It must be in UTC format.
Example: 2019-01-08T10:00:00Z.
Note: Beijing time is 8 hours ahead of UTC. The [ISO 8601 format](https://intl.cloud.tencent.com/document/product/266/11732#iso-date-format) is used.
        :type EndTime: str
        :param _Region: The region where the task was created.
`ap-beijing`: North China (Beijing)
`ap-shanghai`: East China (Shanghai)
`ap-guangzhou`: South China (Guangzhou)
`ap-mumbai`: India
`ap-hongkong`: Hong Kong
`eu-frankfurt`: Germany
`ap-seoul`: Korea
`ap-bangkok`: Thailand
`ap-singapore`: Singapore
`na-siliconvalley`: Western US
`na-ashburn`: Eastern US
`ap-tokyo`: Japan
        :type Region: str
        :param _VodLoopTimes: The number of times to loop video files.
-1: Loop indefinitely
0: Do not loop
> 0: The number of loop times. A task will end either when the videos are looped for the specified number of times or at the specified task end time, whichever is earlier.
This parameter is valid only if the source is video files.
        :type VodLoopTimes: int
        :param _VodRefreshType: The behavior after the source video files (`SourceUrls`) are changed.
ImmediateNewSource: Play the new videos immediately
ContinueBreakPoint: Finish the current video first and then pull from the new source.

This parameter is valid only if the source is video files.
        :type VodRefreshType: str
        :param _CreateTime: The task creation time.
It must be in UTC format.
Example: 2019-01-08T10:00:00Z.
Note: Beijing time is 8 hours ahead of UTC. The [ISO 8601 format](https://intl.cloud.tencent.com/document/product/266/11732#iso-date-format) is used.
        :type CreateTime: str
        :param _UpdateTime: The last updated time.
It must be in UTC format.
Example: 2019-01-08T10:00:00Z.
Note: Beijing time is 8 hours ahead of UTC. The [ISO 8601 format](https://intl.cloud.tencent.com/document/product/266/11732#iso-date-format) is used.
        :type UpdateTime: str
        :param _CreateBy: The task creator.
        :type CreateBy: str
        :param _UpdateBy: The operator of the last update.
        :type UpdateBy: str
        :param _CallbackUrl: The callback URL.
        :type CallbackUrl: str
        :param _CallbackEvents: The events to listen for.
TaskStart: Callback for starting a task
TaskExit: Callback for ending a task
VodSourceFileStart: Callback for starting to pull from video files
VodSourceFileFinish: Callback for stopping pulling from video files
ResetTaskConfig: Callback for modifying a task
        :type CallbackEvents: list of str
        :param _CallbackInfo: Note: This parameter is not returned currently.
The information of the last callback.
        :type CallbackInfo: str
        :param _ErrorInfo: Note: This parameter is not returned currently.
Error message.
        :type ErrorInfo: str
        :param _Status: The task status.
enable: Enabled
pause: Paused
        :type Status: str
        :param _RecentPullInfo: Note: This parameter is returned only if one task is queried.
The latest pull information.
The information includes the source URL, offset, and report time.
        :type RecentPullInfo: :class:`tencentcloud.live.v20180801.models.RecentPullInfo`
        :param _Comment: The remarks for the task.
        :type Comment: str
        :param _BackupSourceType: The backup source type. Valid values:
PullLivePushLive: Live streaming
PullVodPushLive: Video files
Note: This field may return null, indicating that no valid values can be obtained.
        :type BackupSourceType: str
        :param _BackupSourceUrl: The URL of the backup source.
Note: This field may return null, indicating that no valid values can be obtained.
        :type BackupSourceUrl: str
        :param _WatermarkList: The information of watermarks to add.
Note: This field may return null, indicating that no valid values can be obtained.
        :type WatermarkList: list of PullPushWatermarkInfo
        :param _VodLocalMode: Whether to use local mode when the source type is video files. The default is `0`.
0: Do not use local mode
1: Use local mode
Note: This field may return null, indicating that no valid values can be obtained.
        :type VodLocalMode: int
        """
        self._TaskId = None
        self._SourceType = None
        self._SourceUrls = None
        self._DomainName = None
        self._AppName = None
        self._StreamName = None
        self._PushArgs = None
        self._StartTime = None
        self._EndTime = None
        self._Region = None
        self._VodLoopTimes = None
        self._VodRefreshType = None
        self._CreateTime = None
        self._UpdateTime = None
        self._CreateBy = None
        self._UpdateBy = None
        self._CallbackUrl = None
        self._CallbackEvents = None
        self._CallbackInfo = None
        self._ErrorInfo = None
        self._Status = None
        self._RecentPullInfo = None
        self._Comment = None
        self._BackupSourceType = None
        self._BackupSourceUrl = None
        self._WatermarkList = None
        self._VodLocalMode = None

    @property
    def TaskId(self):
        return self._TaskId

    @TaskId.setter
    def TaskId(self, TaskId):
        self._TaskId = TaskId

    @property
    def SourceType(self):
        return self._SourceType

    @SourceType.setter
    def SourceType(self, SourceType):
        self._SourceType = SourceType

    @property
    def SourceUrls(self):
        return self._SourceUrls

    @SourceUrls.setter
    def SourceUrls(self, SourceUrls):
        self._SourceUrls = SourceUrls

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def PushArgs(self):
        return self._PushArgs

    @PushArgs.setter
    def PushArgs(self, PushArgs):
        self._PushArgs = PushArgs

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
    def Region(self):
        return self._Region

    @Region.setter
    def Region(self, Region):
        self._Region = Region

    @property
    def VodLoopTimes(self):
        return self._VodLoopTimes

    @VodLoopTimes.setter
    def VodLoopTimes(self, VodLoopTimes):
        self._VodLoopTimes = VodLoopTimes

    @property
    def VodRefreshType(self):
        return self._VodRefreshType

    @VodRefreshType.setter
    def VodRefreshType(self, VodRefreshType):
        self._VodRefreshType = VodRefreshType

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
    def CreateBy(self):
        return self._CreateBy

    @CreateBy.setter
    def CreateBy(self, CreateBy):
        self._CreateBy = CreateBy

    @property
    def UpdateBy(self):
        return self._UpdateBy

    @UpdateBy.setter
    def UpdateBy(self, UpdateBy):
        self._UpdateBy = UpdateBy

    @property
    def CallbackUrl(self):
        return self._CallbackUrl

    @CallbackUrl.setter
    def CallbackUrl(self, CallbackUrl):
        self._CallbackUrl = CallbackUrl

    @property
    def CallbackEvents(self):
        return self._CallbackEvents

    @CallbackEvents.setter
    def CallbackEvents(self, CallbackEvents):
        self._CallbackEvents = CallbackEvents

    @property
    def CallbackInfo(self):
        return self._CallbackInfo

    @CallbackInfo.setter
    def CallbackInfo(self, CallbackInfo):
        self._CallbackInfo = CallbackInfo

    @property
    def ErrorInfo(self):
        return self._ErrorInfo

    @ErrorInfo.setter
    def ErrorInfo(self, ErrorInfo):
        self._ErrorInfo = ErrorInfo

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status

    @property
    def RecentPullInfo(self):
        return self._RecentPullInfo

    @RecentPullInfo.setter
    def RecentPullInfo(self, RecentPullInfo):
        self._RecentPullInfo = RecentPullInfo

    @property
    def Comment(self):
        return self._Comment

    @Comment.setter
    def Comment(self, Comment):
        self._Comment = Comment

    @property
    def BackupSourceType(self):
        return self._BackupSourceType

    @BackupSourceType.setter
    def BackupSourceType(self, BackupSourceType):
        self._BackupSourceType = BackupSourceType

    @property
    def BackupSourceUrl(self):
        return self._BackupSourceUrl

    @BackupSourceUrl.setter
    def BackupSourceUrl(self, BackupSourceUrl):
        self._BackupSourceUrl = BackupSourceUrl

    @property
    def WatermarkList(self):
        return self._WatermarkList

    @WatermarkList.setter
    def WatermarkList(self, WatermarkList):
        self._WatermarkList = WatermarkList

    @property
    def VodLocalMode(self):
        return self._VodLocalMode

    @VodLocalMode.setter
    def VodLocalMode(self, VodLocalMode):
        self._VodLocalMode = VodLocalMode


    def _deserialize(self, params):
        self._TaskId = params.get("TaskId")
        self._SourceType = params.get("SourceType")
        self._SourceUrls = params.get("SourceUrls")
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        self._PushArgs = params.get("PushArgs")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._Region = params.get("Region")
        self._VodLoopTimes = params.get("VodLoopTimes")
        self._VodRefreshType = params.get("VodRefreshType")
        self._CreateTime = params.get("CreateTime")
        self._UpdateTime = params.get("UpdateTime")
        self._CreateBy = params.get("CreateBy")
        self._UpdateBy = params.get("UpdateBy")
        self._CallbackUrl = params.get("CallbackUrl")
        self._CallbackEvents = params.get("CallbackEvents")
        self._CallbackInfo = params.get("CallbackInfo")
        self._ErrorInfo = params.get("ErrorInfo")
        self._Status = params.get("Status")
        if params.get("RecentPullInfo") is not None:
            self._RecentPullInfo = RecentPullInfo()
            self._RecentPullInfo._deserialize(params.get("RecentPullInfo"))
        self._Comment = params.get("Comment")
        self._BackupSourceType = params.get("BackupSourceType")
        self._BackupSourceUrl = params.get("BackupSourceUrl")
        if params.get("WatermarkList") is not None:
            self._WatermarkList = []
            for item in params.get("WatermarkList"):
                obj = PullPushWatermarkInfo()
                obj._deserialize(item)
                self._WatermarkList.append(obj)
        self._VodLocalMode = params.get("VodLocalMode")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class PushAuthKeyInfo(AbstractModel):
    """Push authentication key information.

    """

    def __init__(self):
        r"""
        :param _DomainName: Domain name.
        :type DomainName: str
        :param _Enable: Whether to enable. 0: disabled; 1: enabled.
        :type Enable: int
        :param _MasterAuthKey: Master authentication key.
        :type MasterAuthKey: str
        :param _BackupAuthKey: Standby authentication key.
        :type BackupAuthKey: str
        :param _AuthDelta: Validity period in seconds.
        :type AuthDelta: int
        """
        self._DomainName = None
        self._Enable = None
        self._MasterAuthKey = None
        self._BackupAuthKey = None
        self._AuthDelta = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def Enable(self):
        return self._Enable

    @Enable.setter
    def Enable(self, Enable):
        self._Enable = Enable

    @property
    def MasterAuthKey(self):
        return self._MasterAuthKey

    @MasterAuthKey.setter
    def MasterAuthKey(self, MasterAuthKey):
        self._MasterAuthKey = MasterAuthKey

    @property
    def BackupAuthKey(self):
        return self._BackupAuthKey

    @BackupAuthKey.setter
    def BackupAuthKey(self, BackupAuthKey):
        self._BackupAuthKey = BackupAuthKey

    @property
    def AuthDelta(self):
        return self._AuthDelta

    @AuthDelta.setter
    def AuthDelta(self, AuthDelta):
        self._AuthDelta = AuthDelta


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._Enable = params.get("Enable")
        self._MasterAuthKey = params.get("MasterAuthKey")
        self._BackupAuthKey = params.get("BackupAuthKey")
        self._AuthDelta = params.get("AuthDelta")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class PushDataInfo(AbstractModel):
    """Push information

    """

    def __init__(self):
        r"""
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _AppName: Push path.
        :type AppName: str
        :param _ClientIp: Push client IP.
        :type ClientIp: str
        :param _ServerIp: IP of the server that receives the stream.
        :type ServerIp: str
        :param _VideoFps: Pushed video frame rate in Hz.
        :type VideoFps: int
        :param _VideoSpeed: Video bitrate (bps) for publishing
        :type VideoSpeed: int
        :param _AudioFps: Pushed audio frame rate in Hz.
        :type AudioFps: int
        :param _AudioSpeed: Audio bitrate (bps) for publishing
        :type AudioSpeed: int
        :param _PushDomain: Push domain name.
        :type PushDomain: str
        :param _BeginPushTime: Push start time.
        :type BeginPushTime: str
        :param _Acodec: Audio codec,
Example: AAC.
        :type Acodec: str
        :param _Vcodec: Video codec,
Example: H.264.
        :type Vcodec: str
        :param _Resolution: Resolution.
        :type Resolution: str
        :param _AsampleRate: Sample rate.
        :type AsampleRate: int
        :param _MetaAudioSpeed: Audio bitrate (bps) in metadata
        :type MetaAudioSpeed: int
        :param _MetaVideoSpeed: Video bitrate (bps) in metadata
        :type MetaVideoSpeed: int
        :param _MetaFps: Frame rate in `metadata`.
        :type MetaFps: int
        """
        self._StreamName = None
        self._AppName = None
        self._ClientIp = None
        self._ServerIp = None
        self._VideoFps = None
        self._VideoSpeed = None
        self._AudioFps = None
        self._AudioSpeed = None
        self._PushDomain = None
        self._BeginPushTime = None
        self._Acodec = None
        self._Vcodec = None
        self._Resolution = None
        self._AsampleRate = None
        self._MetaAudioSpeed = None
        self._MetaVideoSpeed = None
        self._MetaFps = None

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def ClientIp(self):
        return self._ClientIp

    @ClientIp.setter
    def ClientIp(self, ClientIp):
        self._ClientIp = ClientIp

    @property
    def ServerIp(self):
        return self._ServerIp

    @ServerIp.setter
    def ServerIp(self, ServerIp):
        self._ServerIp = ServerIp

    @property
    def VideoFps(self):
        return self._VideoFps

    @VideoFps.setter
    def VideoFps(self, VideoFps):
        self._VideoFps = VideoFps

    @property
    def VideoSpeed(self):
        return self._VideoSpeed

    @VideoSpeed.setter
    def VideoSpeed(self, VideoSpeed):
        self._VideoSpeed = VideoSpeed

    @property
    def AudioFps(self):
        return self._AudioFps

    @AudioFps.setter
    def AudioFps(self, AudioFps):
        self._AudioFps = AudioFps

    @property
    def AudioSpeed(self):
        return self._AudioSpeed

    @AudioSpeed.setter
    def AudioSpeed(self, AudioSpeed):
        self._AudioSpeed = AudioSpeed

    @property
    def PushDomain(self):
        return self._PushDomain

    @PushDomain.setter
    def PushDomain(self, PushDomain):
        self._PushDomain = PushDomain

    @property
    def BeginPushTime(self):
        return self._BeginPushTime

    @BeginPushTime.setter
    def BeginPushTime(self, BeginPushTime):
        self._BeginPushTime = BeginPushTime

    @property
    def Acodec(self):
        return self._Acodec

    @Acodec.setter
    def Acodec(self, Acodec):
        self._Acodec = Acodec

    @property
    def Vcodec(self):
        return self._Vcodec

    @Vcodec.setter
    def Vcodec(self, Vcodec):
        self._Vcodec = Vcodec

    @property
    def Resolution(self):
        return self._Resolution

    @Resolution.setter
    def Resolution(self, Resolution):
        self._Resolution = Resolution

    @property
    def AsampleRate(self):
        return self._AsampleRate

    @AsampleRate.setter
    def AsampleRate(self, AsampleRate):
        self._AsampleRate = AsampleRate

    @property
    def MetaAudioSpeed(self):
        return self._MetaAudioSpeed

    @MetaAudioSpeed.setter
    def MetaAudioSpeed(self, MetaAudioSpeed):
        self._MetaAudioSpeed = MetaAudioSpeed

    @property
    def MetaVideoSpeed(self):
        return self._MetaVideoSpeed

    @MetaVideoSpeed.setter
    def MetaVideoSpeed(self, MetaVideoSpeed):
        self._MetaVideoSpeed = MetaVideoSpeed

    @property
    def MetaFps(self):
        return self._MetaFps

    @MetaFps.setter
    def MetaFps(self, MetaFps):
        self._MetaFps = MetaFps


    def _deserialize(self, params):
        self._StreamName = params.get("StreamName")
        self._AppName = params.get("AppName")
        self._ClientIp = params.get("ClientIp")
        self._ServerIp = params.get("ServerIp")
        self._VideoFps = params.get("VideoFps")
        self._VideoSpeed = params.get("VideoSpeed")
        self._AudioFps = params.get("AudioFps")
        self._AudioSpeed = params.get("AudioSpeed")
        self._PushDomain = params.get("PushDomain")
        self._BeginPushTime = params.get("BeginPushTime")
        self._Acodec = params.get("Acodec")
        self._Vcodec = params.get("Vcodec")
        self._Resolution = params.get("Resolution")
        self._AsampleRate = params.get("AsampleRate")
        self._MetaAudioSpeed = params.get("MetaAudioSpeed")
        self._MetaVideoSpeed = params.get("MetaVideoSpeed")
        self._MetaFps = params.get("MetaFps")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class PushQualityData(AbstractModel):
    """The push data of a stream.

    """

    def __init__(self):
        r"""
        :param _Time: The time of the data in the format of “%Y-%m-%d %H:%M:%S.%ms” (accurate to the millisecond).
        :type Time: str
        :param _PushDomain: The push domain.
        :type PushDomain: str
        :param _AppName: The push path.
        :type AppName: str
        :param _ClientIp: The IP address of the push client.
        :type ClientIp: str
        :param _BeginPushTime: The push start time in the format of “%Y-%m-%d %H:%M:%S.%ms” (accurate to the millisecond).
        :type BeginPushTime: str
        :param _Resolution: The resolution.
        :type Resolution: str
        :param _VCodec: The video codec.
        :type VCodec: str
        :param _ACodec: The audio codec.
        :type ACodec: str
        :param _Sequence: The push sequence number, which uniquely identifies a push.
        :type Sequence: str
        :param _VideoFps: The video frame rate.
        :type VideoFps: int
        :param _VideoRate: The video bitrate (bps).
        :type VideoRate: int
        :param _AudioFps: The audio frame rate.
        :type AudioFps: int
        :param _AudioRate: The audio bitrate (bps).
        :type AudioRate: int
        :param _LocalTs: The local elapsed time (milliseconds). The greater the difference between the local elapsed time and audio/video elapsed time, the poorer the push quality and the more severe the upstream lag.
        :type LocalTs: int
        :param _VideoTs: The video elapsed time (milliseconds).
        :type VideoTs: int
        :param _AudioTs: The audio elapsed time (milliseconds).
        :type AudioTs: int
        :param _MetaVideoRate: The video bitrate (Kbps) in the metadata.
        :type MetaVideoRate: int
        :param _MetaAudioRate: The audio bitrate (Kbps) in the metadata.
        :type MetaAudioRate: int
        :param _MateFps: The frame rate in the metadata.
        :type MateFps: int
        :param _StreamParam: The push parameter.
        :type StreamParam: str
        :param _Bandwidth: The bandwidth (Mbps).
        :type Bandwidth: float
        :param _Flux: The traffic (MB).
        :type Flux: float
        :param _ServerIp: The IP address of the push client.
Note: This field may return null, indicating that no valid values can be obtained.
        :type ServerIp: str
        """
        self._Time = None
        self._PushDomain = None
        self._AppName = None
        self._ClientIp = None
        self._BeginPushTime = None
        self._Resolution = None
        self._VCodec = None
        self._ACodec = None
        self._Sequence = None
        self._VideoFps = None
        self._VideoRate = None
        self._AudioFps = None
        self._AudioRate = None
        self._LocalTs = None
        self._VideoTs = None
        self._AudioTs = None
        self._MetaVideoRate = None
        self._MetaAudioRate = None
        self._MateFps = None
        self._StreamParam = None
        self._Bandwidth = None
        self._Flux = None
        self._ServerIp = None

    @property
    def Time(self):
        return self._Time

    @Time.setter
    def Time(self, Time):
        self._Time = Time

    @property
    def PushDomain(self):
        return self._PushDomain

    @PushDomain.setter
    def PushDomain(self, PushDomain):
        self._PushDomain = PushDomain

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def ClientIp(self):
        return self._ClientIp

    @ClientIp.setter
    def ClientIp(self, ClientIp):
        self._ClientIp = ClientIp

    @property
    def BeginPushTime(self):
        return self._BeginPushTime

    @BeginPushTime.setter
    def BeginPushTime(self, BeginPushTime):
        self._BeginPushTime = BeginPushTime

    @property
    def Resolution(self):
        return self._Resolution

    @Resolution.setter
    def Resolution(self, Resolution):
        self._Resolution = Resolution

    @property
    def VCodec(self):
        return self._VCodec

    @VCodec.setter
    def VCodec(self, VCodec):
        self._VCodec = VCodec

    @property
    def ACodec(self):
        return self._ACodec

    @ACodec.setter
    def ACodec(self, ACodec):
        self._ACodec = ACodec

    @property
    def Sequence(self):
        return self._Sequence

    @Sequence.setter
    def Sequence(self, Sequence):
        self._Sequence = Sequence

    @property
    def VideoFps(self):
        return self._VideoFps

    @VideoFps.setter
    def VideoFps(self, VideoFps):
        self._VideoFps = VideoFps

    @property
    def VideoRate(self):
        return self._VideoRate

    @VideoRate.setter
    def VideoRate(self, VideoRate):
        self._VideoRate = VideoRate

    @property
    def AudioFps(self):
        return self._AudioFps

    @AudioFps.setter
    def AudioFps(self, AudioFps):
        self._AudioFps = AudioFps

    @property
    def AudioRate(self):
        return self._AudioRate

    @AudioRate.setter
    def AudioRate(self, AudioRate):
        self._AudioRate = AudioRate

    @property
    def LocalTs(self):
        return self._LocalTs

    @LocalTs.setter
    def LocalTs(self, LocalTs):
        self._LocalTs = LocalTs

    @property
    def VideoTs(self):
        return self._VideoTs

    @VideoTs.setter
    def VideoTs(self, VideoTs):
        self._VideoTs = VideoTs

    @property
    def AudioTs(self):
        return self._AudioTs

    @AudioTs.setter
    def AudioTs(self, AudioTs):
        self._AudioTs = AudioTs

    @property
    def MetaVideoRate(self):
        return self._MetaVideoRate

    @MetaVideoRate.setter
    def MetaVideoRate(self, MetaVideoRate):
        self._MetaVideoRate = MetaVideoRate

    @property
    def MetaAudioRate(self):
        return self._MetaAudioRate

    @MetaAudioRate.setter
    def MetaAudioRate(self, MetaAudioRate):
        self._MetaAudioRate = MetaAudioRate

    @property
    def MateFps(self):
        return self._MateFps

    @MateFps.setter
    def MateFps(self, MateFps):
        self._MateFps = MateFps

    @property
    def StreamParam(self):
        return self._StreamParam

    @StreamParam.setter
    def StreamParam(self, StreamParam):
        self._StreamParam = StreamParam

    @property
    def Bandwidth(self):
        return self._Bandwidth

    @Bandwidth.setter
    def Bandwidth(self, Bandwidth):
        self._Bandwidth = Bandwidth

    @property
    def Flux(self):
        return self._Flux

    @Flux.setter
    def Flux(self, Flux):
        self._Flux = Flux

    @property
    def ServerIp(self):
        return self._ServerIp

    @ServerIp.setter
    def ServerIp(self, ServerIp):
        self._ServerIp = ServerIp


    def _deserialize(self, params):
        self._Time = params.get("Time")
        self._PushDomain = params.get("PushDomain")
        self._AppName = params.get("AppName")
        self._ClientIp = params.get("ClientIp")
        self._BeginPushTime = params.get("BeginPushTime")
        self._Resolution = params.get("Resolution")
        self._VCodec = params.get("VCodec")
        self._ACodec = params.get("ACodec")
        self._Sequence = params.get("Sequence")
        self._VideoFps = params.get("VideoFps")
        self._VideoRate = params.get("VideoRate")
        self._AudioFps = params.get("AudioFps")
        self._AudioRate = params.get("AudioRate")
        self._LocalTs = params.get("LocalTs")
        self._VideoTs = params.get("VideoTs")
        self._AudioTs = params.get("AudioTs")
        self._MetaVideoRate = params.get("MetaVideoRate")
        self._MetaAudioRate = params.get("MetaAudioRate")
        self._MateFps = params.get("MateFps")
        self._StreamParam = params.get("StreamParam")
        self._Bandwidth = params.get("Bandwidth")
        self._Flux = params.get("Flux")
        self._ServerIp = params.get("ServerIp")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class RecentPullInfo(AbstractModel):
    """The latest pull information.

    """

    def __init__(self):
        r"""
        :param _FileUrl: The URL of the file currently pulled.
        :type FileUrl: str
        :param _OffsetTime: The offset of the file currently pulled.
        :type OffsetTime: int
        :param _ReportTime: The time when the offset is reported, in UTC format.
Example: 2020-07-23T03:20:39Z
Note: Beijing time is 8 hours ahead of UTC.
        :type ReportTime: str
        :param _LoopedTimes: The number of times looped.
        :type LoopedTimes: int
        """
        self._FileUrl = None
        self._OffsetTime = None
        self._ReportTime = None
        self._LoopedTimes = None

    @property
    def FileUrl(self):
        return self._FileUrl

    @FileUrl.setter
    def FileUrl(self, FileUrl):
        self._FileUrl = FileUrl

    @property
    def OffsetTime(self):
        return self._OffsetTime

    @OffsetTime.setter
    def OffsetTime(self, OffsetTime):
        self._OffsetTime = OffsetTime

    @property
    def ReportTime(self):
        return self._ReportTime

    @ReportTime.setter
    def ReportTime(self, ReportTime):
        self._ReportTime = ReportTime

    @property
    def LoopedTimes(self):
        return self._LoopedTimes

    @LoopedTimes.setter
    def LoopedTimes(self, LoopedTimes):
        self._LoopedTimes = LoopedTimes


    def _deserialize(self, params):
        self._FileUrl = params.get("FileUrl")
        self._OffsetTime = params.get("OffsetTime")
        self._ReportTime = params.get("ReportTime")
        self._LoopedTimes = params.get("LoopedTimes")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class RecordParam(AbstractModel):
    """Recording template parameter.

    """

    def __init__(self):
        r"""
        :param _RecordInterval: Max recording time per file
Default value: `1800` (seconds)
Value range: 30-7200
This parameter is invalid for HLS. Only one HLS file will be generated from push start to push end.
        :type RecordInterval: int
        :param _StorageTime: Storage duration of the recording file
Value range: 0-129600000 seconds (0-1500 days)
`0`: permanent
        :type StorageTime: int
        :param _Enable: Whether to enable recording in the current format. Default value: 0. 0: no, 1: yes.
        :type Enable: int
        :param _VodSubAppId: VOD subapplication ID.
        :type VodSubAppId: int
        :param _VodFileName: Recording filename.
Supported special placeholders include:
{StreamID}: stream ID
{StartYear}: start time - year
{StartMonth}: start time - month
{StartDay}: start time - day
{StartHour}: start time - hour
{StartMinute}: start time - minute
{StartSecond}: start time - second
{StartMillisecond}: start time - millisecond
{EndYear}: end time - year
{EndMonth}: end time - month
{EndDay}: end time - day
{EndHour}: end time - hour
{EndMinute}: end time - minute
{EndSecond}: end time - second
{EndMillisecond}: end time - millisecond

If this parameter is not set, the recording filename will be `{StreamID}_{StartYear}-{StartMonth}-{StartDay}-{StartHour}-{StartMinute}-{StartSecond}_{EndYear}-{EndMonth}-{EndDay}-{EndHour}-{EndMinute}-{EndSecond}` by default
        :type VodFileName: str
        :param _Procedure: Task flow
Note: this field may return `null`, indicating that no valid value is obtained.
        :type Procedure: str
        :param _StorageMode: Video storage class. Valid values:
`normal`: STANDARD
`cold`: STANDARD_IA
Note: this field may return `null`, indicating that no valid value is obtained.
        :type StorageMode: str
        :param _ClassId: VOD subapplication category
Note: this field may return `null`, indicating that no valid value is obtained.
        :type ClassId: int
        """
        self._RecordInterval = None
        self._StorageTime = None
        self._Enable = None
        self._VodSubAppId = None
        self._VodFileName = None
        self._Procedure = None
        self._StorageMode = None
        self._ClassId = None

    @property
    def RecordInterval(self):
        return self._RecordInterval

    @RecordInterval.setter
    def RecordInterval(self, RecordInterval):
        self._RecordInterval = RecordInterval

    @property
    def StorageTime(self):
        return self._StorageTime

    @StorageTime.setter
    def StorageTime(self, StorageTime):
        self._StorageTime = StorageTime

    @property
    def Enable(self):
        return self._Enable

    @Enable.setter
    def Enable(self, Enable):
        self._Enable = Enable

    @property
    def VodSubAppId(self):
        return self._VodSubAppId

    @VodSubAppId.setter
    def VodSubAppId(self, VodSubAppId):
        self._VodSubAppId = VodSubAppId

    @property
    def VodFileName(self):
        return self._VodFileName

    @VodFileName.setter
    def VodFileName(self, VodFileName):
        self._VodFileName = VodFileName

    @property
    def Procedure(self):
        return self._Procedure

    @Procedure.setter
    def Procedure(self, Procedure):
        self._Procedure = Procedure

    @property
    def StorageMode(self):
        return self._StorageMode

    @StorageMode.setter
    def StorageMode(self, StorageMode):
        self._StorageMode = StorageMode

    @property
    def ClassId(self):
        return self._ClassId

    @ClassId.setter
    def ClassId(self, ClassId):
        self._ClassId = ClassId


    def _deserialize(self, params):
        self._RecordInterval = params.get("RecordInterval")
        self._StorageTime = params.get("StorageTime")
        self._Enable = params.get("Enable")
        self._VodSubAppId = params.get("VodSubAppId")
        self._VodFileName = params.get("VodFileName")
        self._Procedure = params.get("Procedure")
        self._StorageMode = params.get("StorageMode")
        self._ClassId = params.get("ClassId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class RecordTask(AbstractModel):
    """Recording task.

    """

    def __init__(self):
        r"""
        :param _TaskId: Recording task ID.
        :type TaskId: str
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _AppName: Push path.
        :type AppName: str
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _StartTime: The start time of the recording task in Unix timestamp. 
        :type StartTime: int
        :param _EndTime: The end time of the recording task in Unix timestamp. 
        :type EndTime: int
        :param _TemplateId: Recording template ID.
        :type TemplateId: int
        :param _Stopped: The StopRecordTask API call stops the task at the Unix timestamp. A value of 0 indicates that the API has not been called to stop the task.
        :type Stopped: int
        """
        self._TaskId = None
        self._DomainName = None
        self._AppName = None
        self._StreamName = None
        self._StartTime = None
        self._EndTime = None
        self._TemplateId = None
        self._Stopped = None

    @property
    def TaskId(self):
        return self._TaskId

    @TaskId.setter
    def TaskId(self, TaskId):
        self._TaskId = TaskId

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

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
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId

    @property
    def Stopped(self):
        return self._Stopped

    @Stopped.setter
    def Stopped(self, Stopped):
        self._Stopped = Stopped


    def _deserialize(self, params):
        self._TaskId = params.get("TaskId")
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._TemplateId = params.get("TemplateId")
        self._Stopped = params.get("Stopped")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class RecordTemplateInfo(AbstractModel):
    """Recording template information

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
        :type TemplateId: int
        :param _TemplateName: Template name.
        :type TemplateName: str
        :param _Description: Message description
        :type Description: str
        :param _FlvParam: FLV recording parameter.
        :type FlvParam: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _HlsParam: HLS recording parameter.
        :type HlsParam: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _Mp4Param: MP4 recording parameter.
        :type Mp4Param: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _AacParam: AAC recording parameter.
        :type AacParam: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _IsDelayLive: 0: LVB,
1: LCB.
        :type IsDelayLive: int
        :param _HlsSpecialParam: A special parameter for HLS recording.
        :type HlsSpecialParam: :class:`tencentcloud.live.v20180801.models.HlsSpecialParam`
        :param _Mp3Param: MP3 recording parameter.
        :type Mp3Param: :class:`tencentcloud.live.v20180801.models.RecordParam`
        :param _RemoveWatermark: Whether the watermark is removed.
Note: This field may return `null`, indicating that no valid value was found.
        :type RemoveWatermark: bool
        :param _FlvSpecialParam: A special parameter for FLV recording.
Note: This field may return `null`, indicating that no valid value can be obtained.
        :type FlvSpecialParam: :class:`tencentcloud.live.v20180801.models.FlvSpecialParam`
        """
        self._TemplateId = None
        self._TemplateName = None
        self._Description = None
        self._FlvParam = None
        self._HlsParam = None
        self._Mp4Param = None
        self._AacParam = None
        self._IsDelayLive = None
        self._HlsSpecialParam = None
        self._Mp3Param = None
        self._RemoveWatermark = None
        self._FlvSpecialParam = None

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
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def FlvParam(self):
        return self._FlvParam

    @FlvParam.setter
    def FlvParam(self, FlvParam):
        self._FlvParam = FlvParam

    @property
    def HlsParam(self):
        return self._HlsParam

    @HlsParam.setter
    def HlsParam(self, HlsParam):
        self._HlsParam = HlsParam

    @property
    def Mp4Param(self):
        return self._Mp4Param

    @Mp4Param.setter
    def Mp4Param(self, Mp4Param):
        self._Mp4Param = Mp4Param

    @property
    def AacParam(self):
        return self._AacParam

    @AacParam.setter
    def AacParam(self, AacParam):
        self._AacParam = AacParam

    @property
    def IsDelayLive(self):
        return self._IsDelayLive

    @IsDelayLive.setter
    def IsDelayLive(self, IsDelayLive):
        self._IsDelayLive = IsDelayLive

    @property
    def HlsSpecialParam(self):
        return self._HlsSpecialParam

    @HlsSpecialParam.setter
    def HlsSpecialParam(self, HlsSpecialParam):
        self._HlsSpecialParam = HlsSpecialParam

    @property
    def Mp3Param(self):
        return self._Mp3Param

    @Mp3Param.setter
    def Mp3Param(self, Mp3Param):
        self._Mp3Param = Mp3Param

    @property
    def RemoveWatermark(self):
        return self._RemoveWatermark

    @RemoveWatermark.setter
    def RemoveWatermark(self, RemoveWatermark):
        self._RemoveWatermark = RemoveWatermark

    @property
    def FlvSpecialParam(self):
        return self._FlvSpecialParam

    @FlvSpecialParam.setter
    def FlvSpecialParam(self, FlvSpecialParam):
        self._FlvSpecialParam = FlvSpecialParam


    def _deserialize(self, params):
        self._TemplateId = params.get("TemplateId")
        self._TemplateName = params.get("TemplateName")
        self._Description = params.get("Description")
        if params.get("FlvParam") is not None:
            self._FlvParam = RecordParam()
            self._FlvParam._deserialize(params.get("FlvParam"))
        if params.get("HlsParam") is not None:
            self._HlsParam = RecordParam()
            self._HlsParam._deserialize(params.get("HlsParam"))
        if params.get("Mp4Param") is not None:
            self._Mp4Param = RecordParam()
            self._Mp4Param._deserialize(params.get("Mp4Param"))
        if params.get("AacParam") is not None:
            self._AacParam = RecordParam()
            self._AacParam._deserialize(params.get("AacParam"))
        self._IsDelayLive = params.get("IsDelayLive")
        if params.get("HlsSpecialParam") is not None:
            self._HlsSpecialParam = HlsSpecialParam()
            self._HlsSpecialParam._deserialize(params.get("HlsSpecialParam"))
        if params.get("Mp3Param") is not None:
            self._Mp3Param = RecordParam()
            self._Mp3Param._deserialize(params.get("Mp3Param"))
        self._RemoveWatermark = params.get("RemoveWatermark")
        if params.get("FlvSpecialParam") is not None:
            self._FlvSpecialParam = FlvSpecialParam()
            self._FlvSpecialParam._deserialize(params.get("FlvSpecialParam"))
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class RefererAuthConfig(AbstractModel):
    """Referer allowlist/blocklist configuration of a live streaming domain name

    """

    def __init__(self):
        r"""
        :param _DomainName: Domain name
        :type DomainName: str
        :param _Enable: Whether to enable referer. Valid values: `0` (no), `1` (yes)
        :type Enable: int
        :param _Type: List type. Valid values: `0` (blocklist), `1` (allowlist)
        :type Type: int
        :param _AllowEmpty: Whether to allow empty referer. Valid values: `0` (no), `1` (yes)
        :type AllowEmpty: int
        :param _Rules: Referer list. Separate items in it with semicolons (;).
        :type Rules: str
        """
        self._DomainName = None
        self._Enable = None
        self._Type = None
        self._AllowEmpty = None
        self._Rules = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def Enable(self):
        return self._Enable

    @Enable.setter
    def Enable(self, Enable):
        self._Enable = Enable

    @property
    def Type(self):
        return self._Type

    @Type.setter
    def Type(self, Type):
        self._Type = Type

    @property
    def AllowEmpty(self):
        return self._AllowEmpty

    @AllowEmpty.setter
    def AllowEmpty(self, AllowEmpty):
        self._AllowEmpty = AllowEmpty

    @property
    def Rules(self):
        return self._Rules

    @Rules.setter
    def Rules(self, Rules):
        self._Rules = Rules


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._Enable = params.get("Enable")
        self._Type = params.get("Type")
        self._AllowEmpty = params.get("AllowEmpty")
        self._Rules = params.get("Rules")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ResumeDelayLiveStreamRequest(AbstractModel):
    """ResumeDelayLiveStream request structure.

    """

    def __init__(self):
        r"""
        :param _AppName: Push path, which is the same as the AppName in push and playback addresses and is "live" by default.
        :type AppName: str
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _StreamName: Stream name.
        :type StreamName: str
        """
        self._AppName = None
        self._DomainName = None
        self._StreamName = None

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName


    def _deserialize(self, params):
        self._AppName = params.get("AppName")
        self._DomainName = params.get("DomainName")
        self._StreamName = params.get("StreamName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ResumeDelayLiveStreamResponse(AbstractModel):
    """ResumeDelayLiveStream response structure.

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


class ResumeLiveStreamRequest(AbstractModel):
    """ResumeLiveStream request structure.

    """

    def __init__(self):
        r"""
        :param _AppName: Push path, which is the same as the AppName in push and playback addresses and is "live" by default.
        :type AppName: str
        :param _DomainName: Your push domain name.
        :type DomainName: str
        :param _StreamName: Stream name.
        :type StreamName: str
        """
        self._AppName = None
        self._DomainName = None
        self._StreamName = None

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName


    def _deserialize(self, params):
        self._AppName = params.get("AppName")
        self._DomainName = params.get("DomainName")
        self._StreamName = params.get("StreamName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ResumeLiveStreamResponse(AbstractModel):
    """ResumeLiveStream response structure.

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


class RuleInfo(AbstractModel):
    """Rule information.

    """

    def __init__(self):
        r"""
        :param _CreateTime: The rule creation time.
Note: Beijing time (UTC+8) is used.
        :type CreateTime: str
        :param _UpdateTime: The rule update time.
Note: Beijing time (UTC+8) is used.
        :type UpdateTime: str
        :param _TemplateId: Template ID.
        :type TemplateId: int
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _AppName: Push path.
        :type AppName: str
        :param _StreamName: Stream name.
        :type StreamName: str
        """
        self._CreateTime = None
        self._UpdateTime = None
        self._TemplateId = None
        self._DomainName = None
        self._AppName = None
        self._StreamName = None

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
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName


    def _deserialize(self, params):
        self._CreateTime = params.get("CreateTime")
        self._UpdateTime = params.get("UpdateTime")
        self._TemplateId = params.get("TemplateId")
        self._DomainName = params.get("DomainName")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class SnapshotTemplateInfo(AbstractModel):
    """Screencapturing template information.

    """

    def __init__(self):
        r"""
        :param _TemplateId: Template ID.
        :type TemplateId: int
        :param _TemplateName: Template name.
        :type TemplateName: str
        :param _SnapshotInterval: Screencapturing interval. Value range: 5-300s.
        :type SnapshotInterval: int
        :param _Width: Screenshot width. Value range: 0-3000. 
0: original width and fit to the original ratio.
        :type Width: int
        :param _Height: Screenshot height. Value range: 0-2000.
0: original height and fit to the original ratio.
        :type Height: int
        :param _PornFlag: Whether to enable porn detection. 0: no, 1: yes.
        :type PornFlag: int
        :param _CosAppId: COS application ID.
        :type CosAppId: int
        :param _CosBucket: COS bucket name.
        :type CosBucket: str
        :param _CosRegion: COS region.
        :type CosRegion: str
        :param _Description: Template description.
        :type Description: str
        :param _CosPrefix: COS bucket folder prefix.
Note: this field may return null, indicating that no valid values can be obtained.
        :type CosPrefix: str
        :param _CosFileName: COS filename.
Note: this field may return null, indicating that no valid values can be obtained.
        :type CosFileName: str
        """
        self._TemplateId = None
        self._TemplateName = None
        self._SnapshotInterval = None
        self._Width = None
        self._Height = None
        self._PornFlag = None
        self._CosAppId = None
        self._CosBucket = None
        self._CosRegion = None
        self._Description = None
        self._CosPrefix = None
        self._CosFileName = None

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
    def SnapshotInterval(self):
        return self._SnapshotInterval

    @SnapshotInterval.setter
    def SnapshotInterval(self, SnapshotInterval):
        self._SnapshotInterval = SnapshotInterval

    @property
    def Width(self):
        return self._Width

    @Width.setter
    def Width(self, Width):
        self._Width = Width

    @property
    def Height(self):
        return self._Height

    @Height.setter
    def Height(self, Height):
        self._Height = Height

    @property
    def PornFlag(self):
        return self._PornFlag

    @PornFlag.setter
    def PornFlag(self, PornFlag):
        self._PornFlag = PornFlag

    @property
    def CosAppId(self):
        return self._CosAppId

    @CosAppId.setter
    def CosAppId(self, CosAppId):
        self._CosAppId = CosAppId

    @property
    def CosBucket(self):
        return self._CosBucket

    @CosBucket.setter
    def CosBucket(self, CosBucket):
        self._CosBucket = CosBucket

    @property
    def CosRegion(self):
        return self._CosRegion

    @CosRegion.setter
    def CosRegion(self, CosRegion):
        self._CosRegion = CosRegion

    @property
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def CosPrefix(self):
        return self._CosPrefix

    @CosPrefix.setter
    def CosPrefix(self, CosPrefix):
        self._CosPrefix = CosPrefix

    @property
    def CosFileName(self):
        return self._CosFileName

    @CosFileName.setter
    def CosFileName(self, CosFileName):
        self._CosFileName = CosFileName


    def _deserialize(self, params):
        self._TemplateId = params.get("TemplateId")
        self._TemplateName = params.get("TemplateName")
        self._SnapshotInterval = params.get("SnapshotInterval")
        self._Width = params.get("Width")
        self._Height = params.get("Height")
        self._PornFlag = params.get("PornFlag")
        self._CosAppId = params.get("CosAppId")
        self._CosBucket = params.get("CosBucket")
        self._CosRegion = params.get("CosRegion")
        self._Description = params.get("Description")
        self._CosPrefix = params.get("CosPrefix")
        self._CosFileName = params.get("CosFileName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class StopLiveRecordRequest(AbstractModel):
    """StopLiveRecord request structure.

    """

    def __init__(self):
        r"""
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _TaskId: Task ID returned by the `CreateLiveRecord` API.
        :type TaskId: int
        """
        self._StreamName = None
        self._TaskId = None

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def TaskId(self):
        return self._TaskId

    @TaskId.setter
    def TaskId(self, TaskId):
        self._TaskId = TaskId


    def _deserialize(self, params):
        self._StreamName = params.get("StreamName")
        self._TaskId = params.get("TaskId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class StopLiveRecordResponse(AbstractModel):
    """StopLiveRecord response structure.

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


class StopRecordTaskRequest(AbstractModel):
    """StopRecordTask request structure.

    """

    def __init__(self):
        r"""
        :param _TaskId: Recording task ID.
        :type TaskId: str
        """
        self._TaskId = None

    @property
    def TaskId(self):
        return self._TaskId

    @TaskId.setter
    def TaskId(self, TaskId):
        self._TaskId = TaskId


    def _deserialize(self, params):
        self._TaskId = params.get("TaskId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class StopRecordTaskResponse(AbstractModel):
    """StopRecordTask response structure.

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


class StreamEventInfo(AbstractModel):
    """Streaming event information.

    """

    def __init__(self):
        r"""
        :param _AppName: Application name.
        :type AppName: str
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _StreamStartTime: Push start time.
In UTC format, such as 2019-01-07T12:00:00Z.
        :type StreamStartTime: str
        :param _StreamEndTime: Push end time.
In UTC format, such as 2019-01-07T15:00:00Z.
        :type StreamEndTime: str
        :param _StopReason: Stop reason.
        :type StopReason: str
        :param _Duration: Push duration in seconds.
        :type Duration: int
        :param _ClientIp: The IP address of the host.
If the stream is published from a private network, this parameter will be `-`.
        :type ClientIp: str
        :param _Resolution: Resolution.
        :type Resolution: str
        """
        self._AppName = None
        self._DomainName = None
        self._StreamName = None
        self._StreamStartTime = None
        self._StreamEndTime = None
        self._StopReason = None
        self._Duration = None
        self._ClientIp = None
        self._Resolution = None

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def StreamStartTime(self):
        return self._StreamStartTime

    @StreamStartTime.setter
    def StreamStartTime(self, StreamStartTime):
        self._StreamStartTime = StreamStartTime

    @property
    def StreamEndTime(self):
        return self._StreamEndTime

    @StreamEndTime.setter
    def StreamEndTime(self, StreamEndTime):
        self._StreamEndTime = StreamEndTime

    @property
    def StopReason(self):
        return self._StopReason

    @StopReason.setter
    def StopReason(self, StopReason):
        self._StopReason = StopReason

    @property
    def Duration(self):
        return self._Duration

    @Duration.setter
    def Duration(self, Duration):
        self._Duration = Duration

    @property
    def ClientIp(self):
        return self._ClientIp

    @ClientIp.setter
    def ClientIp(self, ClientIp):
        self._ClientIp = ClientIp

    @property
    def Resolution(self):
        return self._Resolution

    @Resolution.setter
    def Resolution(self, Resolution):
        self._Resolution = Resolution


    def _deserialize(self, params):
        self._AppName = params.get("AppName")
        self._DomainName = params.get("DomainName")
        self._StreamName = params.get("StreamName")
        self._StreamStartTime = params.get("StreamStartTime")
        self._StreamEndTime = params.get("StreamEndTime")
        self._StopReason = params.get("StopReason")
        self._Duration = params.get("Duration")
        self._ClientIp = params.get("ClientIp")
        self._Resolution = params.get("Resolution")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class StreamName(AbstractModel):
    """Stream name list.

    """

    def __init__(self):
        r"""
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _AppName: Application name.
        :type AppName: str
        :param _DomainName: Push domain name.
        :type DomainName: str
        :param _StreamStartTime: Push start time.
In UTC format, such as 2019-01-07T12:00:00Z.
        :type StreamStartTime: str
        :param _StreamEndTime: Push end time.
In UTC format, such as 2019-01-07T15:00:00Z.
        :type StreamEndTime: str
        :param _StopReason: Stop reason.
        :type StopReason: str
        :param _Duration: Push duration in seconds.
        :type Duration: int
        :param _ClientIp: Host IP.
        :type ClientIp: str
        :param _Resolution: Resolution.
        :type Resolution: str
        """
        self._StreamName = None
        self._AppName = None
        self._DomainName = None
        self._StreamStartTime = None
        self._StreamEndTime = None
        self._StopReason = None
        self._Duration = None
        self._ClientIp = None
        self._Resolution = None

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def StreamStartTime(self):
        return self._StreamStartTime

    @StreamStartTime.setter
    def StreamStartTime(self, StreamStartTime):
        self._StreamStartTime = StreamStartTime

    @property
    def StreamEndTime(self):
        return self._StreamEndTime

    @StreamEndTime.setter
    def StreamEndTime(self, StreamEndTime):
        self._StreamEndTime = StreamEndTime

    @property
    def StopReason(self):
        return self._StopReason

    @StopReason.setter
    def StopReason(self, StopReason):
        self._StopReason = StopReason

    @property
    def Duration(self):
        return self._Duration

    @Duration.setter
    def Duration(self, Duration):
        self._Duration = Duration

    @property
    def ClientIp(self):
        return self._ClientIp

    @ClientIp.setter
    def ClientIp(self, ClientIp):
        self._ClientIp = ClientIp

    @property
    def Resolution(self):
        return self._Resolution

    @Resolution.setter
    def Resolution(self, Resolution):
        self._Resolution = Resolution


    def _deserialize(self, params):
        self._StreamName = params.get("StreamName")
        self._AppName = params.get("AppName")
        self._DomainName = params.get("DomainName")
        self._StreamStartTime = params.get("StreamStartTime")
        self._StreamEndTime = params.get("StreamEndTime")
        self._StopReason = params.get("StopReason")
        self._Duration = params.get("Duration")
        self._ClientIp = params.get("ClientIp")
        self._Resolution = params.get("Resolution")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class StreamOnlineInfo(AbstractModel):
    """Queries active push information

    """

    def __init__(self):
        r"""
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _PublishTimeList: Push time list
        :type PublishTimeList: list of PublishTime
        :param _AppName: Application name.
        :type AppName: str
        :param _DomainName: Push domain name.
        :type DomainName: str
        """
        self._StreamName = None
        self._PublishTimeList = None
        self._AppName = None
        self._DomainName = None

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

    @property
    def PublishTimeList(self):
        return self._PublishTimeList

    @PublishTimeList.setter
    def PublishTimeList(self, PublishTimeList):
        self._PublishTimeList = PublishTimeList

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName


    def _deserialize(self, params):
        self._StreamName = params.get("StreamName")
        if params.get("PublishTimeList") is not None:
            self._PublishTimeList = []
            for item in params.get("PublishTimeList"):
                obj = PublishTime()
                obj._deserialize(item)
                self._PublishTimeList.append(obj)
        self._AppName = params.get("AppName")
        self._DomainName = params.get("DomainName")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class TemplateInfo(AbstractModel):
    """Transcoding template information.

    """

    def __init__(self):
        r"""
        :param _Vcodec: Codec: h264/h265/origin. Default value: h264.

origin: keep the original codec.
        :type Vcodec: str
        :param _VideoBitrate: Video bitrate. Value range: 0–8,000 Kbps.
If the value is 0, the original bitrate will be retained.
Note: transcoding templates require a unique bitrate. The final saved bitrate may differ from the input bitrate.
        :type VideoBitrate: int
        :param _Acodec: Audio codec: aac. Default value: aac.
Note: This parameter will not take effect for now and will be supported soon.
        :type Acodec: str
        :param _AudioBitrate: Audio bitrate. Value range: 0–500 Kbps.
0 by default.
        :type AudioBitrate: int
        :param _Width: Width. Default value: 0.
Value range: [0-3,000].
The value must be a multiple of 2. The original width is 0.
        :type Width: int
        :param _Height: Height. Default value: 0.
Value range: [0-3,000].
The value must be a multiple of 2. The original width is 0.
        :type Height: int
        :param _Fps: Frame rate. Default value: 0.
Range: 0-60 Fps.
        :type Fps: int
        :param _Gop: Keyframe interval, unit: second.
Original interval by default
Range: 2-6
        :type Gop: int
        :param _Rotate: Rotation angle. Default value: 0.
Value range: 0, 90, 180, 270
        :type Rotate: int
        :param _Profile: Encoding quality:
baseline/main/high. Default value: baseline.
        :type Profile: str
        :param _BitrateToOrig: Whether to use the original bitrate when the set bitrate is larger than the original bitrate.
0: no, 1: yes
Default value: 0.
        :type BitrateToOrig: int
        :param _HeightToOrig: Whether to use the original height when the set height is higher than the original height.
0: no, 1: yes
Default value: 0.
        :type HeightToOrig: int
        :param _FpsToOrig: Whether to use the original frame rate when the set frame rate is larger than the original frame rate.
0: no, 1: yes
Default value: 0.
        :type FpsToOrig: int
        :param _NeedVideo: Whether to keep the video. 0: no; 1: yes.
        :type NeedVideo: int
        :param _NeedAudio: Whether to keep the audio. 0: no; 1: yes.
        :type NeedAudio: int
        :param _TemplateId: Template ID.
        :type TemplateId: int
        :param _TemplateName: Template name.
        :type TemplateName: str
        :param _Description: Template description.
        :type Description: str
        :param _AiTransCode: Whether it is a top speed codec template. 0: no, 1: yes. Default value: 0.
        :type AiTransCode: int
        :param _AdaptBitratePercent: Bitrate compression ratio of top speed code video.
Target bitrate of top speed code = VideoBitrate * (1-AdaptBitratePercent)

Value range: 0.0-0.5.
        :type AdaptBitratePercent: float
        :param _ShortEdgeAsHeight: Whether to take the shorter side as height. 0: no, 1: yes. Default value: 0.
Note: this field may return `null`, indicating that no valid value is obtained.
        :type ShortEdgeAsHeight: int
        :param _DRMType: The DRM encryption type. Valid values: fairplay, normalaes, widevine.
Note: This field may return null, indicating that no valid values can be obtained.
        :type DRMType: str
        :param _DRMTracks: The tracks to encrypt. Valid values: AUDIO, SD, HD, UHD1, UHD2. Separate multiple tracks with “|”. You can choose only one video track (SD, HD, UHD1, or UHD2).
Note: This field may return null, indicating that no valid values can be obtained.
        :type DRMTracks: str
        """
        self._Vcodec = None
        self._VideoBitrate = None
        self._Acodec = None
        self._AudioBitrate = None
        self._Width = None
        self._Height = None
        self._Fps = None
        self._Gop = None
        self._Rotate = None
        self._Profile = None
        self._BitrateToOrig = None
        self._HeightToOrig = None
        self._FpsToOrig = None
        self._NeedVideo = None
        self._NeedAudio = None
        self._TemplateId = None
        self._TemplateName = None
        self._Description = None
        self._AiTransCode = None
        self._AdaptBitratePercent = None
        self._ShortEdgeAsHeight = None
        self._DRMType = None
        self._DRMTracks = None

    @property
    def Vcodec(self):
        return self._Vcodec

    @Vcodec.setter
    def Vcodec(self, Vcodec):
        self._Vcodec = Vcodec

    @property
    def VideoBitrate(self):
        return self._VideoBitrate

    @VideoBitrate.setter
    def VideoBitrate(self, VideoBitrate):
        self._VideoBitrate = VideoBitrate

    @property
    def Acodec(self):
        return self._Acodec

    @Acodec.setter
    def Acodec(self, Acodec):
        self._Acodec = Acodec

    @property
    def AudioBitrate(self):
        return self._AudioBitrate

    @AudioBitrate.setter
    def AudioBitrate(self, AudioBitrate):
        self._AudioBitrate = AudioBitrate

    @property
    def Width(self):
        return self._Width

    @Width.setter
    def Width(self, Width):
        self._Width = Width

    @property
    def Height(self):
        return self._Height

    @Height.setter
    def Height(self, Height):
        self._Height = Height

    @property
    def Fps(self):
        return self._Fps

    @Fps.setter
    def Fps(self, Fps):
        self._Fps = Fps

    @property
    def Gop(self):
        return self._Gop

    @Gop.setter
    def Gop(self, Gop):
        self._Gop = Gop

    @property
    def Rotate(self):
        return self._Rotate

    @Rotate.setter
    def Rotate(self, Rotate):
        self._Rotate = Rotate

    @property
    def Profile(self):
        return self._Profile

    @Profile.setter
    def Profile(self, Profile):
        self._Profile = Profile

    @property
    def BitrateToOrig(self):
        return self._BitrateToOrig

    @BitrateToOrig.setter
    def BitrateToOrig(self, BitrateToOrig):
        self._BitrateToOrig = BitrateToOrig

    @property
    def HeightToOrig(self):
        return self._HeightToOrig

    @HeightToOrig.setter
    def HeightToOrig(self, HeightToOrig):
        self._HeightToOrig = HeightToOrig

    @property
    def FpsToOrig(self):
        return self._FpsToOrig

    @FpsToOrig.setter
    def FpsToOrig(self, FpsToOrig):
        self._FpsToOrig = FpsToOrig

    @property
    def NeedVideo(self):
        return self._NeedVideo

    @NeedVideo.setter
    def NeedVideo(self, NeedVideo):
        self._NeedVideo = NeedVideo

    @property
    def NeedAudio(self):
        return self._NeedAudio

    @NeedAudio.setter
    def NeedAudio(self, NeedAudio):
        self._NeedAudio = NeedAudio

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
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def AiTransCode(self):
        return self._AiTransCode

    @AiTransCode.setter
    def AiTransCode(self, AiTransCode):
        self._AiTransCode = AiTransCode

    @property
    def AdaptBitratePercent(self):
        return self._AdaptBitratePercent

    @AdaptBitratePercent.setter
    def AdaptBitratePercent(self, AdaptBitratePercent):
        self._AdaptBitratePercent = AdaptBitratePercent

    @property
    def ShortEdgeAsHeight(self):
        return self._ShortEdgeAsHeight

    @ShortEdgeAsHeight.setter
    def ShortEdgeAsHeight(self, ShortEdgeAsHeight):
        self._ShortEdgeAsHeight = ShortEdgeAsHeight

    @property
    def DRMType(self):
        return self._DRMType

    @DRMType.setter
    def DRMType(self, DRMType):
        self._DRMType = DRMType

    @property
    def DRMTracks(self):
        return self._DRMTracks

    @DRMTracks.setter
    def DRMTracks(self, DRMTracks):
        self._DRMTracks = DRMTracks


    def _deserialize(self, params):
        self._Vcodec = params.get("Vcodec")
        self._VideoBitrate = params.get("VideoBitrate")
        self._Acodec = params.get("Acodec")
        self._AudioBitrate = params.get("AudioBitrate")
        self._Width = params.get("Width")
        self._Height = params.get("Height")
        self._Fps = params.get("Fps")
        self._Gop = params.get("Gop")
        self._Rotate = params.get("Rotate")
        self._Profile = params.get("Profile")
        self._BitrateToOrig = params.get("BitrateToOrig")
        self._HeightToOrig = params.get("HeightToOrig")
        self._FpsToOrig = params.get("FpsToOrig")
        self._NeedVideo = params.get("NeedVideo")
        self._NeedAudio = params.get("NeedAudio")
        self._TemplateId = params.get("TemplateId")
        self._TemplateName = params.get("TemplateName")
        self._Description = params.get("Description")
        self._AiTransCode = params.get("AiTransCode")
        self._AdaptBitratePercent = params.get("AdaptBitratePercent")
        self._ShortEdgeAsHeight = params.get("ShortEdgeAsHeight")
        self._DRMType = params.get("DRMType")
        self._DRMTracks = params.get("DRMTracks")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class TimeShiftBillData(AbstractModel):
    """The time shifting billing data.

    """

    def __init__(self):
        r"""
        :param _Domain: The push domain name.
        :type Domain: str
        :param _Duration: The time-shift video length (minutes).
        :type Duration: float
        :param _StoragePeriod: The time-shift days.
        :type StoragePeriod: float
        :param _Time: The time for the data returned. Format: YYYY-MM-DDThh:mm:ssZ.
        :type Time: str
        :param _TotalDuration: The total time-shift duration (minutes).
        :type TotalDuration: float
        """
        self._Domain = None
        self._Duration = None
        self._StoragePeriod = None
        self._Time = None
        self._TotalDuration = None

    @property
    def Domain(self):
        return self._Domain

    @Domain.setter
    def Domain(self, Domain):
        self._Domain = Domain

    @property
    def Duration(self):
        return self._Duration

    @Duration.setter
    def Duration(self, Duration):
        self._Duration = Duration

    @property
    def StoragePeriod(self):
        return self._StoragePeriod

    @StoragePeriod.setter
    def StoragePeriod(self, StoragePeriod):
        self._StoragePeriod = StoragePeriod

    @property
    def Time(self):
        return self._Time

    @Time.setter
    def Time(self, Time):
        self._Time = Time

    @property
    def TotalDuration(self):
        return self._TotalDuration

    @TotalDuration.setter
    def TotalDuration(self, TotalDuration):
        self._TotalDuration = TotalDuration


    def _deserialize(self, params):
        self._Domain = params.get("Domain")
        self._Duration = params.get("Duration")
        self._StoragePeriod = params.get("StoragePeriod")
        self._Time = params.get("Time")
        self._TotalDuration = params.get("TotalDuration")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class TimeShiftRecord(AbstractModel):
    """A recorded time shifting session.

    """

    def __init__(self):
        r"""
        :param _Sid: The session ID.
        :type Sid: str
        :param _StartTime: The recording start time, which is a Unix timestamp.
        :type StartTime: int
        :param _EndTime: The recording end time, which is a Unix timestamp.
        :type EndTime: int
        """
        self._Sid = None
        self._StartTime = None
        self._EndTime = None

    @property
    def Sid(self):
        return self._Sid

    @Sid.setter
    def Sid(self, Sid):
        self._Sid = Sid

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


    def _deserialize(self, params):
        self._Sid = params.get("Sid")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class TimeShiftStreamInfo(AbstractModel):
    """The information of a time shifted stream.

    """

    def __init__(self):
        r"""
        :param _DomainGroup: The group the push domain belongs to.
Note: This field may return null, indicating that no valid values can be obtained.
        :type DomainGroup: str
        :param _Domain: The push domain.
        :type Domain: str
        :param _AppName: The push path.
        :type AppName: str
        :param _StreamName: The stream name.
        :type StreamName: str
        :param _StartTime: The stream start time, which is a Unix timestamp.
        :type StartTime: int
        :param _EndTime: The stream end time (for streams that ended before the time of query), which is a Unix timestamp.
        :type EndTime: int
        :param _TransCodeId: The transcoding template ID.
Note: This field may return null, indicating that no valid values can be obtained.
        :type TransCodeId: int
        :param _StreamType: The stream type. `0`: The original stream; `1`: The watermarked stream; `2`: The transcoded stream.
        :type StreamType: int
        :param _Duration: The storage duration (seconds) of the recording.
Note: This field may return null, indicating that no valid values can be obtained.
        :type Duration: int
        """
        self._DomainGroup = None
        self._Domain = None
        self._AppName = None
        self._StreamName = None
        self._StartTime = None
        self._EndTime = None
        self._TransCodeId = None
        self._StreamType = None
        self._Duration = None

    @property
    def DomainGroup(self):
        return self._DomainGroup

    @DomainGroup.setter
    def DomainGroup(self, DomainGroup):
        self._DomainGroup = DomainGroup

    @property
    def Domain(self):
        return self._Domain

    @Domain.setter
    def Domain(self, Domain):
        self._Domain = Domain

    @property
    def AppName(self):
        return self._AppName

    @AppName.setter
    def AppName(self, AppName):
        self._AppName = AppName

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

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
    def TransCodeId(self):
        return self._TransCodeId

    @TransCodeId.setter
    def TransCodeId(self, TransCodeId):
        self._TransCodeId = TransCodeId

    @property
    def StreamType(self):
        return self._StreamType

    @StreamType.setter
    def StreamType(self, StreamType):
        self._StreamType = StreamType

    @property
    def Duration(self):
        return self._Duration

    @Duration.setter
    def Duration(self, Duration):
        self._Duration = Duration


    def _deserialize(self, params):
        self._DomainGroup = params.get("DomainGroup")
        self._Domain = params.get("Domain")
        self._AppName = params.get("AppName")
        self._StreamName = params.get("StreamName")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._TransCodeId = params.get("TransCodeId")
        self._StreamType = params.get("StreamType")
        self._Duration = params.get("Duration")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class TimeShiftTemplate(AbstractModel):
    """The information of a time shifting template.

    """

    def __init__(self):
        r"""
        :param _TemplateName: The template name.
        :type TemplateName: str
        :param _Duration: The time shifting duration.
Unit: second
        :type Duration: int
        :param _ItemDuration: The segment size.
Value range: 3-10.
Unit: Second.
Default value: 5
        :type ItemDuration: int
        :param _TemplateId: The template ID.
        :type TemplateId: int
        :param _Description: The template description.
        :type Description: str
        :param _Area: The region. Valid values:
`Mainland`: The Chinese mainland.
`Overseas`: Outside the Chinese mainland.
Default value: `Mainland`.
        :type Area: str
        :param _RemoveWatermark: Whether to remove watermarks.
If you pass in `true`, the original stream will be recorded.
Default value: `false`.
        :type RemoveWatermark: bool
        :param _TranscodeTemplateIds: The transcoding template IDs.
This API works only if `RemoveWatermark` is `false`.
        :type TranscodeTemplateIds: list of int non-negative
        """
        self._TemplateName = None
        self._Duration = None
        self._ItemDuration = None
        self._TemplateId = None
        self._Description = None
        self._Area = None
        self._RemoveWatermark = None
        self._TranscodeTemplateIds = None

    @property
    def TemplateName(self):
        return self._TemplateName

    @TemplateName.setter
    def TemplateName(self, TemplateName):
        self._TemplateName = TemplateName

    @property
    def Duration(self):
        return self._Duration

    @Duration.setter
    def Duration(self, Duration):
        self._Duration = Duration

    @property
    def ItemDuration(self):
        return self._ItemDuration

    @ItemDuration.setter
    def ItemDuration(self, ItemDuration):
        self._ItemDuration = ItemDuration

    @property
    def TemplateId(self):
        return self._TemplateId

    @TemplateId.setter
    def TemplateId(self, TemplateId):
        self._TemplateId = TemplateId

    @property
    def Description(self):
        return self._Description

    @Description.setter
    def Description(self, Description):
        self._Description = Description

    @property
    def Area(self):
        return self._Area

    @Area.setter
    def Area(self, Area):
        self._Area = Area

    @property
    def RemoveWatermark(self):
        return self._RemoveWatermark

    @RemoveWatermark.setter
    def RemoveWatermark(self, RemoveWatermark):
        self._RemoveWatermark = RemoveWatermark

    @property
    def TranscodeTemplateIds(self):
        return self._TranscodeTemplateIds

    @TranscodeTemplateIds.setter
    def TranscodeTemplateIds(self, TranscodeTemplateIds):
        self._TranscodeTemplateIds = TranscodeTemplateIds


    def _deserialize(self, params):
        self._TemplateName = params.get("TemplateName")
        self._Duration = params.get("Duration")
        self._ItemDuration = params.get("ItemDuration")
        self._TemplateId = params.get("TemplateId")
        self._Description = params.get("Description")
        self._Area = params.get("Area")
        self._RemoveWatermark = params.get("RemoveWatermark")
        self._TranscodeTemplateIds = params.get("TranscodeTemplateIds")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class TimeValue(AbstractModel):
    """Metric value at a specified point in time.

    """

    def __init__(self):
        r"""
        :param _Time: UTC time in the format of `yyyy-mm-ddTHH:MM:SSZ`.
        :type Time: str
        :param _Num: Value.
        :type Num: int
        """
        self._Time = None
        self._Num = None

    @property
    def Time(self):
        return self._Time

    @Time.setter
    def Time(self, Time):
        self._Time = Time

    @property
    def Num(self):
        return self._Num

    @Num.setter
    def Num(self, Num):
        self._Num = Num


    def _deserialize(self, params):
        self._Time = params.get("Time")
        self._Num = params.get("Num")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class TranscodeDetailInfo(AbstractModel):
    """Transcoding details.

    """

    def __init__(self):
        r"""
        :param _StreamName: Stream name.
        :type StreamName: str
        :param _StartTime: Start time (Beijing time) in the format of `yyyy-mm-dd HH:MM`.
        :type StartTime: str
        :param _EndTime: End time (Beijing time) in the format of `yyyy-mm-dd HH:MM`.
        :type EndTime: str
        :param _Duration: Transcoding duration in minutes.
Note: given the possible interruptions during push, duration here is the sum of actual duration of transcoding instead of the interval between the start time and end time.
        :type Duration: int
        :param _ModuleCodec: Codec with modules,
Example:
liveprocessor_H264: LVB transcoding - H264,
liveprocessor_H265: LVB transcoding - H265,
topspeed_H264: top speed codec - H264,
topspeed_H265: top speed codec - H265.
        :type ModuleCodec: str
        :param _Bitrate: Bitrate.
        :type Bitrate: int
        :param _Type: The task type. Valid values: Transcode, MixStream, WaterMark, Webrtc.
        :type Type: str
        :param _PushDomain: Push domain name.
        :type PushDomain: str
        :param _Resolution: Resolution.
        :type Resolution: str
        :param _MainlandOrOversea: The region. Valid values:
`Mainland`: Inside the Chinese mainland.
`Overseas`: Outside the Chinese mainland.
        :type MainlandOrOversea: str
        """
        self._StreamName = None
        self._StartTime = None
        self._EndTime = None
        self._Duration = None
        self._ModuleCodec = None
        self._Bitrate = None
        self._Type = None
        self._PushDomain = None
        self._Resolution = None
        self._MainlandOrOversea = None

    @property
    def StreamName(self):
        return self._StreamName

    @StreamName.setter
    def StreamName(self, StreamName):
        self._StreamName = StreamName

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
    def Duration(self):
        return self._Duration

    @Duration.setter
    def Duration(self, Duration):
        self._Duration = Duration

    @property
    def ModuleCodec(self):
        return self._ModuleCodec

    @ModuleCodec.setter
    def ModuleCodec(self, ModuleCodec):
        self._ModuleCodec = ModuleCodec

    @property
    def Bitrate(self):
        return self._Bitrate

    @Bitrate.setter
    def Bitrate(self, Bitrate):
        self._Bitrate = Bitrate

    @property
    def Type(self):
        return self._Type

    @Type.setter
    def Type(self, Type):
        self._Type = Type

    @property
    def PushDomain(self):
        return self._PushDomain

    @PushDomain.setter
    def PushDomain(self, PushDomain):
        self._PushDomain = PushDomain

    @property
    def Resolution(self):
        return self._Resolution

    @Resolution.setter
    def Resolution(self, Resolution):
        self._Resolution = Resolution

    @property
    def MainlandOrOversea(self):
        return self._MainlandOrOversea

    @MainlandOrOversea.setter
    def MainlandOrOversea(self, MainlandOrOversea):
        self._MainlandOrOversea = MainlandOrOversea


    def _deserialize(self, params):
        self._StreamName = params.get("StreamName")
        self._StartTime = params.get("StartTime")
        self._EndTime = params.get("EndTime")
        self._Duration = params.get("Duration")
        self._ModuleCodec = params.get("ModuleCodec")
        self._Bitrate = params.get("Bitrate")
        self._Type = params.get("Type")
        self._PushDomain = params.get("PushDomain")
        self._Resolution = params.get("Resolution")
        self._MainlandOrOversea = params.get("MainlandOrOversea")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class TranscodeTaskNum(AbstractModel):
    """The number of tasks.

    """

    def __init__(self):
        r"""
        :param _Time: The time of query.
        :type Time: str
        :param _CodeRate: The bitrate.
        :type CodeRate: int
        :param _Num: The number of tasks.
        :type Num: int
        """
        self._Time = None
        self._CodeRate = None
        self._Num = None

    @property
    def Time(self):
        return self._Time

    @Time.setter
    def Time(self, Time):
        self._Time = Time

    @property
    def CodeRate(self):
        return self._CodeRate

    @CodeRate.setter
    def CodeRate(self, CodeRate):
        self._CodeRate = CodeRate

    @property
    def Num(self):
        return self._Num

    @Num.setter
    def Num(self, Num):
        self._Num = Num


    def _deserialize(self, params):
        self._Time = params.get("Time")
        self._CodeRate = params.get("CodeRate")
        self._Num = params.get("Num")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class TranscodeTotalInfo(AbstractModel):
    """Total usage of the transcoding service

    """

    def __init__(self):
        r"""
        :param _Time: Usage time (Beijing time)
Example: 2019-03-01 00:00:00
        :type Time: str
        :param _Duration: Transcoding duration in minutes
        :type Duration: int
        :param _ModuleCodec: Codec, with modules
Examples:
`liveprocessor_H264`: live transcoding-H264
`liveprocessor_H265`: live transcoding-H265
`topspeed_H264`: top speed codec-H264
`topspeed_H265`: top speed codec-H265
        :type ModuleCodec: str
        :param _Resolution: Resolution
Example: 540*480
        :type Resolution: str
        """
        self._Time = None
        self._Duration = None
        self._ModuleCodec = None
        self._Resolution = None

    @property
    def Time(self):
        return self._Time

    @Time.setter
    def Time(self, Time):
        self._Time = Time

    @property
    def Duration(self):
        return self._Duration

    @Duration.setter
    def Duration(self, Duration):
        self._Duration = Duration

    @property
    def ModuleCodec(self):
        return self._ModuleCodec

    @ModuleCodec.setter
    def ModuleCodec(self, ModuleCodec):
        self._ModuleCodec = ModuleCodec

    @property
    def Resolution(self):
        return self._Resolution

    @Resolution.setter
    def Resolution(self, Resolution):
        self._Resolution = Resolution


    def _deserialize(self, params):
        self._Time = params.get("Time")
        self._Duration = params.get("Duration")
        self._ModuleCodec = params.get("ModuleCodec")
        self._Resolution = params.get("Resolution")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class UnBindLiveDomainCertRequest(AbstractModel):
    """UnBindLiveDomainCert request structure.

    """

    def __init__(self):
        r"""
        :param _DomainName: Playback domain name.
        :type DomainName: str
        :param _Type: Valid values:
`gray`: unbind the canary certificate
`formal` (default): unbind the formal certificate

`formal` will be used if no value is passed in
        :type Type: str
        """
        self._DomainName = None
        self._Type = None

    @property
    def DomainName(self):
        return self._DomainName

    @DomainName.setter
    def DomainName(self, DomainName):
        self._DomainName = DomainName

    @property
    def Type(self):
        return self._Type

    @Type.setter
    def Type(self, Type):
        self._Type = Type


    def _deserialize(self, params):
        self._DomainName = params.get("DomainName")
        self._Type = params.get("Type")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class UnBindLiveDomainCertResponse(AbstractModel):
    """UnBindLiveDomainCert response structure.

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


class UpdateLiveWatermarkRequest(AbstractModel):
    """UpdateLiveWatermark request structure.

    """

    def __init__(self):
        r"""
        :param _WatermarkId: Watermark ID.
Get the watermark ID in the returned value of the [AddLiveWatermark](https://intl.cloud.tencent.com/document/product/267/30154?from_cn_redirect=1) API call.
        :type WatermarkId: int
        :param _PictureUrl: Watermark image URL.
Unallowed characters in the URL:
 ;(){}$>`#"\'|
        :type PictureUrl: str
        :param _XPosition: Display position: X-axis offset in %. Default value: 0.
        :type XPosition: int
        :param _YPosition: Display position: Y-axis offset in %. Default value: 0.
        :type YPosition: int
        :param _WatermarkName: Watermark name.
Up to 16 bytes.
        :type WatermarkName: str
        :param _Width: Watermark width or its percentage of the live streaming video width. It is recommended to just specify either height or width as the other will be scaled proportionally to avoid distortions. The original width is used by default.
        :type Width: int
        :param _Height: Watermark height or its percentage of the live streaming video width. It is recommended to just specify either height or width as the other will be scaled proportionally to avoid distortions. The original height is used by default.
        :type Height: int
        """
        self._WatermarkId = None
        self._PictureUrl = None
        self._XPosition = None
        self._YPosition = None
        self._WatermarkName = None
        self._Width = None
        self._Height = None

    @property
    def WatermarkId(self):
        return self._WatermarkId

    @WatermarkId.setter
    def WatermarkId(self, WatermarkId):
        self._WatermarkId = WatermarkId

    @property
    def PictureUrl(self):
        return self._PictureUrl

    @PictureUrl.setter
    def PictureUrl(self, PictureUrl):
        self._PictureUrl = PictureUrl

    @property
    def XPosition(self):
        return self._XPosition

    @XPosition.setter
    def XPosition(self, XPosition):
        self._XPosition = XPosition

    @property
    def YPosition(self):
        return self._YPosition

    @YPosition.setter
    def YPosition(self, YPosition):
        self._YPosition = YPosition

    @property
    def WatermarkName(self):
        return self._WatermarkName

    @WatermarkName.setter
    def WatermarkName(self, WatermarkName):
        self._WatermarkName = WatermarkName

    @property
    def Width(self):
        return self._Width

    @Width.setter
    def Width(self, Width):
        self._Width = Width

    @property
    def Height(self):
        return self._Height

    @Height.setter
    def Height(self, Height):
        self._Height = Height


    def _deserialize(self, params):
        self._WatermarkId = params.get("WatermarkId")
        self._PictureUrl = params.get("PictureUrl")
        self._XPosition = params.get("XPosition")
        self._YPosition = params.get("YPosition")
        self._WatermarkName = params.get("WatermarkName")
        self._Width = params.get("Width")
        self._Height = params.get("Height")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class UpdateLiveWatermarkResponse(AbstractModel):
    """UpdateLiveWatermark response structure.

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


class WatermarkInfo(AbstractModel):
    """Watermark information.

    """

    def __init__(self):
        r"""
        :param _WatermarkId: Watermark ID.
        :type WatermarkId: int
        :param _PictureUrl: Watermark image URL.
        :type PictureUrl: str
        :param _XPosition: Display position: X-axis offset.
        :type XPosition: int
        :param _YPosition: Display position: Y-axis offset.
        :type YPosition: int
        :param _WatermarkName: Watermark name.
        :type WatermarkName: str
        :param _Status: Current status. 0: not used. 1: in use.
        :type Status: int
        :param _CreateTime: The time when the watermark was added.
Note: Beijing time (UTC+8) is used.
        :type CreateTime: str
        :param _Width: Watermark width.
        :type Width: int
        :param _Height: Watermark height.
        :type Height: int
        """
        self._WatermarkId = None
        self._PictureUrl = None
        self._XPosition = None
        self._YPosition = None
        self._WatermarkName = None
        self._Status = None
        self._CreateTime = None
        self._Width = None
        self._Height = None

    @property
    def WatermarkId(self):
        return self._WatermarkId

    @WatermarkId.setter
    def WatermarkId(self, WatermarkId):
        self._WatermarkId = WatermarkId

    @property
    def PictureUrl(self):
        return self._PictureUrl

    @PictureUrl.setter
    def PictureUrl(self, PictureUrl):
        self._PictureUrl = PictureUrl

    @property
    def XPosition(self):
        return self._XPosition

    @XPosition.setter
    def XPosition(self, XPosition):
        self._XPosition = XPosition

    @property
    def YPosition(self):
        return self._YPosition

    @YPosition.setter
    def YPosition(self, YPosition):
        self._YPosition = YPosition

    @property
    def WatermarkName(self):
        return self._WatermarkName

    @WatermarkName.setter
    def WatermarkName(self, WatermarkName):
        self._WatermarkName = WatermarkName

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
    def Width(self):
        return self._Width

    @Width.setter
    def Width(self, Width):
        self._Width = Width

    @property
    def Height(self):
        return self._Height

    @Height.setter
    def Height(self, Height):
        self._Height = Height


    def _deserialize(self, params):
        self._WatermarkId = params.get("WatermarkId")
        self._PictureUrl = params.get("PictureUrl")
        self._XPosition = params.get("XPosition")
        self._YPosition = params.get("YPosition")
        self._WatermarkName = params.get("WatermarkName")
        self._Status = params.get("Status")
        self._CreateTime = params.get("CreateTime")
        self._Width = params.get("Width")
        self._Height = params.get("Height")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        