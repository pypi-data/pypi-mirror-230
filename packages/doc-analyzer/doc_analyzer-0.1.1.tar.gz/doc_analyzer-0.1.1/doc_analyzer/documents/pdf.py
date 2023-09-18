import os
import pandas as pd

from ..utils import textract
from ..utils import pdf
from ..processors.aws_textract import AWSTextractProcessor
from ..processors.textract import PdfProcessor 
from ..documents.base import BaseDocument

PROCESSORS = {
    'aws': AWSTextractProcessor,
    'pdf': PdfProcessor 
}


class PdfDocument(BaseDocument):
    def __init__(self, bucket, name, uri, processor='pdf'):
        self.name = name
        self.bucket = bucket
        self.uri = uri
        
        # Private attributes 
        self.table_text = "" 
        self.line_text = "" 
        self.pages = {} 
 
        # Set the data directory and source document path
        self.datadir = f".{self.name}__pdf"
        self.source_path = f"{self.datadir}/{self.name}.pdf" 
        self.processor = PROCESSORS[processor](bucket, self.datadir, self.source_path)

        # If the data directory doesn't exist, make the directories; otherwise load from pickles 
        # TODO: check to see if the data exists in s3 
        if not os.path.exists(self.datadir):
            self._mkdirs()

        self.download()

    @property
    def text(self): 
        return self.line_text + '\n\n' + self.table_text
    
    def _mkdirs(self):
        folders = ['', 'subdocs', 'lines', 'tables']
        if not os.path.exists(self.datadir):
            for folder in folders:
                os.mkdir(os.path.join(self.datadir, folder))

    def download(self, sync=False):
        if not os.path.exists(self.source_path):
            pdf.copy_pdf(self.uri, self.source_path)
        else:
            print("File exists locally, skipping download")
        
        if sync:
            self.sync()

    def split(self, pages_per_subdoc=1, sync=False):
        """ Splits the PDF into n subdocs to simplify processing and attribution """
        if self.num_subdocs:
            pdfs = pdf.split_pdf(self.source_path, pages_per_subdoc)
            for subdoc_num, output_pdf in enumerate(pdfs):
            # Generate the ouput pdfs
                output_filename = f"{self.datadir}/subdocs/subdoc_{subdoc_num + 1}.pdf"
                with open(output_filename, "wb") as output_file:
                    output_pdf.write(output_file)
            if sync:
                self.sync()
        else:
            print("Subdocs already created, skipping")

    def process(self, sync=False):
        """ Processes the PDF, extracts text and tables, and uploads data to s3 """
        self.processor.process()
        # Set the line text
        text, page_text = self.processor.get_text()
        self.line_text = text
        self.pages = page_text
        # Set the table text
        tables, subdoc_tables = self.processor.get_tables()
        self.table_text = tables
        self.tables = subdoc_tables
        # Sync the data to s3
        if sync:
            self.sync()
 
    def _get_table_dataframes(self):
        dfs = []
        table_blocks = self._extract_blocks_by_type('TABLE', by_page=False) 
        for table_block in table_blocks:
            data = textract.generate_table_csv(table_block, self.blocks_map)
            df = pd.DataFrame(data) # TODO: figure out a better way to deal with headers
            dfs.append(df)
        return dfs