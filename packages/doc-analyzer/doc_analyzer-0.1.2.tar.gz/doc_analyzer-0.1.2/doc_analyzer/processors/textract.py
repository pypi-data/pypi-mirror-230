import textract

from ..processors.base import BaseProcessor
from ..utils import pdf


class PdfProcessor(BaseProcessor):
    def __init__(self, bucket, datadir, source_path):
        super().__init__(bucket, datadir, source_path)

    def process(self):
        if not self.num_subdocs:
            self._split()
            self._set_num_subdocs()

    def get_text(self):
        """ Constructs the text from the document """
        page_text = {}
        if self.num_texts:
            print("Text files exist, not extracting")
            for subdoc_num in range(1, self.num_subdocs):
                with open(f"./{self.datadir}/lines/subdoc_{subdoc_num}.txt", 'r') as file:
                    line_text = file.read()
                    page_text[subdoc_num] = line_text

        else:
            print("Text files do not, extracting")
            for subdoc_num in range(1, self.num_subdocs):
                pdf_path = f"./{self.datadir}/subdocs/subdoc_{subdoc_num}.pdf"
                line_text = textract.process(pdf_path, method='pdfminer').decode('utf-8')
                page_text[subdoc_num] = line_text 
                with open(f"./{self.datadir}/lines/subdoc_{subdoc_num}.txt", 'w') as file:
                    file.write(line_text)
        full_text = "\n".join(page_text.values())
        return full_text, page_text

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