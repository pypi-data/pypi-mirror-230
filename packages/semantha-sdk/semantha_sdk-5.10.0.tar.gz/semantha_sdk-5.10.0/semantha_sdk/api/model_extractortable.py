from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.extractor_table import ExtractorTable
from semantha_sdk.model.extractor_table import ExtractorTableSchema
from semantha_sdk.rest.rest_client import RestClient

class ModelExtractortableEndpoint(SemanthaAPIEndpoint):
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
    ) -> ExtractorTable:
        """
        Get an extractor table by id
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params).execute().to(ExtractorTableSchema)

    
    
    def delete(
        self,
    ) -> None:
        """
        Delete an extractor table by id
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    def put(
        self,
        body: ExtractorTable
    ) -> ExtractorTable:
        """
        Update an extractor table by id
        """
        return self._session.put(
            url=self._endpoint,
            json=ExtractorTableSchema().dump(body)
        ).execute().to(ExtractorTableSchema)
