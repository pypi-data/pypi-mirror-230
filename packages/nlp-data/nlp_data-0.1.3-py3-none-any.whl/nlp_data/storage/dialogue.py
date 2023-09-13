from ..document import DialogueDoc, DialogueDocList
from .base import BaseDocStore


class DialogueDocStore(BaseDocStore):
    
    bucket_name = 'dialogue'
    
    @classmethod
    def pull(cls, name: str, show_progress: bool = True) -> DialogueDocList[DialogueDoc]:
        return DialogueDocList[DialogueDoc].pull(url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)
    
    @classmethod
    def push(cls, docs: DialogueDocList[DialogueDoc], name: str, show_progress: bool = True) -> None:
        DialogueDocList[DialogueDoc].push(docs, url=f's3://{cls.bucket_name}/{name}', show_progress=show_progress)