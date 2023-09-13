from .base import BaseDocStore
from ..document import APIDoc, APIDocList

class APIDocStore(BaseDocStore):
    
    bucket_name = 'api'
    
    @classmethod
    def pull(cls, name: str, show_progress: bool = True) -> APIDocList[APIDoc]:
        return APIDocList[APIDoc].pull(url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)
    
    @classmethod
    def push(cls, docs: APIDocList[APIDoc], name: str, show_progress: bool = True) -> None:
        APIDocList[APIDoc].push(docs, url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)