from typing import Optional

import requests
import logging

log = logging.getLogger(__name__)

ENDPOINT = "https://api.euw1.rms-npe-internal.com/li/geocode"
GEOCODING_VERSION = "23.0"


class LIAPIClient:
    __slots__ = [
        "access_token",
        "geocoding_version",
        "endpoint",
        "path_to_csv",
    ]

    def __init__(
        self,
        access_token: str,
        endpoint: str = ENDPOINT,
        geocoding_version: str = GEOCODING_VERSION,
    ):
        self.access_token = access_token
        self.geocoding_version = geocoding_version
        self.endpoint = endpoint + "/" + geocoding_version
        self.path_to_csv = None
        log.info(f"Geocoding with LI API using endpoint {self.endpoint}")

    def geocode_address(self, address: dict) -> Optional[dict]:
        """
        Geocode a single address using LI API.

        Parameters:
            address - a dict with the following keys
                "id"
                'CountryCode'
                'CountryScheme'
                'CountryRMSCode'
                'PostalCode'
                'StreetAddress'
                "CityName"
                "Admin1Name"
                "Admin2Name"
                "Admin3Name"
                "Admin4Name"
        """
        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }
        request = {
            "id": address.get("id", ""),
            "countryCode": address.get('CountryCode', ""),
            "countryScheme": address.get('CountryScheme', ""),
            "countryRmsCode": address.get('CountryRMSCode', ""),
            "postalCode": address.get('PostalCode', ""),
            "streetAddress": address.get('StreetAddress', ""),
            "cityName": address.get("CityName", ""),
            "admin1Name": address.get("Admin1Name", ""),
            "admin2Name": address.get("Admin2Name", ""),
            "admin3Name": address.get("Admin3Name", ""),
            "admin4Name": address.get("Admin4Name", "")
        }
        response: Optional[requests.Response] = None
        status_code: Optional[int] = None
        try:
            response = requests.post(
                self.endpoint,
                json=request,
                headers=headers,
                allow_redirects=True,
            )
        except requests.exceptions.HTTPError as err:
            log.warning(
                f"LI API geocoding request failed: {err}\n\n WARNING: Global Connect must be turned off."
            )
        except Exception as e:
            log.error(f"LI API geocoding {e}")
        if response:
            status_code = response.status_code
        if status_code == 200:
            response_json = dict(response.json())
        else:
            log.error(
                f"LI API geocoding failed with status_code: {status_code}"
            )
            response_json = None
        return response_json
