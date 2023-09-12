from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.relation import Relation
from semantha_sdk.model.relation import RelationSchema
from semantha_sdk.rest.rest_client import RestClient

class ModelRelationEndpoint(SemanthaAPIEndpoint):
    """ author semantha, this is a generated class do not change manually! TODO: resource.comment?"""

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + f"/{self._id}"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
        id: str,
    ) -> None:
        super().__init__(session, parent_endpoint)
        self._id = id


    def get(
        self,
    ) -> Relation:
        """
        Get a relation by id
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params).execute().to(RelationSchema)

    
    
    def delete(
        self,
    ) -> None:
        """
        Delete a relation by id
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    def put(
        self,
        body: Relation
    ) -> Relation:
        """
        Update a relation by id
        """
        return self._session.put(
            url=self._endpoint,
            json=RelationSchema().dump(body)
        ).execute().to(RelationSchema)
