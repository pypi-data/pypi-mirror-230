from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.paragraph import Paragraph
from semantha_sdk.model.paragraph import ParagraphSchema
from semantha_sdk.model.paragraph_update import ParagraphUpdate
from semantha_sdk.model.paragraph_update import ParagraphUpdateSchema
from semantha_sdk.rest.rest_client import RestClient

class ParagraphEndpoint(SemanthaAPIEndpoint):
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
    ) -> Paragraph:
        """
        Get paragraph by ID
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params).execute().to(ParagraphSchema)

    
    def patch(
        self,
        body: ParagraphUpdate
    ) -> ParagraphUpdate:
        """
        Update a specific paragraph of a specific reference document of the library
        """
        return self._session.patch(
            url=self._endpoint,
            json=ParagraphUpdateSchema().dump(body)
        ).execute().to(ParagraphSchema)

    def delete(
        self,
    ) -> None:
        """
        Delete a specific paragraph of a specific reference document of the library
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    