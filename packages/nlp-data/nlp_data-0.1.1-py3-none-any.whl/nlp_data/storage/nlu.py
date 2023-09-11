from ..document import NLUDoc, NLUDocList
from .base import BaseDocStore


class NLUDocStore(BaseDocStore):
    bucket_name = 'nlu'
    
    @classmethod
    def pull(cls, name: str, show_progress: bool = True) -> NLUDocList[NLUDoc]:
        return NLUDocList[NLUDoc].pull(url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)
    
    @classmethod
    def push(cls, docs: NLUDocList[NLUDoc], name: str, show_progress: bool = True) -> None:
        NLUDocList[NLUDoc].push(docs, url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)