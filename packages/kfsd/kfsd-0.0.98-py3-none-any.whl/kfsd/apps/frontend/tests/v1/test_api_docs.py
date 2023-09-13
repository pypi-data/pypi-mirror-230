from kfsd.apps.core.tests.base_api import BaseAPITestCases
from django.urls import reverse
from unittest.mock import patch
import os


class APIDocsViewTests(BaseAPITestCases):
    def setUp(self):
        os.environ["env"] = "dev"

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    @patch(
        "kfsd.apps.core.common.kubefacets_config.KubefacetsConfig.getLocalKubefacetsSettingsConfig"
    )
    def test_get_auth_allok(self, rawSettingsMocked, tokenUserInfoMocked):
        rawConfig = self.readJSONData(
            "kfsd/apps/core/tests/v1/data/requests/common/kubefacets/local_settings_withauth.json"
        )
        rawSettingsMocked.return_value = rawConfig
        staffUserInfoResp = {
            "status": True,
            "data": {
                "user": {
                    "identifier": "123",
                    "is_staff": True,
                    "is_active": True,
                    "is_email_verified": True,
                }
            },
        }
        tokenUserInfoMocked.return_value = staffUserInfoResp
        url = reverse("api_doc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    @patch(
        "kfsd.apps.core.common.kubefacets_config.KubefacetsConfig.getLocalKubefacetsSettingsConfig"
    )
    def test_get_auth_isnot_staff(self, rawSettingsMocked, tokenUserInfoMocked):
        rawConfig = self.readJSONData(
            "kfsd/apps/core/tests/v1/data/requests/common/kubefacets/local_settings_withauth.json"
        )
        rawSettingsMocked.return_value = rawConfig
        staffUserInfoResp = {
            "status": True,
            "data": {
                "user": {
                    "identifier": "123",
                    "is_staff": False,
                    "is_active": True,
                    "is_email_verified": True,
                }
            },
        }
        tokenUserInfoMocked.return_value = staffUserInfoResp
        url = reverse("api_doc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    @patch(
        "kfsd.apps.core.common.kubefacets_config.KubefacetsConfig.getLocalKubefacetsSettingsConfig"
    )
    def test_get_auth_isnot_active(self, rawSettingsMocked, tokenUserInfoMocked):
        rawConfig = self.readJSONData(
            "kfsd/apps/core/tests/v1/data/requests/common/kubefacets/local_settings_withauth.json"
        )
        rawSettingsMocked.return_value = rawConfig
        staffUserInfoResp = {
            "status": True,
            "data": {
                "user": {
                    "identifier": "123",
                    "is_staff": True,
                    "is_active": False,
                    "is_email_verified": True,
                }
            },
        }
        tokenUserInfoMocked.return_value = staffUserInfoResp
        url = reverse("api_doc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 403)

    @patch("kfsd.apps.core.auth.api.token.TokenAuth.getTokenUserInfo")
    @patch(
        "kfsd.apps.core.common.kubefacets_config.KubefacetsConfig.getLocalKubefacetsSettingsConfig"
    )
    def test_get_auth_isnot_emailverified(self, rawSettingsMocked, tokenUserInfoMocked):
        rawConfig = self.readJSONData(
            "kfsd/apps/core/tests/v1/data/requests/common/kubefacets/local_settings_withauth.json"
        )
        rawSettingsMocked.return_value = rawConfig
        staffUserInfoResp = {
            "status": True,
            "data": {
                "user": {
                    "identifier": "123",
                    "is_staff": True,
                    "is_active": True,
                    "is_email_verified": False,
                }
            },
        }
        tokenUserInfoMocked.return_value = staffUserInfoResp
        url = reverse("api_doc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    @patch(
        "kfsd.apps.core.common.kubefacets_config.KubefacetsConfig.getLocalKubefacetsSettingsConfig"
    )
    def test_get_noauth(self, rawSettingsMocked):
        rawConfig = self.readJSONData(
            "kfsd/apps/core/tests/v1/data/requests/common/kubefacets/local_settings_noauth.json"
        )
        rawSettingsMocked.return_value = rawConfig
        url = reverse("api_doc")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
