import subprocess
import boto3


class BaseDocument(object):
    def __init__(self, name, uri, bucket):
        self.name = name
        self.bucket = bucket
        self.uri = uri
        self.source_path = "" 
        self.datadir = ""
 
    def download(self):
        """ Downloads the source document """
        return

    def split(self):
        """ Splits source file into smaller chunks for processing """
        return

    def process(self):
        """ Processes the document(s) to extract text """
        return

    def open(self):
        """ Opens the source file """
        commands = ['open', self.source_path]
        subprocess.call(commands)

    def sync(self):
        """ Syncs the datadir to the s3 bucket using the AWS cli as a hack """
        # TODO: move to Base Document class
        s3 = boto3.client('s3')
        local_folder = f'./{self.datadir}'
        target_bucket = f's3://{self.bucket}/{self.datadir}'
        commands = ['aws', 's3', 'sync', local_folder, target_bucket]
        subprocess.call(commands)

    def cleanup(self):
        """ Removes local files """
        return