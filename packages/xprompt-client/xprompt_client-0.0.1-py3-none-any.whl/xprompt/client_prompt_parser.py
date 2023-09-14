from xprompt_common.base_service import BaseService
from xprompt_common.prompt_parser import PromptParser
from xprompt.client_services.dummy_parser import DummyParser

TAG_TO_SERVICE = {
    "dummy": DummyParser,
}

try:
    import importlib.util
    import sys

    name = 'llama_index'

    if name in sys.modules:
        from xprompt.client_services.llamahub_connectors.google_docs import GoogleDoc

        TAG_TO_SERVICE.update({
            "gdoc": GoogleDoc,
        })
except ImportError:
    pass


class ClientPromptParser(PromptParser):
    tag_to_service: dict[str, BaseService.__class__] = TAG_TO_SERVICE
