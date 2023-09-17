from . import superpowered


def create_chat_thread(knowledge_base_ids: list[str] = None, supp_id: str = None, model: str = None, temperature: float = None, segment_length: str = None, system_message: str = None, title: str = None, use_rse: bool = True) -> dict:
    """
    Create a chat thread. Chat threads are used to store the state of a conversation.

    Args:
        knowledge_base_ids (list[str], optional): A list of knowledge base IDs to use for the thread. Defaults to None.
        supp_id (str, optional): A supp ID to use for the thread. Defaults to None.
        model (str, optional): The model to use for the thread. Defaults to None.
        temperature (float, optional): The temperature to use for the thread. Defaults to None.
        system_message (str, optional): The system message to use for the thread. Defaults to None.
        title (str, optional): The title to use for the thread. Defaults to None.
        use_rse (bool, optional): Whether or not to use Relevant Segment Extraction (RSE). Defaults to True.
        segment_length (str, optional): The segment length to use for the thread. Ignored if `use_rse` is False. Defaults to None.

    Note:
        All parameters besides ``supp_id`` are the thread's default options. These options can be overridden when using the ``get_chat_response()`` function.

    Returns:
        dict: A chat thread object.

    References:
        ``POST /chat/threads``
    """
    data = {
        'default_options': {}
    }
    if supp_id:
        data['supp_id'] = supp_id
    if title:
        data['title'] = title
    if knowledge_base_ids:
        data['default_options']['knowledge_base_ids'] = knowledge_base_ids
    if model:
        data['default_options']['model'] = model
    if temperature:
        data['default_options']['temperature'] = temperature
    if segment_length:
        data['default_options']['segment_length'] = segment_length
    if system_message:
        data['default_options']['system_message'] = system_message
    if use_rse is not None:
        data['default_options']['use_rse'] = use_rse
    args = {
        'method': 'POST',
        'url': f'{superpowered.get_base_url()}/chat/threads',
        'json': data,
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)


def list_chat_threads(supp_id: str = None) -> dict:
    """
    List chat threads.

    Args:
        supp_id (str, optional): The supp_id of the thread. Defaults to None.

    Returns:
        dict: A list of chat thread objects.
    
    References:
        ``GET /chat/threads``
    """
    params = {}
    if supp_id:
        params['supp_id'] = supp_id

    args = {
        'method': 'GET',
        'url': f'{superpowered.get_base_url()}/chat/threads',
        'auth': superpowered.auth(),
        'params': params,
    }
    resp = superpowered.make_api_call(args)
    threads = resp.get('chat_threads', [])

    while resp.get('next_page_token'):
        args['params']['next_page_token'] = resp['next_page_token']
        resp = superpowered.make_api_call(args)
        threads.extend(resp.get('chat_threads', []))

    return threads


def get_chat_thread(thread_id: str) -> dict:
    """
    Get a chat thread.

    Args:
        thread_id (str): The ID of the thread.

    Returns:
        dict: A chat thread object.

    References:
        ``GET /chat/threads/{thread_id}``
    """
    args = {
        'method': 'GET',
        'url': f'{superpowered.get_base_url()}/chat/threads/{thread_id}',
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)


def update_chat_thread(thread_id: str, knowledge_base_ids: list[str] = None, supp_id: str = None, model: str = None, temperature: float = None, segment_length: str = None, system_message: str = None, title: str = None, use_rse: bool = None) -> dict:
    """
    Update a chat thread.

    Args:
        thread_id (str): The ID of the thread.
        knowledge_base_ids (list[str], optional): A list of knowledge base IDs to use for the thread. Defaults to None.
        supp_id (str, optional): A supp ID to use for the thread. Defaults to None.
        model (str, optional): The model to use for the thread. Defaults to None.
        temperature (float, optional): The temperature to use for the thread. Defaults to None.
        system_message (str, optional): The system message to use for the thread. Defaults to None.
        title (str, optional): The title to use for the thread. Defaults to None.
        use_rse (bool, optional): Whether or not to use Relevant Segment Extraction (RSE). Defaults to None.
        segment_length (str, optional): The segment length to use for the thread. Ignored if `use_rse` is False. Defaults to None.

    Returns:
        dict: A chat thread object.

    References:
        ``PATCH /chat/threads/{thread_id}``
    """
    data = {
        'default_options': {}
    }
    default_options = {}
    if supp_id:
        data['supp_id'] = supp_id
    if title:
        data['title'] = title
    if knowledge_base_ids:
        default_options['knowledge_base_ids'] = knowledge_base_ids
    if model:
        default_options['model'] = model
    if temperature:
        default_options['temperature'] = temperature
    if segment_length:
        default_options['segment_length'] = segment_length
    if system_message:
        default_options['system_message'] = system_message
    if use_rse is not None:
        default_options['use_rse'] = use_rse

    if default_options:
        data['default_options'] = default_options

    args = {
        'method': 'PATCH',
        'url': f'{superpowered.get_base_url()}/chat/threads/{thread_id}',
        'json': data,
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)


