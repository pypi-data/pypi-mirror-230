## 普强内部NLP数据存储分享工具


### 安装

- pip install nlp-data

### 使用
- 读取数据
   ```python 
    from nlp_data import NLUDocStore
    # 查看文档
    NLUDocStore.list()
    # 获取文档
    docs = NLUDocStore.pull('xxx')
    # 推送文档
    NLUDocStore.push(docs=docs, name='xxx')
    ```