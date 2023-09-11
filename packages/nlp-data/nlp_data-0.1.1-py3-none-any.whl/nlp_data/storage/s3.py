import boto3
from wasabi import msg
from rich.table import Table
from rich.console import Console
from typing import List


class S3Storage():
    def __init__(self, 
                 endpoint_url: str = "http://192.168.130.5:9005", 
                 access_key: str = "minioadmin", 
                 secret_key: str = "minioadmin"):
        super().__init__()
        self.s3 = boto3.resource(service_name='s3',
                                 endpoint_url=endpoint_url,
                                 aws_access_key_id=access_key,
                                 aws_secret_access_key=secret_key)
        
    @property
    def buckets(self):
        return [b.name for b in self.s3.buckets.all()]
    
    def get_bucket_files(self, bucket_name: str) -> List[str]:
        """获取某个bucket下的所有文件名称
        """
        return [obj.key for obj in self.s3.Bucket(bucket_name).objects.all()]
    
    def list_buckets(self):
        """基于rich库更好的展示所有的bucket的名称和文件数量"""
        table = Table(title="Buckets", show_header=True, header_style="bold magenta")
        table.add_column("Bucket Name", style="dim", width=12)
        table.add_column("File Count", justify="right", width=12)
        for bucket in self.s3.buckets.all():
            table.add_row(bucket.name, str(len(list(bucket.objects.all()))))
        console = Console()
        console.print(table)
        
    def list_files(self, bucket_name: str):
        """基于rich库更好的展示某个bucket下的所有文件的名称"""
        if bucket_name not in self.buckets:
            msg.fail(f"Bucket {bucket_name} does not exist.")
            return
        table = Table(title=f"Files in {bucket_name}", show_header=True, header_style="bold magenta")
        table.add_column("File Name", style="dim")
        for obj in self.s3.Bucket(bucket_name).objects.all():
            table.add_row(obj.key)
        console = Console()
        console.print(table)
        
    def create_bucket(self, bucket_name: str):
        """创建一个bucket
        """
        if bucket_name in self.buckets:
            msg.fail(f"Bucket {bucket_name} already exists.")
        else:
            self.s3.create_bucket(Bucket=bucket_name)
            msg.good(f"Bucket {bucket_name} created.")
            
    def delete_bucket(self, bucket_name: str):
        """删除一个bucket
        """
        if bucket_name not in self.buckets:
            msg.fail(f"Bucket {bucket_name} does not exist.")
        else:
            for obj in self.s3.Bucket(bucket_name).objects.all():
                obj.delete()
            self.s3.Bucket(bucket_name).delete()
            msg.good(f"Bucket {bucket_name} deleted.")
            
    def delete_file(self, bucket_name: str, file_name: str):
        """根据文件名删除文件
        """
        if bucket_name not in self.buckets:
            msg.fail(f'{bucket_name} not found')
        for obj in self.s3.Bucket(bucket_name).objects.all():
            if obj.key == file_name:
                obj.delete()
                msg.good(f'{file_name} deleted')
                return