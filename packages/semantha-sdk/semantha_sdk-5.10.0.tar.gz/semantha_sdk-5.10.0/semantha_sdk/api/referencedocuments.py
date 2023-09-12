from io import IOBase
from semantha_sdk.api.clusters import ClustersEndpoint
from semantha_sdk.api.namedentities import NamedentitiesEndpoint
from semantha_sdk.api.referencedocument import ReferencedocumentEndpoint
from semantha_sdk.api.semantha_endpoint import SemanthaAPIEndpoint
from semantha_sdk.api.statistic import StatisticEndpoint
from semantha_sdk.model.document_information import DocumentInformation
from semantha_sdk.model.document_information import DocumentInformationSchema
from semantha_sdk.model.reference_documents_response_container import ReferenceDocumentsResponseContainer
from semantha_sdk.model.reference_documents_response_container import ReferenceDocumentsResponseContainerSchema
from semantha_sdk.rest.rest_client import MediaType
from semantha_sdk.rest.rest_client import RestClient
from typing import List

class ReferencedocumentsEndpoint(SemanthaAPIEndpoint):
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
        self.__clusters = ClustersEndpoint(session, self._endpoint)
        self.__namedentities = NamedentitiesEndpoint(session, self._endpoint)
        self.__statistic = StatisticEndpoint(session, self._endpoint)

    @property
    def clusters(self) -> ClustersEndpoint:
        return self.__clusters
    @property
    def namedentities(self) -> NamedentitiesEndpoint:
        return self.__namedentities
    @property
    def statistic(self) -> StatisticEndpoint:
        return self.__statistic
    def __call__(
            self,
            documentid: str,
    ) -> ReferencedocumentEndpoint:
        return ReferencedocumentEndpoint(self._session, self._endpoint, documentid)

    def get(
        self,
        tags: str = None,
        documentids: str = None,
        name: str = None,
        createdafter: int = None,
        createdbefore: int = None,
        updatedafter: int = None,
        updatedbefore: int = None,
        documentclassids: str = None,
        withoutdocumentclass: bool = None,
        mincharacters: int = None,
        metadata: str = None,
        comment: str = None,
        sourcedoc: bool = None,
        offset: int = None,
        limit: int = None,
        sort: str = None,
        fields: str = None,
    ) -> ReferenceDocumentsResponseContainer:
        """
        Get all reference documents
            Please be aware that this service is limited: The query parameter ‚tags‘ can only be used in combination with an JSON export.
        Args:
        tags str: List of tags to filter the reference library. You can combine the tags using a comma (OR) and using a plus sign (AND).
    documentids str: List of document Ids for target. The limit here is 65000 IDs.
            The IDs are passed as a JSON array.
    name str: The document name in your library (in contrast to the file name being used during upload).
    createdafter int: Use this parameter to filter the returned reference documents by their date of creation using a UNIX timestamp. The createdafter filter only works when also using the parameters offset and limit.
    createdbefore int: Use this parameter to filter the returned reference documents by their date of creation using a UNIX timestamp. The createdbefore filter only works when also using the parameters offset and limit.
    updatedafter int: 
    updatedbefore int: 
    documentclassids str: List of documentclass IDs for the target. The limit here is 1000 IDs.
            The IDs are passed as a JSON array.
            This does not apply on the GET referencedocuments call. Here the ids are separated with a comma.
    withoutdocumentclass bool: Use this parameter to filter the returned reference documents to include only documents that are not linked to a documentclass. The parameter is of type boolean and is set to false by default.
    mincharacters int: 
    metadata str: Filter by metadata
    comment str: Use this parameter to add a comment to your reference document.
    sourcedoc bool: 
    offset int: Specify from which number on reference documents should be returned.
    limit int: Specify the number of reference documents to be returned.
    sort str: Sort the returned reference documents by name, created, updated and/or metadata. Add a - before the field name to sort in descending order.
    fields str: Define which fields should be returned by the /referencedocuments endpoints. The following values can be sent as a comma-separated list: id, name, tags, metadata, filename, created, processed, lang, updated.
        """
        q_params = {}
        if tags is not None:
            q_params["tags"] = tags
        if documentids is not None:
            q_params["documentids"] = documentids
        if name is not None:
            q_params["name"] = name
        if createdafter is not None:
            q_params["createdafter"] = createdafter
        if createdbefore is not None:
            q_params["createdbefore"] = createdbefore
        if updatedafter is not None:
            q_params["updatedafter"] = updatedafter
        if updatedbefore is not None:
            q_params["updatedbefore"] = updatedbefore
        if documentclassids is not None:
            q_params["documentclassids"] = documentclassids
        if withoutdocumentclass is not None:
            q_params["withoutdocumentclass"] = withoutdocumentclass
        if mincharacters is not None:
            q_params["mincharacters"] = mincharacters
        if metadata is not None:
            q_params["metadata"] = metadata
        if comment is not None:
            q_params["comment"] = comment
        if sourcedoc is not None:
            q_params["sourcedoc"] = sourcedoc
        if offset is not None:
            q_params["offset"] = offset
        if limit is not None:
            q_params["limit"] = limit
        if sort is not None:
            q_params["sort"] = sort
        if fields is not None:
            q_params["fields"] = fields
    
        return self._session.get(self._endpoint, q_params=q_params).execute().to(ReferenceDocumentsResponseContainerSchema)
    def get_as_xlsx(
        self,
        tags: str = None,
        documentids: str = None,
        name: str = None,
        createdafter: int = None,
        createdbefore: int = None,
        updatedafter: int = None,
        updatedbefore: int = None,
        documentclassids: str = None,
        withoutdocumentclass: bool = None,
        mincharacters: int = None,
        metadata: str = None,
        comment: str = None,
        sourcedoc: bool = None,
        offset: int = None,
        limit: int = None,
        sort: str = None,
        fields: str = None,
    ) -> IOBase:
        """
        Get all reference documents
            Please be aware that this service is limited: The query parameter ‚tags‘ can only be used in combination with an JSON export.
        Args:
        tags str: List of tags to filter the reference library. You can combine the tags using a comma (OR) and using a plus sign (AND).
    documentids str: List of document Ids for target. The limit here is 65000 IDs.
            The IDs are passed as a JSON array.
    name str: The document name in your library (in contrast to the file name being used during upload).
    createdafter int: Use this parameter to filter the returned reference documents by their date of creation using a UNIX timestamp. The createdafter filter only works when also using the parameters offset and limit.
    createdbefore int: Use this parameter to filter the returned reference documents by their date of creation using a UNIX timestamp. The createdbefore filter only works when also using the parameters offset and limit.
    updatedafter int: 
    updatedbefore int: 
    documentclassids str: List of documentclass IDs for the target. The limit here is 1000 IDs.
            The IDs are passed as a JSON array.
            This does not apply on the GET referencedocuments call. Here the ids are separated with a comma.
    withoutdocumentclass bool: Use this parameter to filter the returned reference documents to include only documents that are not linked to a documentclass. The parameter is of type boolean and is set to false by default.
    mincharacters int: 
    metadata str: Filter by metadata
    comment str: Use this parameter to add a comment to your reference document.
    sourcedoc bool: 
    offset int: Specify from which number on reference documents should be returned.
    limit int: Specify the number of reference documents to be returned.
    sort str: Sort the returned reference documents by name, created, updated and/or metadata. Add a - before the field name to sort in descending order.
    fields str: Define which fields should be returned by the /referencedocuments endpoints. The following values can be sent as a comma-separated list: id, name, tags, metadata, filename, created, processed, lang, updated.
        """
        q_params = {}
        if tags is not None:
            q_params["tags"] = tags
        if documentids is not None:
            q_params["documentids"] = documentids
        if name is not None:
            q_params["name"] = name
        if createdafter is not None:
            q_params["createdafter"] = createdafter
        if createdbefore is not None:
            q_params["createdbefore"] = createdbefore
        if updatedafter is not None:
            q_params["updatedafter"] = updatedafter
        if updatedbefore is not None:
            q_params["updatedbefore"] = updatedbefore
        if documentclassids is not None:
            q_params["documentclassids"] = documentclassids
        if withoutdocumentclass is not None:
            q_params["withoutdocumentclass"] = withoutdocumentclass
        if mincharacters is not None:
            q_params["mincharacters"] = mincharacters
        if metadata is not None:
            q_params["metadata"] = metadata
        if comment is not None:
            q_params["comment"] = comment
        if sourcedoc is not None:
            q_params["sourcedoc"] = sourcedoc
        if offset is not None:
            q_params["offset"] = offset
        if limit is not None:
            q_params["limit"] = limit
        if sort is not None:
            q_params["sort"] = sort
        if fields is not None:
            q_params["fields"] = fields
    
        return self._session.get(self._endpoint, q_params=q_params).execute().as_bytesio()

    def post(
        self,
        name: str = None,
        tags: str = None,
        metadata: str = None,
        file: IOBase = None,
        text: str = None,
        documenttype: str = None,
        color: str = None,
        comment: str = None,
        documentclassid: str = None,
        addparagraphsasdocuments: bool = None,
        detectlanguage: bool = None,
    ) -> List[DocumentInformation]:
        """
        Upload reference document
        Args:
        name (str): The document name in your library (in contrast to the file name being used during upload).
    tags (str): List of tags to filter the reference library. You can combine the tags using a comma (OR) and using a plus sign (AND).
    metadata (str): Filter by metadata
    file (IOBase): Input document (left document).
    text (str): Plain text input (left document). If set, the parameter `file` will be ignored.
    documenttype (str): Specifies the document type that is to be used by semantha when reading the uploaded document.
    color (str): Use this parameter to specify the color for your reference document. Possible values are RED, MAGENTA, AQUA, ORANGE, GREY, or LAVENDER.
    comment (str): Use this parameter to add a comment to your reference document.
    documentclassid (str): List of documentclass ID for the target. The limit here is 1 ID.
    addparagraphsasdocuments (bool): Use this parameter to create individual reference documents in the library for each paragraph in your document. The parameter is of type boolean and is set to false by default.
        """
        q_params = {}
        if detectlanguage is not None:
            q_params["detectlanguage"] = detectlanguage
        response = self._session.post(
            url=self._endpoint,
            body={
                "name": name,
                "tags": tags,
                "metadata": metadata,
                "file": file,
                "text": text,
                "documenttype": documenttype,
                "color": color,
                "comment": comment,
                "documentclassid": documentclassid,
                "addparagraphsasdocuments": addparagraphsasdocuments,
            },
            headers=RestClient.to_header(MediaType.JSON),
            q_params=q_params
        ).execute()
        return response.to(DocumentInformationSchema)

    
    def delete(
        self,
    ) -> None:
        """
        Delete all reference documents
        """
        self._session.delete(
            url=self._endpoint,
        ).execute()

    