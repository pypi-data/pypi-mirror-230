from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.entity import Entity
from semantha_sdk.model.entity import EntitySchema
from semantha_sdk.rest.rest_client import RestClient
from typing import List

class ModelExtractorsEndpoint(SemanthaAPIEndpoint):
    """ author semantha, this is a generated class do not change manually! TODO: resource.comment?"""

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/extractors"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)


    def get(
        self,
    ) -> List[Entity]:
        """
        Get all extractors
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params).execute().to(EntitySchema)

    
    
    
    