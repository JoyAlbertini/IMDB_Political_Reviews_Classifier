import re

import numpy as np
import pandas as pd
import spacy

MODEL_DIR = './NLP/spacy_model'
MODEL_BEST = './NLP/spacy_model/model-best/'
TEST = './NLP/political_test.spacy'
TRAIN = './NLP/political_train.spacy'
VALIDATION = './NLP/political_validation.spacy'
CONFIG = './NLP/config.cfg'


def extract_imdb_id(url):
    match = re.search(r'/title/(tt\d+)/', url)
    if match:
        return match.group(1)
    else:
        return None


def json_to_dataframe(data):
    movie_info = {
        'Type': data.get('type', 'N/A'),
        'Name': data.get('name', 'N/A'),
        'URL': data.get('url', 'N/A'),
        'Poster': data.get('poster', 'N/A'),
        'Description': data.get('description', 'N/A'),
        'ContentRating': data.get('contentRating', 'N/A'),
        'DatePublished': data.get('datePublished', 'N/A'),
        'Keywords': data.get('keywords', 'N/A'),
        'Duration': data.get('duration', 'N/A'),
        'RatingCount': data.get('rating', {}).get('ratingCount', 0),
        'RatingValue': data.get('rating', {}).get('ratingValue', 0.0)
    }

    genres = data.get('genre', [])
    movie_info['Genres'] = ', '.join(genres) if isinstance(genres, list) else genres  # Join list to string

    actors = data.get('actor', [])
    movie_info['Actors'] = ', '.join([actor.get('name', 'N/A') for actor in actors]) if isinstance(actors,
                                                                                                   list) else 'N/A'

    directors = data.get('director', [])
    movie_info['Directors'] = ', '.join([director.get('name', 'N/A') for director in directors]) if isinstance(
        directors, list) else 'N/A'

    creators = data.get('creator', [])
    movie_info['Creators'] = ', '.join([creator.get('name', 'N/A') for creator in creators]) if isinstance(creators,
                                                                                                           list) else 'N/A'

    df = pd.DataFrame([movie_info])

    return df


def predict_reviews(df):
    nlp = spacy.load(MODEL_BEST)
    model = nlp.get_pipe('textcat')

    df_filtered = df.dropna(subset=['review_title', 'review_body'])
    docs_with_ratings = [
        (nlp(title + " " + body), rating, title)
        for title, body, rating in zip(df_filtered['review_title'], df_filtered['review_body'], df_filtered['rating'])
    ]
    results = []
    for doc, rating, title in docs_with_ratings:
        prediction_scores = model.predict([doc])[0]
        max_index = np.argmax(prediction_scores)
        max_score = prediction_scores[max_index]
        max_label = model.labels[max_index]

        doc_result = {
            "review_title": title,
            "document": doc.text,
            "politics": max_label,
            "confidence": max_score,
            "rating": rating,
            "text_length": len(doc.text)
        }
        results.append(doc_result)

    return pd.DataFrame(results)


def predict_reviews_chunks(df, model, nlp, chunk_size=200):
    df_filtered = df.dropna(subset=['review_title', 'review_body'])

    results = []

    for title, body, rating in zip(df_filtered['review_title'], df_filtered['review_body'], df_filtered['rating']):
        full_text = title + " " + body

        chunks = [full_text[i:i + chunk_size] for i in range(0, len(full_text), chunk_size)]

        label_scores = {label: 0 for label in model.labels}

        for chunk in chunks:
            doc = nlp(chunk)
            prediction_scores = model.predict([doc])[0]
            for label, score in zip(model.labels, prediction_scores):
                label_scores[label] += score

        label_means = {label: label_scores[label] / len(chunks) for label in model.labels}

        max_label = max(label_means, key=label_means.get)
        max_mean_score = label_scores[max_label] / len(chunks)

        doc_result = {
            "review_title": title,
            "document": full_text,
            "predicted_label": max_label,
            "confidence": max_mean_score,
            "rating": rating,
            "text_length": len(full_text)
        }
        results.append(doc_result)

    return pd.DataFrame(results)


def confidence_threshold(df, threshold):
    high_confidence_df = df[df['confidence'] > threshold]
    high_confidence_df['text_length'] = high_confidence_df['document'].apply(len)
    sort_by_confidence(df)


def sort_by_confidence(df):
    return df.sort_values(by='confidence', ascending=False)


def filter_outside_range(df, min_rating, max_rating):
    df_filtered = df[(df['rating'] <= min_rating) | (df['rating'] >= max_rating)]
    return df_filtered


def df_rating_is(df, rating):
    df_filtered = df[(df['rating'] == rating)]
    return df_filtered


def split_by_politics(df, label):
    return df[df['politics'] == label]


def print_prediction_results(df):
    for index, row in df.iterrows():
        print(f"Document title: {row['review_title']}")
        print(f"Document: {row['document']}")
        print(f"Confidence: {row['confidence']}")
        print("===========================")
