from . import superpowered

def get_total_storage():
    """
    Get the total account storage in bytes, tokens, and percent of free-tier used.

    References:
        ``GET /usage/total_storage``
    """
    args = {
        'method': 'GET',
        'url': f'{superpowered.get_base_url()}/usage/total_storage',
        'auth': superpowered.auth(),
    }
    return superpowered.make_api_call(args)