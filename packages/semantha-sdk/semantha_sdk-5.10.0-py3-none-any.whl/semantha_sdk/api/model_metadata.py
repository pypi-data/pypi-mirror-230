from semantha_sdk.api.model_onemetadata import ModelOnemetadataEndpoint
from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.metadata import Metadata
from semantha_sdk.model.metadata import MetadataSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient
from typing import List

class ModelMetadataEndpoint(SemanthaAPIEndpoint):
    """ author semantha, this is a generated class do not change manually! TODO: resource.comment?"""

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/metadata"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            id: str,
    ) -> ModelOnemetadataEndpoint:
        return ModelOnemetadataEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[Metadata]:
        """
        Get metadata
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params).execute().to(MetadataSchema)

    def post(
        self,
        body: Metadata = None,
    ) -> Metadata:
        """
        Create metadata
        Args:
        body (Metadata): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=MetadataSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(MetadataSchema)

    
    def delete(
        self,
    ) -> None:
        """
        Delete all metadata
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    