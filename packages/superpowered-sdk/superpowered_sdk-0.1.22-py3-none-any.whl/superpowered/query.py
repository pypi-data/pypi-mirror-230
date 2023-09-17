import warnings

from . import superpowered


def query(knowledge_base_ids: list, query: str, top_k: int = 5, summarize_results: bool = False):
    """
    BACKWARD COMPATIBILITY
    POST /knowledge_bases/query
    """
    class RenameWarning(Warning):
        pass
    
    warnings.warn(
        message="The 'query' function has been renamed to 'query_knowledge_bases' for clarity.",
        category=RenameWarning,
        stacklevel=2
    )
    return query_knowledge_bases(knowledge_base_ids, query, top_k, summarize_results)


def query_knowledge_bases(knowledge_base_ids: list, query: str, top_k: int = 5, summarize_results: bool = False, summary_system_message: str = None, summary_config: dict = {}, exclude_irrelevant_results: bool = True, use_auto_query: bool = False, use_rse: bool = True, segment_length: str = 'medium') -> dict:
    """
    Query one or more knowledge bases.

    Args:
        knowledge_base_ids (list): A list of knowledge base IDs to query.
        query (str): The query string.
        top_k (int, optional): The maximum number of results to return. Defaults to 5.
        summarize_results (bool, optional): Whether to summarize the results. Defaults to False.
        summary_config (dict, optional): A dictionary of summary configuration options. Defaults to {}.
        exclude_irrelevant_results (bool, optional): Whether to exclude irrelevant results. Defaults to True.
        use_auto_query (bool, optional): Whether to use the auto query feature. Defaults to False.
        use_rse (bool, optional): Whether to use the RSE feature. Defaults to False.
        segment_length (str, optional): Ignored if `use_rse` is False. The length of the segments to use. Defaults to 'medium'. Must be one of 'very_short', 'short', 'medium', or 'long'.

    Note:
        The ``summary_config`` dictionary will look as follows:
        
        .. code-block:: python

            {
                'system_message': 'string',  # a system message to guide the LLM summary.
                'include_references': True,  # whether to include references/citations in the summary itself.
            }

    Returns:
        dict: A query response object.

    Note:
        The returned object will look as follows:
        
        .. code-block:: python

            {
                'ranked_results': [
                    {
                        'cosine_similarity': 0.0,  # the cosine similarity score
                        'reranker_score': 0.0,  # the relevance score
                        'metadata': {
                            'content': 'content of the chunk,
                            'original_content': 'content of the chunk before prepending chunk headers',
                            'knowledge_base_id': 'uuid',
                            'document_id': 'uuid',
                            'account_id': 'uuid',
                            'document': {}  # document object
                        },  # a dictionary of metadata
                        'content': 'string',  # the text of the chunk
                    }
                ],
                'summary': 'string',  # the summary text
                'search_queries': [{'knowledge_base': {}, 'query': 'string'}],
            }

    References:
        ``POST /knowledge_bases/query``
    """
    data = {
        'query': query,
        'knowledge_base_ids': knowledge_base_ids,
        'summary_config': summary_config or {},
    }

    if top_k:
        data['top_k'] = top_k
    if summarize_results is not None:
        data['summarize_results'] = summarize_results
    if exclude_irrelevant_results is not None:
        data['exclude_irrelevant_results'] = exclude_irrelevant_results
    if use_auto_query is not None:
        data['use_auto_query'] = use_auto_query
    if use_rse is not None:
        data['use_rse'] = use_rse
    if segment_length is not None:
        data['segment_length'] = segment_length
    # handle the deprecated summary_system_message argument
    if summary_system_message and not data['summary_config'].get('system_message'):
        data['summary_config']['system_message'] = summary_system_message
    args = {
        'method': 'POST',
        'url': f'{superpowered.get_base_url()}/knowledge_bases/query',
        'json': data,
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)
