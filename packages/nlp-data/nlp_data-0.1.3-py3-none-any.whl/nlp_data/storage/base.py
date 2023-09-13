from docarray.store.s3 import S3DocStore
from typing import Dict, List, Optional
from docarray import DocList, BaseDoc
import boto3
from botocore.client import Config
import botocore
from wasabi import msg



class BaseDocStore(S3DocStore):
    """对docarray本地文件存储的封装
    """
    bucket_name = None
    s3_url = "http://192.168.130.5:9005"
    boto3.Session.client.__defaults__ = ("us-east-1",
                                         None,
                                         False,
                                         None,
                                         "http://192.168.130.5:9005",
                                         "minioadmin",
                                         "minioadmin",
                                         None,
                                         Config(signature_version="s3v4"))
    
    @classmethod
    def list(cls, name_space: Optional[str] = None, show_table: bool = True) -> List[str]:
        """列出embedding bucket下的所有DocLists
        """
        s3 = boto3.resource(service_name='s3',
                            region_name="us-east-1",
                            use_ssl=False,
                            endpoint_url=cls.s3_url,
                            aws_access_key_id="minioadmin",
                            aws_secret_access_key="minioadmin",
                            config=Config(signature_version="s3v4"))
        s3_bucket = s3.Bucket(cls.bucket_name)
        da_files = []
        for obj in s3_bucket.objects.all():
            if name_space is None:
                if obj.key.endswith('.docs'):
                    da_files.append(obj)
            else:
                if obj.key.endswith('.docs') and obj.key.startswith(name_space):
                    da_files.append(obj)
                    
        da_names = [f.key.split('.')[0] for f in da_files]

        if show_table:
            from rich import box, filesize
            from rich.console import Console
            from rich.table import Table

            table = Table(
                title=f'DocList in bucket s3://{cls.bucket_name}',
                box=box.SIMPLE,
                highlight=True,
            )
            table.add_column('Name')
            table.add_column('Last Modified', justify='center')
            table.add_column('Size')

            for da_name, da_file in zip(da_names, da_files):
                table.add_row(
                    da_name,
                    str(da_file.last_modified),
                    str(filesize.decimal(da_file.size)),
                )

            Console().print(table)
        return da_names
    
    
    @classmethod
    def delete(cls, name: str, missing_ok: bool = True) -> bool:
        """
        """
        s3 = boto3.resource(service_name='s3',
            region_name="us-east-1",
            use_ssl=False,
            endpoint_url=cls.s3_url,
            aws_access_key_id="minioadmin",
            aws_secret_access_key="minioadmin",
            config=Config(signature_version="s3v4"))
        object = s3.Object(cls.bucket_name, name + '.docs')
        try:
            object.load()
        except botocore.exceptions.ClientError as e:
            if e.response['Error']['Code'] == "404":
                if missing_ok:
                    return False
                else:
                    raise ValueError(f'Object {name} does not exist')
            else:
                raise
        object.delete()
        return True
    
    
    @classmethod
    def pull(cls, name: str, show_progress: bool):
        raise NotImplementedError
    
    @classmethod
    def push(cls, docs: DocList[BaseDoc], name: str, show_progress: bool) -> Dict:
        raise NotImplementedError
    
    @classmethod
    def rename(cls, raw_name: str, change_name: str, show_table: bool = False):
        """Rename a DocList on s3
        Args:
            raw_name (str): 文档列表的原始名称
            change_name (str): 文档列表的新名称
        """
        names = cls.list(show_table=False)
        if raw_name not in names:
            msg.fail(f"DocList {raw_name} does not exist. all DocLists: {names}")
            return
        if change_name in names:
            msg.fail(f"DocList {change_name} already exists")
            return
        raw_docs = cls.pull(raw_name, show_progress=False)
        cls.delete(raw_name)
        _ = cls.push(raw_docs, change_name, show_progress=False)
        names = cls.list(show_table=show_table)
        if change_name in names:
            msg.good(f"Rename {raw_name} to {change_name} successfully")
        else:
            msg.fail(f"Rename {raw_name} to {change_name} failed")