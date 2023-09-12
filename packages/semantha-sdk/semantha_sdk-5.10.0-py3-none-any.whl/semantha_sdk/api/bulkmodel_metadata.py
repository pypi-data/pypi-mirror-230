from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.metadata import Metadata
from semantha_sdk.model.metadata import MetadataSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient
from typing import List

class BulkmodelMetadataEndpoint(SemanthaAPIEndpoint):
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


    def get(
        self,
    ) -> List[Metadata]:
        """
        Get all metadata
            This is the quiet version of  'get /api/domains/{domainname}/metadata'
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params).execute().to(MetadataSchema)

    def post(
        self,
        body: List[Metadata] = None,
    ) -> None:
        """
        Create one or more metadata
            This is the quiet version of  'post /api/domains/{domainname}/metadata'
        Args:
        body (List[Metadata]): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=MetadataSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.as_none()

    
    
    