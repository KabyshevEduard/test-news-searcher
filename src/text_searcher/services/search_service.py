import sqlite3
from src.text_searcher.settings import settings
import faiss
import json
import numpy as np
from sentence_transformers import SentenceTransformer
import logging
import math


logging.basicConfig(level=logging.INFO)


class SearchService:
    def __init__(self):
        self.conn = sqlite3.connect(settings.BASE_DIR + '/' + settings.DB_FILE)
        self.faiss_index = None
        self.embedder = SentenceTransformer('sentence-transformers/paraphrase-multilingual-mpnet-base-v2')

    def build_faiss_index(self, k=None):
        '''
        Create faiss index for databases documents
        '''
        try:
            self.faiss_index = faiss.read_index('news.index')
        except Exception as e:
            embeddings_all = self._get_all()
            embeddings_all_to_index = np.array([
                json.loads(emb[0]) for emb in embeddings_all
            ], dtype=np.float32)
            k = int(math.sqrt(embeddings_all_to_index.shape[0])) if k is None else k
            quantiser = faiss.IndexFlatL2(embeddings_all_to_index.shape[1])
            self.faiss_index = faiss.IndexIVFFlat(quantiser, embeddings_all_to_index.shape[1], k)
            self.faiss_index.train(embeddings_all_to_index)
            self.faiss_index.add(embeddings_all_to_index)
            faiss.write_index(self.faiss_index, 'news.index')

    def retrieve(self, query: str, top_n=10, columns=('summary', 'url')):
        '''
        Find top_n nearest examples
        '''
        query_embedding = self.embedder.encode(query)
        query_embedding = np.expand_dims(query_embedding, axis=0)
        logging.info(f'Query: {query}, embedding shape: {query_embedding.shape}')


        docs = self._get_all(columns=columns)

        if self.faiss_index is None:
            logging.error('FAISS indexes were not created')
            raise Exception('There is no faiss index')

        distances, indices = self.faiss_index.search(query_embedding, top_n)
        results = [docs[idx] for idx in indices[0] if idx < len(docs)]
        return results

    def _get_all(self, columns=None):
        cursor = self.conn.cursor()
        sql_columns = columns if columns is not None else 'embeddings'
        if isinstance(columns, tuple) or isinstance(columns, list):
            sql_columns = ', '.join(sql_columns)
        sql_query = f'SELECT {sql_columns} FROM news'
        cursor.execute(sql_query)
        embeddings_all = cursor.fetchall()
        return embeddings_all