from enum import Enum
import openai
import os
from ..document import NLUDocList, NLUDoc, APIDocList, APIDoc, DialogueDoc, DialogueDocList, APIParam
from ..document.dialogue import Message
from pydantic import validate_arguments
from tqdm import tqdm, trange
from wasabi import msg


class Localism(str, Enum):
    """方言
    """
    guangdong: str = '广东话'
    sichuan: str = '四川话'
    
    
class GPTAugmentor:
    """基于ChatGPT的数据增强器
    """
    def __init__(self, 
                 api_key: str = None,
                 model: str = 'gpt-3.5-turbo',
                 api_base: str = 'https://record.pachira.cn/v1'):
        
        api_key = api_key or os.environ.get('OPENAI_API_KEY')
        if not api_key:
            raise ValueError('请设置OPENAI_API_KEY环境变量')
        openai.api_key = api_key
        openai.api_base = api_base
        self.chat_model = model
        
    @validate_arguments
    def get_chatgpt_response(self, query: str, system: str = None):
        messages = [{"role": "user", "content": query}]
        if system:
            messages = [{"role": "system", "content": system}] + messages
            
        chat_completion = openai.ChatCompletion.create(model=self.chat_model, messages=messages)
        return chat_completion.choices[0].message.content

    @validate_arguments
    def augment_nlu_by_localism(self, docs: NLUDocList,  localism: Localism = Localism.guangdong):
        """利用chatgpt数据增强不同方言的表述

        Args:
            docs (NLUDocList): 原始文档,如果doc.abnf_output为None,则不会增强.
            localism (Localism, optional): 方言. Defaults to Localism.guangdong.

        Returns:
            Tuple[NLUDocList, NLUDocList] : 增强后的文档和增强失败的文档
        """
        prompt = "将下面的标注文本转换为{}方言表述形式,要求保留标注符号.文本:".format(localism.value)
        new_docs = NLUDocList[NLUDoc]()
        fail_docs = NLUDocList[NLUDoc]()
        for doc in tqdm(docs):
            doc: NLUDoc
            try:
                query = prompt + "\n{}".format(doc.abnf_output)
                response = self.get_chatgpt_response(query=query)
                new_docs.append(NLUDoc.from_abnf_output_line(line=response, domain=doc.domain.text, intention=doc.intention.text))
            except:
                msg.fail(f'augment doc {doc.id} fail')
                fail_docs.append(doc)
        return new_docs, fail_docs
    
    @validate_arguments
    def complete_api_docs(self, docs: APIDocList, max_retry: int = 5):
        """补充API文档的描述

        Args:
            docs (APIDocList): API文档列表

        Returns:
            _type_: APIDocList
        """
        complete_docs = APIDocList[APIDoc]()
        for doc in tqdm(docs):
            retry = 0
            while retry < max_retry:
                try:
                    if not doc.description or doc.description == 'nan' or doc.description == 'None' or doc.description == 'none':
                        prompt = "API名称:{},API参数:{}, 请根据上面的信息给出API的描述,只返回描述:\n\n".format(doc.name, doc.params.name)
                        description = self.get_chatgpt_response(prompt).strip()
                        new_doc = APIDoc(name=doc.name, description=description)
                    else:
                        new_doc = doc.copy()
                    for param in doc.params:
                        if not param.description or param.description == 'nan' or param.description == 'None' or param.description == 'none':
                            prompt = "{}是API{}的参数名称,API{}的描述如下:{} 给出{}参数描述,要求1.要求参数的描述尽可能简洁. 2.要求要举例说明参数. 3.要求只返回该参数的描述:\n\n".format(param.name, doc.name, doc.name, doc.description, param.name)
                            param_description = self.get_chatgpt_response(prompt).strip()
                            param = APIParam(name=param.name, description=param_description, type=param.type, required=param.required)
                            new_doc.params.append(param)
                        else:
                            new_doc.params.append(param.copy())
                            
                    complete_docs.append(new_doc)
                    retry = max_retry
                except:
                    msg.fail(f'complete doc {doc.id} fail')
                    retry += 1
        return complete_docs
    
    
    # 基于gpt生成多轮对话数据
    def generate_dialogue_docs(self, theme: str, situation: str, num_docs: int = 5, max_retry: int = 5):
        """跟定一个主题,生成多轮对话数据

        Args:
            theme (str): 对话主题.
            num_docs (int, optional): 生成的文档数. Defaults to 5.
        """
        docs = DialogueDocList[DialogueDoc]()
        for j in trange(num_docs):
            retry = 0
            while retry < max_retry:
                try:
                    prompt = f"帮我生成一个在{situation}情景下,关于{theme}的多轮对话, 仅用以下格式返回: User: xxx, Bot: xxx"
                    response = self.get_chatgpt_response(prompt)
                    doc = DialogueDoc()
                    doc.theme = theme
                    doc.situation = situation
                    turns = []
                    for turn in response.split('\n'):
                        if len(turn) > 0:
                            turns.append(turn)
                    assert len(turns) % 2 == 0
                    for i in range(0, len(turns), 2):
                        assert turns[i].startswith('User:')
                        assert turns[i+1].startswith('Bot:')
                        message = Message(role='user', content=turns[i][5:])
                        doc.conversation.append(message)
                        message = Message(role='assistant', content=turns[i+1][5:])
                        doc.conversation.append(message)
                    docs.append(doc)
                    retry = max_retry
                except:
                    retry += 1
                    msg.fail(f'generate doc {j} fail. retry {retry}')
                
        return docs