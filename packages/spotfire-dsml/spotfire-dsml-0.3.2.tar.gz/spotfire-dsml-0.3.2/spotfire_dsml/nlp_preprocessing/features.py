import pandas as pd
import re
import nltk
import numpy as np
import pickle
import scipy
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from nltk.tokenize import TreebankWordTokenizer
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('omw-1.4')

# Classify an ngram as unigram (1), bigram (2), etc.
def get_ngram_length(ngram_text):
    return len(ngram_text.split(" "))


# Check if a phrase is in the preprocessed text; helper function to filter keywords_df
def is_feature_in_text(row):
    return (row['feature'] in row['preprocessed_text']) and all(
        [word in row['preprocessed_text'].split() for word in row['feature'].split()])


# Converts NLTK POS (part-of-speech) tag to a Wordnet POS tag
def get_wordnet_pos(nltk_pos):
    if nltk_pos.startswith('J'):
        return wordnet.ADJ
    elif nltk_pos.startswith('V'):
        return wordnet.VERB
    elif nltk_pos.startswith('N'):
        return wordnet.NOUN
    elif nltk_pos.startswith('R'):
        return wordnet.ADV
    else:
        return wordnet.NOUN  # or None

def remove_stopwords_fun(df, stopwords_list=None):
    if 'stopwords_list' and isinstance(stopwords_list, pd.Series) and stopwords_list.dtype == 'object':
        stop_words = stopwords_list
    else:
        lowercase_alphabet = list(map(chr, range(97, 123)))
        stop_words = stopwords.words('english') + lowercase_alphabet
    stop_words = {word.lower() for word in stop_words}

    df = df.apply(lambda text: " ".join([word for word in nltk.word_tokenize(text) if word not in stop_words]))
    return df

def preprocess_text(input_df, text_column_name, id_column_name=None, text_normalization='lemmatization',
                    case_sensitive=False, remove_numbers=True, remove_special_characters=True, remove_stopwords=True):
    """
        Preprocess text

        This function returns the preprocessed text column along with ID column

        Parameters
        ----------
        input_df : data frame
            A data frame with a text column and ID column
        id_column_name : str
            ID column name in input_df
        text_column_name : str
            text column name in input_df
        text_normalization : str
            Refers to text normalization methods; either 'stemming' or 'lemmatization'. Any other value
            performs no normalization.
        case_sensitive: bool
            Whether upper and lowercase text should be treated differently
        remove_numbers: bool
            Remove digits from text
        remove_special_characters: bool
            remove nonalphanumerics
        remove_stopwords: bool
            remove default NLTK English stopwords

        Returns
        -------
        features_df: data frame
            preprocessed text column as data frame
        id_column: column
            corresponding id column to features_df
    """

    # Check if an ID column is given otherwise assign a default one
    if not (id_column_name and id_column_name in input_df.columns and input_df[id_column_name].nunique() == len(input_df)):
        id_column_name = "ID"
        input_df[id_column_name] = range(0, len(input_df))
    assert (input_df[id_column_name].nunique() == len(input_df))
    assert (id_column_name in input_df.columns and text_column_name in input_df.columns)

    # Grab the text column and ID column from the input data
    features_df = input_df[text_column_name]
    assert (isinstance(features_df, pd.Series))
    id_column = input_df[id_column_name]
    assert (isinstance(id_column, pd.Series))
    assert (len(features_df) == len(id_column))

    ### Preprocessing ###
    # Replace missing values with empty string
    features_df.fillna('', inplace=True)

    # Lowercase all text
    if not case_sensitive:
        features_df = features_df.apply(lambda text: text.lower())

    # Remove all numbers (standalone and within words)
    if remove_numbers:
        features_df = features_df.apply(lambda text: re.sub(r'[\d]', "", text))

    # Replace everything besides non-alphanumerics and whitespaces with empty string (meant to get rid of special characters, punctuation)
    if remove_special_characters:
        features_df = features_df.apply(lambda text: re.sub(r'[^a-zA-Z0-9\s]', " ", text))

    # Removes stopwords if flag is set to true
    if remove_stopwords:
        features_df = remove_stopwords_fun(features_df)

    # Perform either stemming or lemmatization or neither
    if text_normalization:
        if text_normalization == "stemming":
            stemmer = nltk.stem.SnowballStemmer('english')
            features_df = features_df.apply(
                lambda text: ' '.join([stemmer.stem(word) for word in nltk.word_tokenize(text)]))
        elif text_normalization == "lemmatization":
            lemmatizer = WordNetLemmatizer()
            features_df = features_df.apply(lambda text: " ".join(lemmatizer.lemmatize(word, get_wordnet_pos(nltk_pos))
                                                                  for word, nltk_pos in
                                                                  nltk.pos_tag(nltk.word_tokenize(text))))
        else:
            pass

    # store tokenized text (list of str lists) as Binary in document property
    tokenize_text = [[tok for tok in text.split()] for text in features_df]
    tokenize_text = [elem for elem in tokenize_text if len(elem) > 0]
    store_tokenize_text = pickle.dumps(tokenize_text)  # Read: pickle.loads(<document property>)

    # Add transformed text column with original text columns; retains empty text rows
    preprocessed_text = input_df[text_column_name].to_frame()
    preprocessed_text.rename(columns={text_column_name: "original_text"}, inplace=True)
    preprocessed_text["preprocessed_text"] = features_df
    preprocessed_text['id'] = id_column

    # Remove empty text rows
    features_df = features_df[features_df != ""]
    which_indices = list((features_df != "").index)
    id_column = id_column.loc[which_indices]
    assert (list(id_column.index) == list(features_df.index))

    return features_df, id_column

