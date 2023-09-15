from inspqcommun.fhir.clients.base_client import BaseClient
from fhirclient.models.immunization import Immunization
from requests import Response
import requests
import logging
import json

log = logging.getLogger(__name__)

class ImmunizationClient(BaseClient):

    immunization_endpoint = "{0}/Immunization"

    def __init__(self, base_url=None, base_uri=None, token_header=None, validate_certs=True) -> None:
        super().__init__(base_url=base_url, base_uri=base_uri, token_header=token_header)
        self.validate_certs = validate_certs

    def create(self, immunization: Immunization):
        immunization.meta = None
        response = requests.post(
            url=self.immunization_endpoint.format(self.get_fhir_url()),
            data=json.dumps(immunization.as_json()),
            headers=self.headers,
            verify=self.validate_certs)
        log.info("POST Immunization : {}".format(response.status_code))
        return response
    
    def extract_immunization_from_response(self, response: Response) -> Immunization:
        if response.status_code == 200 or response.status_code == 201:
            content = json.loads(response.content)
            return Immunization(jsondict=content)
        else:
            return None