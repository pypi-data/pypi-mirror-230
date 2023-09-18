import boto3
import pandas as pd
from sklearn.manifold import TSNE
from sklearn.cluster import DBSCAN


def start_document_analysis(bucket, document, feature_types=['TABLES', 'FORMS']):
    """ Kicks off AWS Textract document analysis process """
    textract_client = boto3.client('textract', region_name='us-east-1')
    # Specify the S3 bucket and document name
    s3_object = {
        'S3Object': {'Bucket': bucket, 'Name': document}
    }
    # Start the document analysis job
    response = textract_client.start_document_analysis(
        DocumentLocation=s3_object,
        FeatureTypes=feature_types
    )
    # Retrieve the JobId from the response
    job_id = response['JobId']
    return job_id


def get_document_analysis(job_id):
    """ Gets an AWS Textract document analysis object """
    textract_client = boto3.client('textract', region_name='us-east-1')
    # Get the analysis results for the specified job
    response = textract_client.get_document_analysis(JobId=job_id)
    # Check the status of the job
    status = response['JobStatus']
    # Return if the job succeeded, else fail and print
    if status == 'SUCCEEDED':
        # Process and extract relevant information from the document analysis
        document_analysis = response['Blocks']
        return document_analysis
    elif status == 'FAILED':
        # Handle failed job
        error_message = response['StatusMessage']
        print("Document analysis job failed with message:", error_message)
    else:
        # Handle other job statuses (IN_PROGRESS, PARTIAL_SUCCESS, etc.)
        print("Document analysis job is still in progress.")
    return None


def get_rows_columns_map(table_result, blocks_map):
    """ Gets a map of rows and columns from a textract table """
    rows = {}
    for relationship in table_result['Relationships']:
        if relationship['Type'] == 'CHILD':
            for child_id in relationship['Ids']:
                cell = blocks_map[child_id]
                if cell['BlockType'] == 'CELL':
                    row_index = cell['RowIndex']
                    col_index = cell['ColumnIndex']
                    if row_index not in rows:
                        # create new row
                        rows[row_index] = {}
                        
                    # get the text value
                    rows[row_index][col_index] = get_text(cell, blocks_map)
    return rows


def get_text(result, blocks_map):
    """ Gets text data from an AWS Textract table block """
    text = ''
    if 'Relationships' in result:
        for relationship in result['Relationships']:
            if relationship['Type'] == 'CHILD':
                for child_id in relationship['Ids']:
                    word = blocks_map[child_id]
                    if word['BlockType'] == 'WORD':
                        text += word['Text'] + ' '
                    if word['BlockType'] == 'SELECTION_ELEMENT':
                        if word['SelectionStatus'] =='SELECTED':
                            text +=  'X '    
    return text


def generate_table_csv(table_result, blocks_map):
    """ Generates a 'csv' of AWS Textract table information """
    rows = get_rows_columns_map(table_result, blocks_map)
    # get cells.
    _rows = []
    for row_index, cols in rows.items():
        row = []
        for col_index, text in cols.items():
            row.append(text)
        _rows.append(row)
    return _rows


def get_title(table_block, blocks_map):
    """ Gets the text of a table title from a table block """
    title_ids = []
    for relationship in table_block.get('Relationships'):
        if relationship.get('Type') == 'TABLE_TITLE':
            title_ids.extend(relationship.get('Ids'))

    title_text = "No title available"
    for id in title_ids:
        block = blocks_map[id]
        text = get_text(block, blocks_map)
        title_text = text
    return title_text


def create_cluster_df(line_attrs):
    """ Creates clusters based on page position of textract blocks """
    attr_df = pd.DataFrame(line_attrs, columns=['top', 'left', 'width', 'height', 'text', 'block_id', 'subdoc_num'])
    attr_df['next_line_top_dist'] = (attr_df.top.shift(-1) - (attr_df.top))

    # Project the dataframe onto a 2d subspace
    if attr_df.shape[0] > 5:
        tsne = TSNE(n_components=2, perplexity=5)
        X = attr_df.drop(['width', 'text', 'block_id', 'subdoc_num'], axis=1).fillna(0)
        X_fit = tsne.fit_transform(X)
    else:
        X_fit = attr_df.drop(['width', 'text', 'block_id', 'subdoc_num'], axis=1).fillna(0).to_numpy()
    
    # Fit the DBSCAN model to the data
    dbscan = DBSCAN(eps=2, min_samples=1)
    dbscan.fit(X_fit)
    
    # Extract the labels and core samples
    labels = dbscan.labels_
    core_samples = dbscan.core_sample_indices_
    
    # Number of clusters in labels, ignoring noise if present
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = list(labels).count(-1)

    # Add the cluster id and column information to the dataframe
    attr_df['cluster'] = labels
    attr_df['column'] = attr_df.left.apply(lambda l: 0 if l < .5 else 1)
    
    # Generate the cluster text dataframe
    cluster_text_df = attr_df.groupby('cluster').apply(get_cluster_info)
    cluster_df = pd.DataFrame.from_records(cluster_text_df)
    
    # Generate the cluster ordering on the page
    cluster_ordering = attr_df.groupby('cluster').first().sort_values(['column', 'top'])
    
    return labels, attr_df, cluster_df.loc[cluster_ordering.index], cluster_ordering


def get_cluster_info(cluster_df, sep=" "):
    """ Converts a dataframe of cluster lines to a single record with concatenated lines """
    return {
        'text': cluster_df.text.str.cat(sep=sep),
        'block_ids': cluster_df.block_id.values,
        'page_nums': cluster_df.subdoc_num.unique(),
        'cluster': cluster_df.cluster.unique()
    }

def generate_cluster_dfs(blocks, num_docs):
    """ Generate dataframes that are outputs from the clustering based on pages """
    label_values = []
    attr_dfs = []
    cluster_dfs = []
    ordering_dfs = []
    
    for target_doc in range(0, num_docs):
        # Generate the line attributes
        line_attrs = []
        for block in blocks[target_doc]:
            box = block['Geometry']['BoundingBox']
            text = block['Text']    
            line_attrs.append([box['Top'], box['Left'], box['Width'], box['Height'], text, block['Id'], target_doc])
         
        #try:
        # Generate the clusters
        labels, attr_df, cluster_df, ordering_df = create_cluster_df(line_attrs)
        # Append the clusters
        label_values.append(labels)
        attr_dfs.append(attr_df)
        cluster_dfs.append(cluster_df)
        ordering_dfs.append(ordering_df)
        #except Exception as e:
        #    print(f"Error with doc {target_doc}: {e}")
        
    return label_values, attr_dfs, cluster_dfs, ordering_dfs