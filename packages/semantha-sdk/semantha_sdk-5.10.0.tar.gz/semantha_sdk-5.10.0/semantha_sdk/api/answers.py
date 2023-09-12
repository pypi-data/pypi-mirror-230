from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.answer import Answer
from semantha_sdk.model.answer import AnswerSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient

class AnswersEndpoint(SemanthaAPIEndpoint):
    """ author semantha, this is a generated class do not change manually! TODO: resource.comment?"""

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/answers"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)


    
    def post(
        self,
        question: str = None,
        maxreferences: int = None,
        similaritythreshold: float = None,
    ) -> Answer:
        """
        
        Args:
        question (str): 
    maxreferences (int): Maximum number of returned results.
    similaritythreshold (float): Threshold for the similarity score. semantha will not deliver results with a sentence score lower than the threshold.
            In general, the higher the threshold, the more precise the results.
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "question": question,
                "maxreferences": maxreferences,
                "similaritythreshold": similaritythreshold,
            },
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(AnswerSchema)

    
    
    