def delete_chat_thread(thread_id: str) -> dict:
    """
    Delete a chat thread.

    Args:
        thread_id (str): The ID of the thread.

    Returns:
        dict: A chat thread object.

    References:
        ``DELETE /chat/threads/{thread_id}``
    """
    args = {
        'method': 'DELETE',
        'url': f'{superpowered.get_base_url()}/chat/threads/{thread_id}',
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)


def get_chat_response(thread_id: str, input: str, knowledge_base_ids: list = None, model: str = None, temperature: float = None, system_message: str = None, use_rse: bool = None, segment_length: str = None) -> dict:
    """
    Get a response for a specific chat thread. This endpoint uses a tool we call "Auto Query" to reformulate queries to the knowledge base given the recent chat history as well as user input.

    Note:
        To ensure "Auto Query" works as well as it can, please ensure the knowledge bases you are using have good titles and descriptions. If you are only querying from a single knowledge base, this doesn't matter.

    Args:
        thread_id (str): The ID of the thread.
        input (str): The user's input.
        knowledge_base_ids (list, optional): A list of knowledge base IDs to use for the thread. **These override any default config options defined in the thread itself**. Defaults to None.
        model (str, optional): The model to use for the thread. **This overrides any default config options defined in the thread itself**. Defaults to None.
        temperature (float, optional): The temperature to use for the thread. **This overrides any default config options defined in the thread itself**. Defaults to None.
        system_message (str, optional): The system message to use for the thread. **This overrides any default config options defined in the thread itself**. Defaults to None.
        use_rse (bool, optional): Whether or not to use Relevant Segment Extraction (RSE). **This overrides any default config options defined in the thread itself**. Defaults to None.
        segment_length (str, optional): The segment length to use for the thread. **This overrides any default config options defined in the thread itself**. Defaults to None.

    Returns:
        dict: A chat response object.

    References:
        ``POST /chat/threads/{thread_id}/get_response``
    """
    data = {
        'input': input,
    }
    if knowledge_base_ids:
        data['knowledge_base_ids'] = knowledge_base_ids
    if model:
        data['model'] = model
    if temperature:
        data['temperature'] = temperature
    if system_message:
        data['system_message'] = system_message
    if use_rse is not None:
        data['use_rse'] = use_rse
    if segment_length:
        data['segment_length'] = segment_length
    args = {
        'method': 'POST',
        'url': f'{superpowered.get_base_url()}/chat/threads/{thread_id}/get_response',
        'json': data,
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)


def list_thread_interactions(thread_id: str, order: str = None) -> dict:
    """
    List interactions for a chat thread.

    Args:
        thread_id (str): The ID of the thread.
        order (str, optional): The order to return the interactions in. Must be `asc` or `desc`. Defaults to `desc`.

    Returns:
        dict: A list of chat interaction objects.

    References:
        ``GET /chat/threads/{thread_id}/interactions``
    """
    params = {}
    if order:
        if order.lower() not in ['asc', 'desc']:
            raise ValueError('`order` parameter must be "asc" or "desc"')
        params['order'] = order.lower()

    args = {
        'method': 'GET',
        'url': f'{superpowered.get_base_url()}/chat/threads/{thread_id}/interactions',
        'auth': superpowered.auth(),
        'params': params,
    }
    resp = superpowered.make_api_call(args)
    interactions = resp.get('interactions', [])

    while resp.get('next_page_token'):
        args['params']['next_page_token'] = resp['next_page_token']
        resp = superpowered.make_api_call(args)
        interactions.extend(resp.get('interactions', []))

    return interactions
