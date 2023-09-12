import base64
import hashlib
import os
import requests

from . import superpowered


def create_document_via_text(knowledge_base_id: str, content: str, title: str = None, link_to_source: str = None, description: str = None, supp_id: str = None, chunk_header: str = None) -> dict:
    """
    Create a document in a knowledge base with raw text. For example, if you are adding Tweets to a knowledge base, you can just pass the text of the Tweet to this method.
    
    Args:
        knowledge_base_id (str): The ID of the knowledge base.
        content (str): The content of the document.
        title (str, optional): The title of the document. Defaults to None.
        link_to_source (str, optional): A link to the source of the document. Defaults to None.
        description (str, optional): The description of the document. Defaults to None.
        supp_id (str, optional): The ID of the document in your system. Defaults to None.
        chunk_header (str, optional): This is used to prepend context to every chunk created from this document. Defaults to None.
    
    Returns:
        dict: The document object.

    References:
        ``POST /knowledge_bases/{knowledge_base_id}/documents/raw_text``
    """
    data = {
        'content': content,
    }
    if title:
        data['title'] = title
    if description:
        data['description'] = description
    if supp_id:
        data['supp_id'] = supp_id
    if link_to_source:
        data['link_to_source'] = link_to_source
    if chunk_header:
        data['chunk_header'] = chunk_header
    args = {
        'method': 'POST',
        'url': f'{superpowered.get_base_url()}/knowledge_bases/{knowledge_base_id}/documents/raw_text',
        'json': data,
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)


def create_document_via_url(knowledge_base_id: str, url: str, title: str = None, description: str = None, supp_id: str = None, chunk_header: str = None) -> dict:
    """
    Create a document in a knowledge base with a URL. The URL must be publicly accessible. We will scrape the website asynchronously and add the content to the document returned by this function.

    Note:
        This can also be used to create documents from files (.pdf, .docx, .txt). Just pass the URL of the file.

    Args:
        knowledge_base_id (str): The ID of the knowledge base.
        url (str): The URL of the website or file.
        title (str, optional): The title of the document. Defaults to None.
        description (str, optional): The description of the document. Defaults to None.
        supp_id (str, optional): The ID of the document in your system. Defaults to None.
        chunk_header (str, optional): This is used to prepend context to every chunk created from this document. Defaults to None.

    Returns:
        dict: The document object.
        
    References:
        ``POST /knowledge_bases/{knowledge_base_id}/documents/url``
    """
    data = {
        'url': url,
    }
    if title:
        data['title'] = title
    if description:
        data['description'] = description
    if supp_id:
        data['supp_id'] = supp_id
    if chunk_header:
        data['chunk_header'] = chunk_header
    args = {
        'method': 'POST',
        'url': f'{superpowered.get_base_url()}/knowledge_bases/{knowledge_base_id}/documents/url',
        'json': data,
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)


def create_document_via_file(knowledge_base_id: str, file_path: str, description: str = None, supp_id: str = None, chunk_header: str = None) -> dict:
    """
    Create a document in a knowledge base with a local file.

    Note:
        Accepted file types are:
            - .pdf
            - .docx
            - .txt
            - .md
            - .epub
            - .wav
            - .mp3
            - .m4a

        Any audio files will be automatically transcribed with a Whisper model before chunking.
    
    Args:
        knowledge_base_id (str): The ID of the knowledge base.
        file_path (str): The path to the file.
        description (str, optional): The description of the document. Defaults to None.
        supp_id (str, optional): The ID of the document in your system. Defaults to None.
        chunk_header (str, optional): This is used to prepend context to every chunk created from this document. Defaults to None.

    Returns:
        dict: The document object.
    
    References:
        ``POST /knowledge_bases/{knowledge_base_id}/documents/request_signed_file_url``
        +
        ``PUT response['temporary_url']``
    """
    # read the file and get the encoded md5 for the presigned url request
    with open(file_path, 'rb') as f:
        file_content = f.read()
        file_md5 = hashlib.md5(file_content).hexdigest()
        encoded_md5 = base64.b64encode(bytes.fromhex(file_md5)).decode('utf-8')

    # make the request for the presigned url
    data = {
        'filename': os.path.basename(file_path),
        'method': 'PUT',
        'encoded_md5': encoded_md5,
    }
    if description:
        data['description'] = description
    if supp_id:
        data['supp_id'] = supp_id
    if chunk_header:
        data['chunk_header'] = chunk_header

    args = {
        'method': 'POST',
        'url': f'{superpowered.get_base_url()}/knowledge_bases/{knowledge_base_id}/documents/request_signed_file_url',
        'json': data,
        'auth': superpowered.auth(),
    }
    resp = superpowered.make_api_call(args)

    # upload the file to the presigned url
    headers = {
        'Content-MD5': encoded_md5,
    }
    args = {
        'url': resp['temporary_url'],
        'data': file_content,
        'headers': headers,
    }
    with requests.put(**args) as r:
        pass

    return resp['document']


