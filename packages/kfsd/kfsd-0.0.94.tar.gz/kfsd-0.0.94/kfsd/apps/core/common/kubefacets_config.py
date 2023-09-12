from django.conf import settings
from rest_framework import status

from kfsd.apps.core.common.configuration import Configuration
from kfsd.apps.core.utils.dict import DictUtils
from kfsd.apps.core.utils.system import System
from kfsd.apps.core.utils.http.headers.contenttype import ContentType
from kfsd.apps.core.common.cache import cache
from kfsd.apps.core.exceptions.api import KubefacetsAPIException
from kfsd.apps.core.utils.http.django.request import DjangoRequest
from kfsd.apps.core.auth.api.gateway import APIGateway
from kfsd.apps.core.common.logger import Logger, LogLevel

logger = Logger.getSingleton(__name__, LogLevel.DEBUG)


class KubefacetsConfig(APIGateway):
    def __init__(self):
        self.__localConfig = self.genLocalConfig()
        APIGateway.__init__(self, self.genRequest())

    def genRequest(self):
        self.setHttpHeaders()
        request = DjangoRequest.genDjangoRequest("http://commonconfig/request", "GET")
        request.config = self.__localConfig
        return request

    def getLocalConfig(self):
        return self.__localConfig

    def getLocalKubefacetsSettingsConfig(self):
        return settings.KUBEFACETS

    def isLocalConfig(self):
        isLocalConfig = DictUtils.get_by_path(
            self.getLocalKubefacetsSettingsConfig(), "config.is_local_config"
        )
        if isLocalConfig:
            return True
        return False

    def getLocalConfigDimensions(self):
        localConfigLookupDimensions = DictUtils.get_by_path(
            self.getLocalKubefacetsSettingsConfig(), "config.lookup_dimension_keys"
        )
        if not localConfigLookupDimensions:
            return []
        return localConfigLookupDimensions

    def genLocalConfig(self):
        dimensions = self.constructDimensionsFromEnv(self.getLocalConfigDimensions())
        localConfig = DictUtils.get_by_path(
            self.getLocalKubefacetsSettingsConfig(), "config.local"
        )
        return Configuration(
            settings=localConfig, dimensions=dimensions
        ).getFinalConfig()

    @cache("kfsd.gateway.common.config")
    def deriveRemoteConfig(self):
        if self.isLocalConfig():
            return {}

        self.setHttpHeaders()
        resp = self.get(
            self.getCommonConfigUrl(),
            status.HTTP_200_OK,
            headers=self.getReqHeaders(),
        )
        gatewayResp = resp.json()
        if DictUtils.get(gatewayResp, "status"):
            return DictUtils.get(gatewayResp, "data")
        else:
            raise KubefacetsAPIException(
                "Getting Common Config error",
                "config_error",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
                DictUtils.get(gatewayResp, "error"),
            )

    def deriveLocalConfig(self):
        commonConfig = DictUtils.get(self.__localConfig, "common", {})
        return DictUtils.merge(
            dict1=DictUtils.deepcopy(self.__localConfig),
            dict2=DictUtils.deepcopy(commonConfig),
        )

    def getConfig(self):
        if self.isLocalConfig():
            config = self.deriveLocalConfig()
            return DictUtils.filter_by_keys_neg(config, ["common"])
        else:
            try:
                remoteConfig = self.deriveRemoteConfig()
                remoteConfigMerged = DictUtils.merge(
                    dict1=DictUtils.deepcopy(self.__localConfig),
                    dict2=DictUtils.deepcopy(remoteConfig),
                )
                return remoteConfigMerged
            except KubefacetsAPIException:
                return self.__localConfig

    def constructUrl(self, configPaths):
        uris = self.findConfigs(configPaths)
        return self.formatUrl(uris)

    def findConfigs(self, paths):
        return Configuration.findConfigValues(self.__localConfig, paths)

    def getServicesAPIKey(self):
        return self.findConfigs(["services.api_key"])[0]

    def setHttpHeaders(self):
        self.setAPIKey(self.getServicesAPIKey())
        self.setContentType(ContentType.APPLICATION_JSON)

    def getCommonConfigUrl(self):
        return self.constructUrl(
            ["services.gateway_api.host", "services.gateway_api.core.common_config_uri"]
        )

    def constructDimensionsFromEnv(self, dimensionKeys):
        return {key: System.getEnv(key) for key in dimensionKeys}
