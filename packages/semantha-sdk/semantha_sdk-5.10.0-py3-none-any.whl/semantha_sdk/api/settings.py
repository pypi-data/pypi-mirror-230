from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.settings import Settings
from semantha_sdk.model.settings import SettingsSchema
from semantha_sdk.rest.rest_client import RestClient

class SettingsEndpoint(SemanthaAPIEndpoint):
    """ author semantha, this is a generated class do not change manually! TODO: resource.comment?"""

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/settings"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)


    def get(
        self,
        withsimilaritymodelid: bool = None,
    ) -> Settings:
        """
        Get the configuration settings of a specific domain
        Args:
        withsimilaritymodelid bool: 
        """
        q_params = {}
        if withsimilaritymodelid is not None:
            q_params["withsimilaritymodelid"] = withsimilaritymodelid
    
        return self._session.get(self._endpoint, q_params=q_params).execute().to(SettingsSchema)

    
    def patch(
        self,
        body: Settings
    ) -> Settings:
        """
        Update configuration settings for this domain, e.g. which similarity model to use
        """
        return self._session.patch(
            url=self._endpoint,
            json=SettingsSchema().dump(body)
        ).execute().to(SettingsSchema)

    
    