def update_file(knowledge_base_id: str, document_id: str, new_file_path: str):
    """
    Update an existing knowledge base file.

    Note:
        The ``document.file_name`` field is immutable. It is generally recommended that you use the same file extension as the original file in ``new_file_path``.

    Args:
        knowledge_base_id (str): The ID of the knowledge base.
        document_id (str): The ID of the document.
        new_file_path (str): The path to the new file.

    Returns:
        dict: The document object associated with the updated file.

    References:
        ``POST /knowledge_bases/{knowledge_base_id}/documents/request_signed_file_url``
        +
        ``PUT response['temporary_url']``
    """
    # read the file and get the encoded md5 for the presigned url request
    with open(new_file_path, 'rb') as f:
        file_content = f.read()
        file_md5 = hashlib.md5(file_content).hexdigest()
        encoded_md5 = base64.b64encode(bytes.fromhex(file_md5)).decode('utf-8')

    # get the document object
    document = get_document(knowledge_base_id, document_id)
    if document.get('document_type') != 'file' or not document.get('file_name'):
        raise ValueError(f'The document with ID {document_id} does not have a file associated with it.')

    file_name = document['file_name']

    # make the request for the presigned url
    data = {
        'filename': file_name,
        'method': 'PUT',
        'encoded_md5': encoded_md5,
        'is_update': True
    }
    args = {
        'method': 'POST',
        'url': f'{superpowered.get_base_url()}/knowledge_bases/{knowledge_base_id}/documents/request_signed_file_url',
        'json': data,
        'auth': superpowered.auth(),
    }
    resp = superpowered.make_api_call(args)

    # upload the file to the presigned url
    headers = {
        'Content-MD5': encoded_md5,
    }
    args = {
        'url': resp['temporary_url'],
        'data': file_content,
        'headers': headers,
    }
    with requests.put(**args) as r:
        pass

    return resp['document']


def download_file(knowledge_base_id: str, document_id: str, destination_path: str = None) -> bytes:
    """
    Download a file from a knowledge base for the given document.

    Args:
        knowledge_base_id (str): The ID of the knowledge base.
        document_id (str): The ID of the document.
        destination_path (str, optional): The path to save the file to. Defaults to None.

    Returns:
        bytes: The file content.

    References:
        ``POST /knowledge_bases/{knowledge_base_id}/documents/request_signed_file_url``
        +
        ``GET response['temporary_url']``
    """
    # get the document object
    document = get_document(knowledge_base_id, document_id)
    if document.get('document_type') != 'file' or not document.get('file_name'):
        raise ValueError(f'The document with ID {document_id} does not have a file associated with it.')

    file_name = document['file_name']

    # make the request for the presigned url
    data = {
        'filename': file_name,
        'method': 'GET',
    }
    args = {
        'method': 'POST',
        'url': f'{superpowered.get_base_url()}/knowledge_bases/{knowledge_base_id}/documents/request_signed_file_url',
        'json': data,
        'auth': superpowered.auth(),
    }
    resp = superpowered.make_api_call(args)
    download_url = resp['temporary_url']

    # download the file from the presigned url
    file = requests.get(download_url).content

    # save the file to the destination path if provided
    # make the file path if it doesn't exist
    if destination_path:
        os.makedirs(os.path.dirname(destination_path), exist_ok=True)
        with open(destination_path, 'wb') as f:
            f.write(file)

    return file


