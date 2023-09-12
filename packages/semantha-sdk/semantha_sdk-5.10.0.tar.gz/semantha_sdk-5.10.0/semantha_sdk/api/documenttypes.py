from semantha_sdk.api.documenttype import DocumenttypeEndpoint
from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.document_type import DocumentType
from semantha_sdk.model.document_type import DocumentTypeSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient
from typing import List

class DocumenttypesEndpoint(SemanthaAPIEndpoint):
    """ author semantha, this is a generated class do not change manually! TODO: resource.comment?"""

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/documenttypes"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            id: str,
    ) -> DocumenttypeEndpoint:
        return DocumenttypeEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[DocumentType]:
        """
        
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params).execute().to(DocumentTypeSchema)

    def post(
        self,
        body: DocumentType = None,
    ) -> DocumentType:
        """
        
        Args:
        body (DocumentType): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=DocumentTypeSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(DocumentTypeSchema)

    
    def delete(
        self,
    ) -> None:
        """
        
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    