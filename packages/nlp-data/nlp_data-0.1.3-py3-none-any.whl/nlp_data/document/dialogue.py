from docarray import BaseDoc, DocList
from typing import Optional, Literal
import srsly



class Message(BaseDoc):
    role: Literal['user', 'assistant']
    content: str
    
    
class DialogueDoc(BaseDoc):
    """存放openai格式的对话历史
    """
    system: Optional[str] = None
    conversation: DocList[Message] = DocList[Message]()
    theme: Optional[str] = None
    situation: Optional[str] = None
        
    
    
    
class DialogueDocList(DocList[DialogueDoc]):
    
    @classmethod
    def from_instruction_jsonl(cls, jsonl_path: str) -> DocList[DialogueDoc]:
        """json格式需要为instruction, input, output, history
        注意:
        - history的格式应为[{'role': 'user', 'content': 'hello'}, {'role': 'assistant', 'content': 'hello'}].
        - role只能为user或者assistant.
        """
        docs = DialogueDocList[DialogueDoc]()
        for line in srsly.read_jsonl(jsonl_path):
            doc = DialogueDoc(system=line['instruction'])
            if line['history']:
                for his in line['history']:
                    doc.conversation.append(Message(role=his['role'], content=his['content']))
                
            input_message = Message(role='user', content=line['input'])
            output_message = Message(role='assistant', content=str(line['output']))
            doc.conversation.append(input_message)
            doc.conversation.append(output_message)
            docs.append(doc)
        return docs
            
                