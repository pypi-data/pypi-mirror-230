from unittest.mock import patch
import os

from kfsd.apps.core.tests.base_api import BaseAPITestCases
from kfsd.apps.core.common.kubefacets_config import KubefacetsConfig

middleware_settings = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "kfsd.apps.core.middleware.token.KubefacetsTokenMiddleware",
]


class KubefacetsConfigTests(BaseAPITestCases):
    def setUp(self):
        os.environ["env"] = "dev"

    @patch(
        "kfsd.apps.core.common.kubefacets_config.KubefacetsConfig.getLocalKubefacetsSettingsConfig"
    )
    def test_kubefacets_config_local(self, rawSettingsMocked):
        rawConfig = self.readJSONData(
            "kfsd/apps/core/tests/v1/data/requests/common/kubefacets/local_settings_noauth.json"
        )
        rawSettingsMocked.return_value = rawConfig
        obsConfig = KubefacetsConfig().getConfig()
        expConfig = self.readJSONData(
            "kfsd/apps/core/tests/v1/data/responses/common/kubefacets/test_kubefacets_config_local.json"
        )
        self.assertEquals(obsConfig, expConfig)

        localObsConfig = KubefacetsConfig().getLocalConfig()
        localExpConfig = self.readJSONData(
            "kfsd/apps/core/tests/v1/data/responses/common/kubefacets/test_kubefacets_config_local_localconfigobj.json"
        )
        self.assertEquals(localObsConfig, localExpConfig)