def list_documents(knowledge_base_id: str, title_begins_with: str = None, link_to_source: str = None, supp_id: str = None, vectorization_status: str = None) -> list:
    """
    List the documents in a knowledge base.

    Args:
        knowledge_base_id (str): The ID of the knowledge base.
        title_begins_with (str, optional): A title prefix filter. Defaults to None.
        link_to_source (str, optional): Filter documents by their URL. Defaults to None.
        supp_id (str, optional): Filter documents by ``supp_id``. Defaults to None.

    Returns:
        list: A list of document objects.

    References:
        ``GET /knowledge_bases/{knowledge_base_id}/documents``
    """
    params = {}
    if title_begins_with:
        params['title_begins_with'] = title_begins_with
    if supp_id:
        params['supp_id'] = supp_id
    if vectorization_status:
        params['status'] = vectorization_status
    if link_to_source:
        params['link_to_source'] = link_to_source

    args = {
        'method': 'GET',
        'url': f'{superpowered.get_base_url()}/knowledge_bases/{knowledge_base_id}/documents',
        'params': params,
        'auth': superpowered.auth(),
    }
    resp = superpowered.make_api_call(args)
    documents = resp.get('documents', [])
    while resp.get('next_page_token'):
        args['params']['next_page_token'] = resp['next_page_token']
        resp = superpowered.make_api_call(args)
        documents.extend(resp.get('documents', []))

    return documents


def get_document(knowledge_base_id: str, document_id: str, include_content: bool = True) -> dict:
    """
    Get an individual document from a knowledge base.

    Args:
        knowledge_base_id (str): The ID of the knowledge base.
        document_id (str): The ID of the document.
        include_content (bool, optional): Whether to include the document content in the response. If you don't plan on displaying the content, setting this parameter to ``False`` could improve latency for large documents. Defaults to True.

    Returns:
        dict: A document object.

    References:
        ``GET /knowledge_bases/{knowledge_base_id}/documents/{document_id}``
    """
    params = {
        'include_content': include_content,
    }
    args = {
        'method': 'GET',
        'url': f'{superpowered.get_base_url()}/knowledge_bases/{knowledge_base_id}/documents/{document_id}',
        'auth': superpowered.auth(),
        'params': params,
    }
    return superpowered.make_api_call(args)


def update_document(knowledge_base_id: str, document_id: str, title: str = None, description: str = None, supp_id: str = None) -> dict:
    """
    Update a document in a knowledge base.

    Args:
        knowledge_base_id (str): The ID of the knowledge base.
        document_id (str): The ID of the document.
        title (str, optional): The title of the document. Defaults to None.
        description (str, optional): The description of the document. Defaults to None.
        supp_id (str, optional): The ``supp_id`` of the document. Defaults to None.

    Returns:
        dict: A document object.

    References:
        ``PATCH /knowledge_bases/{knowledge_base_id}/documents/{document_id}``
    """
    data = {}
    if title:
        data['title'] = title
    if description:
        data['description'] = description
    if supp_id:
        data['supp_id'] = supp_id
    args = {
        'method': 'PATCH',
        'url': f'{superpowered.get_base_url()}/knowledge_bases/{knowledge_base_id}/documents/{document_id}',
        'json': data,
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)


def delete_document(knowledge_base_id: str, document_id: str) -> bool:
    """
    Delete a document from a knowledge base.

    Args:
        knowledge_base_id (str): The ID of the knowledge base.
        document_id (str): The ID of the document.

    Returns:
        bool: Whether the document was successfully deleted.

    References:
        DELETE /knowledge_bases/{knowledge_base_id}/documents/{document_id}
    """
    args = {
        'method': 'DELETE',
        'url': f'{superpowered.get_base_url()}/knowledge_bases/{knowledge_base_id}/documents/{document_id}',
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)
