from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.document_named_entity import DocumentNamedEntity
from semantha_sdk.model.document_named_entity import DocumentNamedEntitySchema
from semantha_sdk.rest.rest_client import RestClient
from typing import List

class NamedentitiesEndpoint(SemanthaAPIEndpoint):
    """ author semantha, this is a generated class do not change manually! TODO: resource.comment?"""

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/namedentities"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)


    def get(
        self,
        tags: str = None,
        documentclassids: str = None,
    ) -> List[DocumentNamedEntity]:
        """
        Get all custom entities
        Args:
        tags str: List of tags to filter the reference library. You can combine the tags using a comma (OR) and using a plus sign (AND).
    documentclassids str: List of documentclass IDs for the target. The limit here is 1000 IDs.
            The IDs are passed as a JSON array.
            This does not apply on the GET referencedocuments call. Here the ids are separated with a comma.
        """
        q_params = {}
        if tags is not None:
            q_params["tags"] = tags
        if documentclassids is not None:
            q_params["documentclassids"] = documentclassids
    
        return self._session.get(self._endpoint, q_params=q_params).execute().to(DocumentNamedEntitySchema)

    
    
    
    