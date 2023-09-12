from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.document_information import DocumentInformation
from semantha_sdk.model.document_information import DocumentInformationSchema
from semantha_sdk.rest.rest_client import RestClient
from typing import List

class DocclassReferencedocumentsEndpoint(SemanthaAPIEndpoint):
    """ author semantha, this is a generated class do not change manually! TODO: resource.comment?"""

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/referencedocuments"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)


    def get(
        self,
    ) -> List[DocumentInformation]:
        """
        Get all library documents belonging to a document class identified by its id
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params).execute().to(DocumentInformationSchema)

    
    def patch(
        self,
        body: List[str]
    ) -> List[str]:
        """
        Add a library document to a document class identified by its id
        """
        return self._session.patch(
            url=self._endpoint,
            json=body
        ).execute().as_none()

    def delete(
        self,
        body: List[str],
    ) -> None:
        """
        Delete library documents from a document class identified by its id
        """
        self._session.delete(
            url=self._endpoint,
            json=body
        ).execute()

    