import requests
from dataclasses import dataclass
from typing import List, Dict, Any

class OperatorSearch:
    BASE_URL = 'https://api.operator.io/'
    
    ENTITY_TYPE_MAP = {
        "identity": "identity",
        "nft": "nft",
        "token": "token",
    }

    class HTTPError(Exception):
        pass

    class ValidationError(Exception):
        pass

    class ConnectionError(Exception):
        pass

    class TimeoutError(Exception):
        pass

    class UnauthorizedError(Exception):
        pass

    class ServiceUnavailable(Exception):
        pass

    @dataclass
    class Address:
        address: str
        description: str
        semantic_similarity: float
        network_value: float = 0.0
        rank: float = 0.0

    @dataclass
    class AddressMatch:
        address: str
        metadata: Dict[str, Any]

    @dataclass
    class Addresses:
        query: str
        matches: List[Address]

    def __init__(self, api_key: str):
        self.api_key = api_key

    def findAddress(self, query: str, blockchain: str, entity_type: str, query_by: List[str]) -> Addresses:
        mapped_entity_type = self.ENTITY_TYPE_MAP.get(entity_type)
        if mapped_entity_type is None:
            raise self.ValidationError("Invalid entity_type")
        
        headers = {"X-API-Key": self.api_key}
        try:
            response = requests.post(
                self.BASE_URL + 'search/',
                headers=headers,
                json={
                    "query": query,
                    "blockchain": blockchain,
                    "entity_type": mapped_entity_type,
                    "query_by": query_by
                },
                timeout=5
            )
            response.raise_for_status()
        except requests.Timeout:
            raise self.TimeoutError("API request timed out")
        except requests.RequestException as e:
            if e.response:
                if e.response.status_code == 401:
                    raise self.UnauthorizedError("Invalid API Key")
                elif e.response.status_code == 503:
                    raise self.ServiceUnavailable("Service is unavailable")
                else:
                    raise self.HTTPError(f"Received {e.response.status_code} HTTP status code")
            else:
                raise self.ConnectionError("Could not connect to API")

        data = response.json()
        return self.Addresses(query=data['query'], matches=[self.Address(**address) for address in data['matches']])

    def describeAddress(self, addresses: List[str], blockchain: str) -> List[AddressMatch]:
        headers = {"X-API-Key": self.api_key}
        try:
            response = requests.post(
                self.BASE_URL + 'describe/',
                headers=headers,
                json={"addresses": addresses, "blockchain": blockchain},
                timeout=5
            )
            response.raise_for_status()
        except requests.Timeout:
            raise self.TimeoutError("API request timed out")
        except requests.RequestException as e:
            if e.response:
                if e.response.status_code == 401:
                    raise self.UnauthorizedError("Invalid API Key")
                elif e.response.status_code == 503:
                    raise self.ServiceUnavailable("Service is unavailable")
                else:
                    raise self.HTTPError(f"Received {e.response.status_code} HTTP status code")
            else:
                raise self.ConnectionError("Could not connect to API")

        data = response.json()
        return [self.AddressMatch(**match) for match in data['matches']]