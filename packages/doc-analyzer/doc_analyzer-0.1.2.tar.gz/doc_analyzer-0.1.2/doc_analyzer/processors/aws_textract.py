import itertools
import os
import pickle
import re
import time
import pandas as pd

from ..processors.base import BaseProcessor
from ..utils import textract, pdf

class AWSTextractProcessor(BaseProcessor):
    def __init__(self, bucket, datadir, source_path):
        super().__init__(bucket, datadir, source_path)
        # Textract-specific attributes
        self.job_id_map = {} # Map of subdoc_num: analysis job_id
        self.analyses_map = {} # Map of subdoc_num: analysis (blocks)
        self.blocks_map = {} # Map of block_id: block

    def process(self):
        if self.num_pickles:
            self._set_subdoc_analyses_map_from_pickles()
            self._set_blocks_map()
        else:
            self._split()
            self._set_num_subdocs()
            self._analyze_subdocs()
            time.sleep(10)
            self._set_subdoc_analyses_map_from_jobs()

    def get_text(self):
        """ Constructs the text from the document """
        page_text = {}
        line_blocks_by_page = self._extract_blocks_by_type('LINE')
        for subdoc_num, line_blocks in line_blocks_by_page.items():
            if len(line_blocks) > 0:
                _, _, cluster_dfs, _ = textract.generate_cluster_dfs([line_blocks], 1)
                clustered_text = list(itertools.chain(*[list(df.text.values) for df in cluster_dfs]))
                line_text = "\n".join(clustered_text)
            else:
                line_text = ""
            page_text[subdoc_num] = line_text
            # with open(f"./{self.datadir}/lines/subdoc_{subdoc_num}.txt", 'w') as file:
            #     file.write(line_text)
        full_text = "\n".join(page_text.values())
        return full_text, page_text

    def get_tables(self):
        """ Gets the tables from a document """
        subdoc_tables = []
        table_blocks_by_page = self._extract_blocks_by_type('TABLE')
        for subdoc_num, table_blocks in table_blocks_by_page.items():
            for table_num, table_block in enumerate(table_blocks):
                try:
                    data = textract.generate_table_csv(table_block, self.blocks_map)
                    df = pd.DataFrame(data[1:], columns=data[0])
                    table_text = "\n".join([df.to_csv(index=False)])
                    subdoc_tables.append(table_text)
                    #with open(f"./{self.datadir}/tables/subdoc_{subdoc_num}_table_{table_num}.txt", 'w') as file:
                    #    file.write(table_text)
                except:
                    print(f"Error extracting block: {table_block.get('Id')}")
        table_text = "\n".join(subdoc_tables)   
        return table_text, subdoc_tables

    def _split(self, pages_per_subdoc=1):
        """ Splits the PDF into n subdocs to simplify processing and attribution """
        if not self.num_subdocs:
            print("Splitting PDF into subdocs")
            pdfs = pdf.split_pdf(self.source_path, pages_per_subdoc)
            for subdoc_num, output_pdf in enumerate(pdfs):
            # Generate the ouput pdfs
                output_filename = f"{self.datadir}/subdocs/subdoc_{subdoc_num + 1}.pdf"
                with open(output_filename, "wb") as output_file:
                    output_pdf.write(output_file)
        else:
            print("Subdocs already created, skipping")

    def _analyze_subdocs(self):
        """ Analyzes document, extracting text and tables """
        if not self.job_id_map.values():
            print("Analyzing subdocs")
            for subdoc_num in range(1, self.num_subdocs + 1):
                 document = f'{self.datadir}/subdocs/subdoc_{subdoc_num}.pdf'
                 job_id = textract.start_document_analysis(self.bucket, document)
                 self.job_id_map[subdoc_num] = job_id
        else:
            print("Job ids exist, skipping")

    def _set_subdoc_analyses_map_from_jobs(self):
        """Fetches the AWS textract document analysis for the subdocuments"""
        print("Getting analysis jobs")
        if self.job_id_map.values():
            for subdoc_num, job_id in self.job_id_map.items():
                analysis = textract.get_document_analysis(job_id)
                self.analyses_map[subdoc_num] = analysis
                pickle_filename = f'./{self.datadir}/pickles/subdoc_{subdoc_num}_analysis.pkl'
                with open(pickle_filename, 'wb') as pickle_file:
                    pickle.dump(analysis, pickle_file)
        else:
            print("No job ids, please run `analyze` first")

    def _set_subdoc_analyses_map_from_pickles(self):
        # TODO: check if the files exist locally but also fail back to s3 
        analysis_pickle_filesnames = os.listdir(f'./{self.datadir}/pickles')
        subdoc_nums = sorted([int(re.findall(r'\d+', filename)[0]) for filename in analysis_pickle_filesnames])
        for subdoc_num in subdoc_nums:
            try:
                with open(f'{self.datadir}/pickles/subdoc_{subdoc_num}_analysis.pkl', 'rb') as f:
                    analysis = pickle.load(f)
                    self.analyses_map[subdoc_num] = analysis
            except Exception as e:
                print(f"Error reading subdoc num {subdoc_num}: {e}")

    def _set_blocks_map(self):
        print("Setting blocks map")
        if self.analyses_map.values():
            for subdoc_num, analysis in self.analyses_map.items():
                if analysis:
                    for block in analysis:
                        block['subdoc_num'] = subdoc_num
                        self.blocks_map[block['Id']] = block
        else:
            print("No analyses map. Please set from either jobs or pickes")

    def _extract_blocks_by_type(self, block_type, by_page=True):
        blocks = {} 
        if self.analyses_map.values():
            for subdoc_num, analysis in self.analyses_map.items():
                blocks[subdoc_num] = []
                if analysis:
                    for block in analysis:
                        if block.get('BlockType') == block_type:
                            blocks[subdoc_num].append(block)
            if not by_page:
                blocks = itertools.chain(*blocks.values())
            return blocks