import json


class XPromptOutput(dict):
    def __str__(self):
        obj = dict(self)
        return json.dumps(obj, indent=2)
