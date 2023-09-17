# This is the official Superpowered AI Python SDK

## Installation

`pip install superpowered-sdk`

_Note_: To create API keys, please login to the Superpowered AI dashboard and click the "Account" tab on the left navigation.


## Knowledge Base Operations

**Create a knowledge base**

```python
kb = superpowered.create_knowledge_base(
    title='research-biology',
    description='Papers, podcasts, and articles about biology.',  # OPTIONAL
    supp_id='<internal_id>'                                       # OPTIONAL
)
# use kb['id'] when uploading documents for this knowledge base
```


**Get knowledge base(s)**

```python
# list all knowledge bases
kbs = superpowered.list_knowledge_bases()  # returns list of kb objects

# list knowledge bases that meet criteria
kbs = superpowered.list_knowledge_bases(supp_id='<internal_id>')
# OR
kbs = superpowered.list_knowledge_bases(title_begins_with='research-')

# get single knowledge base
kb = superpowered.get_knowledge_base(kb_id)  # returns a single kb object
```


**Delete knowledge base**

```python
ok = superpowered.delete_knowledge_base(kb_id)
```



## Document Operations

**Create Documents**

*NOTE: We currently support `.txt`, `.md`, `.pdf`, `.docx`, `.wav`, `.mp3`, `.m4a` files.*

```python
# create a document via plain text
superpowered.create_document_via_text(
    knowledge_base_id=kb_id,
    content='Observation suggests that people are switching to using ChatGPT '
            'to write things for them with almost indecent haste. Most people '
            'hate to write as much as they hate math. Way more than admit it. '
            'Within a year the median piece of writing could be by AI.',
    title='pg-twitter-20230509',                                                                        # OPTIONAL
    link_to_source='https://twitter.com/paulg/status/1655925905527537666?s=42&t=blTOe1mODRIfVwjJvMJ52w' # OPTIONAL
    description=None,                                                                                   # OPTIONAL
    supp_id='<internal_id>',                                                                            # OPTIONAL
)

# create a document via a url
superpowered.create_document_via_url(
    knowledge_base_id=kb_id,
    url='https://superpoweredai.notion.site/',
    title=None,                                   # OPTIONAL - scraped from HTML <title> tag if not provided
    description='Superpowered AI Documentation',  # OPTIONAL
    supp_id='<internal_id>'                       # OPTIONAL
)

# create a document via file upload
superpowered.create_document_via_file(
    knowledge_base_id=kb_id,
    file_path='/path/to/podcast_audio.mp3',
    description=None,                             # OPTIONAL
    supp_id=None                                  # OPTIONAL
)
```



**Get document(s)**

```python
# list all documents
# NOTE: `content` is not returned with `list_documents()` - only with `get_document()`
docs = superpowered.list_documents()

# list documents with filter
docs = superpowered.list_documents(knowledge_base_id=kb_id, title_begins_with='pg-twitter')
# OR
docs = superpowered.list_documents(knowledge_base_id=kb_id, link_to_source='https://superpoweredai.notion.site/')
# OR
docs = superpowered.list_documents(knowledge_base_id=kb_id, supp_id='<internal_id>')
# OR
docs = superpowered.list_documents(knowledge_base_id=kb_id, vectorization_status='PENDING|IN_PROGRESS|COMPLETE|FAILED')

# get individual document by id
doc = superpowered.get_document(kb_id, doc_id)
```



**Update document**

```python
# valid params: title, supp_id, description
doc = superpowered.update_document(
    knowledge_base_id=kb_id,
    document_id=doc_id,
    title='patched title',                      # OPTIONAL
    supp_id='<internal_id>',                    # OPTIONAL
    description='I am a document about X'       # OPTIONAL
)
```



**Delete document**

```python
ok = superpowered.delete_document(
    knowledge_base_id=kb_id,
    document_id=doc_id
)
```



## Query Operations

**Query knowledge bases**

```python
result = superpowered.query_knowledge_bases(
    knowledge_base_ids=[tweets_kb_id, research_papers_kb_kd, podcasts_kb_id],
    query='What are some of the biggest hurdles we '
          'need to overcome to achieve superintelligence?',
    top_k=10,                                                                   # OPTIONAL
    summarize_results=True                                                      # OPTIONAL
)
```



**Query passages directly without having to create a knowledge base**

This functionality is perfect for web search applications like Google Chrome extensions.

```python
# if passages are longer than `max_chunk_length`, we will chunk the passages to 
# make them more easily parsable by our model
result = superpowered.query_passages(
    query='What technological advancements do need to construct a dyson sphere?',
    passages=[
        '<web page content',
        '<text content>',
        '<etc.>'
    ],
    top_k=10,                       # OPTIONAL
    max_chunk_length=500,           # OPTIONAL
    summarize_results=True          # OPTIONAL
)
```



## Usage Operations

**Get total storage used**

```python
storage_stats = superpowered.get_total_storage()
```