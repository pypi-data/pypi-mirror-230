# Copyright 2016- Game Server Services, Inc. or its affiliates. All Rights
# Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# A copy of the License is located at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# or in the "license" file accompanying this file. This file is distributed
# on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
# express or implied. See the License for the specific language governing
# permissions and limitations under the License.
from __future__ import annotations
from typing import *

from ...core.model import CdkResource, Stack
from ...core.func import GetAttr
from .AdMob import AdMob
from .UnityAd import UnityAd
from ...core.model import NotificationSetting
from ...core.model import LogSetting

from ..ref.NamespaceRef import NamespaceRef

from .options.NamespaceOptions import NamespaceOptions


class Namespace(CdkResource):
    stack: Stack
    name: str
    change_point_notification: NotificationSetting
    admob: Optional[AdMob] = None
    unity_ad: Optional[UnityAd] = None
    description: Optional[str] = None
    log_setting: Optional[LogSetting] = None

    def __init__(
        self,
        stack: Stack,
        name: str,
        change_point_notification: NotificationSetting,
        options: Optional[NamespaceOptions] = NamespaceOptions(),
    ):
        super().__init__(
            "AdReward_Namespace_" + name
        )

        self.stack = stack
        self.name = name
        self.change_point_notification = change_point_notification
        self.admob = options.admob if options.admob else None
        self.unity_ad = options.unity_ad if options.unity_ad else None
        self.description = options.description if options.description else None
        self.log_setting = options.log_setting if options.log_setting else None
        stack.add_resource(
            self,
        )


    def alternate_keys(
        self,
    ):
        return "name"

    def resource_type(
        self,
    ) -> str:
        return "GS2::AdReward::Namespace"

    def properties(
        self,
    ) -> Dict[str, Any]:
        properties: Dict[str, Any] = {}

        if self.name is not None:
            properties["Name"] = self.name
        if self.admob is not None:
            properties["Admob"] = self.admob.properties(
            )
        if self.unity_ad is not None:
            properties["UnityAd"] = self.unity_ad.properties(
            )
        if self.description is not None:
            properties["Description"] = self.description
        if self.change_point_notification is not None:
            properties["ChangePointNotification"] = self.change_point_notification.properties(
            )
        if self.log_setting is not None:
            properties["LogSetting"] = self.log_setting.properties(
            )

        return properties

    def ref(
        self,
    ) -> NamespaceRef:
        return NamespaceRef(
            self.name,
        )

    def get_attr_namespace_id(
        self,
    ) -> GetAttr:
        return GetAttr(
            self,
            "Item.NamespaceId",
            None,
        )
