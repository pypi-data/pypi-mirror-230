from xprompt_common.base_service import BaseService


class DummyParser(BaseService):
    val: str = ""

    def run(self) -> str:
        return self.val
