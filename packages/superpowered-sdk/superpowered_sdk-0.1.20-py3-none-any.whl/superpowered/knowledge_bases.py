
from . import superpowered


def create_knowledge_base(title: str, description: str = None, supp_id: str = None, language_code: str = None) -> dict:
    """
    Create a knowledge base.

    Args:
        title (str): The title of the knowledge base.
        description (str, optional): The description of the knowledge base. Defaults to None.
        supp_id (str, optional): A supplemental ID for the knowledge base for internal use. Defaults to None.
        language_code (str, optional): The language code of the knowledge base. Defaults to 'en'.

    Returns:
        dict: The knowledge base object.

    Note:
        The ``title`` and ``description`` fields are important for "Auto Query", which is used to automatically generate search queries for particular knowledge bases based on the user's input.

    References:
        ``POST /knowledge_bases``
    """
    data = {
        'title': title,
    }
    if description:
        data['description'] = description
    if supp_id:
        data['supp_id'] = supp_id
    if language_code:
        data['language_code'] = language_code
    args = {
        'method': 'POST',
        'url': f'{superpowered.get_base_url()}/knowledge_bases',
        'json': data,
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)


def update_knowledge_base(knowledge_base_id: str, title: str = None, description: str = None, supp_id: str = None, language_code: str = None) -> dict:
    """
    Update a knowledge base object.

    Args:
        knowledge_base_id (str): The ID of the knowledge base.
        title (str, optional): The title of the knowledge base. Defaults to None.
        description (str, optional): The description of the knowledge base. Defaults to None.
        supp_id (str, optional): The ID of the knowledge base in your system. Defaults to None.
        language_code (str, optional): The language code of the knowledge base. Defaults to None.

    Returns:
        dict: The knowledge base object.

    References:
        ``PATCH /knowledge_bases/{knowledge_base_id}``
    """
    data = {}
    if title:
        data['title'] = title
    if description:
        data['description'] = description
    if supp_id:
        data['supp_id'] = supp_id
    if language_code:
        data['language_code'] = language_code
    args = {
        'method': 'PATCH',
        'url': f'{superpowered.get_base_url()}/knowledge_bases/{knowledge_base_id}',
        'json': data,
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)


def list_knowledge_bases(title: str = None, supp_id: str = None) -> list:
    """
    List all knowledge bases.

    Args:
        title (str, optional): The title of the knowledge base. Defaults to None.
        supp_id (str, optional): The ID of the knowledge base in your system. Defaults to None.

    Returns:
        list: A list of knowledge base objects that match the filter criteria.

    Note:
        You can use ``title`` as a prefix to filter your search. For example, if you have a knowledge base titled "FAQ", you can use ``title="F"`` to find it.

    References:
        ``GET /knowledge_bases``
    """
    params = {}
    if title:
        params['title_begins_with'] = title
    if supp_id:
        params['supp_id'] = supp_id

    args = {
        'method': 'GET',
        'url': f'{superpowered.get_base_url()}/knowledge_bases',
        'params': params,
        'auth': superpowered.auth(),
    }
    resp = superpowered.make_api_call(args)
    knowledge_bases = resp.get('knowledge_bases', [])

    while resp.get('next_page_token'):
        args['params']['next_page_token'] = resp['next_page_token']
        resp = superpowered.make_api_call(args)
        knowledge_bases.extend(resp.get('knowledge_bases', []))

    return knowledge_bases


def get_knowledge_base(knowledge_base_id: str) -> dict:
    """
    Get an individual knowledge base by it's ID.

    Args:
        knowledge_base_id (str): The ID of the knowledge base.

    Returns:
        dict: The knowledge base object.
    
    References:
       ``GET /knowledge_bases/{knowledge_base_id}``
    """
    args = {
        'method': 'GET',
        'url': f'{superpowered.get_base_url()}/knowledge_bases/{knowledge_base_id}',
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)


def delete_knowledge_base(knowledge_base_id: str) -> bool:
    """
    Delete a knowledge base by it's ID.

    Args:
        knowledge_base_id (str): The ID of the knowledge base.

    Returns:
        bool: True if the knowledge base was deleted successfully, False otherwise.

    References:
        ``DELETE /knowledge_bases/{knowledge_base_id}``
    """
    args = {
        'method': 'DELETE',
        'url': f'{superpowered.get_base_url()}/knowledge_bases/{knowledge_base_id}',
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)