def get_features(features_df, id_column, ngram_method='tfidf', ngram_size=3, max_features=1000, keywords_per_doc=5):
    """
        Extracts N-gram/Count Features

        This function returns tables referencing the N-gram or frequency matrices, top N-grams, and keywords

        Parameters
        ----------
        features_df : data frame
            A data frame with a text column and ID column
        id_column : str
            ID column name in input_df
        ngram_method : str
            either 'tfidf' for term frequency inverse document frequency or 'tf' for term frequency
        ngram_size : int
            max ngram sizes computed; lower bound is 1
        max_features: int
            max features in the ngram matrix. should be greater than 0
        keywords_per_doc: int
            max number of keywords per document to retrieve

        Returns
        -------
        Ngram_mat: scipy sparse matrix
            ngram_matrix often saved as binary document property
        top_ngrams_df: data frame
            top ngrams across corpus
        keywords_df:
            top keywords per document
        text_order_df: data frame
            order of text in ngram matrix
        ngrams_order_df: data frame
            order of ngrams in ngram matrix
    """

    Ngram_mat, top_ngrams_df, text_order_df, ngrams_order_df, keywords_df = None, None, None, None, None

    ### Ngram Operations ###
    try:
        # Calculate Ngram frequency matrix
        pipeline = Pipeline([('count_vectorizer', CountVectorizer(ngram_range=(1, ngram_size),
                                                                  tokenizer=TreebankWordTokenizer().tokenize))])
        Ngram_mat = pipeline.fit_transform(features_df)  # sparse array
        ngram_features = np.array(pipeline['count_vectorizer'].get_feature_names_out())

        # number of times each ngram appears across whole corpus
        ngram_frequencies = Ngram_mat.sum(axis=0)  # sparse matrix operation returns matrix
        ngram_frequencies = np.asarray(ngram_frequencies).flatten()

        # top features and frequencies are in order from most frequent to least frequent
        top_ngram_features = ngram_features[np.argsort(ngram_frequencies)[::-1]]
        top_ngram_frequencies = ngram_frequencies[np.argsort(ngram_frequencies)[::-1]]

        # retrieving most frequent features and optionally changing matrix to tfidf
        if ngram_method == 'tfidf':
            pipeline = pipeline = Pipeline([('tfidf_vectorizer', TfidfVectorizer(ngram_range=(1, ngram_size),
                                                                                 tokenizer=TreebankWordTokenizer().tokenize,
                                                                                 sublinear_tf=True))])
            Ngram_mat = pipeline.fit_transform(features_df)  # sparse array

        if not (max_features != None and max_features > 0 and max_features <= 10000):
            max_features = 1000

        # get subset of ngram matrix by most frequent ngrams (number set by max_features)
        subset_ngrams_mat_indices = np.argsort(ngram_frequencies)[::-1][:max_features]
        subset_ngrams_mat_features = top_ngram_features[:max_features]
        subset_ngrams_mat = Ngram_mat[:, subset_ngrams_mat_indices]

        # Save ngram matrix
        # scipy.sparse.save_npz('ngram_matrix.npz', subset_ngrams_mat)

        # format ngram frequencies into dataframe
        top_ngrams_df = pd.DataFrame()
        top_ngrams_df['ngram'] = top_ngram_features
        top_ngrams_df['frequencies'] = top_ngram_frequencies
        top_ngrams_df['length'] = top_ngrams_df['ngram'].apply(lambda text: get_ngram_length(text))

        # Order of text rows for subset_ngrams_mat
        text_order_df = pd.DataFrame()
        corpus = list(features_df)
        text_order_df['ngram_mat_row_number'] = [i for i in range(len(corpus))]

        text_order_df['id'] = list(id_column)
        text_order_df['preprocessed_text'] = corpus
        assert (subset_ngrams_mat.shape[0] == len(text_order_df))

        # Order of ngrams columns for subset_ngrams_mat
        ngrams_order_df = pd.DataFrame()
        features = [str(elem) for elem in list(subset_ngrams_mat_features)]
        ngrams_order_df['ngram_mat_column_number'] = [i for i in range(len(features))]
        ngrams_order_df['ngram'] = features
        assert (subset_ngrams_mat.shape[1] == len(ngrams_order_df))

        # store ngrams matrix as Binary in document property
        store_ngrams_mat = pickle.dumps(subset_ngrams_mat)  # Read: pickle.loads(<document property>)

        ### Top Scoring Words per Document ###
        dense_ngrams_mat = subset_ngrams_mat.toarray()
        top_keywords_indices = np.argpartition(dense_ngrams_mat, -keywords_per_doc, axis=1)[:, -keywords_per_doc:]
        all_features, all_scores, all_ids, all_texts = [], [], [], []
        for i in range(len(top_keywords_indices)):
            scores_per_doc = dense_ngrams_mat[i, top_keywords_indices[i, :]]
            sort_ind_per_doc = np.argsort(scores_per_doc)[::-1]
            scores_per_doc = scores_per_doc[sort_ind_per_doc]
            features_per_doc = subset_ngrams_mat_features[top_keywords_indices[i, :]][sort_ind_per_doc]
            id_per_doc = text_order_df.iloc[i]['id']
            text_per_doc = text_order_df.iloc[i]['preprocessed_text']

            all_features += [str(elem) for elem in features_per_doc]
            all_scores += [elem for elem in scores_per_doc]
            all_ids += [id_per_doc] * keywords_per_doc
            all_texts += [text_per_doc] * keywords_per_doc
        assert (len(all_features) == len(all_scores) == len(all_ids) == len(all_texts))
        keywords_df = pd.DataFrame.from_dict(
            data={'id': all_ids, 'preprocessed_text': all_texts, 'feature': all_features, 'score': all_scores})
        keywords_df['feature_in_text'] = keywords_df.apply(is_feature_in_text, axis=1)
        keywords_df = keywords_df[keywords_df['feature_in_text'] == True]
        keywords_df.drop(columns='feature_in_text', inplace=True)

    except Exception as err:
        print(err)

    return Ngram_mat, top_ngrams_df, text_order_df, ngrams_order_df, keywords_df

#example of sequential function calls
def main(input_df, text_column_name):
    features_df, id_column = preprocess_text(input_df, text_column_name)
    Ngram_mat, top_ngrams_df, text_order_df, ngrams_order_df, keywords_df = get_features(features_df, id_column)
    return Ngram_mat, top_ngrams_df, text_order_df, ngrams_order_df, keywords_df