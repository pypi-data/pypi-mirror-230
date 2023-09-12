from io import IOBase
from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.model.document_meta_data import DocumentMetaData
from semantha_sdk.model.document_meta_data import DocumentMetaDataSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient
from typing import List

class DocumentcomparisonsEndpoint(SemanthaAPIEndpoint):
    """ author semantha, this is a generated class do not change manually! TODO: resource.comment?"""

    @property
    def _endpoint(self) -> str:
        return self._parent_endpoint + "/documentcomparisons"

    def __init__(
        self,
        session: RestClient,
        parent_endpoint: str,
    ) -> None:
        super().__init__(session, parent_endpoint)


    
    def post_as_xlsx(
        self,
        file: IOBase = None,
        referencedocument: IOBase = None,
        similaritythreshold: float = None,
        synonymousthreshold: float = None,
        marknomatch: bool = None,
        withreferencetext: bool = None,
        documenttype: str = None,
        metadata: List[DocumentMetaData] = None,
        considertexttype: bool = None,
        resizeparagraphs: bool = None,
        xlsxlegalstandard: bool = None,
    ) -> IOBase:
        """
        Determine references (for temporary data)
        Args:
        file (IOBase): Input document (left document).
    referencedocument (IOBase): Reference document(s) to be used instead of the documents in the domain's library.
    similaritythreshold (float): Threshold for the similarity score. semantha will not deliver results with a sentence score lower than the threshold.
            In general, the higher the threshold, the more precise the results.
    synonymousthreshold (float): Threshold for good matches.
    marknomatch (bool): Marks the paragraphs that have not matched
    withreferencetext (bool): Provide the reference text in the result JSON. If set to false, you have to query the library to resolve the references yourself.
    documenttype (str): Specifies the document type that is to be used by semantha when reading the uploaded document.
    metadata (List[DocumentMetaData]): Filter by metadata
    considertexttype (bool): Use this parameter to ensure that only paragraphs of the same type are compared with each other. The parameter is of type boolean and is set to false by default.
    resizeparagraphs (bool): Automatically resizes paragraphs based on their semantic meaning.
    xlsxlegalstandard (bool): 
        """
        q_params = {}
        response = self._session.post(
            url=self._endpoint,
            body={
                "file": file,
                "referencedocument": referencedocument,
                "similaritythreshold": similaritythreshold,
                "synonymousthreshold": synonymousthreshold,
                "marknomatch": marknomatch,
                "withreferencetext": withreferencetext,
                "documenttype": documenttype,
                "metadata": metadata,
                "considertexttype": considertexttype,
                "resizeparagraphs": resizeparagraphs,
                "xlsxlegalstandard": xlsxlegalstandard,
            },
            headers=RestClient.to_header(MediaType.XLSX),
            q_params=q_params
        ).execute()
        return response.as_bytesio()

    
    
    