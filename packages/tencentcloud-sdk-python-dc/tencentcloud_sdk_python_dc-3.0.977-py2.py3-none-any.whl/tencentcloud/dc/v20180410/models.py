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


class AcceptDirectConnectTunnelRequest(AbstractModel):
    """AcceptDirectConnectTunnel请求参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectTunnelId: 物理专线拥有者接受共享专用通道申请
        :type DirectConnectTunnelId: str
        """
        self._DirectConnectTunnelId = None

    @property
    def DirectConnectTunnelId(self):
        return self._DirectConnectTunnelId

    @DirectConnectTunnelId.setter
    def DirectConnectTunnelId(self, DirectConnectTunnelId):
        self._DirectConnectTunnelId = DirectConnectTunnelId


    def _deserialize(self, params):
        self._DirectConnectTunnelId = params.get("DirectConnectTunnelId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class AcceptDirectConnectTunnelResponse(AbstractModel):
    """AcceptDirectConnectTunnel返回参数结构体

    """

    def __init__(self):
        r"""
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
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


class AccessPoint(AbstractModel):
    """接入点信息。

    """

    def __init__(self):
        r"""
        :param _AccessPointName: 接入点的名称。
        :type AccessPointName: str
        :param _AccessPointId: 接入点唯一ID。
        :type AccessPointId: str
        :param _State: 接入点的状态。可用，不可用。
        :type State: str
        :param _Location: 接入点的位置。
        :type Location: str
        :param _LineOperator: 接入点支持的运营商列表。
        :type LineOperator: list of str
        :param _RegionId: 接入点管理的大区ID。
        :type RegionId: str
        :param _AvailablePortType: 接入点可用的端口类型列表。1000BASE-T代表千兆电口，1000BASE-LX代表千兆单模光口10km，1000BASE-ZX代表千兆单模光口80km,10GBASE-LR代表万兆单模光口10km,10GBASE-ZR代表万兆单模光口80km,10GBASE-LH代表万兆单模光口40km,100GBASE-LR4代表100G单模光口10km
注意：此字段可能返回 null，表示取不到有效值。
        :type AvailablePortType: list of str
        :param _Coordinate: 接入点经纬度
注意：此字段可能返回 null，表示取不到有效值。
        :type Coordinate: :class:`tencentcloud.dc.v20180410.models.Coordinate`
        :param _City: 接入点所在城市
注意：此字段可能返回 null，表示取不到有效值。
        :type City: str
        :param _Area: 接入点地域名称
注意：此字段可能返回 null，表示取不到有效值。
        :type Area: str
        :param _AccessPointType: 接入点类型。VXLAN/QCPL/QCAR
注意：此字段可能返回 null，表示取不到有效值。
        :type AccessPointType: str
        """
        self._AccessPointName = None
        self._AccessPointId = None
        self._State = None
        self._Location = None
        self._LineOperator = None
        self._RegionId = None
        self._AvailablePortType = None
        self._Coordinate = None
        self._City = None
        self._Area = None
        self._AccessPointType = None

    @property
    def AccessPointName(self):
        return self._AccessPointName

    @AccessPointName.setter
    def AccessPointName(self, AccessPointName):
        self._AccessPointName = AccessPointName

    @property
    def AccessPointId(self):
        return self._AccessPointId

    @AccessPointId.setter
    def AccessPointId(self, AccessPointId):
        self._AccessPointId = AccessPointId

    @property
    def State(self):
        return self._State

    @State.setter
    def State(self, State):
        self._State = State

    @property
    def Location(self):
        return self._Location

    @Location.setter
    def Location(self, Location):
        self._Location = Location

    @property
    def LineOperator(self):
        return self._LineOperator

    @LineOperator.setter
    def LineOperator(self, LineOperator):
        self._LineOperator = LineOperator

    @property
    def RegionId(self):
        return self._RegionId

    @RegionId.setter
    def RegionId(self, RegionId):
        self._RegionId = RegionId

    @property
    def AvailablePortType(self):
        return self._AvailablePortType

    @AvailablePortType.setter
    def AvailablePortType(self, AvailablePortType):
        self._AvailablePortType = AvailablePortType

    @property
    def Coordinate(self):
        return self._Coordinate

    @Coordinate.setter
    def Coordinate(self, Coordinate):
        self._Coordinate = Coordinate

    @property
    def City(self):
        return self._City

    @City.setter
    def City(self, City):
        self._City = City

    @property
    def Area(self):
        return self._Area

    @Area.setter
    def Area(self, Area):
        self._Area = Area

    @property
    def AccessPointType(self):
        return self._AccessPointType

    @AccessPointType.setter
    def AccessPointType(self, AccessPointType):
        self._AccessPointType = AccessPointType


    def _deserialize(self, params):
        self._AccessPointName = params.get("AccessPointName")
        self._AccessPointId = params.get("AccessPointId")
        self._State = params.get("State")
        self._Location = params.get("Location")
        self._LineOperator = params.get("LineOperator")
        self._RegionId = params.get("RegionId")
        self._AvailablePortType = params.get("AvailablePortType")
        if params.get("Coordinate") is not None:
            self._Coordinate = Coordinate()
            self._Coordinate._deserialize(params.get("Coordinate"))
        self._City = params.get("City")
        self._Area = params.get("Area")
        self._AccessPointType = params.get("AccessPointType")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ApplyInternetAddressRequest(AbstractModel):
    """ApplyInternetAddress请求参数结构体

    """

    def __init__(self):
        r"""
        :param _MaskLen: CIDR地址掩码长度
        :type MaskLen: int
        :param _AddrType: 0:BGP类型地址
1：中国电信
2：中国移动
3：中国联通
        :type AddrType: int
        :param _AddrProto: 0：IPv4
1:IPv6
        :type AddrProto: int
        """
        self._MaskLen = None
        self._AddrType = None
        self._AddrProto = None

    @property
    def MaskLen(self):
        return self._MaskLen

    @MaskLen.setter
    def MaskLen(self, MaskLen):
        self._MaskLen = MaskLen

    @property
    def AddrType(self):
        return self._AddrType

    @AddrType.setter
    def AddrType(self, AddrType):
        self._AddrType = AddrType

    @property
    def AddrProto(self):
        return self._AddrProto

    @AddrProto.setter
    def AddrProto(self, AddrProto):
        self._AddrProto = AddrProto


    def _deserialize(self, params):
        self._MaskLen = params.get("MaskLen")
        self._AddrType = params.get("AddrType")
        self._AddrProto = params.get("AddrProto")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ApplyInternetAddressResponse(AbstractModel):
    """ApplyInternetAddress返回参数结构体

    """

    def __init__(self):
        r"""
        :param _InstanceId: 互联网公网地址ID
注意：此字段可能返回 null，表示取不到有效值。
        :type InstanceId: str
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
        :type RequestId: str
        """
        self._InstanceId = None
        self._RequestId = None

    @property
    def InstanceId(self):
        return self._InstanceId

    @InstanceId.setter
    def InstanceId(self, InstanceId):
        self._InstanceId = InstanceId

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._InstanceId = params.get("InstanceId")
        self._RequestId = params.get("RequestId")


class BFDInfo(AbstractModel):
    """BFD配置信息

    """

    def __init__(self):
        r"""
        :param _ProbeFailedTimes: 健康检查次数
        :type ProbeFailedTimes: int
        :param _Interval: 健康检查间隔
        :type Interval: int
        """
        self._ProbeFailedTimes = None
        self._Interval = None

    @property
    def ProbeFailedTimes(self):
        return self._ProbeFailedTimes

    @ProbeFailedTimes.setter
    def ProbeFailedTimes(self, ProbeFailedTimes):
        self._ProbeFailedTimes = ProbeFailedTimes

    @property
    def Interval(self):
        return self._Interval

    @Interval.setter
    def Interval(self, Interval):
        self._Interval = Interval


    def _deserialize(self, params):
        self._ProbeFailedTimes = params.get("ProbeFailedTimes")
        self._Interval = params.get("Interval")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class BGPStatus(AbstractModel):
    """bgp状态信息

    """

    def __init__(self):
        r"""
        :param _TencentAddressBgpState: 腾讯侧主互联IP BGP状态
        :type TencentAddressBgpState: str
        :param _TencentBackupAddressBgpState: 腾讯侧备互联IP BGP状态
        :type TencentBackupAddressBgpState: str
        """
        self._TencentAddressBgpState = None
        self._TencentBackupAddressBgpState = None

    @property
    def TencentAddressBgpState(self):
        return self._TencentAddressBgpState

    @TencentAddressBgpState.setter
    def TencentAddressBgpState(self, TencentAddressBgpState):
        self._TencentAddressBgpState = TencentAddressBgpState

    @property
    def TencentBackupAddressBgpState(self):
        return self._TencentBackupAddressBgpState

    @TencentBackupAddressBgpState.setter
    def TencentBackupAddressBgpState(self, TencentBackupAddressBgpState):
        self._TencentBackupAddressBgpState = TencentBackupAddressBgpState


    def _deserialize(self, params):
        self._TencentAddressBgpState = params.get("TencentAddressBgpState")
        self._TencentBackupAddressBgpState = params.get("TencentBackupAddressBgpState")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class BgpPeer(AbstractModel):
    """bgp参数，包括Asn，AuthKey

    """

    def __init__(self):
        r"""
        :param _Asn: 用户侧，BGP Asn
        :type Asn: int
        :param _AuthKey: 用户侧BGP密钥
        :type AuthKey: str
        """
        self._Asn = None
        self._AuthKey = None

    @property
    def Asn(self):
        return self._Asn

    @Asn.setter
    def Asn(self, Asn):
        self._Asn = Asn

    @property
    def AuthKey(self):
        return self._AuthKey

    @AuthKey.setter
    def AuthKey(self, AuthKey):
        self._AuthKey = AuthKey


    def _deserialize(self, params):
        self._Asn = params.get("Asn")
        self._AuthKey = params.get("AuthKey")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class Coordinate(AbstractModel):
    """坐标，经维度描述

    """

    def __init__(self):
        r"""
        :param _Lat: 纬度
        :type Lat: float
        :param _Lng: 经度
        :type Lng: float
        """
        self._Lat = None
        self._Lng = None

    @property
    def Lat(self):
        return self._Lat

    @Lat.setter
    def Lat(self, Lat):
        self._Lat = Lat

    @property
    def Lng(self):
        return self._Lng

    @Lng.setter
    def Lng(self, Lng):
        self._Lng = Lng


    def _deserialize(self, params):
        self._Lat = params.get("Lat")
        self._Lng = params.get("Lng")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateDirectConnectRequest(AbstractModel):
    """CreateDirectConnect请求参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectName: 物理专线的名称。
        :type DirectConnectName: str
        :param _AccessPointId: 物理专线所在的接入点。
您可以通过调用 DescribeAccessPoints接口获取地域ID。所选择的接入点必须存在且处于可接入的状态。
        :type AccessPointId: str
        :param _LineOperator: 提供接入物理专线的运营商。
ChinaTelecom：中国电信； 
ChinaMobile：中国移动；
ChinaUnicom：中国联通；
 In-houseWiring：楼内线；
ChinaOther：中国其他；
 InternationalOperator：境外其他。
        :type LineOperator: str
        :param _PortType: 物理专线接入端口类型，取值：
100Base-T：百兆电口；
1000Base-T（默认值）：千兆电口；
1000Base-LX：千兆单模光口（10千米）；
10GBase-T：万兆电口；
10GBase-LR（默认值）：万兆单模光口（10千米）。
        :type PortType: str
        :param _CircuitCode: 运营商或者服务商为物理专线提供的电路编码。
        :type CircuitCode: str
        :param _Location: 本地数据中心的地理位置。
        :type Location: str
        :param _Bandwidth: 物理专线接入接口带宽，单位为Mbps，默认值为1000，取值范围为 [2, 10240]。
        :type Bandwidth: int
        :param _RedundantDirectConnectId: 冗余物理专线的ID。
        :type RedundantDirectConnectId: str
        :param _Vlan: 物理专线调试VLAN。默认开启VLAN，自动分配VLAN。
        :type Vlan: int
        :param _TencentAddress: 物理专线调试腾讯侧互联 IP。默认自动分配。
        :type TencentAddress: str
        :param _CustomerAddress: 物理专线调试用户侧互联 IP。默认自动分配。
        :type CustomerAddress: str
        :param _CustomerName: 物理专线申请者姓名。默认从账户体系获取。
        :type CustomerName: str
        :param _CustomerContactMail: 物理专线申请者联系邮箱。默认从账户体系获取。
        :type CustomerContactMail: str
        :param _CustomerContactNumber: 物理专线申请者联系号码。默认从账户体系获取。
        :type CustomerContactNumber: str
        :param _FaultReportContactPerson: 报障联系人。
        :type FaultReportContactPerson: str
        :param _FaultReportContactNumber: 报障联系电话。
        :type FaultReportContactNumber: str
        :param _SignLaw: 物理专线申请者是否签署了用户使用协议。默认已签署。
        :type SignLaw: bool
        """
        self._DirectConnectName = None
        self._AccessPointId = None
        self._LineOperator = None
        self._PortType = None
        self._CircuitCode = None
        self._Location = None
        self._Bandwidth = None
        self._RedundantDirectConnectId = None
        self._Vlan = None
        self._TencentAddress = None
        self._CustomerAddress = None
        self._CustomerName = None
        self._CustomerContactMail = None
        self._CustomerContactNumber = None
        self._FaultReportContactPerson = None
        self._FaultReportContactNumber = None
        self._SignLaw = None

    @property
    def DirectConnectName(self):
        return self._DirectConnectName

    @DirectConnectName.setter
    def DirectConnectName(self, DirectConnectName):
        self._DirectConnectName = DirectConnectName

    @property
    def AccessPointId(self):
        return self._AccessPointId

    @AccessPointId.setter
    def AccessPointId(self, AccessPointId):
        self._AccessPointId = AccessPointId

    @property
    def LineOperator(self):
        return self._LineOperator

    @LineOperator.setter
    def LineOperator(self, LineOperator):
        self._LineOperator = LineOperator

    @property
    def PortType(self):
        return self._PortType

    @PortType.setter
    def PortType(self, PortType):
        self._PortType = PortType

    @property
    def CircuitCode(self):
        return self._CircuitCode

    @CircuitCode.setter
    def CircuitCode(self, CircuitCode):
        self._CircuitCode = CircuitCode

    @property
    def Location(self):
        return self._Location

    @Location.setter
    def Location(self, Location):
        self._Location = Location

    @property
    def Bandwidth(self):
        return self._Bandwidth

    @Bandwidth.setter
    def Bandwidth(self, Bandwidth):
        self._Bandwidth = Bandwidth

    @property
    def RedundantDirectConnectId(self):
        return self._RedundantDirectConnectId

    @RedundantDirectConnectId.setter
    def RedundantDirectConnectId(self, RedundantDirectConnectId):
        self._RedundantDirectConnectId = RedundantDirectConnectId

    @property
    def Vlan(self):
        return self._Vlan

    @Vlan.setter
    def Vlan(self, Vlan):
        self._Vlan = Vlan

    @property
    def TencentAddress(self):
        return self._TencentAddress

    @TencentAddress.setter
    def TencentAddress(self, TencentAddress):
        self._TencentAddress = TencentAddress

    @property
    def CustomerAddress(self):
        return self._CustomerAddress

    @CustomerAddress.setter
    def CustomerAddress(self, CustomerAddress):
        self._CustomerAddress = CustomerAddress

    @property
    def CustomerName(self):
        return self._CustomerName

    @CustomerName.setter
    def CustomerName(self, CustomerName):
        self._CustomerName = CustomerName

    @property
    def CustomerContactMail(self):
        return self._CustomerContactMail

    @CustomerContactMail.setter
    def CustomerContactMail(self, CustomerContactMail):
        self._CustomerContactMail = CustomerContactMail

    @property
    def CustomerContactNumber(self):
        return self._CustomerContactNumber

    @CustomerContactNumber.setter
    def CustomerContactNumber(self, CustomerContactNumber):
        self._CustomerContactNumber = CustomerContactNumber

    @property
    def FaultReportContactPerson(self):
        return self._FaultReportContactPerson

    @FaultReportContactPerson.setter
    def FaultReportContactPerson(self, FaultReportContactPerson):
        self._FaultReportContactPerson = FaultReportContactPerson

    @property
    def FaultReportContactNumber(self):
        return self._FaultReportContactNumber

    @FaultReportContactNumber.setter
    def FaultReportContactNumber(self, FaultReportContactNumber):
        self._FaultReportContactNumber = FaultReportContactNumber

    @property
    def SignLaw(self):
        return self._SignLaw

    @SignLaw.setter
    def SignLaw(self, SignLaw):
        self._SignLaw = SignLaw


    def _deserialize(self, params):
        self._DirectConnectName = params.get("DirectConnectName")
        self._AccessPointId = params.get("AccessPointId")
        self._LineOperator = params.get("LineOperator")
        self._PortType = params.get("PortType")
        self._CircuitCode = params.get("CircuitCode")
        self._Location = params.get("Location")
        self._Bandwidth = params.get("Bandwidth")
        self._RedundantDirectConnectId = params.get("RedundantDirectConnectId")
        self._Vlan = params.get("Vlan")
        self._TencentAddress = params.get("TencentAddress")
        self._CustomerAddress = params.get("CustomerAddress")
        self._CustomerName = params.get("CustomerName")
        self._CustomerContactMail = params.get("CustomerContactMail")
        self._CustomerContactNumber = params.get("CustomerContactNumber")
        self._FaultReportContactPerson = params.get("FaultReportContactPerson")
        self._FaultReportContactNumber = params.get("FaultReportContactNumber")
        self._SignLaw = params.get("SignLaw")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateDirectConnectResponse(AbstractModel):
    """CreateDirectConnect返回参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectIdSet: 物理专线的ID。
        :type DirectConnectIdSet: list of str
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
        :type RequestId: str
        """
        self._DirectConnectIdSet = None
        self._RequestId = None

    @property
    def DirectConnectIdSet(self):
        return self._DirectConnectIdSet

    @DirectConnectIdSet.setter
    def DirectConnectIdSet(self, DirectConnectIdSet):
        self._DirectConnectIdSet = DirectConnectIdSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._DirectConnectIdSet = params.get("DirectConnectIdSet")
        self._RequestId = params.get("RequestId")


class CreateDirectConnectTunnelRequest(AbstractModel):
    """CreateDirectConnectTunnel请求参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectId: 专线 ID，例如：dc-kd7d06of
        :type DirectConnectId: str
        :param _DirectConnectTunnelName: 专用通道名称
        :type DirectConnectTunnelName: str
        :param _DirectConnectOwnerAccount: 物理专线 owner，缺省为当前客户（物理专线 owner）
共享专线时这里需要填写共享专线的开发商账号 ID
        :type DirectConnectOwnerAccount: str
        :param _NetworkType: 网络类型，分别为VPC、BMVPC，CCN，默认是VPC
VPC：私有网络
BMVPC：黑石网络
CCN：云联网
        :type NetworkType: str
        :param _NetworkRegion: 网络地域
        :type NetworkRegion: str
        :param _VpcId: 私有网络统一 ID 或者黑石网络统一 ID
        :type VpcId: str
        :param _DirectConnectGatewayId: 专线网关 ID，例如 dcg-d545ddf
        :type DirectConnectGatewayId: str
        :param _Bandwidth: 专线带宽，单位：Mbps
默认是物理专线带宽值
        :type Bandwidth: int
        :param _RouteType: BGP ：BGP路由
STATIC：静态
默认为 BGP 路由
        :type RouteType: str
        :param _BgpPeer: BgpPeer，用户侧bgp信息，包括Asn和AuthKey
        :type BgpPeer: :class:`tencentcloud.dc.v20180410.models.BgpPeer`
        :param _RouteFilterPrefixes: 静态路由，用户IDC的网段地址
        :type RouteFilterPrefixes: list of RouteFilterPrefix
        :param _Vlan: vlan，范围：0 ~ 3000
0：不开启子接口
默认值是非0
        :type Vlan: int
        :param _TencentAddress: TencentAddress，腾讯侧互联 IP
        :type TencentAddress: str
        :param _CustomerAddress: CustomerAddress，用户侧互联 IP
        :type CustomerAddress: str
        :param _TencentBackupAddress: TencentBackupAddress，腾讯侧备用互联 IP
        :type TencentBackupAddress: str
        :param _CloudAttachId: 高速上云服务ID
        :type CloudAttachId: str
        :param _BfdEnable: 是否开启BFD
        :type BfdEnable: int
        :param _NqaEnable: 是否开启NQA
        :type NqaEnable: int
        :param _BfdInfo: BFD配置信息
        :type BfdInfo: :class:`tencentcloud.dc.v20180410.models.BFDInfo`
        :param _NqaInfo: NQA配置信息
        :type NqaInfo: :class:`tencentcloud.dc.v20180410.models.NQAInfo`
        """
        self._DirectConnectId = None
        self._DirectConnectTunnelName = None
        self._DirectConnectOwnerAccount = None
        self._NetworkType = None
        self._NetworkRegion = None
        self._VpcId = None
        self._DirectConnectGatewayId = None
        self._Bandwidth = None
        self._RouteType = None
        self._BgpPeer = None
        self._RouteFilterPrefixes = None
        self._Vlan = None
        self._TencentAddress = None
        self._CustomerAddress = None
        self._TencentBackupAddress = None
        self._CloudAttachId = None
        self._BfdEnable = None
        self._NqaEnable = None
        self._BfdInfo = None
        self._NqaInfo = None

    @property
    def DirectConnectId(self):
        return self._DirectConnectId

    @DirectConnectId.setter
    def DirectConnectId(self, DirectConnectId):
        self._DirectConnectId = DirectConnectId

    @property
    def DirectConnectTunnelName(self):
        return self._DirectConnectTunnelName

    @DirectConnectTunnelName.setter
    def DirectConnectTunnelName(self, DirectConnectTunnelName):
        self._DirectConnectTunnelName = DirectConnectTunnelName

    @property
    def DirectConnectOwnerAccount(self):
        return self._DirectConnectOwnerAccount

    @DirectConnectOwnerAccount.setter
    def DirectConnectOwnerAccount(self, DirectConnectOwnerAccount):
        self._DirectConnectOwnerAccount = DirectConnectOwnerAccount

    @property
    def NetworkType(self):
        return self._NetworkType

    @NetworkType.setter
    def NetworkType(self, NetworkType):
        self._NetworkType = NetworkType

    @property
    def NetworkRegion(self):
        return self._NetworkRegion

    @NetworkRegion.setter
    def NetworkRegion(self, NetworkRegion):
        self._NetworkRegion = NetworkRegion

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def DirectConnectGatewayId(self):
        return self._DirectConnectGatewayId

    @DirectConnectGatewayId.setter
    def DirectConnectGatewayId(self, DirectConnectGatewayId):
        self._DirectConnectGatewayId = DirectConnectGatewayId

    @property
    def Bandwidth(self):
        return self._Bandwidth

    @Bandwidth.setter
    def Bandwidth(self, Bandwidth):
        self._Bandwidth = Bandwidth

    @property
    def RouteType(self):
        return self._RouteType

    @RouteType.setter
    def RouteType(self, RouteType):
        self._RouteType = RouteType

    @property
    def BgpPeer(self):
        return self._BgpPeer

    @BgpPeer.setter
    def BgpPeer(self, BgpPeer):
        self._BgpPeer = BgpPeer

    @property
    def RouteFilterPrefixes(self):
        return self._RouteFilterPrefixes

    @RouteFilterPrefixes.setter
    def RouteFilterPrefixes(self, RouteFilterPrefixes):
        self._RouteFilterPrefixes = RouteFilterPrefixes

    @property
    def Vlan(self):
        return self._Vlan

    @Vlan.setter
    def Vlan(self, Vlan):
        self._Vlan = Vlan

    @property
    def TencentAddress(self):
        return self._TencentAddress

    @TencentAddress.setter
    def TencentAddress(self, TencentAddress):
        self._TencentAddress = TencentAddress

    @property
    def CustomerAddress(self):
        return self._CustomerAddress

    @CustomerAddress.setter
    def CustomerAddress(self, CustomerAddress):
        self._CustomerAddress = CustomerAddress

    @property
    def TencentBackupAddress(self):
        return self._TencentBackupAddress

    @TencentBackupAddress.setter
    def TencentBackupAddress(self, TencentBackupAddress):
        self._TencentBackupAddress = TencentBackupAddress

    @property
    def CloudAttachId(self):
        return self._CloudAttachId

    @CloudAttachId.setter
    def CloudAttachId(self, CloudAttachId):
        self._CloudAttachId = CloudAttachId

    @property
    def BfdEnable(self):
        return self._BfdEnable

    @BfdEnable.setter
    def BfdEnable(self, BfdEnable):
        self._BfdEnable = BfdEnable

    @property
    def NqaEnable(self):
        return self._NqaEnable

    @NqaEnable.setter
    def NqaEnable(self, NqaEnable):
        self._NqaEnable = NqaEnable

    @property
    def BfdInfo(self):
        return self._BfdInfo

    @BfdInfo.setter
    def BfdInfo(self, BfdInfo):
        self._BfdInfo = BfdInfo

    @property
    def NqaInfo(self):
        return self._NqaInfo

    @NqaInfo.setter
    def NqaInfo(self, NqaInfo):
        self._NqaInfo = NqaInfo


    def _deserialize(self, params):
        self._DirectConnectId = params.get("DirectConnectId")
        self._DirectConnectTunnelName = params.get("DirectConnectTunnelName")
        self._DirectConnectOwnerAccount = params.get("DirectConnectOwnerAccount")
        self._NetworkType = params.get("NetworkType")
        self._NetworkRegion = params.get("NetworkRegion")
        self._VpcId = params.get("VpcId")
        self._DirectConnectGatewayId = params.get("DirectConnectGatewayId")
        self._Bandwidth = params.get("Bandwidth")
        self._RouteType = params.get("RouteType")
        if params.get("BgpPeer") is not None:
            self._BgpPeer = BgpPeer()
            self._BgpPeer._deserialize(params.get("BgpPeer"))
        if params.get("RouteFilterPrefixes") is not None:
            self._RouteFilterPrefixes = []
            for item in params.get("RouteFilterPrefixes"):
                obj = RouteFilterPrefix()
                obj._deserialize(item)
                self._RouteFilterPrefixes.append(obj)
        self._Vlan = params.get("Vlan")
        self._TencentAddress = params.get("TencentAddress")
        self._CustomerAddress = params.get("CustomerAddress")
        self._TencentBackupAddress = params.get("TencentBackupAddress")
        self._CloudAttachId = params.get("CloudAttachId")
        self._BfdEnable = params.get("BfdEnable")
        self._NqaEnable = params.get("NqaEnable")
        if params.get("BfdInfo") is not None:
            self._BfdInfo = BFDInfo()
            self._BfdInfo._deserialize(params.get("BfdInfo"))
        if params.get("NqaInfo") is not None:
            self._NqaInfo = NQAInfo()
            self._NqaInfo._deserialize(params.get("NqaInfo"))
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class CreateDirectConnectTunnelResponse(AbstractModel):
    """CreateDirectConnectTunnel返回参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectTunnelIdSet: 专用通道ID
        :type DirectConnectTunnelIdSet: list of str
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
        :type RequestId: str
        """
        self._DirectConnectTunnelIdSet = None
        self._RequestId = None

    @property
    def DirectConnectTunnelIdSet(self):
        return self._DirectConnectTunnelIdSet

    @DirectConnectTunnelIdSet.setter
    def DirectConnectTunnelIdSet(self, DirectConnectTunnelIdSet):
        self._DirectConnectTunnelIdSet = DirectConnectTunnelIdSet

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._DirectConnectTunnelIdSet = params.get("DirectConnectTunnelIdSet")
        self._RequestId = params.get("RequestId")


class DeleteDirectConnectRequest(AbstractModel):
    """DeleteDirectConnect请求参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectId: 物理专线的ID。
        :type DirectConnectId: str
        """
        self._DirectConnectId = None

    @property
    def DirectConnectId(self):
        return self._DirectConnectId

    @DirectConnectId.setter
    def DirectConnectId(self, DirectConnectId):
        self._DirectConnectId = DirectConnectId


    def _deserialize(self, params):
        self._DirectConnectId = params.get("DirectConnectId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteDirectConnectResponse(AbstractModel):
    """DeleteDirectConnect返回参数结构体

    """

    def __init__(self):
        r"""
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
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


class DeleteDirectConnectTunnelRequest(AbstractModel):
    """DeleteDirectConnectTunnel请求参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectTunnelId: 专用通道ID
        :type DirectConnectTunnelId: str
        """
        self._DirectConnectTunnelId = None

    @property
    def DirectConnectTunnelId(self):
        return self._DirectConnectTunnelId

    @DirectConnectTunnelId.setter
    def DirectConnectTunnelId(self, DirectConnectTunnelId):
        self._DirectConnectTunnelId = DirectConnectTunnelId


    def _deserialize(self, params):
        self._DirectConnectTunnelId = params.get("DirectConnectTunnelId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DeleteDirectConnectTunnelResponse(AbstractModel):
    """DeleteDirectConnectTunnel返回参数结构体

    """

    def __init__(self):
        r"""
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
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


class DescribeAccessPointsRequest(AbstractModel):
    """DescribeAccessPoints请求参数结构体

    """

    def __init__(self):
        r"""
        :param _RegionId: 接入点所在的地域。使用DescribeRegions查询

您可以通过调用 DescribeRegions接口获取地域ID。
        :type RegionId: str
        :param _Offset: 偏移量，默认为0。
        :type Offset: int
        :param _Limit: 返回数量，默认为20，最大值为100。
        :type Limit: int
        """
        self._RegionId = None
        self._Offset = None
        self._Limit = None

    @property
    def RegionId(self):
        return self._RegionId

    @RegionId.setter
    def RegionId(self, RegionId):
        self._RegionId = RegionId

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
        self._RegionId = params.get("RegionId")
        self._Offset = params.get("Offset")
        self._Limit = params.get("Limit")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeAccessPointsResponse(AbstractModel):
    """DescribeAccessPoints返回参数结构体

    """

    def __init__(self):
        r"""
        :param _AccessPointSet: 接入点信息。
        :type AccessPointSet: list of AccessPoint
        :param _TotalCount: 符合接入点数量。
        :type TotalCount: int
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
        :type RequestId: str
        """
        self._AccessPointSet = None
        self._TotalCount = None
        self._RequestId = None

    @property
    def AccessPointSet(self):
        return self._AccessPointSet

    @AccessPointSet.setter
    def AccessPointSet(self, AccessPointSet):
        self._AccessPointSet = AccessPointSet

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
        if params.get("AccessPointSet") is not None:
            self._AccessPointSet = []
            for item in params.get("AccessPointSet"):
                obj = AccessPoint()
                obj._deserialize(item)
                self._AccessPointSet.append(obj)
        self._TotalCount = params.get("TotalCount")
        self._RequestId = params.get("RequestId")


class DescribeDirectConnectTunnelExtraRequest(AbstractModel):
    """DescribeDirectConnectTunnelExtra请求参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectTunnelId: 专用通道ID
        :type DirectConnectTunnelId: str
        """
        self._DirectConnectTunnelId = None

    @property
    def DirectConnectTunnelId(self):
        return self._DirectConnectTunnelId

    @DirectConnectTunnelId.setter
    def DirectConnectTunnelId(self, DirectConnectTunnelId):
        self._DirectConnectTunnelId = DirectConnectTunnelId


    def _deserialize(self, params):
        self._DirectConnectTunnelId = params.get("DirectConnectTunnelId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeDirectConnectTunnelExtraResponse(AbstractModel):
    """DescribeDirectConnectTunnelExtra返回参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectTunnelExtra: 专用通道扩展信息
        :type DirectConnectTunnelExtra: :class:`tencentcloud.dc.v20180410.models.DirectConnectTunnelExtra`
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
        :type RequestId: str
        """
        self._DirectConnectTunnelExtra = None
        self._RequestId = None

    @property
    def DirectConnectTunnelExtra(self):
        return self._DirectConnectTunnelExtra

    @DirectConnectTunnelExtra.setter
    def DirectConnectTunnelExtra(self, DirectConnectTunnelExtra):
        self._DirectConnectTunnelExtra = DirectConnectTunnelExtra

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DirectConnectTunnelExtra") is not None:
            self._DirectConnectTunnelExtra = DirectConnectTunnelExtra()
            self._DirectConnectTunnelExtra._deserialize(params.get("DirectConnectTunnelExtra"))
        self._RequestId = params.get("RequestId")


class DescribeDirectConnectTunnelsRequest(AbstractModel):
    """DescribeDirectConnectTunnels请求参数结构体

    """

    def __init__(self):
        r"""
        :param _Filters: 过滤条件:
参数不支持同时指定DirectConnectTunnelIds和Filters。
<li> direct-connect-tunnel-name, 专用通道名称。</li>
<li> direct-connect-tunnel-id, 专用通道实例ID，如dcx-abcdefgh。</li>
<li>direct-connect-id, 物理专线实例ID，如，dc-abcdefgh。</li>
        :type Filters: list of Filter
        :param _DirectConnectTunnelIds: 专用通道 ID数组
        :type DirectConnectTunnelIds: list of str
        :param _Offset: 偏移量，默认为0
        :type Offset: int
        :param _Limit: 返回数量，默认为20，最大值为100
        :type Limit: int
        """
        self._Filters = None
        self._DirectConnectTunnelIds = None
        self._Offset = None
        self._Limit = None

    @property
    def Filters(self):
        return self._Filters

    @Filters.setter
    def Filters(self, Filters):
        self._Filters = Filters

    @property
    def DirectConnectTunnelIds(self):
        return self._DirectConnectTunnelIds

    @DirectConnectTunnelIds.setter
    def DirectConnectTunnelIds(self, DirectConnectTunnelIds):
        self._DirectConnectTunnelIds = DirectConnectTunnelIds

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
        if params.get("Filters") is not None:
            self._Filters = []
            for item in params.get("Filters"):
                obj = Filter()
                obj._deserialize(item)
                self._Filters.append(obj)
        self._DirectConnectTunnelIds = params.get("DirectConnectTunnelIds")
        self._Offset = params.get("Offset")
        self._Limit = params.get("Limit")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeDirectConnectTunnelsResponse(AbstractModel):
    """DescribeDirectConnectTunnels返回参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectTunnelSet: 专用通道列表
        :type DirectConnectTunnelSet: list of DirectConnectTunnel
        :param _TotalCount: 符合专用通道数量。
        :type TotalCount: int
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
        :type RequestId: str
        """
        self._DirectConnectTunnelSet = None
        self._TotalCount = None
        self._RequestId = None

    @property
    def DirectConnectTunnelSet(self):
        return self._DirectConnectTunnelSet

    @DirectConnectTunnelSet.setter
    def DirectConnectTunnelSet(self, DirectConnectTunnelSet):
        self._DirectConnectTunnelSet = DirectConnectTunnelSet

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
        if params.get("DirectConnectTunnelSet") is not None:
            self._DirectConnectTunnelSet = []
            for item in params.get("DirectConnectTunnelSet"):
                obj = DirectConnectTunnel()
                obj._deserialize(item)
                self._DirectConnectTunnelSet.append(obj)
        self._TotalCount = params.get("TotalCount")
        self._RequestId = params.get("RequestId")


class DescribeDirectConnectsRequest(AbstractModel):
    """DescribeDirectConnects请求参数结构体

    """

    def __init__(self):
        r"""
        :param _Filters: 过滤条件:
        :type Filters: list of Filter
        :param _DirectConnectIds: 物理专线 ID数组
        :type DirectConnectIds: list of str
        :param _Offset: 偏移量，默认为0
        :type Offset: int
        :param _Limit: 返回数量，默认为20，最大值为100
        :type Limit: int
        """
        self._Filters = None
        self._DirectConnectIds = None
        self._Offset = None
        self._Limit = None

    @property
    def Filters(self):
        return self._Filters

    @Filters.setter
    def Filters(self, Filters):
        self._Filters = Filters

    @property
    def DirectConnectIds(self):
        return self._DirectConnectIds

    @DirectConnectIds.setter
    def DirectConnectIds(self, DirectConnectIds):
        self._DirectConnectIds = DirectConnectIds

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
        if params.get("Filters") is not None:
            self._Filters = []
            for item in params.get("Filters"):
                obj = Filter()
                obj._deserialize(item)
                self._Filters.append(obj)
        self._DirectConnectIds = params.get("DirectConnectIds")
        self._Offset = params.get("Offset")
        self._Limit = params.get("Limit")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeDirectConnectsResponse(AbstractModel):
    """DescribeDirectConnects返回参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectSet: 物理专线列表。
        :type DirectConnectSet: list of DirectConnect
        :param _TotalCount: 符合物理专线列表数量。
        :type TotalCount: int
        :param _AllSignLaw: 用户名下物理专线是否都签署了用户协议
注意：此字段可能返回 null，表示取不到有效值。
        :type AllSignLaw: bool
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
        :type RequestId: str
        """
        self._DirectConnectSet = None
        self._TotalCount = None
        self._AllSignLaw = None
        self._RequestId = None

    @property
    def DirectConnectSet(self):
        return self._DirectConnectSet

    @DirectConnectSet.setter
    def DirectConnectSet(self, DirectConnectSet):
        self._DirectConnectSet = DirectConnectSet

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def AllSignLaw(self):
        return self._AllSignLaw

    @AllSignLaw.setter
    def AllSignLaw(self, AllSignLaw):
        self._AllSignLaw = AllSignLaw

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        if params.get("DirectConnectSet") is not None:
            self._DirectConnectSet = []
            for item in params.get("DirectConnectSet"):
                obj = DirectConnect()
                obj._deserialize(item)
                self._DirectConnectSet.append(obj)
        self._TotalCount = params.get("TotalCount")
        self._AllSignLaw = params.get("AllSignLaw")
        self._RequestId = params.get("RequestId")


class DescribeInternetAddressQuotaRequest(AbstractModel):
    """DescribeInternetAddressQuota请求参数结构体

    """


class DescribeInternetAddressQuotaResponse(AbstractModel):
    """DescribeInternetAddressQuota返回参数结构体

    """

    def __init__(self):
        r"""
        :param _Ipv6PrefixLen: IPv6互联网公网允许的最小前缀长度
注意：此字段可能返回 null，表示取不到有效值。
        :type Ipv6PrefixLen: int
        :param _Ipv4BgpQuota: BGP类型IPv4互联网地址配额
注意：此字段可能返回 null，表示取不到有效值。
        :type Ipv4BgpQuota: int
        :param _Ipv4OtherQuota: 非BGP类型IPv4互联网地址配额
注意：此字段可能返回 null，表示取不到有效值。
        :type Ipv4OtherQuota: int
        :param _Ipv4BgpNum: BGP类型IPv4互联网地址已使用数量
注意：此字段可能返回 null，表示取不到有效值。
        :type Ipv4BgpNum: int
        :param _Ipv4OtherNum: 非BGP类型互联网地址已使用数量
注意：此字段可能返回 null，表示取不到有效值。
        :type Ipv4OtherNum: int
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
        :type RequestId: str
        """
        self._Ipv6PrefixLen = None
        self._Ipv4BgpQuota = None
        self._Ipv4OtherQuota = None
        self._Ipv4BgpNum = None
        self._Ipv4OtherNum = None
        self._RequestId = None

    @property
    def Ipv6PrefixLen(self):
        return self._Ipv6PrefixLen

    @Ipv6PrefixLen.setter
    def Ipv6PrefixLen(self, Ipv6PrefixLen):
        self._Ipv6PrefixLen = Ipv6PrefixLen

    @property
    def Ipv4BgpQuota(self):
        return self._Ipv4BgpQuota

    @Ipv4BgpQuota.setter
    def Ipv4BgpQuota(self, Ipv4BgpQuota):
        self._Ipv4BgpQuota = Ipv4BgpQuota

    @property
    def Ipv4OtherQuota(self):
        return self._Ipv4OtherQuota

    @Ipv4OtherQuota.setter
    def Ipv4OtherQuota(self, Ipv4OtherQuota):
        self._Ipv4OtherQuota = Ipv4OtherQuota

    @property
    def Ipv4BgpNum(self):
        return self._Ipv4BgpNum

    @Ipv4BgpNum.setter
    def Ipv4BgpNum(self, Ipv4BgpNum):
        self._Ipv4BgpNum = Ipv4BgpNum

    @property
    def Ipv4OtherNum(self):
        return self._Ipv4OtherNum

    @Ipv4OtherNum.setter
    def Ipv4OtherNum(self, Ipv4OtherNum):
        self._Ipv4OtherNum = Ipv4OtherNum

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._Ipv6PrefixLen = params.get("Ipv6PrefixLen")
        self._Ipv4BgpQuota = params.get("Ipv4BgpQuota")
        self._Ipv4OtherQuota = params.get("Ipv4OtherQuota")
        self._Ipv4BgpNum = params.get("Ipv4BgpNum")
        self._Ipv4OtherNum = params.get("Ipv4OtherNum")
        self._RequestId = params.get("RequestId")


class DescribeInternetAddressRequest(AbstractModel):
    """DescribeInternetAddress请求参数结构体

    """

    def __init__(self):
        r"""
        :param _Offset: 偏移量，默认为0
        :type Offset: int
        :param _Limit: 返回数量，默认为20，最大值100
        :type Limit: int
        :param _Filters: 过滤条件：
<li>AddrType, 地址类型。0：BGP 1; 1: 电信， 2：移动， 3：联通</li>
<li>AddrProto地址类型。0：IPv4 1:IPv6</li>
<li>Status 地址状态。 0：使用中， 1：已停用， 2：已退还</li>
<li>Subnet 互联网公网地址，数组</li>
<InstanceIds>互联网公网地址ID，数组</li>
        :type Filters: list of Filter
        """
        self._Offset = None
        self._Limit = None
        self._Filters = None

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

    @property
    def Filters(self):
        return self._Filters

    @Filters.setter
    def Filters(self, Filters):
        self._Filters = Filters


    def _deserialize(self, params):
        self._Offset = params.get("Offset")
        self._Limit = params.get("Limit")
        if params.get("Filters") is not None:
            self._Filters = []
            for item in params.get("Filters"):
                obj = Filter()
                obj._deserialize(item)
                self._Filters.append(obj)
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribeInternetAddressResponse(AbstractModel):
    """DescribeInternetAddress返回参数结构体

    """

    def __init__(self):
        r"""
        :param _TotalCount: 互联网公网地址数量
        :type TotalCount: int
        :param _Subnets: 互联网公网地址列表
注意：此字段可能返回 null，表示取不到有效值。
        :type Subnets: list of InternetAddressDetail
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
        :type RequestId: str
        """
        self._TotalCount = None
        self._Subnets = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def Subnets(self):
        return self._Subnets

    @Subnets.setter
    def Subnets(self, Subnets):
        self._Subnets = Subnets

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("Subnets") is not None:
            self._Subnets = []
            for item in params.get("Subnets"):
                obj = InternetAddressDetail()
                obj._deserialize(item)
                self._Subnets.append(obj)
        self._RequestId = params.get("RequestId")


class DescribeInternetAddressStatisticsRequest(AbstractModel):
    """DescribeInternetAddressStatistics请求参数结构体

    """


class DescribeInternetAddressStatisticsResponse(AbstractModel):
    """DescribeInternetAddressStatistics返回参数结构体

    """

    def __init__(self):
        r"""
        :param _TotalCount: 互联网公网地址统计信息数量
        :type TotalCount: int
        :param _InternetAddressStatistics: 互联网公网地址统计信息列表
注意：此字段可能返回 null，表示取不到有效值。
        :type InternetAddressStatistics: list of InternetAddressStatistics
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
        :type RequestId: str
        """
        self._TotalCount = None
        self._InternetAddressStatistics = None
        self._RequestId = None

    @property
    def TotalCount(self):
        return self._TotalCount

    @TotalCount.setter
    def TotalCount(self, TotalCount):
        self._TotalCount = TotalCount

    @property
    def InternetAddressStatistics(self):
        return self._InternetAddressStatistics

    @InternetAddressStatistics.setter
    def InternetAddressStatistics(self, InternetAddressStatistics):
        self._InternetAddressStatistics = InternetAddressStatistics

    @property
    def RequestId(self):
        return self._RequestId

    @RequestId.setter
    def RequestId(self, RequestId):
        self._RequestId = RequestId


    def _deserialize(self, params):
        self._TotalCount = params.get("TotalCount")
        if params.get("InternetAddressStatistics") is not None:
            self._InternetAddressStatistics = []
            for item in params.get("InternetAddressStatistics"):
                obj = InternetAddressStatistics()
                obj._deserialize(item)
                self._InternetAddressStatistics.append(obj)
        self._RequestId = params.get("RequestId")


class DescribePublicDirectConnectTunnelRoutesRequest(AbstractModel):
    """DescribePublicDirectConnectTunnelRoutes请求参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectTunnelId: 专用通道ID
        :type DirectConnectTunnelId: str
        :param _Filters: 过滤条件：
route-type：路由类型，取值：BGP/STATIC
route-subnet：路由cidr，取值如：192.68.1.0/24
        :type Filters: list of Filter
        :param _Offset: 偏移量，默认为0
        :type Offset: int
        :param _Limit: 返回数量，默认为20，最大值为100
        :type Limit: int
        """
        self._DirectConnectTunnelId = None
        self._Filters = None
        self._Offset = None
        self._Limit = None

    @property
    def DirectConnectTunnelId(self):
        return self._DirectConnectTunnelId

    @DirectConnectTunnelId.setter
    def DirectConnectTunnelId(self, DirectConnectTunnelId):
        self._DirectConnectTunnelId = DirectConnectTunnelId

    @property
    def Filters(self):
        return self._Filters

    @Filters.setter
    def Filters(self, Filters):
        self._Filters = Filters

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
        self._DirectConnectTunnelId = params.get("DirectConnectTunnelId")
        if params.get("Filters") is not None:
            self._Filters = []
            for item in params.get("Filters"):
                obj = Filter()
                obj._deserialize(item)
                self._Filters.append(obj)
        self._Offset = params.get("Offset")
        self._Limit = params.get("Limit")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DescribePublicDirectConnectTunnelRoutesResponse(AbstractModel):
    """DescribePublicDirectConnectTunnelRoutes返回参数结构体

    """

    def __init__(self):
        r"""
        :param _Routes: 互联网通道路由列表
        :type Routes: list of DirectConnectTunnelRoute
        :param _TotalCount: 记录总数
        :type TotalCount: int
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
        :type RequestId: str
        """
        self._Routes = None
        self._TotalCount = None
        self._RequestId = None

    @property
    def Routes(self):
        return self._Routes

    @Routes.setter
    def Routes(self, Routes):
        self._Routes = Routes

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
        if params.get("Routes") is not None:
            self._Routes = []
            for item in params.get("Routes"):
                obj = DirectConnectTunnelRoute()
                obj._deserialize(item)
                self._Routes.append(obj)
        self._TotalCount = params.get("TotalCount")
        self._RequestId = params.get("RequestId")


class DirectConnect(AbstractModel):
    """物理专线信息列表

    """

    def __init__(self):
        r"""
        :param _DirectConnectId: 物理专线ID。
        :type DirectConnectId: str
        :param _DirectConnectName: 物理专线的名称。
        :type DirectConnectName: str
        :param _AccessPointId: 物理专线的接入点ID。
        :type AccessPointId: str
        :param _State: 物理专线的状态。
申请中：PENDING 
申请驳回：REJECTED   
待付款：TOPAY 
已付款：PAID 
建设中：ALLOCATED   
已开通：AVAILABLE  
删除中 ：DELETING
已删除：DELETED 。
        :type State: str
        :param _CreatedTime: 物理专线创建时间。
        :type CreatedTime: str
        :param _EnabledTime: 物理专线的开通时间。
        :type EnabledTime: str
        :param _LineOperator: 提供接入物理专线的运营商。ChinaTelecom：中国电信， ChinaMobile：中国移动，ChinaUnicom：中国联通， In-houseWiring：楼内线，ChinaOther：中国其他， InternationalOperator：境外其他。
        :type LineOperator: str
        :param _Location: 本地数据中心的地理位置。
        :type Location: str
        :param _Bandwidth: 物理专线接入接口带宽，单位为Mbps。
        :type Bandwidth: int
        :param _PortType: 用户侧物理专线接入端口类型,取值：100Base-T：百兆电口,1000Base-T（默认值）：千兆电口,1000Base-LX：千兆单模光口（10千米）,10GBase-T：万兆电口10GBase-LR：万兆单模光口（10千米），默认值，千兆单模光口（10千米）
        :type PortType: str
        :param _CircuitCode: 运营商或者服务商为物理专线提供的电路编码。
注意：此字段可能返回 null，表示取不到有效值。
        :type CircuitCode: str
        :param _RedundantDirectConnectId: 冗余物理专线的ID。
        :type RedundantDirectConnectId: str
        :param _Vlan: 物理专线调试VLAN。默认开启VLAN，自动分配VLAN。
注意：此字段可能返回 null，表示取不到有效值。
        :type Vlan: int
        :param _TencentAddress: 物理专线调试腾讯侧互联IP。
注意：此字段可能返回 null，表示取不到有效值。
        :type TencentAddress: str
        :param _CustomerAddress: 物理专线调试用户侧互联IP。
注意：此字段可能返回 null，表示取不到有效值。
        :type CustomerAddress: str
        :param _CustomerName: 物理专线申请者姓名。默认从账户体系获取。
注意：此字段可能返回 null，表示取不到有效值。
        :type CustomerName: str
        :param _CustomerContactMail: 物理专线申请者联系邮箱。默认从账户体系获取。
注意：此字段可能返回 null，表示取不到有效值。
        :type CustomerContactMail: str
        :param _CustomerContactNumber: 物理专线申请者联系号码。默认从账户体系获取。
注意：此字段可能返回 null，表示取不到有效值。
        :type CustomerContactNumber: str
        :param _ExpiredTime: 物理专线的过期时间。
注意：此字段可能返回 null，表示取不到有效值。
        :type ExpiredTime: str
        :param _ChargeType: 物理专线计费类型。 NON_RECURRING_CHARGE：一次性接入费用；PREPAID_BY_YEAR：按年预付费。
注意：此字段可能返回 null，表示取不到有效值。
        :type ChargeType: str
        :param _FaultReportContactPerson: 报障联系人。
注意：此字段可能返回 null，表示取不到有效值。
        :type FaultReportContactPerson: str
        :param _FaultReportContactNumber: 报障联系电话。
注意：此字段可能返回 null，表示取不到有效值。
        :type FaultReportContactNumber: str
        :param _TagSet: 标签键值对
注意：此字段可能返回 null，表示取不到有效值。
        :type TagSet: list of Tag
        :param _AccessPointType: 物理专线的接入点类型。
        :type AccessPointType: str
        :param _IdcCity: IDC所在城市
注意：此字段可能返回 null，表示取不到有效值。
        :type IdcCity: str
        :param _ChargeState: 计费状态
注意：此字段可能返回 null，表示取不到有效值。
        :type ChargeState: str
        :param _StartTime: 物理专线开通时间
注意：此字段可能返回 null，表示取不到有效值。
        :type StartTime: str
        :param _SignLaw: 物理专线是否已签署用户协议
注意：此字段可能返回 null，表示取不到有效值。
        :type SignLaw: bool
        :param _LocalZone: 物理专线是否为LocalZone
注意：此字段可能返回 null，表示取不到有效值。
        :type LocalZone: bool
        :param _VlanZeroDirectConnectTunnelCount: 该物理专线下vlan 0的专用通道数量
注意：此字段可能返回 null，表示取不到有效值。
        :type VlanZeroDirectConnectTunnelCount: int
        :param _OtherVlanDirectConnectTunnelCount: 该物理专线下非vlan 0的专用通道数量
注意：此字段可能返回 null，表示取不到有效值。
        :type OtherVlanDirectConnectTunnelCount: int
        :param _MinBandwidth: 物理专线最小带宽
注意：此字段可能返回 null，表示取不到有效值。
        :type MinBandwidth: int
        """
        self._DirectConnectId = None
        self._DirectConnectName = None
        self._AccessPointId = None
        self._State = None
        self._CreatedTime = None
        self._EnabledTime = None
        self._LineOperator = None
        self._Location = None
        self._Bandwidth = None
        self._PortType = None
        self._CircuitCode = None
        self._RedundantDirectConnectId = None
        self._Vlan = None
        self._TencentAddress = None
        self._CustomerAddress = None
        self._CustomerName = None
        self._CustomerContactMail = None
        self._CustomerContactNumber = None
        self._ExpiredTime = None
        self._ChargeType = None
        self._FaultReportContactPerson = None
        self._FaultReportContactNumber = None
        self._TagSet = None
        self._AccessPointType = None
        self._IdcCity = None
        self._ChargeState = None
        self._StartTime = None
        self._SignLaw = None
        self._LocalZone = None
        self._VlanZeroDirectConnectTunnelCount = None
        self._OtherVlanDirectConnectTunnelCount = None
        self._MinBandwidth = None

    @property
    def DirectConnectId(self):
        return self._DirectConnectId

    @DirectConnectId.setter
    def DirectConnectId(self, DirectConnectId):
        self._DirectConnectId = DirectConnectId

    @property
    def DirectConnectName(self):
        return self._DirectConnectName

    @DirectConnectName.setter
    def DirectConnectName(self, DirectConnectName):
        self._DirectConnectName = DirectConnectName

    @property
    def AccessPointId(self):
        return self._AccessPointId

    @AccessPointId.setter
    def AccessPointId(self, AccessPointId):
        self._AccessPointId = AccessPointId

    @property
    def State(self):
        return self._State

    @State.setter
    def State(self, State):
        self._State = State

    @property
    def CreatedTime(self):
        return self._CreatedTime

    @CreatedTime.setter
    def CreatedTime(self, CreatedTime):
        self._CreatedTime = CreatedTime

    @property
    def EnabledTime(self):
        return self._EnabledTime

    @EnabledTime.setter
    def EnabledTime(self, EnabledTime):
        self._EnabledTime = EnabledTime

    @property
    def LineOperator(self):
        return self._LineOperator

    @LineOperator.setter
    def LineOperator(self, LineOperator):
        self._LineOperator = LineOperator

    @property
    def Location(self):
        return self._Location

    @Location.setter
    def Location(self, Location):
        self._Location = Location

    @property
    def Bandwidth(self):
        return self._Bandwidth

    @Bandwidth.setter
    def Bandwidth(self, Bandwidth):
        self._Bandwidth = Bandwidth

    @property
    def PortType(self):
        return self._PortType

    @PortType.setter
    def PortType(self, PortType):
        self._PortType = PortType

    @property
    def CircuitCode(self):
        return self._CircuitCode

    @CircuitCode.setter
    def CircuitCode(self, CircuitCode):
        self._CircuitCode = CircuitCode

    @property
    def RedundantDirectConnectId(self):
        return self._RedundantDirectConnectId

    @RedundantDirectConnectId.setter
    def RedundantDirectConnectId(self, RedundantDirectConnectId):
        self._RedundantDirectConnectId = RedundantDirectConnectId

    @property
    def Vlan(self):
        return self._Vlan

    @Vlan.setter
    def Vlan(self, Vlan):
        self._Vlan = Vlan

    @property
    def TencentAddress(self):
        return self._TencentAddress

    @TencentAddress.setter
    def TencentAddress(self, TencentAddress):
        self._TencentAddress = TencentAddress

    @property
    def CustomerAddress(self):
        return self._CustomerAddress

    @CustomerAddress.setter
    def CustomerAddress(self, CustomerAddress):
        self._CustomerAddress = CustomerAddress

    @property
    def CustomerName(self):
        return self._CustomerName

    @CustomerName.setter
    def CustomerName(self, CustomerName):
        self._CustomerName = CustomerName

    @property
    def CustomerContactMail(self):
        return self._CustomerContactMail

    @CustomerContactMail.setter
    def CustomerContactMail(self, CustomerContactMail):
        self._CustomerContactMail = CustomerContactMail

    @property
    def CustomerContactNumber(self):
        return self._CustomerContactNumber

    @CustomerContactNumber.setter
    def CustomerContactNumber(self, CustomerContactNumber):
        self._CustomerContactNumber = CustomerContactNumber

    @property
    def ExpiredTime(self):
        return self._ExpiredTime

    @ExpiredTime.setter
    def ExpiredTime(self, ExpiredTime):
        self._ExpiredTime = ExpiredTime

    @property
    def ChargeType(self):
        return self._ChargeType

    @ChargeType.setter
    def ChargeType(self, ChargeType):
        self._ChargeType = ChargeType

    @property
    def FaultReportContactPerson(self):
        return self._FaultReportContactPerson

    @FaultReportContactPerson.setter
    def FaultReportContactPerson(self, FaultReportContactPerson):
        self._FaultReportContactPerson = FaultReportContactPerson

    @property
    def FaultReportContactNumber(self):
        return self._FaultReportContactNumber

    @FaultReportContactNumber.setter
    def FaultReportContactNumber(self, FaultReportContactNumber):
        self._FaultReportContactNumber = FaultReportContactNumber

    @property
    def TagSet(self):
        return self._TagSet

    @TagSet.setter
    def TagSet(self, TagSet):
        self._TagSet = TagSet

    @property
    def AccessPointType(self):
        return self._AccessPointType

    @AccessPointType.setter
    def AccessPointType(self, AccessPointType):
        self._AccessPointType = AccessPointType

    @property
    def IdcCity(self):
        return self._IdcCity

    @IdcCity.setter
    def IdcCity(self, IdcCity):
        self._IdcCity = IdcCity

    @property
    def ChargeState(self):
        return self._ChargeState

    @ChargeState.setter
    def ChargeState(self, ChargeState):
        self._ChargeState = ChargeState

    @property
    def StartTime(self):
        return self._StartTime

    @StartTime.setter
    def StartTime(self, StartTime):
        self._StartTime = StartTime

    @property
    def SignLaw(self):
        return self._SignLaw

    @SignLaw.setter
    def SignLaw(self, SignLaw):
        self._SignLaw = SignLaw

    @property
    def LocalZone(self):
        return self._LocalZone

    @LocalZone.setter
    def LocalZone(self, LocalZone):
        self._LocalZone = LocalZone

    @property
    def VlanZeroDirectConnectTunnelCount(self):
        return self._VlanZeroDirectConnectTunnelCount

    @VlanZeroDirectConnectTunnelCount.setter
    def VlanZeroDirectConnectTunnelCount(self, VlanZeroDirectConnectTunnelCount):
        self._VlanZeroDirectConnectTunnelCount = VlanZeroDirectConnectTunnelCount

    @property
    def OtherVlanDirectConnectTunnelCount(self):
        return self._OtherVlanDirectConnectTunnelCount

    @OtherVlanDirectConnectTunnelCount.setter
    def OtherVlanDirectConnectTunnelCount(self, OtherVlanDirectConnectTunnelCount):
        self._OtherVlanDirectConnectTunnelCount = OtherVlanDirectConnectTunnelCount

    @property
    def MinBandwidth(self):
        return self._MinBandwidth

    @MinBandwidth.setter
    def MinBandwidth(self, MinBandwidth):
        self._MinBandwidth = MinBandwidth


    def _deserialize(self, params):
        self._DirectConnectId = params.get("DirectConnectId")
        self._DirectConnectName = params.get("DirectConnectName")
        self._AccessPointId = params.get("AccessPointId")
        self._State = params.get("State")
        self._CreatedTime = params.get("CreatedTime")
        self._EnabledTime = params.get("EnabledTime")
        self._LineOperator = params.get("LineOperator")
        self._Location = params.get("Location")
        self._Bandwidth = params.get("Bandwidth")
        self._PortType = params.get("PortType")
        self._CircuitCode = params.get("CircuitCode")
        self._RedundantDirectConnectId = params.get("RedundantDirectConnectId")
        self._Vlan = params.get("Vlan")
        self._TencentAddress = params.get("TencentAddress")
        self._CustomerAddress = params.get("CustomerAddress")
        self._CustomerName = params.get("CustomerName")
        self._CustomerContactMail = params.get("CustomerContactMail")
        self._CustomerContactNumber = params.get("CustomerContactNumber")
        self._ExpiredTime = params.get("ExpiredTime")
        self._ChargeType = params.get("ChargeType")
        self._FaultReportContactPerson = params.get("FaultReportContactPerson")
        self._FaultReportContactNumber = params.get("FaultReportContactNumber")
        if params.get("TagSet") is not None:
            self._TagSet = []
            for item in params.get("TagSet"):
                obj = Tag()
                obj._deserialize(item)
                self._TagSet.append(obj)
        self._AccessPointType = params.get("AccessPointType")
        self._IdcCity = params.get("IdcCity")
        self._ChargeState = params.get("ChargeState")
        self._StartTime = params.get("StartTime")
        self._SignLaw = params.get("SignLaw")
        self._LocalZone = params.get("LocalZone")
        self._VlanZeroDirectConnectTunnelCount = params.get("VlanZeroDirectConnectTunnelCount")
        self._OtherVlanDirectConnectTunnelCount = params.get("OtherVlanDirectConnectTunnelCount")
        self._MinBandwidth = params.get("MinBandwidth")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DirectConnectTunnel(AbstractModel):
    """专用通道信息列表

    """

    def __init__(self):
        r"""
        :param _DirectConnectTunnelId: 专用通道ID
        :type DirectConnectTunnelId: str
        :param _DirectConnectId: 物理专线ID
        :type DirectConnectId: str
        :param _State: 专用通道状态
AVAILABLE:就绪或者已连接
PENDING:申请中
ALLOCATING:配置中
ALLOCATED:配置完成
ALTERING:修改中
DELETING:删除中
DELETED:删除完成
COMFIRMING:待接受
REJECTED:拒绝
        :type State: str
        :param _DirectConnectOwnerAccount: 物理专线的拥有者，开发商账号 ID
        :type DirectConnectOwnerAccount: str
        :param _OwnerAccount: 专用通道的拥有者，开发商账号 ID
        :type OwnerAccount: str
        :param _NetworkType: 网络类型，分别为VPC、BMVPC、CCN
 VPC：私有网络 ，BMVPC：黑石网络，CCN：云联网
        :type NetworkType: str
        :param _NetworkRegion: VPC地域对应的网络名，如ap-guangzhou
        :type NetworkRegion: str
        :param _VpcId: 私有网络统一 ID 或者黑石网络统一 ID
        :type VpcId: str
        :param _DirectConnectGatewayId: 专线网关 ID
        :type DirectConnectGatewayId: str
        :param _RouteType: BGP ：BGP路由 STATIC：静态 默认为 BGP 路由
        :type RouteType: str
        :param _BgpPeer: 用户侧BGP，Asn，AuthKey
        :type BgpPeer: :class:`tencentcloud.dc.v20180410.models.BgpPeer`
        :param _RouteFilterPrefixes: 用户侧网段地址
        :type RouteFilterPrefixes: list of RouteFilterPrefix
        :param _Vlan: 专用通道的Vlan
        :type Vlan: int
        :param _TencentAddress: TencentAddress，腾讯侧互联 IP
        :type TencentAddress: str
        :param _CustomerAddress: CustomerAddress，用户侧互联 IP
        :type CustomerAddress: str
        :param _DirectConnectTunnelName: 专用通道名称
        :type DirectConnectTunnelName: str
        :param _CreatedTime: 专用通道创建时间
        :type CreatedTime: str
        :param _Bandwidth: 专用通道带宽值
        :type Bandwidth: int
        :param _TagSet: 专用通道标签值
        :type TagSet: list of Tag
        :param _NetDetectId: 关联的网络自定义探测ID
注意：此字段可能返回 null，表示取不到有效值。
        :type NetDetectId: str
        :param _EnableBGPCommunity: BGP community开关
注意：此字段可能返回 null，表示取不到有效值。
        :type EnableBGPCommunity: bool
        :param _NatType: 是否为Nat通道
注意：此字段可能返回 null，表示取不到有效值。
        :type NatType: int
        :param _VpcRegion: VPC地域简码，如gz、cd
注意：此字段可能返回 null，表示取不到有效值。
        :type VpcRegion: str
        :param _BfdEnable: 是否开启BFD
注意：此字段可能返回 null，表示取不到有效值。
        :type BfdEnable: int
        :param _AccessPointType: 专用通道接入点类型
注意：此字段可能返回 null，表示取不到有效值。
        :type AccessPointType: str
        :param _DirectConnectGatewayName: 专线网关名称
注意：此字段可能返回 null，表示取不到有效值。
        :type DirectConnectGatewayName: str
        :param _VpcName: VPC名称
注意：此字段可能返回 null，表示取不到有效值。
        :type VpcName: str
        :param _TencentBackupAddress: TencentBackupAddress，腾讯侧备用互联 IP
注意：此字段可能返回 null，表示取不到有效值。
        :type TencentBackupAddress: str
        :param _SignLaw: 专用通道关联的物理专线是否签署了用户协议
注意：此字段可能返回 null，表示取不到有效值。
        :type SignLaw: bool
        :param _CloudAttachId: 高速上云服务ID
注意：此字段可能返回 null，表示取不到有效值。
        :type CloudAttachId: str
        """
        self._DirectConnectTunnelId = None
        self._DirectConnectId = None
        self._State = None
        self._DirectConnectOwnerAccount = None
        self._OwnerAccount = None
        self._NetworkType = None
        self._NetworkRegion = None
        self._VpcId = None
        self._DirectConnectGatewayId = None
        self._RouteType = None
        self._BgpPeer = None
        self._RouteFilterPrefixes = None
        self._Vlan = None
        self._TencentAddress = None
        self._CustomerAddress = None
        self._DirectConnectTunnelName = None
        self._CreatedTime = None
        self._Bandwidth = None
        self._TagSet = None
        self._NetDetectId = None
        self._EnableBGPCommunity = None
        self._NatType = None
        self._VpcRegion = None
        self._BfdEnable = None
        self._AccessPointType = None
        self._DirectConnectGatewayName = None
        self._VpcName = None
        self._TencentBackupAddress = None
        self._SignLaw = None
        self._CloudAttachId = None

    @property
    def DirectConnectTunnelId(self):
        return self._DirectConnectTunnelId

    @DirectConnectTunnelId.setter
    def DirectConnectTunnelId(self, DirectConnectTunnelId):
        self._DirectConnectTunnelId = DirectConnectTunnelId

    @property
    def DirectConnectId(self):
        return self._DirectConnectId

    @DirectConnectId.setter
    def DirectConnectId(self, DirectConnectId):
        self._DirectConnectId = DirectConnectId

    @property
    def State(self):
        return self._State

    @State.setter
    def State(self, State):
        self._State = State

    @property
    def DirectConnectOwnerAccount(self):
        return self._DirectConnectOwnerAccount

    @DirectConnectOwnerAccount.setter
    def DirectConnectOwnerAccount(self, DirectConnectOwnerAccount):
        self._DirectConnectOwnerAccount = DirectConnectOwnerAccount

    @property
    def OwnerAccount(self):
        return self._OwnerAccount

    @OwnerAccount.setter
    def OwnerAccount(self, OwnerAccount):
        self._OwnerAccount = OwnerAccount

    @property
    def NetworkType(self):
        return self._NetworkType

    @NetworkType.setter
    def NetworkType(self, NetworkType):
        self._NetworkType = NetworkType

    @property
    def NetworkRegion(self):
        return self._NetworkRegion

    @NetworkRegion.setter
    def NetworkRegion(self, NetworkRegion):
        self._NetworkRegion = NetworkRegion

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def DirectConnectGatewayId(self):
        return self._DirectConnectGatewayId

    @DirectConnectGatewayId.setter
    def DirectConnectGatewayId(self, DirectConnectGatewayId):
        self._DirectConnectGatewayId = DirectConnectGatewayId

    @property
    def RouteType(self):
        return self._RouteType

    @RouteType.setter
    def RouteType(self, RouteType):
        self._RouteType = RouteType

    @property
    def BgpPeer(self):
        return self._BgpPeer

    @BgpPeer.setter
    def BgpPeer(self, BgpPeer):
        self._BgpPeer = BgpPeer

    @property
    def RouteFilterPrefixes(self):
        return self._RouteFilterPrefixes

    @RouteFilterPrefixes.setter
    def RouteFilterPrefixes(self, RouteFilterPrefixes):
        self._RouteFilterPrefixes = RouteFilterPrefixes

    @property
    def Vlan(self):
        return self._Vlan

    @Vlan.setter
    def Vlan(self, Vlan):
        self._Vlan = Vlan

    @property
    def TencentAddress(self):
        return self._TencentAddress

    @TencentAddress.setter
    def TencentAddress(self, TencentAddress):
        self._TencentAddress = TencentAddress

    @property
    def CustomerAddress(self):
        return self._CustomerAddress

    @CustomerAddress.setter
    def CustomerAddress(self, CustomerAddress):
        self._CustomerAddress = CustomerAddress

    @property
    def DirectConnectTunnelName(self):
        return self._DirectConnectTunnelName

    @DirectConnectTunnelName.setter
    def DirectConnectTunnelName(self, DirectConnectTunnelName):
        self._DirectConnectTunnelName = DirectConnectTunnelName

    @property
    def CreatedTime(self):
        return self._CreatedTime

    @CreatedTime.setter
    def CreatedTime(self, CreatedTime):
        self._CreatedTime = CreatedTime

    @property
    def Bandwidth(self):
        return self._Bandwidth

    @Bandwidth.setter
    def Bandwidth(self, Bandwidth):
        self._Bandwidth = Bandwidth

    @property
    def TagSet(self):
        return self._TagSet

    @TagSet.setter
    def TagSet(self, TagSet):
        self._TagSet = TagSet

    @property
    def NetDetectId(self):
        return self._NetDetectId

    @NetDetectId.setter
    def NetDetectId(self, NetDetectId):
        self._NetDetectId = NetDetectId

    @property
    def EnableBGPCommunity(self):
        return self._EnableBGPCommunity

    @EnableBGPCommunity.setter
    def EnableBGPCommunity(self, EnableBGPCommunity):
        self._EnableBGPCommunity = EnableBGPCommunity

    @property
    def NatType(self):
        return self._NatType

    @NatType.setter
    def NatType(self, NatType):
        self._NatType = NatType

    @property
    def VpcRegion(self):
        return self._VpcRegion

    @VpcRegion.setter
    def VpcRegion(self, VpcRegion):
        self._VpcRegion = VpcRegion

    @property
    def BfdEnable(self):
        return self._BfdEnable

    @BfdEnable.setter
    def BfdEnable(self, BfdEnable):
        self._BfdEnable = BfdEnable

    @property
    def AccessPointType(self):
        return self._AccessPointType

    @AccessPointType.setter
    def AccessPointType(self, AccessPointType):
        self._AccessPointType = AccessPointType

    @property
    def DirectConnectGatewayName(self):
        return self._DirectConnectGatewayName

    @DirectConnectGatewayName.setter
    def DirectConnectGatewayName(self, DirectConnectGatewayName):
        self._DirectConnectGatewayName = DirectConnectGatewayName

    @property
    def VpcName(self):
        return self._VpcName

    @VpcName.setter
    def VpcName(self, VpcName):
        self._VpcName = VpcName

    @property
    def TencentBackupAddress(self):
        return self._TencentBackupAddress

    @TencentBackupAddress.setter
    def TencentBackupAddress(self, TencentBackupAddress):
        self._TencentBackupAddress = TencentBackupAddress

    @property
    def SignLaw(self):
        return self._SignLaw

    @SignLaw.setter
    def SignLaw(self, SignLaw):
        self._SignLaw = SignLaw

    @property
    def CloudAttachId(self):
        return self._CloudAttachId

    @CloudAttachId.setter
    def CloudAttachId(self, CloudAttachId):
        self._CloudAttachId = CloudAttachId


    def _deserialize(self, params):
        self._DirectConnectTunnelId = params.get("DirectConnectTunnelId")
        self._DirectConnectId = params.get("DirectConnectId")
        self._State = params.get("State")
        self._DirectConnectOwnerAccount = params.get("DirectConnectOwnerAccount")
        self._OwnerAccount = params.get("OwnerAccount")
        self._NetworkType = params.get("NetworkType")
        self._NetworkRegion = params.get("NetworkRegion")
        self._VpcId = params.get("VpcId")
        self._DirectConnectGatewayId = params.get("DirectConnectGatewayId")
        self._RouteType = params.get("RouteType")
        if params.get("BgpPeer") is not None:
            self._BgpPeer = BgpPeer()
            self._BgpPeer._deserialize(params.get("BgpPeer"))
        if params.get("RouteFilterPrefixes") is not None:
            self._RouteFilterPrefixes = []
            for item in params.get("RouteFilterPrefixes"):
                obj = RouteFilterPrefix()
                obj._deserialize(item)
                self._RouteFilterPrefixes.append(obj)
        self._Vlan = params.get("Vlan")
        self._TencentAddress = params.get("TencentAddress")
        self._CustomerAddress = params.get("CustomerAddress")
        self._DirectConnectTunnelName = params.get("DirectConnectTunnelName")
        self._CreatedTime = params.get("CreatedTime")
        self._Bandwidth = params.get("Bandwidth")
        if params.get("TagSet") is not None:
            self._TagSet = []
            for item in params.get("TagSet"):
                obj = Tag()
                obj._deserialize(item)
                self._TagSet.append(obj)
        self._NetDetectId = params.get("NetDetectId")
        self._EnableBGPCommunity = params.get("EnableBGPCommunity")
        self._NatType = params.get("NatType")
        self._VpcRegion = params.get("VpcRegion")
        self._BfdEnable = params.get("BfdEnable")
        self._AccessPointType = params.get("AccessPointType")
        self._DirectConnectGatewayName = params.get("DirectConnectGatewayName")
        self._VpcName = params.get("VpcName")
        self._TencentBackupAddress = params.get("TencentBackupAddress")
        self._SignLaw = params.get("SignLaw")
        self._CloudAttachId = params.get("CloudAttachId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DirectConnectTunnelExtra(AbstractModel):
    """专用通道扩展信息

    """

    def __init__(self):
        r"""
        :param _DirectConnectTunnelId: 专用通道ID
        :type DirectConnectTunnelId: str
        :param _DirectConnectId: 物理专线ID
        :type DirectConnectId: str
        :param _State: 专用通道状态
AVAILABLE:就绪或者已连接
PENDING:申请中
ALLOCATING:配置中
ALLOCATED:配置完成
ALTERING:修改中
DELETING:删除中
DELETED:删除完成
COMFIRMING:待接受
REJECTED:拒绝
        :type State: str
        :param _DirectConnectOwnerAccount: 物理专线的拥有者，开发商账号 ID
        :type DirectConnectOwnerAccount: str
        :param _OwnerAccount: 专用通道的拥有者，开发商账号 ID
        :type OwnerAccount: str
        :param _NetworkType: 网络类型，分别为VPC、BMVPC、CCN
 VPC：私有网络 ，BMVPC：黑石网络，CCN：云联网
        :type NetworkType: str
        :param _NetworkRegion: VPC地域对应的网络名，如ap-guangzhou
        :type NetworkRegion: str
        :param _VpcId: 私有网络统一 ID 或者黑石网络统一 ID
        :type VpcId: str
        :param _DirectConnectGatewayId: 专线网关 ID
        :type DirectConnectGatewayId: str
        :param _RouteType: BGP ：BGP路由 STATIC：静态 默认为 BGP 路由
        :type RouteType: str
        :param _BgpPeer: 用户侧BGP，Asn，AuthKey
        :type BgpPeer: :class:`tencentcloud.dc.v20180410.models.BgpPeer`
        :param _RouteFilterPrefixes: 用户侧网段地址
        :type RouteFilterPrefixes: list of RouteFilterPrefix
        :param _PublicAddresses: 互联网通道公网网段地址
        :type PublicAddresses: list of RouteFilterPrefix
        :param _Vlan: 专用通道的Vlan
        :type Vlan: int
        :param _TencentAddress: 腾讯侧互联 IP
        :type TencentAddress: str
        :param _TencentBackupAddress: 腾讯侧备用互联IP
        :type TencentBackupAddress: str
        :param _CustomerAddress: 用户侧互联 IP
        :type CustomerAddress: str
        :param _DirectConnectTunnelName: 专用通道名称
        :type DirectConnectTunnelName: str
        :param _CreatedTime: 专用通道创建时间
        :type CreatedTime: str
        :param _Bandwidth: 专用通道带宽值
        :type Bandwidth: int
        :param _NetDetectId: 关联的网络自定义探测ID
        :type NetDetectId: str
        :param _EnableBGPCommunity: BGP community开关
        :type EnableBGPCommunity: bool
        :param _NatType: 是否为Nat通道
        :type NatType: int
        :param _VpcRegion: VPC地域简码，如gz、cd
        :type VpcRegion: str
        :param _BfdEnable: 是否开启BFD
        :type BfdEnable: int
        :param _NqaEnable: 是否开启NQA
        :type NqaEnable: int
        :param _AccessPointType: 专用通道接入点类型
        :type AccessPointType: str
        :param _DirectConnectGatewayName: 专线网关名称
        :type DirectConnectGatewayName: str
        :param _VpcName: VPC名称
        :type VpcName: str
        :param _SignLaw: 专用通道关联的物理专线是否签署了用户协议
        :type SignLaw: bool
        :param _BfdInfo: BFD配置信息
        :type BfdInfo: :class:`tencentcloud.dc.v20180410.models.BFDInfo`
        :param _NqaInfo: NQA配置信息
        :type NqaInfo: :class:`tencentcloud.dc.v20180410.models.NQAInfo`
        :param _BgpStatus: BGP状态
        :type BgpStatus: :class:`tencentcloud.dc.v20180410.models.BGPStatus`
        :param _IPv6Enable: 是否开启IPv6
注意：此字段可能返回 null，表示取不到有效值。
        :type IPv6Enable: int
        :param _TencentIPv6Address: 腾讯侧互联IPv6地址
注意：此字段可能返回 null，表示取不到有效值。
        :type TencentIPv6Address: str
        :param _TencentBackupIPv6Address: 腾讯侧备用互联IPv6地址
注意：此字段可能返回 null，表示取不到有效值。
        :type TencentBackupIPv6Address: str
        :param _BgpIPv6Status: BGPv6状态
注意：此字段可能返回 null，表示取不到有效值。
        :type BgpIPv6Status: :class:`tencentcloud.dc.v20180410.models.BGPStatus`
        :param _CustomerIPv6Address: 用户侧互联IPv6地址
注意：此字段可能返回 null，表示取不到有效值。
        :type CustomerIPv6Address: str
        :param _JumboEnable: 专用通道是否支持巨帧。1 支持，0 不支持
注意：此字段可能返回 null，表示取不到有效值。
        :type JumboEnable: int
        :param _HighPrecisionBFDEnable: 专用通道是否支持高精度BFD。1支持，0不支持
注意：此字段可能返回 null，表示取不到有效值。
        :type HighPrecisionBFDEnable: int
        """
        self._DirectConnectTunnelId = None
        self._DirectConnectId = None
        self._State = None
        self._DirectConnectOwnerAccount = None
        self._OwnerAccount = None
        self._NetworkType = None
        self._NetworkRegion = None
        self._VpcId = None
        self._DirectConnectGatewayId = None
        self._RouteType = None
        self._BgpPeer = None
        self._RouteFilterPrefixes = None
        self._PublicAddresses = None
        self._Vlan = None
        self._TencentAddress = None
        self._TencentBackupAddress = None
        self._CustomerAddress = None
        self._DirectConnectTunnelName = None
        self._CreatedTime = None
        self._Bandwidth = None
        self._NetDetectId = None
        self._EnableBGPCommunity = None
        self._NatType = None
        self._VpcRegion = None
        self._BfdEnable = None
        self._NqaEnable = None
        self._AccessPointType = None
        self._DirectConnectGatewayName = None
        self._VpcName = None
        self._SignLaw = None
        self._BfdInfo = None
        self._NqaInfo = None
        self._BgpStatus = None
        self._IPv6Enable = None
        self._TencentIPv6Address = None
        self._TencentBackupIPv6Address = None
        self._BgpIPv6Status = None
        self._CustomerIPv6Address = None
        self._JumboEnable = None
        self._HighPrecisionBFDEnable = None

    @property
    def DirectConnectTunnelId(self):
        return self._DirectConnectTunnelId

    @DirectConnectTunnelId.setter
    def DirectConnectTunnelId(self, DirectConnectTunnelId):
        self._DirectConnectTunnelId = DirectConnectTunnelId

    @property
    def DirectConnectId(self):
        return self._DirectConnectId

    @DirectConnectId.setter
    def DirectConnectId(self, DirectConnectId):
        self._DirectConnectId = DirectConnectId

    @property
    def State(self):
        return self._State

    @State.setter
    def State(self, State):
        self._State = State

    @property
    def DirectConnectOwnerAccount(self):
        return self._DirectConnectOwnerAccount

    @DirectConnectOwnerAccount.setter
    def DirectConnectOwnerAccount(self, DirectConnectOwnerAccount):
        self._DirectConnectOwnerAccount = DirectConnectOwnerAccount

    @property
    def OwnerAccount(self):
        return self._OwnerAccount

    @OwnerAccount.setter
    def OwnerAccount(self, OwnerAccount):
        self._OwnerAccount = OwnerAccount

    @property
    def NetworkType(self):
        return self._NetworkType

    @NetworkType.setter
    def NetworkType(self, NetworkType):
        self._NetworkType = NetworkType

    @property
    def NetworkRegion(self):
        return self._NetworkRegion

    @NetworkRegion.setter
    def NetworkRegion(self, NetworkRegion):
        self._NetworkRegion = NetworkRegion

    @property
    def VpcId(self):
        return self._VpcId

    @VpcId.setter
    def VpcId(self, VpcId):
        self._VpcId = VpcId

    @property
    def DirectConnectGatewayId(self):
        return self._DirectConnectGatewayId

    @DirectConnectGatewayId.setter
    def DirectConnectGatewayId(self, DirectConnectGatewayId):
        self._DirectConnectGatewayId = DirectConnectGatewayId

    @property
    def RouteType(self):
        return self._RouteType

    @RouteType.setter
    def RouteType(self, RouteType):
        self._RouteType = RouteType

    @property
    def BgpPeer(self):
        return self._BgpPeer

    @BgpPeer.setter
    def BgpPeer(self, BgpPeer):
        self._BgpPeer = BgpPeer

    @property
    def RouteFilterPrefixes(self):
        return self._RouteFilterPrefixes

    @RouteFilterPrefixes.setter
    def RouteFilterPrefixes(self, RouteFilterPrefixes):
        self._RouteFilterPrefixes = RouteFilterPrefixes

    @property
    def PublicAddresses(self):
        return self._PublicAddresses

    @PublicAddresses.setter
    def PublicAddresses(self, PublicAddresses):
        self._PublicAddresses = PublicAddresses

    @property
    def Vlan(self):
        return self._Vlan

    @Vlan.setter
    def Vlan(self, Vlan):
        self._Vlan = Vlan

    @property
    def TencentAddress(self):
        return self._TencentAddress

    @TencentAddress.setter
    def TencentAddress(self, TencentAddress):
        self._TencentAddress = TencentAddress

    @property
    def TencentBackupAddress(self):
        return self._TencentBackupAddress

    @TencentBackupAddress.setter
    def TencentBackupAddress(self, TencentBackupAddress):
        self._TencentBackupAddress = TencentBackupAddress

    @property
    def CustomerAddress(self):
        return self._CustomerAddress

    @CustomerAddress.setter
    def CustomerAddress(self, CustomerAddress):
        self._CustomerAddress = CustomerAddress

    @property
    def DirectConnectTunnelName(self):
        return self._DirectConnectTunnelName

    @DirectConnectTunnelName.setter
    def DirectConnectTunnelName(self, DirectConnectTunnelName):
        self._DirectConnectTunnelName = DirectConnectTunnelName

    @property
    def CreatedTime(self):
        return self._CreatedTime

    @CreatedTime.setter
    def CreatedTime(self, CreatedTime):
        self._CreatedTime = CreatedTime

    @property
    def Bandwidth(self):
        return self._Bandwidth

    @Bandwidth.setter
    def Bandwidth(self, Bandwidth):
        self._Bandwidth = Bandwidth

    @property
    def NetDetectId(self):
        return self._NetDetectId

    @NetDetectId.setter
    def NetDetectId(self, NetDetectId):
        self._NetDetectId = NetDetectId

    @property
    def EnableBGPCommunity(self):
        return self._EnableBGPCommunity

    @EnableBGPCommunity.setter
    def EnableBGPCommunity(self, EnableBGPCommunity):
        self._EnableBGPCommunity = EnableBGPCommunity

    @property
    def NatType(self):
        return self._NatType

    @NatType.setter
    def NatType(self, NatType):
        self._NatType = NatType

    @property
    def VpcRegion(self):
        return self._VpcRegion

    @VpcRegion.setter
    def VpcRegion(self, VpcRegion):
        self._VpcRegion = VpcRegion

    @property
    def BfdEnable(self):
        return self._BfdEnable

    @BfdEnable.setter
    def BfdEnable(self, BfdEnable):
        self._BfdEnable = BfdEnable

    @property
    def NqaEnable(self):
        return self._NqaEnable

    @NqaEnable.setter
    def NqaEnable(self, NqaEnable):
        self._NqaEnable = NqaEnable

    @property
    def AccessPointType(self):
        return self._AccessPointType

    @AccessPointType.setter
    def AccessPointType(self, AccessPointType):
        self._AccessPointType = AccessPointType

    @property
    def DirectConnectGatewayName(self):
        return self._DirectConnectGatewayName

    @DirectConnectGatewayName.setter
    def DirectConnectGatewayName(self, DirectConnectGatewayName):
        self._DirectConnectGatewayName = DirectConnectGatewayName

    @property
    def VpcName(self):
        return self._VpcName

    @VpcName.setter
    def VpcName(self, VpcName):
        self._VpcName = VpcName

    @property
    def SignLaw(self):
        return self._SignLaw

    @SignLaw.setter
    def SignLaw(self, SignLaw):
        self._SignLaw = SignLaw

    @property
    def BfdInfo(self):
        return self._BfdInfo

    @BfdInfo.setter
    def BfdInfo(self, BfdInfo):
        self._BfdInfo = BfdInfo

    @property
    def NqaInfo(self):
        return self._NqaInfo

    @NqaInfo.setter
    def NqaInfo(self, NqaInfo):
        self._NqaInfo = NqaInfo

    @property
    def BgpStatus(self):
        return self._BgpStatus

    @BgpStatus.setter
    def BgpStatus(self, BgpStatus):
        self._BgpStatus = BgpStatus

    @property
    def IPv6Enable(self):
        return self._IPv6Enable

    @IPv6Enable.setter
    def IPv6Enable(self, IPv6Enable):
        self._IPv6Enable = IPv6Enable

    @property
    def TencentIPv6Address(self):
        return self._TencentIPv6Address

    @TencentIPv6Address.setter
    def TencentIPv6Address(self, TencentIPv6Address):
        self._TencentIPv6Address = TencentIPv6Address

    @property
    def TencentBackupIPv6Address(self):
        return self._TencentBackupIPv6Address

    @TencentBackupIPv6Address.setter
    def TencentBackupIPv6Address(self, TencentBackupIPv6Address):
        self._TencentBackupIPv6Address = TencentBackupIPv6Address

    @property
    def BgpIPv6Status(self):
        return self._BgpIPv6Status

    @BgpIPv6Status.setter
    def BgpIPv6Status(self, BgpIPv6Status):
        self._BgpIPv6Status = BgpIPv6Status

    @property
    def CustomerIPv6Address(self):
        return self._CustomerIPv6Address

    @CustomerIPv6Address.setter
    def CustomerIPv6Address(self, CustomerIPv6Address):
        self._CustomerIPv6Address = CustomerIPv6Address

    @property
    def JumboEnable(self):
        return self._JumboEnable

    @JumboEnable.setter
    def JumboEnable(self, JumboEnable):
        self._JumboEnable = JumboEnable

    @property
    def HighPrecisionBFDEnable(self):
        return self._HighPrecisionBFDEnable

    @HighPrecisionBFDEnable.setter
    def HighPrecisionBFDEnable(self, HighPrecisionBFDEnable):
        self._HighPrecisionBFDEnable = HighPrecisionBFDEnable


    def _deserialize(self, params):
        self._DirectConnectTunnelId = params.get("DirectConnectTunnelId")
        self._DirectConnectId = params.get("DirectConnectId")
        self._State = params.get("State")
        self._DirectConnectOwnerAccount = params.get("DirectConnectOwnerAccount")
        self._OwnerAccount = params.get("OwnerAccount")
        self._NetworkType = params.get("NetworkType")
        self._NetworkRegion = params.get("NetworkRegion")
        self._VpcId = params.get("VpcId")
        self._DirectConnectGatewayId = params.get("DirectConnectGatewayId")
        self._RouteType = params.get("RouteType")
        if params.get("BgpPeer") is not None:
            self._BgpPeer = BgpPeer()
            self._BgpPeer._deserialize(params.get("BgpPeer"))
        if params.get("RouteFilterPrefixes") is not None:
            self._RouteFilterPrefixes = []
            for item in params.get("RouteFilterPrefixes"):
                obj = RouteFilterPrefix()
                obj._deserialize(item)
                self._RouteFilterPrefixes.append(obj)
        if params.get("PublicAddresses") is not None:
            self._PublicAddresses = []
            for item in params.get("PublicAddresses"):
                obj = RouteFilterPrefix()
                obj._deserialize(item)
                self._PublicAddresses.append(obj)
        self._Vlan = params.get("Vlan")
        self._TencentAddress = params.get("TencentAddress")
        self._TencentBackupAddress = params.get("TencentBackupAddress")
        self._CustomerAddress = params.get("CustomerAddress")
        self._DirectConnectTunnelName = params.get("DirectConnectTunnelName")
        self._CreatedTime = params.get("CreatedTime")
        self._Bandwidth = params.get("Bandwidth")
        self._NetDetectId = params.get("NetDetectId")
        self._EnableBGPCommunity = params.get("EnableBGPCommunity")
        self._NatType = params.get("NatType")
        self._VpcRegion = params.get("VpcRegion")
        self._BfdEnable = params.get("BfdEnable")
        self._NqaEnable = params.get("NqaEnable")
        self._AccessPointType = params.get("AccessPointType")
        self._DirectConnectGatewayName = params.get("DirectConnectGatewayName")
        self._VpcName = params.get("VpcName")
        self._SignLaw = params.get("SignLaw")
        if params.get("BfdInfo") is not None:
            self._BfdInfo = BFDInfo()
            self._BfdInfo._deserialize(params.get("BfdInfo"))
        if params.get("NqaInfo") is not None:
            self._NqaInfo = NQAInfo()
            self._NqaInfo._deserialize(params.get("NqaInfo"))
        if params.get("BgpStatus") is not None:
            self._BgpStatus = BGPStatus()
            self._BgpStatus._deserialize(params.get("BgpStatus"))
        self._IPv6Enable = params.get("IPv6Enable")
        self._TencentIPv6Address = params.get("TencentIPv6Address")
        self._TencentBackupIPv6Address = params.get("TencentBackupIPv6Address")
        if params.get("BgpIPv6Status") is not None:
            self._BgpIPv6Status = BGPStatus()
            self._BgpIPv6Status._deserialize(params.get("BgpIPv6Status"))
        self._CustomerIPv6Address = params.get("CustomerIPv6Address")
        self._JumboEnable = params.get("JumboEnable")
        self._HighPrecisionBFDEnable = params.get("HighPrecisionBFDEnable")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DirectConnectTunnelRoute(AbstractModel):
    """专用通道路由

    """

    def __init__(self):
        r"""
        :param _RouteId: 专用通道路由ID
        :type RouteId: str
        :param _DestinationCidrBlock: 网段CIDR
        :type DestinationCidrBlock: str
        :param _RouteType: 路由类型：BGP/STATIC路由
        :type RouteType: str
        :param _Status: ENABLE：路由启用，DISABLE：路由禁用
        :type Status: str
        :param _ASPath: ASPath信息
        :type ASPath: list of str
        :param _NextHop: 路由下一跳IP
        :type NextHop: str
        """
        self._RouteId = None
        self._DestinationCidrBlock = None
        self._RouteType = None
        self._Status = None
        self._ASPath = None
        self._NextHop = None

    @property
    def RouteId(self):
        return self._RouteId

    @RouteId.setter
    def RouteId(self, RouteId):
        self._RouteId = RouteId

    @property
    def DestinationCidrBlock(self):
        return self._DestinationCidrBlock

    @DestinationCidrBlock.setter
    def DestinationCidrBlock(self, DestinationCidrBlock):
        self._DestinationCidrBlock = DestinationCidrBlock

    @property
    def RouteType(self):
        return self._RouteType

    @RouteType.setter
    def RouteType(self, RouteType):
        self._RouteType = RouteType

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status

    @property
    def ASPath(self):
        return self._ASPath

    @ASPath.setter
    def ASPath(self, ASPath):
        self._ASPath = ASPath

    @property
    def NextHop(self):
        return self._NextHop

    @NextHop.setter
    def NextHop(self, NextHop):
        self._NextHop = NextHop


    def _deserialize(self, params):
        self._RouteId = params.get("RouteId")
        self._DestinationCidrBlock = params.get("DestinationCidrBlock")
        self._RouteType = params.get("RouteType")
        self._Status = params.get("Status")
        self._ASPath = params.get("ASPath")
        self._NextHop = params.get("NextHop")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DisableInternetAddressRequest(AbstractModel):
    """DisableInternetAddress请求参数结构体

    """

    def __init__(self):
        r"""
        :param _InstanceId: 公网互联网地址ID
        :type InstanceId: str
        """
        self._InstanceId = None

    @property
    def InstanceId(self):
        return self._InstanceId

    @InstanceId.setter
    def InstanceId(self, InstanceId):
        self._InstanceId = InstanceId


    def _deserialize(self, params):
        self._InstanceId = params.get("InstanceId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class DisableInternetAddressResponse(AbstractModel):
    """DisableInternetAddress返回参数结构体

    """

    def __init__(self):
        r"""
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
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


class EnableInternetAddressRequest(AbstractModel):
    """EnableInternetAddress请求参数结构体

    """

    def __init__(self):
        r"""
        :param _InstanceId: 互联网公网地址ID
        :type InstanceId: str
        """
        self._InstanceId = None

    @property
    def InstanceId(self):
        return self._InstanceId

    @InstanceId.setter
    def InstanceId(self, InstanceId):
        self._InstanceId = InstanceId


    def _deserialize(self, params):
        self._InstanceId = params.get("InstanceId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class EnableInternetAddressResponse(AbstractModel):
    """EnableInternetAddress返回参数结构体

    """

    def __init__(self):
        r"""
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
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


class Filter(AbstractModel):
    """用于条件过滤查询

    """

    def __init__(self):
        r"""
        :param _Name: 需要过滤的字段。
        :type Name: str
        :param _Values: 字段的过滤值。
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
        


class InternetAddressDetail(AbstractModel):
    """互联网地址详细信息

    """

    def __init__(self):
        r"""
        :param _InstanceId: 互联网地址ID
注意：此字段可能返回 null，表示取不到有效值。
        :type InstanceId: str
        :param _Subnet: 互联网网络地址
注意：此字段可能返回 null，表示取不到有效值。
        :type Subnet: str
        :param _MaskLen: 网络地址掩码长度
注意：此字段可能返回 null，表示取不到有效值。
        :type MaskLen: int
        :param _AddrType: 0:BGP
1:电信
2:移动
3:联通
注意：此字段可能返回 null，表示取不到有效值。
        :type AddrType: int
        :param _Status: 0:使用中
1:已停用
2:已退还
        :type Status: int
        :param _ApplyTime: 申请时间
注意：此字段可能返回 null，表示取不到有效值。
        :type ApplyTime: str
        :param _StopTime: 停用时间
注意：此字段可能返回 null，表示取不到有效值。
        :type StopTime: str
        :param _ReleaseTime: 退还时间
注意：此字段可能返回 null，表示取不到有效值。
        :type ReleaseTime: str
        :param _Region: 地域信息
注意：此字段可能返回 null，表示取不到有效值。
        :type Region: str
        :param _AppId: 用户ID
注意：此字段可能返回 null，表示取不到有效值。
        :type AppId: int
        :param _AddrProto: 0:IPv4 1:IPv6
注意：此字段可能返回 null，表示取不到有效值。
        :type AddrProto: int
        :param _ReserveTime: 释放状态的IP地址保留的天数
注意：此字段可能返回 null，表示取不到有效值。
        :type ReserveTime: int
        """
        self._InstanceId = None
        self._Subnet = None
        self._MaskLen = None
        self._AddrType = None
        self._Status = None
        self._ApplyTime = None
        self._StopTime = None
        self._ReleaseTime = None
        self._Region = None
        self._AppId = None
        self._AddrProto = None
        self._ReserveTime = None

    @property
    def InstanceId(self):
        return self._InstanceId

    @InstanceId.setter
    def InstanceId(self, InstanceId):
        self._InstanceId = InstanceId

    @property
    def Subnet(self):
        return self._Subnet

    @Subnet.setter
    def Subnet(self, Subnet):
        self._Subnet = Subnet

    @property
    def MaskLen(self):
        return self._MaskLen

    @MaskLen.setter
    def MaskLen(self, MaskLen):
        self._MaskLen = MaskLen

    @property
    def AddrType(self):
        return self._AddrType

    @AddrType.setter
    def AddrType(self, AddrType):
        self._AddrType = AddrType

    @property
    def Status(self):
        return self._Status

    @Status.setter
    def Status(self, Status):
        self._Status = Status

    @property
    def ApplyTime(self):
        return self._ApplyTime

    @ApplyTime.setter
    def ApplyTime(self, ApplyTime):
        self._ApplyTime = ApplyTime

    @property
    def StopTime(self):
        return self._StopTime

    @StopTime.setter
    def StopTime(self, StopTime):
        self._StopTime = StopTime

    @property
    def ReleaseTime(self):
        return self._ReleaseTime

    @ReleaseTime.setter
    def ReleaseTime(self, ReleaseTime):
        self._ReleaseTime = ReleaseTime

    @property
    def Region(self):
        return self._Region

    @Region.setter
    def Region(self, Region):
        self._Region = Region

    @property
    def AppId(self):
        return self._AppId

    @AppId.setter
    def AppId(self, AppId):
        self._AppId = AppId

    @property
    def AddrProto(self):
        return self._AddrProto

    @AddrProto.setter
    def AddrProto(self, AddrProto):
        self._AddrProto = AddrProto

    @property
    def ReserveTime(self):
        return self._ReserveTime

    @ReserveTime.setter
    def ReserveTime(self, ReserveTime):
        self._ReserveTime = ReserveTime


    def _deserialize(self, params):
        self._InstanceId = params.get("InstanceId")
        self._Subnet = params.get("Subnet")
        self._MaskLen = params.get("MaskLen")
        self._AddrType = params.get("AddrType")
        self._Status = params.get("Status")
        self._ApplyTime = params.get("ApplyTime")
        self._StopTime = params.get("StopTime")
        self._ReleaseTime = params.get("ReleaseTime")
        self._Region = params.get("Region")
        self._AppId = params.get("AppId")
        self._AddrProto = params.get("AddrProto")
        self._ReserveTime = params.get("ReserveTime")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class InternetAddressStatistics(AbstractModel):
    """互联网公网地址统计

    """

    def __init__(self):
        r"""
        :param _Region: 地域
注意：此字段可能返回 null，表示取不到有效值。
        :type Region: str
        :param _SubnetNum: 互联网公网地址数量
注意：此字段可能返回 null，表示取不到有效值。
        :type SubnetNum: int
        """
        self._Region = None
        self._SubnetNum = None

    @property
    def Region(self):
        return self._Region

    @Region.setter
    def Region(self, Region):
        self._Region = Region

    @property
    def SubnetNum(self):
        return self._SubnetNum

    @SubnetNum.setter
    def SubnetNum(self, SubnetNum):
        self._SubnetNum = SubnetNum


    def _deserialize(self, params):
        self._Region = params.get("Region")
        self._SubnetNum = params.get("SubnetNum")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyDirectConnectAttributeRequest(AbstractModel):
    """ModifyDirectConnectAttribute请求参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectId: 物理专线的ID。
        :type DirectConnectId: str
        :param _DirectConnectName: 物理专线名称。
        :type DirectConnectName: str
        :param _CircuitCode: 运营商或者服务商为物理专线提供的电路编码。
        :type CircuitCode: str
        :param _Vlan: 物理专线调试VLAN。
        :type Vlan: int
        :param _TencentAddress: 物理专线调试腾讯侧互联 IP。
        :type TencentAddress: str
        :param _CustomerAddress: 物理专线调试用户侧互联 IP。
        :type CustomerAddress: str
        :param _CustomerName: 物理专线申请者姓名。默认从账户体系获取。
        :type CustomerName: str
        :param _CustomerContactMail: 物理专线申请者联系邮箱。默认从账户体系获取。
        :type CustomerContactMail: str
        :param _CustomerContactNumber: 物理专线申请者联系号码。默认从账户体系获取。
        :type CustomerContactNumber: str
        :param _FaultReportContactPerson: 报障联系人。
        :type FaultReportContactPerson: str
        :param _FaultReportContactNumber: 报障联系电话。
        :type FaultReportContactNumber: str
        :param _SignLaw: 物理专线申请者补签用户使用协议
        :type SignLaw: bool
        :param _Bandwidth: 物理专线带宽
        :type Bandwidth: int
        """
        self._DirectConnectId = None
        self._DirectConnectName = None
        self._CircuitCode = None
        self._Vlan = None
        self._TencentAddress = None
        self._CustomerAddress = None
        self._CustomerName = None
        self._CustomerContactMail = None
        self._CustomerContactNumber = None
        self._FaultReportContactPerson = None
        self._FaultReportContactNumber = None
        self._SignLaw = None
        self._Bandwidth = None

    @property
    def DirectConnectId(self):
        return self._DirectConnectId

    @DirectConnectId.setter
    def DirectConnectId(self, DirectConnectId):
        self._DirectConnectId = DirectConnectId

    @property
    def DirectConnectName(self):
        return self._DirectConnectName

    @DirectConnectName.setter
    def DirectConnectName(self, DirectConnectName):
        self._DirectConnectName = DirectConnectName

    @property
    def CircuitCode(self):
        return self._CircuitCode

    @CircuitCode.setter
    def CircuitCode(self, CircuitCode):
        self._CircuitCode = CircuitCode

    @property
    def Vlan(self):
        return self._Vlan

    @Vlan.setter
    def Vlan(self, Vlan):
        self._Vlan = Vlan

    @property
    def TencentAddress(self):
        return self._TencentAddress

    @TencentAddress.setter
    def TencentAddress(self, TencentAddress):
        self._TencentAddress = TencentAddress

    @property
    def CustomerAddress(self):
        return self._CustomerAddress

    @CustomerAddress.setter
    def CustomerAddress(self, CustomerAddress):
        self._CustomerAddress = CustomerAddress

    @property
    def CustomerName(self):
        return self._CustomerName

    @CustomerName.setter
    def CustomerName(self, CustomerName):
        self._CustomerName = CustomerName

    @property
    def CustomerContactMail(self):
        return self._CustomerContactMail

    @CustomerContactMail.setter
    def CustomerContactMail(self, CustomerContactMail):
        self._CustomerContactMail = CustomerContactMail

    @property
    def CustomerContactNumber(self):
        return self._CustomerContactNumber

    @CustomerContactNumber.setter
    def CustomerContactNumber(self, CustomerContactNumber):
        self._CustomerContactNumber = CustomerContactNumber

    @property
    def FaultReportContactPerson(self):
        return self._FaultReportContactPerson

    @FaultReportContactPerson.setter
    def FaultReportContactPerson(self, FaultReportContactPerson):
        self._FaultReportContactPerson = FaultReportContactPerson

    @property
    def FaultReportContactNumber(self):
        return self._FaultReportContactNumber

    @FaultReportContactNumber.setter
    def FaultReportContactNumber(self, FaultReportContactNumber):
        self._FaultReportContactNumber = FaultReportContactNumber

    @property
    def SignLaw(self):
        return self._SignLaw

    @SignLaw.setter
    def SignLaw(self, SignLaw):
        self._SignLaw = SignLaw

    @property
    def Bandwidth(self):
        return self._Bandwidth

    @Bandwidth.setter
    def Bandwidth(self, Bandwidth):
        self._Bandwidth = Bandwidth


    def _deserialize(self, params):
        self._DirectConnectId = params.get("DirectConnectId")
        self._DirectConnectName = params.get("DirectConnectName")
        self._CircuitCode = params.get("CircuitCode")
        self._Vlan = params.get("Vlan")
        self._TencentAddress = params.get("TencentAddress")
        self._CustomerAddress = params.get("CustomerAddress")
        self._CustomerName = params.get("CustomerName")
        self._CustomerContactMail = params.get("CustomerContactMail")
        self._CustomerContactNumber = params.get("CustomerContactNumber")
        self._FaultReportContactPerson = params.get("FaultReportContactPerson")
        self._FaultReportContactNumber = params.get("FaultReportContactNumber")
        self._SignLaw = params.get("SignLaw")
        self._Bandwidth = params.get("Bandwidth")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyDirectConnectAttributeResponse(AbstractModel):
    """ModifyDirectConnectAttribute返回参数结构体

    """

    def __init__(self):
        r"""
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
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


class ModifyDirectConnectTunnelAttributeRequest(AbstractModel):
    """ModifyDirectConnectTunnelAttribute请求参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectTunnelId: 专用通道ID
        :type DirectConnectTunnelId: str
        :param _DirectConnectTunnelName: 专用通道名称
        :type DirectConnectTunnelName: str
        :param _BgpPeer: 用户侧BGP，包括Asn，AuthKey
        :type BgpPeer: :class:`tencentcloud.dc.v20180410.models.BgpPeer`
        :param _RouteFilterPrefixes: 用户侧网段地址
        :type RouteFilterPrefixes: list of RouteFilterPrefix
        :param _TencentAddress: 腾讯侧互联IP
        :type TencentAddress: str
        :param _CustomerAddress: 用户侧互联IP
        :type CustomerAddress: str
        :param _Bandwidth: 专用通道带宽值，单位为M。
        :type Bandwidth: int
        :param _TencentBackupAddress: 腾讯侧备用互联IP
        :type TencentBackupAddress: str
        """
        self._DirectConnectTunnelId = None
        self._DirectConnectTunnelName = None
        self._BgpPeer = None
        self._RouteFilterPrefixes = None
        self._TencentAddress = None
        self._CustomerAddress = None
        self._Bandwidth = None
        self._TencentBackupAddress = None

    @property
    def DirectConnectTunnelId(self):
        return self._DirectConnectTunnelId

    @DirectConnectTunnelId.setter
    def DirectConnectTunnelId(self, DirectConnectTunnelId):
        self._DirectConnectTunnelId = DirectConnectTunnelId

    @property
    def DirectConnectTunnelName(self):
        return self._DirectConnectTunnelName

    @DirectConnectTunnelName.setter
    def DirectConnectTunnelName(self, DirectConnectTunnelName):
        self._DirectConnectTunnelName = DirectConnectTunnelName

    @property
    def BgpPeer(self):
        return self._BgpPeer

    @BgpPeer.setter
    def BgpPeer(self, BgpPeer):
        self._BgpPeer = BgpPeer

    @property
    def RouteFilterPrefixes(self):
        return self._RouteFilterPrefixes

    @RouteFilterPrefixes.setter
    def RouteFilterPrefixes(self, RouteFilterPrefixes):
        self._RouteFilterPrefixes = RouteFilterPrefixes

    @property
    def TencentAddress(self):
        return self._TencentAddress

    @TencentAddress.setter
    def TencentAddress(self, TencentAddress):
        self._TencentAddress = TencentAddress

    @property
    def CustomerAddress(self):
        return self._CustomerAddress

    @CustomerAddress.setter
    def CustomerAddress(self, CustomerAddress):
        self._CustomerAddress = CustomerAddress

    @property
    def Bandwidth(self):
        return self._Bandwidth

    @Bandwidth.setter
    def Bandwidth(self, Bandwidth):
        self._Bandwidth = Bandwidth

    @property
    def TencentBackupAddress(self):
        return self._TencentBackupAddress

    @TencentBackupAddress.setter
    def TencentBackupAddress(self, TencentBackupAddress):
        self._TencentBackupAddress = TencentBackupAddress


    def _deserialize(self, params):
        self._DirectConnectTunnelId = params.get("DirectConnectTunnelId")
        self._DirectConnectTunnelName = params.get("DirectConnectTunnelName")
        if params.get("BgpPeer") is not None:
            self._BgpPeer = BgpPeer()
            self._BgpPeer._deserialize(params.get("BgpPeer"))
        if params.get("RouteFilterPrefixes") is not None:
            self._RouteFilterPrefixes = []
            for item in params.get("RouteFilterPrefixes"):
                obj = RouteFilterPrefix()
                obj._deserialize(item)
                self._RouteFilterPrefixes.append(obj)
        self._TencentAddress = params.get("TencentAddress")
        self._CustomerAddress = params.get("CustomerAddress")
        self._Bandwidth = params.get("Bandwidth")
        self._TencentBackupAddress = params.get("TencentBackupAddress")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyDirectConnectTunnelAttributeResponse(AbstractModel):
    """ModifyDirectConnectTunnelAttribute返回参数结构体

    """

    def __init__(self):
        r"""
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
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


class ModifyDirectConnectTunnelExtraRequest(AbstractModel):
    """ModifyDirectConnectTunnelExtra请求参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectTunnelId: 专用通道ID
        :type DirectConnectTunnelId: str
        :param _Vlan: 专用通道的Vlan
        :type Vlan: int
        :param _BgpPeer: 用户侧BGP，Asn，AuthKey
        :type BgpPeer: :class:`tencentcloud.dc.v20180410.models.BgpPeer`
        :param _RouteFilterPrefixes: 用户侧过滤网段地址
        :type RouteFilterPrefixes: :class:`tencentcloud.dc.v20180410.models.RouteFilterPrefix`
        :param _TencentAddress: 腾讯侧互联IP
        :type TencentAddress: str
        :param _TencentBackupAddress: 腾讯侧备用互联IP
        :type TencentBackupAddress: str
        :param _CustomerAddress: 用户侧互联IP
        :type CustomerAddress: str
        :param _Bandwidth: 专用通道带宽值
        :type Bandwidth: int
        :param _EnableBGPCommunity: BGP community开关
        :type EnableBGPCommunity: bool
        :param _BfdEnable: 是否开启BFD
        :type BfdEnable: int
        :param _NqaEnable: 是否开启NQA
        :type NqaEnable: int
        :param _BfdInfo: BFD配置信息
        :type BfdInfo: :class:`tencentcloud.dc.v20180410.models.BFDInfo`
        :param _NqaInfo: NQA配置信息
        :type NqaInfo: :class:`tencentcloud.dc.v20180410.models.NQAInfo`
        :param _IPv6Enable: 0：停用IPv6
1: 启用IPv6
        :type IPv6Enable: int
        :param _CustomerIDCRoutes: 去往用户侧的路由信息
        :type CustomerIDCRoutes: list of RouteFilterPrefix
        :param _JumboEnable: 是否开启巨帧
1：开启
0：不开启
        :type JumboEnable: int
        """
        self._DirectConnectTunnelId = None
        self._Vlan = None
        self._BgpPeer = None
        self._RouteFilterPrefixes = None
        self._TencentAddress = None
        self._TencentBackupAddress = None
        self._CustomerAddress = None
        self._Bandwidth = None
        self._EnableBGPCommunity = None
        self._BfdEnable = None
        self._NqaEnable = None
        self._BfdInfo = None
        self._NqaInfo = None
        self._IPv6Enable = None
        self._CustomerIDCRoutes = None
        self._JumboEnable = None

    @property
    def DirectConnectTunnelId(self):
        return self._DirectConnectTunnelId

    @DirectConnectTunnelId.setter
    def DirectConnectTunnelId(self, DirectConnectTunnelId):
        self._DirectConnectTunnelId = DirectConnectTunnelId

    @property
    def Vlan(self):
        return self._Vlan

    @Vlan.setter
    def Vlan(self, Vlan):
        self._Vlan = Vlan

    @property
    def BgpPeer(self):
        return self._BgpPeer

    @BgpPeer.setter
    def BgpPeer(self, BgpPeer):
        self._BgpPeer = BgpPeer

    @property
    def RouteFilterPrefixes(self):
        return self._RouteFilterPrefixes

    @RouteFilterPrefixes.setter
    def RouteFilterPrefixes(self, RouteFilterPrefixes):
        self._RouteFilterPrefixes = RouteFilterPrefixes

    @property
    def TencentAddress(self):
        return self._TencentAddress

    @TencentAddress.setter
    def TencentAddress(self, TencentAddress):
        self._TencentAddress = TencentAddress

    @property
    def TencentBackupAddress(self):
        return self._TencentBackupAddress

    @TencentBackupAddress.setter
    def TencentBackupAddress(self, TencentBackupAddress):
        self._TencentBackupAddress = TencentBackupAddress

    @property
    def CustomerAddress(self):
        return self._CustomerAddress

    @CustomerAddress.setter
    def CustomerAddress(self, CustomerAddress):
        self._CustomerAddress = CustomerAddress

    @property
    def Bandwidth(self):
        return self._Bandwidth

    @Bandwidth.setter
    def Bandwidth(self, Bandwidth):
        self._Bandwidth = Bandwidth

    @property
    def EnableBGPCommunity(self):
        return self._EnableBGPCommunity

    @EnableBGPCommunity.setter
    def EnableBGPCommunity(self, EnableBGPCommunity):
        self._EnableBGPCommunity = EnableBGPCommunity

    @property
    def BfdEnable(self):
        return self._BfdEnable

    @BfdEnable.setter
    def BfdEnable(self, BfdEnable):
        self._BfdEnable = BfdEnable

    @property
    def NqaEnable(self):
        return self._NqaEnable

    @NqaEnable.setter
    def NqaEnable(self, NqaEnable):
        self._NqaEnable = NqaEnable

    @property
    def BfdInfo(self):
        return self._BfdInfo

    @BfdInfo.setter
    def BfdInfo(self, BfdInfo):
        self._BfdInfo = BfdInfo

    @property
    def NqaInfo(self):
        return self._NqaInfo

    @NqaInfo.setter
    def NqaInfo(self, NqaInfo):
        self._NqaInfo = NqaInfo

    @property
    def IPv6Enable(self):
        return self._IPv6Enable

    @IPv6Enable.setter
    def IPv6Enable(self, IPv6Enable):
        self._IPv6Enable = IPv6Enable

    @property
    def CustomerIDCRoutes(self):
        return self._CustomerIDCRoutes

    @CustomerIDCRoutes.setter
    def CustomerIDCRoutes(self, CustomerIDCRoutes):
        self._CustomerIDCRoutes = CustomerIDCRoutes

    @property
    def JumboEnable(self):
        return self._JumboEnable

    @JumboEnable.setter
    def JumboEnable(self, JumboEnable):
        self._JumboEnable = JumboEnable


    def _deserialize(self, params):
        self._DirectConnectTunnelId = params.get("DirectConnectTunnelId")
        self._Vlan = params.get("Vlan")
        if params.get("BgpPeer") is not None:
            self._BgpPeer = BgpPeer()
            self._BgpPeer._deserialize(params.get("BgpPeer"))
        if params.get("RouteFilterPrefixes") is not None:
            self._RouteFilterPrefixes = RouteFilterPrefix()
            self._RouteFilterPrefixes._deserialize(params.get("RouteFilterPrefixes"))
        self._TencentAddress = params.get("TencentAddress")
        self._TencentBackupAddress = params.get("TencentBackupAddress")
        self._CustomerAddress = params.get("CustomerAddress")
        self._Bandwidth = params.get("Bandwidth")
        self._EnableBGPCommunity = params.get("EnableBGPCommunity")
        self._BfdEnable = params.get("BfdEnable")
        self._NqaEnable = params.get("NqaEnable")
        if params.get("BfdInfo") is not None:
            self._BfdInfo = BFDInfo()
            self._BfdInfo._deserialize(params.get("BfdInfo"))
        if params.get("NqaInfo") is not None:
            self._NqaInfo = NQAInfo()
            self._NqaInfo._deserialize(params.get("NqaInfo"))
        self._IPv6Enable = params.get("IPv6Enable")
        if params.get("CustomerIDCRoutes") is not None:
            self._CustomerIDCRoutes = []
            for item in params.get("CustomerIDCRoutes"):
                obj = RouteFilterPrefix()
                obj._deserialize(item)
                self._CustomerIDCRoutes.append(obj)
        self._JumboEnable = params.get("JumboEnable")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ModifyDirectConnectTunnelExtraResponse(AbstractModel):
    """ModifyDirectConnectTunnelExtra返回参数结构体

    """

    def __init__(self):
        r"""
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
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


class NQAInfo(AbstractModel):
    """nqa配置信息

    """

    def __init__(self):
        r"""
        :param _ProbeFailedTimes: 健康检查次数
        :type ProbeFailedTimes: int
        :param _Interval: 健康检查间隔
        :type Interval: int
        :param _DestinationIp: 健康检查地址
        :type DestinationIp: str
        """
        self._ProbeFailedTimes = None
        self._Interval = None
        self._DestinationIp = None

    @property
    def ProbeFailedTimes(self):
        return self._ProbeFailedTimes

    @ProbeFailedTimes.setter
    def ProbeFailedTimes(self, ProbeFailedTimes):
        self._ProbeFailedTimes = ProbeFailedTimes

    @property
    def Interval(self):
        return self._Interval

    @Interval.setter
    def Interval(self, Interval):
        self._Interval = Interval

    @property
    def DestinationIp(self):
        return self._DestinationIp

    @DestinationIp.setter
    def DestinationIp(self, DestinationIp):
        self._DestinationIp = DestinationIp


    def _deserialize(self, params):
        self._ProbeFailedTimes = params.get("ProbeFailedTimes")
        self._Interval = params.get("Interval")
        self._DestinationIp = params.get("DestinationIp")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class RejectDirectConnectTunnelRequest(AbstractModel):
    """RejectDirectConnectTunnel请求参数结构体

    """

    def __init__(self):
        r"""
        :param _DirectConnectTunnelId: 无
        :type DirectConnectTunnelId: str
        """
        self._DirectConnectTunnelId = None

    @property
    def DirectConnectTunnelId(self):
        return self._DirectConnectTunnelId

    @DirectConnectTunnelId.setter
    def DirectConnectTunnelId(self, DirectConnectTunnelId):
        self._DirectConnectTunnelId = DirectConnectTunnelId


    def _deserialize(self, params):
        self._DirectConnectTunnelId = params.get("DirectConnectTunnelId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class RejectDirectConnectTunnelResponse(AbstractModel):
    """RejectDirectConnectTunnel返回参数结构体

    """

    def __init__(self):
        r"""
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
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


class ReleaseInternetAddressRequest(AbstractModel):
    """ReleaseInternetAddress请求参数结构体

    """

    def __init__(self):
        r"""
        :param _InstanceId: 公网互联网地址ID
        :type InstanceId: str
        """
        self._InstanceId = None

    @property
    def InstanceId(self):
        return self._InstanceId

    @InstanceId.setter
    def InstanceId(self, InstanceId):
        self._InstanceId = InstanceId


    def _deserialize(self, params):
        self._InstanceId = params.get("InstanceId")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class ReleaseInternetAddressResponse(AbstractModel):
    """ReleaseInternetAddress返回参数结构体

    """

    def __init__(self):
        r"""
        :param _RequestId: 唯一请求 ID，每次请求都会返回。定位问题时需要提供该次请求的 RequestId。
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


class RouteFilterPrefix(AbstractModel):
    """用户侧网段地址

    """

    def __init__(self):
        r"""
        :param _Cidr: 用户侧网段地址
        :type Cidr: str
        """
        self._Cidr = None

    @property
    def Cidr(self):
        return self._Cidr

    @Cidr.setter
    def Cidr(self, Cidr):
        self._Cidr = Cidr


    def _deserialize(self, params):
        self._Cidr = params.get("Cidr")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        


class Tag(AbstractModel):
    """标签键值对

    """

    def __init__(self):
        r"""
        :param _Key: 标签键
注意：此字段可能返回 null，表示取不到有效值。
        :type Key: str
        :param _Value: 标签值
注意：此字段可能返回 null，表示取不到有效值。
        :type Value: str
        """
        self._Key = None
        self._Value = None

    @property
    def Key(self):
        return self._Key

    @Key.setter
    def Key(self, Key):
        self._Key = Key

    @property
    def Value(self):
        return self._Value

    @Value.setter
    def Value(self, Value):
        self._Value = Value


    def _deserialize(self, params):
        self._Key = params.get("Key")
        self._Value = params.get("Value")
        memeber_set = set(params.keys())
        for name, value in vars(self).items():
            property_name = name[1:]
            if property_name in memeber_set:
                memeber_set.remove(property_name)
        if len(memeber_set) > 0:
            warnings.warn("%s fileds are useless." % ",".join(memeber_set))
        