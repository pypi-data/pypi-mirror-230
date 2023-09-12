from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.instance import Instance
from semantha_sdk.model.instance import InstanceSchema
from semantha_sdk.rest.rest_client import RestClient
from typing import List

class BulkmodelclassInstancesEndpoint(SemanthaAPIEndpoint):
    """ author semantha, this is a generated class do not change manually! TODO: resource.comment?"""

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/instances"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)


    def get(
        self,
    ) -> List[Instance]:
        """
        Get all instances of the classes by class id
            This is the quiet version of 'get /api/model/domains/{domainname}/classes/{id}/instances'
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params).execute().to(InstanceSchema)

    
    
    
    