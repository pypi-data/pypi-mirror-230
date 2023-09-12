from semantha_sdk.api.model_extractortable import ModelExtractortableEndpoint
from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.extractor_table import ExtractorTable
from semantha_sdk.model.extractor_table import ExtractorTableSchema
from semantha_sdk.model.table import Table
from semantha_sdk.model.table import TableSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient
from typing import List

class ModelExtractortablesEndpoint(SemanthaAPIEndpoint):
    """ author semantha, this is a generated class do not change manually! TODO: resource.comment?"""

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/extractortables"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)

    def __call__(
            self,
            id: str,
    ) -> ModelExtractortableEndpoint:
        return ModelExtractortableEndpoint(self._session, self._endpoint, id)

    def get(
        self,
    ) -> List[Table]:
        """
        Get all extractor tables
        Args:
            """
        q_params = {}
    
        return self._session.get(self._endpoint, q_params=q_params).execute().to(TableSchema)

    def post(
        self,
        body: ExtractorTable = None,
    ) -> ExtractorTable:
        """
        Create an extractor table
        Args:
        body (ExtractorTable): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            json=ExtractorTableSchema().dump(body),
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(ExtractorTableSchema)

    
    def delete(
        self,
    ) -> None:
        """
        Delete all extractortables
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    