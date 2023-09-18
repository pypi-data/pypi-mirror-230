import os
import fitz
import PyPDF2
import requests
import shutil
from urllib.parse import urlparse


def copy_pdf(uri, destination_path):
    parsed_uri = urlparse(uri)

    if os.path.exists(destination_path):
        print("File already exists, skipping")
        return

    # Check if it's an HTTP or HTTPS link
    if parsed_uri.scheme in ["http", "https"]:
        download_pdf(uri, destination_path) 
    # Check if it's a local path
    elif os.path.exists(uri):
        print("Found local file")
        shutil.copy(uri, destination_path)
    else:
        return print("Not sure how to access file") 
        raise


def download_pdf(url, file_path):
    response = requests.get(url)
    if response.status_code == 200:
        with open(file_path, 'wb') as file:
            file.write(response.content)
        print(f"PDF downloaded and saved as '{file_path}'")
    else:
        print("Failed to download PDF")


def extract_links_with_text(pdf_path):
    doc = fitz.open(pdf_path)

    inlined_text = ""

    for page_num in range(len(doc)):
        page = doc[page_num]
        links = page.get_links()

        # Extracting all text blocks
        all_text_blocks = page.get_text("blocks")

        # Sorting blocks by vertical position and then by horizontal position
        all_text_blocks.sort(key=lambda block: (block[1], block[0]))

        # Let's track which links have been processed
        processed_links = [False] * len(links)

        for block in all_text_blocks:
            block_text = block[4]
            for link_index, link in enumerate(links):
                # If a link's rectangle intersects with the current text block
                if fitz.Rect(link['from']).intersects(block[:4]):
                    if 'uri' in link.keys():
                        rect = fitz.Rect(link['from'])
                        link_text_blocks = page.get_text("blocks", clip=rect)
                        link_text_str = ' '.join([ltb[4] for ltb in link_text_blocks]).strip()
                        # if link_text_str is not empty, replace it in the block_text
                        if link_text_str and link_text_str == 'Staff Report':
                            block_text = block_text.replace(link_text_str, f"{link_text_str} (Link: {link['uri']})")
                        # else:
                        #     block_text += f" (Link: {link['uri']})"
                            processed_links[link_index] = True

            inlined_text += block_text + '\n'

        # Add links that were not associated with any text block
        # for link_index, link_processed in enumerate(processed_links):
        #     if not link_processed and 'uri' in links[link_index].keys():
        #         inlined_text += f"(Link: {links[link_index]['uri']})\n"

    return inlined_text.strip()


def split_pdf(source_path, pages_per_subdoc=1):
    """ Splits the PDF into n subdocs to simplify processing and attribution """
    pdf_reader = PyPDF2.PdfReader(source_path)
    # Create the number of subdocs
    total_pages = len(pdf_reader.pages)
    total_subdocs = (total_pages // pages_per_subdoc) + 1

    pdfs = []
    # Generate the new PDF subdocs
    for subdoc_num in range(total_subdocs):
        output_pdf = PyPDF2.PdfWriter()

        start_page = subdoc_num * pages_per_subdoc
        end_page = min((subdoc_num + 1) * pages_per_subdoc, total_pages)

        for page_num in range(start_page, end_page):
            page = pdf_reader.pages[page_num]
            output_pdf.add_page(page)
        pdfs.append(output_pdf)

    return pdfs