import os

class BaseProcessor(object):
    def __init__(self, bucket, datadir, source_path):
        # Processors like textract will sometimes have 
        # some kind of python object intermediate representation
        # of the document.
        self.bucket = bucket
        self.datadir = datadir
        self.source_path = source_path
        self.num_subdocs = None
        self.num_pickles = None
        self.num_texts = None

        if not os.path.exists(self.datadir):
            self._mkdirs()
        else:
            self._set_num_subdocs()
            self._set_num_pickles()
            self._set_num_texts()
            print(f"Num subdocs: {self.num_subdocs}")

    def process(self):
        """ Processes a document into an intermediate representation """
        return

    def get_text(self):
        """ Gets the text of a pdf """
        return "", {}

    def get_tables(self):
        """ Gets the tables from a pdf """
        return "", {}

    def _mkdirs(self):
        folders = ['', 'subdocs', 'pickles', 'lines', 'tables']
        if not os.path.exists(self.datadir):
            for folder in folders:
                os.mkdir(os.path.join(self.datadir, folder))

    def _set_num_subdocs(self):
        # Set the number of subdocs
        subdoc_filenames = [f for f in os.listdir(f'./{self.datadir}/subdocs') if f.startswith('subdoc')] 
        self.num_subdocs = len(subdoc_filenames)

    # TODO: refactor
    def _set_num_pickles(self):
        # Set the number of subdocs 
        pickle_filenames = [f for f in os.listdir(f'./{self.datadir}/pickles') if f.startswith('subdoc')] 
        self.num_pickles = len(pickle_filenames)
    
    # TODO: refactor
    def _set_num_texts(self):
        text_filenames = [f for f in os.listdir(f'./{self.datadir}/lines') if f.startswith('subdoc')] 
        self.num_texts = len(text_filenames)
