## 普强内部NLP数据存储分享工具


### 安装

- pip install nlp-data

### 使用
- **Store**的使用
   ```python 
    # Store相当于是S3对象存储的一个Bucket的封装,每个数据类型对应一个Bucket
    from nlp_data import NLUDocStore
    # 查看文档
    NLUDocStore.list()
    # 获取文档
    docs = NLUDocStore.pull('xxx')
    # 推送文档
    NLUDocStore.push(docs=docs, name='xxx')
    ```

- **Doc**的使用
  ```python
      # Doc是nlp-data的一个存储结构,可以用来存储该格式的数据,以及对数据进行一些操作
      # DocList是Doc的集合,可以用来存储多个Doc,相当于一个python List,有几本的append,extend等类方法, 但不同的DocList有特定的方法用来处理# 该数据类型
      # 以NLUDoc为例,该文档里面有domain,slots,intention等字段,可以用来存储NLU的结果
      from nlp_data import NLUDoc, NLUDocList
      # 创建一个NLUDoc
      doc = NLUDoc(text='添加明天上午跟张三开会的提醒')
      doc.set_domain('schedule_cmn')
      doc.set_intention('add_schedule')
      doc.set_slot(text='明天上午', label='date')
      doc.set_slot(text='跟张三开会', label='title')
      # 创建一个NLUDocList,并添加doc
      docs = NLUDocList()
      docs.append(doc)
      # 从abnf句式输出文件中批量初始化
      docs = NLUDocList.from_abnf_output(output_dir='your/dir', domain='schedule_cmn')
      # 上传到bucket
      from nlp_data import NLUDocStore
      NLUDocStore.push(docs=docs, name='xxx')
  ```