from rest_framework import status
from django.urls import reverse

from kfsd.apps.endpoints.tests.endpoints_test_handler import EndpointsTestHandler


class AttrUtilsTestCases(EndpointsTestHandler):
    def setUp(self):
        super().setUp()

    def test_utils_expr(self):
        postData = self.readJSONData(
            "kfsd/apps/endpoints/tests/v1/data/requests/utils/attr/test_utils_expr.json"
        )
        obsResponse = self.post(reverse("utils-attr"), postData, status.HTTP_200_OK)
        expResponse = self.readJSONData(
            "kfsd/apps/endpoints/tests/v1/data/responses/utils/attr/test_utils_expr.json"
        )
        self.assertEqual(obsResponse, expResponse)
