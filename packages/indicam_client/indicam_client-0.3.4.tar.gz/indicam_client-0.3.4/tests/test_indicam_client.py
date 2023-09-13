"""Tests for `indicam_client` package."""

import unittest
import responses

from indicam_client import indicam_client as client
from indicam_client import GaugeMeasurement

# Recurring valid values
INDICAM_ID = 1
INDICAM_HANDLE = "test_handle"
API_KEY = "Test API Key"
ROOT_URL = "https://app.hausnet.io/indicam/api"
HEADERS = {'Authorization': f'Token {API_KEY}'}


class TestIndicamClient(unittest.TestCase):
    """Tests for `indicam_client` package."""

    def setUp(self) -> None:
        """Create the service client used by all tests."""
        self.service_client = client.IndiCamServiceClient(ROOT_URL, api_key=API_KEY)

    @responses.activate
    def test_indicam_id_found(self):
        """Test that a valid indicam handle produces the indicam key."""
        responses.get(
            f"{ROOT_URL}/indicams/?handle={INDICAM_HANDLE}",
            headers=HEADERS,
            status=200,
            json=[{'id': INDICAM_ID}],
        )
        camconfig = self.service_client.get_indicam_id(INDICAM_HANDLE)
        self.assertIsNotNone(camconfig)

    @responses.activate
    def test_indicam_id_not_found(self):
        """Test that a valid indicam handle produces the indicam key."""
        responses.get(
            f"{ROOT_URL}/indicams/?handle={INDICAM_HANDLE + 'x'}",
            headers=HEADERS,
            status=404,
            json='',
        )
        camconfig = self.service_client.get_indicam_id(INDICAM_HANDLE + 'x')
        self.assertIsNone(camconfig)

    @responses.activate
    def test_camconfig_retrieved(self):
        """Test getting the camera configuration."""
        responses.get(
            f"{ROOT_URL}/indicams/{INDICAM_ID}/camconfig_current/",
            headers=HEADERS,
            status=200,
            json={client.CAMCONFIG_MIN_KEY: 10, client.CAMCONFIG_MAX_KEY: 11},
        )
        camconfig = self.service_client.get_camconfig(INDICAM_ID)
        self.assertIsNotNone(camconfig)
        self.assertEqual(10, camconfig.min_perc)
        self.assertEqual(11, camconfig.max_perc)

    @responses.activate
    def test_camconfig_retrieve_failed(self):
        """Test that when getting the camera configuration fails, None is returned."""
        responses.get(
            f"{ROOT_URL}/{INDICAM_ID}/camconfig_current/",
            headers=HEADERS,
            status=404
        )
        responses.get(
            f"{ROOT_URL}/indicams/{INDICAM_ID}/camconfig_current/",
            headers=HEADERS,
            status=200,
            json={},
        )
        camconfig = self.service_client.get_camconfig(INDICAM_ID)
        self.assertIsNone(camconfig)
        camconfig = self.service_client.get_camconfig(INDICAM_ID)
        self.assertIsNone(camconfig)

    @responses.activate
    def test_camconfig_created(self):
        """ Test that a camconfig can be created. """
        responses.post(
            f"{ROOT_URL}/camconfigs/",
            headers=HEADERS,
            status=201,
            match=[
                responses.matchers.json_params_matcher(
                    {
                        'indicam': INDICAM_ID,
                        client.CAMCONFIG_MIN_KEY: 11,
                        client.CAMCONFIG_MAX_KEY: 13,
                    }
                )
            ]
        )
        new_camconfig = client.CamConfig(min_perc=11, max_perc=13)
        success = self.service_client.create_camconfig(INDICAM_ID, new_camconfig)
        self.assertTrue(success)

    @responses.activate
    def test_camconfig_not_created(self):
        """ Test that an error creating a new camconfig is handled. """
        responses.post(
            f"{ROOT_URL}/camconfigs/",
            headers=HEADERS,
            status=404,
            match=[
                responses.matchers.json_params_matcher(
                    {
                        'indicam': INDICAM_ID,
                        client.CAMCONFIG_MIN_KEY: 11,
                        client.CAMCONFIG_MAX_KEY: 13,
                    }
                )
            ]
        )
        new_camconfig = client.CamConfig(min_perc=11, max_perc=13)
        success = self.service_client.create_camconfig(INDICAM_ID, new_camconfig)
        self.assertFalse(success)

    @responses.activate
    def test_image_uploaded(self) -> None:
        """ Test the image upload function. """
        responses.post(
            f"{ROOT_URL}/images/{INDICAM_ID}/upload/",
            status=200,
            headers=HEADERS,
            json={"image_id": 5678},
        )
        image_id = self.service_client.upload_image(INDICAM_ID, b"Hello")
        self.assertEqual(5678, image_id)

    @responses.activate
    def test_image_upload_fails(self) -> None:
        """ Test the image upload function when it fails. """
        responses.post(
            f"{ROOT_URL}/images/{INDICAM_ID}/upload/",
            status=404,
            headers=HEADERS,
            body="error in ....",
        )
        image_id = self.service_client.upload_image(INDICAM_ID, b"Hello")
        self.assertIsNone(image_id)

    @responses.activate
    def test_get_measurement(self) -> None:
        """ Test getting a measurement. """
        test_measurement = {
            'id': 1234,
            'prediction_model': 5,
            'error': 0,
            'value': 30.0,
            'gauge_left_col': 10,
            'gauge_right_col': 100,
            'gauge_top_row': 5,
            'gauge_bottom_row': 500,
            'float_top_col': 200,
            'decorated_image': 'http://dummyhost.com/media/images/uid_1/testdev/20230821163518545474-decorated-v5.jpg',
            'src_image': 5678,
        }
        responses.get(
            f"{ROOT_URL}/measurements/?src_image={5678}",
            headers=HEADERS,
            status=200,
            json=[test_measurement, ]
        )
        measurement = self.service_client.get_measurement(5678)
        expected_measurement = GaugeMeasurement(
            body_left=int(test_measurement['gauge_left_col']),
            body_right=int(test_measurement['gauge_right_col']),
            body_top=int(test_measurement['gauge_top_row']),
            body_bottom=int(test_measurement['gauge_bottom_row']),
            float_top=int(test_measurement['float_top_col']),
            value=float(test_measurement['value'])
        )
        self.assertEqual(expected_measurement, measurement)

    @responses.activate
    def test_get_measurement_failed(self) -> None:
        """ Test a failed measurement retrieval. """
        test_measurement = {
            'id': 1234,
            'prediction_model': 5,
            'error': 2,
            'value': 0.0,
            'gauge_left_col': None,
            'gauge_right_col': None,
            'gauge_top_row': None,
            'gauge_bottom_row': None,
            'float_top_col': None,
            'decorated_image': None,
            'src_image': 5678,
        }
        responses.get(
            f"{ROOT_URL}/measurements/?src_image={5678}",
            headers=HEADERS,
            status=200,
            json=[test_measurement, ]
        )
        measurement = self.service_client.get_measurement(5678)
        self.assertIsNone(measurement)
