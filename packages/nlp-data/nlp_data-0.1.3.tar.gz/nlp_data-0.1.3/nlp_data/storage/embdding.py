from ..document import EmbeddingDocList, EmbeddingDoc
from .base import BaseDocStore

class EmbeddingDocStore(BaseDocStore):
    
    bucket_name = 'embedding'
    
    @classmethod
    def pull(cls, name: str, show_progress: bool = True) -> EmbeddingDocList[EmbeddingDoc]:
        return EmbeddingDocList[EmbeddingDoc].pull(url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)
    
    @classmethod
    def push(cls, docs: EmbeddingDocList[EmbeddingDoc], name: str, show_progress: bool = True) -> None:
        EmbeddingDocList[EmbeddingDoc].push(docs, url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)