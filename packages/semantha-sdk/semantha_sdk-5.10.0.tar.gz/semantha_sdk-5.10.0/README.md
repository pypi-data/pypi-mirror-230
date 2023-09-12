![](https://www.semantha.de/wp-content/uploads/semantha-inverted.svg)

# semantha® SDK

The semantha SDK is a high-level REST client to access the [semantha](http://semantha.ai) API.
The SDK is still under development.
An overview of the current progress (i.e. implemented and tested resources and endpoints) may be found at the end of
this document (State of Development).
The semantha SDK is compatible with python >= 3.8.

## Design guideline/idea
Every api call can easily be translated into a python sdk call:
`GET /api/info -> api.info.get()`
The SDK offers type hints and doc strings for services, parameters, input types and return types within your IDE.

## Update Notes
### Version 5.10.0
Improved Use Case SDK

### Version 5.9.0
Removed endpoint:
- **/api/domains/{domainname}/referencedocuments/{documentid}/paragraphs/{id}/links**

### Version 5.8.0
Added endpoints:
- **/api/domains/{domainname}/documentclasses/{id}/documentclasses**
- **/api/domains/{domainname}/documentclasses/{id}/referencedocuments**
- **/api/domains/{domainname}/referencedocuments/{documentid}/paragraphs/{id}/links**
- **/api/model/domains/{domainname}/backups**

SDK covers now 193/197 services.

### Version 5.7.0
Added new endpoints in:
- **/api/domains/{domainname}/documenttypes/*** 
- **/api/domains/{domainname}/documentclasses/{id}/customfields**
- **/api/model/domains/{domainname}/classes/***

SDK covers now 184/197 services.


### Version 5.6.0
Added most endpoints in **/api/models/* **
SDK covers now 158/180 services.

### Version 5.5.0
Removed language parameter on **/api/domains/{domainname}/references**
Fixed bug on serialization of **/api/domains/{domainname}/modelinstances** response.
Fixed return of binary responses of bulk services.

### Version 5.4.0
Added **new** service: 
- **/api/domains/{domainname}/summarizations** which generations a summarization for a given list of texts and a given topic.

Added support for **existing** services: 
- /api/model/domains/{domainname}/boostwords/{id}
- /api/model/domains/{domainname}/namedentities
- /api/model/domains/{domainname}/namedentities/{id}
- /api/model/domains/{domainname}/stopwords
- /api/model/domains/{domainname}/stopwords/{id}
- /api/model/domains/{domainname}/synonyms/{id}

### Version 5.3.0

Added new service: **/api/domains/{domainid}/answers** with retrieval augemented answer generation based on your library entries.
Added new parameter on /modelinstances

### Version 5.2.0

The SDK is now automatically generated from our openapi.json specification. It covers 71/169 (=42%) of all available services. Many class names and package names have been changed.

### Version 4.5.0
Major restructuring of the SDK.
All sub-resources are directly accessible (instead of invoking getters).
That also means that (except for a few) all functions are plain get/post/delete/put/patch.
For example, in Versions < 4.5.0 a domain resource was fetched using `semantha_sdk.domains.get_one("domain_name")`.
Starting with 4.5.0 it is `semantha_sdk.domains("domain_name")`.
That also means that get/post/put/patch functions return semantha model objects (and never resources), which makes usage more consistent.

### Access

To access semantha's API you will need an API and a server url.
Both can be requested via [this contact form](https://www.semantha.de/request/).

## Example Usage

### Authentication with key

```python
import semantha_sdk
api = semantha_sdk.login(server_url="<semantha server URL>", key="<your key>")
print("Talking to semantha server: " + api.info.get().version)
```

### Authentication with key file

```python
import semantha_sdk
api = semantha_sdk.login(server_url="<semantha server URL>", key_file="<path to your key file (json format)>")
# end-points (resp. resources) can be used like objects
my_domain = api.domains("my_domain")
# they may have sub-resources, which can be retrieved as objects as well
reference_documents = my_domain.referencedocuments
# GET all reference documents
print("Library contains "+ len(reference_documents.get()) + " entries")
```

Example key file in json format:

```json
{ "API_Key" : "<your key>" }
```

### CRUD on End-points

```python
# CRUD operations are functions
domain_settings = my_domain.settings.get()
#Warning: this deletes ALL reference documents/library entries
my_domain.referencedocuments.delete() 
```

### Function Return Types & semantha Data Model

```python
# some functions only return None, e.g.
my_domain.referencedocuments.delete() # returns NoneType

# others return built in types, e.g
roles_list = currentuser.roles.get() # returns List[str]

# but most return objects of the semantha Data Model
# (all returned objects are instances of frozen dataclasses)
settings = my_domain.settings.get() # returns instance of Settings
# attributes can be accessed as properties, e.g.
settings.enable_tagging # returns true or false
# Data Model objects may be complex
document = my_domain.references.post(file=a, referencedocument=b) # returns instance of Document
# the following returns the similarity value of the first references of the first sentence of the
# the first paragraph on the first page of the document (if a reference was found for this sentence)
similarity = pages[0].contents[0].paragraphs[0].references[0].similarity # returns float
```

## State of Development

The following resources and end-points are fully functional and (partially) tested:

- [x] **/bulk** -> BulkEndpoint
- [x] **/bulk/domains** -> BulkDomainsEndpoint
- [x] **/bulk/domains/{domainname}** -> BulkdomainsDomainEndpoint
- [x] **/bulk/domains/{domainname}/documentclasses** -> BulkdomainsDocumentclassesEndpoint
    - [x] **GET** -> List[DocumentClassBulk]
    - [x] **POST** -> None
- [x] **/bulk/domains/{domainname}/documenttypes** -> BulkdomainsDocumenttypesEndpoint
    - [x] **GET** -> List[DocumentType]
    - [x] **POST** -> None
- [x] **/bulk/domains/{domainname}/referencedocuments** -> BulkdomainsReferencedocumentsEndpoint
    - [x] **GET** -> List[Document]
    - [x] **POST** -> None
    - [x] **DELETE** -> None
- [x] **/bulk/domains/{domainname}/references** -> BulkdomainsReferencesEndpoint
    - [x] **POST** -> List[Document]
- [x] **/bulk/model** -> BulkModelEndpoint
- [x] **/bulk/model/domains** -> BulkmodelDomainsEndpoint
- [x] **/bulk/model/domains/{domainname}** -> BulkmodelDomainEndpoint
- [x] **/bulk/model/domains/{domainname}/boostwords** -> BulkmodelBoostwordsEndpoint
    - [x] **POST** -> None
- [x] **/bulk/model/domains/{domainname}/classes** -> BulkmodelClassesEndpoint
    - [x] **GET** -> List[ClassBulk]
    - [x] **POST** -> None
- [x] **/bulk/model/domains/{domainname}/classes/{classid}** -> BulkmodelClassEndpoint
- [x] **/bulk/model/domains/{domainname}/classes/{classid}/instances** -> BulkmodelclassInstancesEndpoint
    - [x] **GET** -> List[Instance]
- [x] **/bulk/model/domains/{domainname}/dataproperties** -> BulkmodelDatapropertiesEndpoint
    - [x] **GET** -> List[DataProperty]
    - [x] **POST** -> None
- [x] **/bulk/model/domains/{domainname}/instances** -> BulkmodelInstancesEndpoint
    - [x] **GET** -> List[Instance]
    - [x] **POST** -> None
- [x] **/bulk/model/domains/{domainname}/metadata** -> BulkmodelMetadataEndpoint
    - [x] **GET** -> List[Metadata]
    - [x] **POST** -> None
- [x] **/bulk/model/domains/{domainname}/namedentities** -> BulkmodelNamedentitiesEndpoint
    - [x] **POST** -> None
- [x] **/bulk/model/domains/{domainname}/rules** -> BulkmodelRulesEndpoint
    - [x] **GET** -> List[Rule]
    - [x] **POST** -> None
- [x] **/bulk/model/domains/{domainname}/stopwords** -> BulkmodelStopwordsEndpoint
    - [x] **POST** -> None
- [x] **/bulk/model/domains/{domainname}/synonyms** -> BulkmodelSynonymsEndpoint
    - [x] **POST** -> None
- [x] **/celltypes** -> CelltypesEndpoint
    - [x] **GET** -> List[CellType]
- [x] **/currentuser** -> CurrentuserEndpoint
    - [x] **GET** -> CurrentUser
- [x] **/currentuser/roles** -> RolesEndpoint
    - [x] **GET** -> List[str]
- [x] **/diff** -> DiffEndpoint
    - [x] **POST** -> List[Difference]
- [x] **/domains** -> DomainsEndpoint
    - [x] **GET** -> List[Domain]
- [x] **/domains/{domainname}** -> DomainEndpoint
    - [x] **GET** -> Domain
- [x] **/domains/{domainname}/answers** -> AnswersEndpoint
    - [x] **POST** -> Answer
- [x] **/domains/{domainname}/documentannotations** -> DocumentannotationsEndpoint
    - [x] **POST** (Accept: docx) -> IOBase
    - [x] **POST** (Accept: pdf) -> IOBase
- [x] **/domains/{domainname}/documentclasses** -> DocumentclassesEndpoint
    - [x] **GET** -> List[DocumentClass]
    - [x] **POST** -> DocumentClass
    - [x] **DELETE** -> None
- [x] **/domains/{domainname}/documentclasses/{id}** -> DocumentclassEndpoint
    - [x] **GET** -> DocumentClass
    - [x] **DELETE** -> None
    - [x] **PUT** -> DocumentClass
- [x] **/domains/{domainname}/documentclasses/{id}/customfields** -> DocclassCustomfieldsEndpoint
    - [x] **DELETE** -> None
    - [x] **PUT** -> None
- [x] **/domains/{domainname}/documentclasses/{id}/documentclasses** -> DocclassDocumentclassesEndpoint
    - [x] **GET** -> List[DocumentClass]
    - [x] **POST** -> DocumentClass
    - [x] **DELETE** -> List[DocumentClass]
    - [x] **PATCH** -> List[DocumentClass]
- [x] **/domains/{domainname}/documentclasses/{id}/referencedocuments** -> DocclassReferencedocumentsEndpoint
    - [x] **GET** -> List[DocumentInformation]
    - [x] **DELETE** -> None
    - [x] **PATCH** -> None
- [x] **/domains/{domainname}/documentcomparisons** -> DocumentcomparisonsEndpoint
    - [x] **POST** (Accept: xlsx) -> IOBase
- [x] **/domains/{domainname}/documents** -> DocumentsEndpoint
    - [x] **POST** -> List[Document]
    - [x] **POST** (Accept: xlsx) -> IOBase
    - [x] **POST** (Accept: docx) -> IOBase
- [x] **/domains/{domainname}/documenttypes** -> DocumenttypesEndpoint
    - [x] **GET** -> List[DocumentType]
    - [x] **POST** -> DocumentType
    - [x] **DELETE** -> None
- [x] **/domains/{domainname}/documenttypes/{id}** -> DocumenttypeEndpoint
    - [x] **GET** -> DocumentType
    - [x] **DELETE** -> None
    - [x] **PATCH** -> DocumentType
- [x] **/domains/{domainname}/documenttypes/{id}/clone** -> CloneEndpoint
    - [x] **POST** -> DocumentType
- [x] **/domains/{domainname}/modelclasses** -> ModelclassesEndpoint
    - [x] **GET** -> List[ModelClass]
- [x] **/domains/{domainname}/modelinstances** -> ModelinstancesEndpoint
    - [x] **POST** -> SemanticModel
    - [x] **POST** (Accept: xlsx) -> IOBase
- [x] **/domains/{domainname}/referencedocuments** -> ReferencedocumentsEndpoint
    - [x] **GET** -> ReferenceDocumentsResponseContainer
    - [x] **GET** (Accept: xlsx) -> IOBase
    - [x] **POST** -> List[DocumentInformation]
    - [x] **DELETE** -> None
- [x] **/domains/{domainname}/referencedocuments/clusters** -> ClustersEndpoint
    - [x] **GET** -> SmartClusterResponseContainer
    - [x] **PUT** -> SmartClusterResponseContainer
- [x] **/domains/{domainname}/referencedocuments/namedentities** -> NamedentitiesEndpoint
    - [x] **GET** -> List[DocumentNamedEntity]
- [x] **/domains/{domainname}/referencedocuments/statistic** -> StatisticEndpoint
    - [x] **GET** -> Statistic
- [x] **/domains/{domainname}/referencedocuments/{documentid}** -> ReferencedocumentEndpoint
    - [x] **GET** -> Document
    - [x] **DELETE** -> None
    - [x] **PATCH** -> DocumentInformation
- [x] **/domains/{domainname}/referencedocuments/{documentid}/paragraphs** -> ParagraphsEndpoint
- [x] **/domains/{domainname}/referencedocuments/{documentid}/paragraphs/{id}** -> ParagraphEndpoint
    - [x] **GET** -> Paragraph
    - [x] **DELETE** -> None
    - [x] **PATCH** -> Paragraph
- [x] **/domains/{domainname}/referencedocuments/{documentid}/sentences** -> SentencesEndpoint
- [x] **/domains/{domainname}/referencedocuments/{documentid}/sentences/{id}** -> SentenceEndpoint
    - [x] **GET** -> Sentence
- [x] **/domains/{domainname}/references** -> ReferencesEndpoint
    - [x] **POST** -> Document
    - [x] **POST** (Accept: xlsx) -> IOBase
    - [x] **POST** (Accept: docx) -> IOBase
    - [x] **POST** (Accept: pdf) -> IOBase
- [x] **/domains/{domainname}/settings** -> SettingsEndpoint
    - [x] **GET** -> Settings
    - [x] **PATCH** -> Settings
- [x] **/domains/{domainname}/similaritymatrix** -> SimilaritymatrixEndpoint
    - [x] **POST** -> List[MatrixRow]
- [x] **/domains/{domainname}/similaritymatrix/cluster** -> SimilaritymatrixClusterEndpoint
    - [x] **POST** -> List[MatrixRow]
- [x] **/domains/{domainname}/summarizations** -> SummarizationsEndpoint
    - [x] **POST** -> str
- [x] **/domains/{domainname}/tags** -> TagsEndpoint
    - [x] **GET** -> List[str]
- [x] **/domains/{domainname}/tags/{tagname}** -> TagEndpoint
- [x] **/domains/{domainname}/tags/{tagname}/referencedocuments** -> TagReferencedocumentsEndpoint
    - [x] **GET** -> List[DocumentInformation]
    - [x] **DELETE** -> None
- [x] **/domains/{domainname}/validation** -> ValidationEndpoint
    - [x] **POST** -> SemanticModel
- [x] **/info** -> InfoEndpoint
    - [x] **GET** -> Info
- [x] **/languages** -> LanguagesEndpoint
    - [x] **POST** -> LanguageDetection
- [x] **/model** -> ModelEndpoint
- [x] **/model/datatypes** -> ModelDatatypesEndpoint
    - [x] **GET** -> List[str]
- [x] **/model/domains** -> ModelDomainsEndpoint
- [x] **/model/domains/{domainname}** -> ModelDomainEndpoint
    - [x] **GET** (Accept: xlsx) -> IOBase
    - [x] **PATCH** -> IOBase
- [x] **/model/domains/{domainname}/attributes** -> ModelAttributesEndpoint
    - [x] **GET** -> List[AttributeOverview]
- [x] **/model/domains/{domainname}/backups** -> ModelBackupsEndpoint
    - [x] **POST** -> None
- [x] **/model/domains/{domainname}/boostwords** -> ModelBoostwordsEndpoint
    - [x] **GET** -> List[BoostWord]
    - [x] **POST** -> BoostWord
    - [x] **DELETE** -> None
- [x] **/model/domains/{domainname}/boostwords/{id}** -> ModelBoostwordEndpoint
    - [x] **GET** -> BoostWord
    - [x] **DELETE** -> None
    - [x] **PUT** -> BoostWord
- [x] **/model/domains/{domainname}/classes** -> ModelontClassesEndpoint
    - [x] **GET** -> List[ClassesOverview]
    - [x] **POST** -> Clazz
    - [x] **DELETE** -> None
- [x] **/model/domains/{domainname}/classes/{classid}** -> ModelontClassEndpoint
    - [x] **GET** -> Clazz
    - [x] **DELETE** -> None
    - [x] **PUT** -> Clazz
- [x] **/model/domains/{domainname}/classes/{classid}/attributes** -> ModelontAttributesEndpoint
    - [x] **GET** -> List[Attribute]
    - [x] **POST** -> Attribute
    - [x] **DELETE** -> None
- [x] **/model/domains/{domainname}/classes/{classid}/attributes/{id}** -> ModelontAttributeEndpoint
    - [x] **GET** -> Attribute
    - [x] **DELETE** -> None
    - [x] **PUT** -> Attribute
- [x] **/model/domains/{domainname}/classes/{classid}/instances** -> ModelontclassInstancesEndpoint
    - [x] **GET** -> List[Instance]
    - [x] **DELETE** -> None
- [x] **/model/domains/{domainname}/dataproperties** -> ModelDatapropertiesEndpoint
    - [x] **GET** -> List[Overview]
    - [x] **POST** -> DataProperty
    - [x] **DELETE** -> None
- [x] **/model/domains/{domainname}/dataproperties/{id}** -> ModelDatapropertyEndpoint
    - [x] **GET** -> DataProperty
    - [x] **DELETE** -> None
    - [x] **PUT** -> DataProperty
- [x] **/model/domains/{domainname}/extractorclasses** -> ModelExtractorclassesEndpoint
    - [x] **GET** -> List[ExtractorClassOverview]
    - [x] **POST** -> ExtractorClass
    - [x] **DELETE** -> None
    - [x] **PUT** -> None
- [x] **/model/domains/{domainname}/extractorclasses/{id}** -> ModelExtractorclassEndpoint
    - [x] **GET** -> ExtractorClass
    - [x] **DELETE** -> None
    - [x] **PUT** -> ExtractorClass
- [x] **/model/domains/{domainname}/extractorclasses/{id}/extractorclasses** -> ChildExtractorclassesEndpoint
    - [x] **POST** -> ExtractorClass
- [x] **/model/domains/{domainname}/extractors** -> ModelExtractorsEndpoint
    - [x] **GET** -> List[Entity]
- [x] **/model/domains/{domainname}/extractortables** -> ModelExtractortablesEndpoint
    - [x] **GET** -> List[Table]
    - [x] **POST** -> ExtractorTable
    - [x] **DELETE** -> None
- [x] **/model/domains/{domainname}/extractortables/{id}** -> ModelExtractortableEndpoint
    - [x] **GET** -> ExtractorTable
    - [x] **DELETE** -> None
    - [x] **PUT** -> ExtractorTable
- [x] **/model/domains/{domainname}/formatters** -> ModelFormattersEndpoint
    - [x] **GET** -> List[Formatter]
- [x] **/model/domains/{domainname}/instances** -> ModelontInstancesEndpoint
    - [x] **GET** -> List[InstanceOverview]
    - [x] **GET** (Accept: xlsx) -> IOBase
    - [x] **POST** -> Instance
    - [x] **DELETE** -> None
    - [x] **PATCH** -> None
- [x] **/model/domains/{domainname}/instances/{id}** -> ModelontInstanceEndpoint
    - [x] **GET** -> Instance
    - [x] **DELETE** -> None
    - [x] **PUT** -> Instance
- [x] **/model/domains/{domainname}/metadata** -> ModelMetadataEndpoint
    - [x] **GET** -> List[Metadata]
    - [x] **POST** -> Metadata
    - [x] **DELETE** -> None
- [x] **/model/domains/{domainname}/metadata/{id}** -> ModelOnemetadataEndpoint
    - [x] **GET** -> Metadata
    - [x] **DELETE** -> None
    - [x] **PUT** -> Metadata
- [x] **/model/domains/{domainname}/namedentities** -> ModelNamedentitiesEndpoint
    - [x] **GET** -> List[NamedEntity]
    - [x] **POST** -> NamedEntity
    - [x] **DELETE** -> None
- [x] **/model/domains/{domainname}/namedentities/{id}** -> ModelNamedentityEndpoint
    - [x] **GET** -> NamedEntity
    - [x] **DELETE** -> None
    - [x] **PUT** -> NamedEntity
- [x] **/model/domains/{domainname}/objectproperties** -> ModelObjectpropertiesEndpoint
    - [x] **GET** -> List[Overview]
- [x] **/model/domains/{domainname}/regexes** -> ModelRegexesEndpoint
    - [x] **GET** -> List[Regex]
    - [x] **POST** -> Regex
    - [x] **DELETE** -> None
- [x] **/model/domains/{domainname}/regexes/{id}** -> ModelRegexEndpoint
    - [x] **GET** -> Regex
    - [x] **DELETE** -> None
    - [x] **PUT** -> Regex
- [x] **/model/domains/{domainname}/relations** -> ModelRelationsEndpoint
    - [x] **GET** -> List[Relation]
    - [x] **POST** -> Relation
    - [x] **DELETE** -> None
- [x] **/model/domains/{domainname}/relations/{id}** -> ModelRelationEndpoint
    - [x] **GET** -> Relation
    - [x] **DELETE** -> None
    - [x] **PUT** -> Relation
- [x] **/model/domains/{domainname}/rulefunctions** -> ModelRulefunctionsEndpoint
    - [x] **GET** -> List[RuleFunction]
- [x] **/model/domains/{domainname}/rules** -> ModelRulesEndpoint
    - [x] **GET** -> List[RuleOverview]
    - [x] **POST** -> Rule
    - [x] **DELETE** -> None
- [x] **/model/domains/{domainname}/rules/{id}** -> ModelRuleEndpoint
    - [x] **GET** -> Rule
    - [x] **DELETE** -> None
    - [x] **PUT** -> Rule
- [x] **/model/domains/{domainname}/stopwords** -> ModelStopwordsEndpoint
    - [x] **GET** -> List[StopWord]
    - [x] **POST** -> StopWord
    - [x] **DELETE** -> None
- [x] **/model/domains/{domainname}/stopwords/{id}** -> ModelStopwordEndpoint
    - [x] **GET** -> StopWord
    - [x] **DELETE** -> None
    - [x] **PUT** -> StopWord
- [x] **/model/domains/{domainname}/synonyms** -> ModelSynonymsEndpoint
    - [x] **GET** -> List[Synonym]
    - [x] **POST** -> Synonym
    - [x] **DELETE** -> None
- [x] **/model/domains/{domainname}/synonyms/{id}** -> ModelSynonymEndpoint
    - [x] **GET** -> Synonym
    - [x] **DELETE** -> None
    - [x] **PUT** -> Synonym
- [x] **/model/extractortypes** -> ModelExtractortypesEndpoint
    - [x] **GET** -> List[str]
- [x] **/model/metadatatypes** -> ModelMetadatatypesEndpoint
    - [x] **GET** -> List[str]
