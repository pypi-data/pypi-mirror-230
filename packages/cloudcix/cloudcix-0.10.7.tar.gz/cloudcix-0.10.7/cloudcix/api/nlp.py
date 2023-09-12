from cloudcix.client import Client


class NLP:
    """
    The NLP Application is a software system that manages CloudCIX Natural Language Processing services.
    """
    _application_name = 'nlp'

    embedding = Client(
        _application_name,
        'embedding/',
    )
