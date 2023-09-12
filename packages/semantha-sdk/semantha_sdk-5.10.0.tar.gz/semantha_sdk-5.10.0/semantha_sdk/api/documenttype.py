from semantha_sdk.api.clone import CloneEndpoint
from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.document_type import DocumentType
from semantha_sdk.model.document_type import DocumentTypeSchema
from semantha_sdk.model.document_type_change import DocumentTypeChange
from semantha_sdk.model.document_type_change import DocumentTypeChangeSchema
from semantha_sdk.rest.rest_client import RestClient

class DocumenttypeEndpoint(SemanthaAPIEndpoint):
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
        self.__clone = CloneEndpoint(session, self._endpoint)

    @property
    def clone(self) -> CloneEndpoint:
        return self.__clone

    def get(
        self,
    ) -> DocumentType:
        """
        
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params).execute().to(DocumentTypeSchema)

    
    def patch(
        self,
        body: DocumentTypeChange
    ) -> DocumentTypeChange:
        """
        
        """
        return self._session.patch(
            url=self._endpoint,
            json=DocumentTypeChangeSchema().dump(body)
        ).execute().to(DocumentTypeSchema)

    def delete(
        self,
    ) -> None:
        """
        
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    