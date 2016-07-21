""" This class deals with topic modeling.

Time-stamp: <2016-07-21 11:06:11 yaning>

Author: Yaning Liu

 The methods considered are:
1) Latent Dirichlet Allocation
2) Latent Semantic Analysis

Main used modules are gensim
"""


import nltk
import gensim
from gensim import corpora, models, similarities
import logging
import sys

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s',
                    level=logging.INFO)

class topic_modeling(object):

    def __init__(self, TM_method, use_pool=False, pool_size=1,
                 save_dict=False, save_dict_name=None,
                 save_corpus=False, save_corpus_name=None,
                 save_topic_model=False, save_topic_model_name=None):
        """initializer for topic modeling class

        :param TM_method: topic modelin method, valid methods are
        LDA(Latent Dirichlet Allocation)
        LSI(Latent Semantic Indexing)
        TFIDF(Term frequency inverse document frequency)
        RP(Random Projections)
        HDP(Hierarchical Dirichlet Process)
        :param use_pool: boolean, if parallel
        :param pool_size: integer, size of pool
        :param save_dict: if saving dictionary
        :param save_dict_name: the name of the dictioanry if saving
        :param save_corpus: if saving corpus
        :param save_corpus_name: the file name of the copus if saving
        :param save_topic_model: boolean, if saving the topic model
        :param save_topic_model_name: string, the name of the topic model file
        :returns: the class
        :rtype: topic_modeling

        """
        self.TM_method = TM_method
        self.use_pool = use_pool
        self.pool_size = pool_size
        self.save_dict = save_dict
        self.save_dict_name = save_dict_name
        self.save_corpus = save_corpus
        self.save_corpus_name = save_corpus_name
        self.save_topic_model = save_topic_model
        self.save_topic_model_name = save_topic_model_name


    def get_topics(self, dict_list, product_id, id_type, review_col_name,
                   ntopic=10):
        """Get the topics given a list of dictionaries, each list element
        is a cleaned text (a list of words), given the product id and id type
        show the top ntopic topics

        :param dict_list: a list of dictionaries, each element is a list of words
        :param ntopic: show only the top ntopic topics
        :param product_id: string, the product id
        :param id_type: string, the type of the id, e.g. asin
        :param review_col_name, string the key of the review text value
        :returns:
        :rtype:

        """
        if review_col_name not in dic_list[0].keys():
            sys.exit('get_topics: The specified key {0} '
                     'can not be found in the dictionaries'
                     .format(review_col_name))

        if ( (product_id is not None and id_type is None) or
             (product_id) is None and id_type is not None):
            sys.exit('get_topics: both/neither product_id and id_type'
                    ' should be provided!' .format(id_type))

        if id_type is not None and id_type not in dic_list[0].keys():
            sys.exit('get_topics: The specified id type {0} '
                     'can not be found in the dictionaries'
                     .format(id_type))

        # The review list of the product
        prod_text_list = [dic[review_col_name] for dic in dict_list
                          if dic[id_type]==product_id]
        dictionary = self.build_dictionary(dict_list, self.save_dict,
                                          self.save_dict_name)

        corpus = self.get_corpus(dictionary, prod_text_list, self.save_corpus,
                                 self.save_corpus_name, self.use_pool,
                                 self.pool_size)
        topic_model = self.get_topic_model(self.TM_method, dictionary,
                                           self.ntopic,
                                           self.save_topic_model,
                                           self.save_topic_name)


    @staticmethod
    def build_dictionary(cleaned_text_list, save_dict=False, save_name=None):
        """build dictionary from cleaned texts

        :param cleaned_text_list: a list of a list of words,
        obtained from cleaned texts. The inner list of words could
        be a single cleaned review
        :param save_dict: bolean, if saving the dictioanry
        :param save_name: string, the file name to save to. If not saving, None
        :returns: dictionary
        :rtype: a gensim dictionary

        """
        dictionary = corpora.Dictionary(cleaned_text_list)
        if save_dict:
            if save_name is None:
                sys.exit('build_dictionary: the file name to save to should be '
                         'provided!')
            else:
                dictionary.save(save_name)
        return dictionary

    @staticmethod
    def get_corpus(dictionary, text_list, save_corpus=False,
                   save_corpus_name=None, use_pool=None, pool_size=1):
        """Compute corpus

        :param dictionary: the gensim dictionary
        :param text_list: a list of texts
        :param save_corpus: boolean if saving the corpus
        :param save_corpus_name: the name of the corpus to save to
        :param use_pool: boolean, if using pool
        :param pool_size: integer, the size of the pool
        :returns: corpus
        :rtype: gensim corpus

        """
        # corpus is a list of bag of words (bow)
        if use_pool:
            pool = Pool(pool_size)
            corpus = pool.map(dictionary.doc2bow, text_list)
            pool.close()
        else:
            corpus = [dictionary.doc2bow(text) for text in text_list]

        if self.save_corpus:
            # save corpus for later use
            corpora.MmCorpus.serialize(save_corpus_name, corpus)


    def get_topic_model(corpus, trans_method, dictionary, ntopics,
                                 save_trans_model=False,
                                 save_trans_name=None):
        """Obtain a topic model based on one of the transformation method

        :param corpus: the corpus, a list of bag of words
        :param trans_method: the method for transformation
        :param dictionaory: the gensim dictionary
        :param ntopics: number of topics
        :param save_trans_model: boolean if saving transformed
        :param save_trans_name: string, the file name of the
        transformed vector
        :returns: the topic/transformation model
        :rtype:

        """
        if trans_method == 'TFIDF':
            tfidf = models.TfidfModel(corpus)  # initialize a tfidf model
            if save_trans_model:
                if save_trans_name is not None:
                    tfidf.save(save_trans_name)
                else:
                    sys.exit('get_topic_model: no file name specified '
                             'for topic model!')
            return tfidf
        elif trans_method == 'LSI':
            tfidf = models.TfidfModel(corpus)  # initialize a tfidf model
            corpus_tfidf = tfidf[corpus]
            lsi = models.LsiModel(corpus_tfidf, id2word=dictionary,
                                  num_topics=ntopics)
            # corpus_lsi = lsi[corpus_tridf]
            if save_trans_model:
                if save_trans_name is not None:
                    lsi.save(save_trans_name)
                else:
                    sys.exit('get_topic_model: no file name specified '
                             'for topic model!')
            return lsi
        elif trans_method == 'LDA':
            lda = models.LdaModel(corpus, id2word=dictionary,
                                  num_topics=ntopics)
            if save_trans_model:
                if save_trans_name is not None:
                    lda.save(save_trans_name)
                else:
                    sys.exit('get_topic_model: no file name specified '
                             'for topic model!')
            return lda
        elif trans_method == 'HDP':
            hdp = models.HdpModel(corpus, id2word=dictionary)
            if save_trans_model:
                if save_trans_name is not None:
                    hdp.save(save_trans_name)
                else:
                    sys.exit('get_topic_model: no file name specified '
                             'for topic model!')
            return hdp
        elif trans_method == 'RP':
            tfidf = models.TfidfModel(corpus)  # initialize a tfidf model
            corpus_tfidf = tfidf[corpus]
            rp = models.RpModel(corpus_tfidf, num_topics=ntopics)
            if save_trans_model:
                if save_trans_name is not None:
                    rp.save(save_trans_name)
                else:
                    sys.exit('get_topic_model: no file name specified '
                             'for topic model!')
            return rp
        else:
            sys.exit('corpus_transform: topic method {0} is not valid!'
                     .format(transform_method))