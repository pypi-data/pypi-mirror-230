# Import packages
from io import StringIO
import pandas as pd
import numpy as np
import string
from unidecode import unidecode
import warnings
import time
import s3fs
import boto3
import jaro  # pip install jaro-winkler

# ------------------------------------
# -- Define cleaning function
# ------------------------------------


def clean_entity_name(original_entity: str, remove_stop_words: bool = True):

    clean_entity_name = str(original_entity)
    clean_entity_name = clean_entity_name.lower()
    clean_entity_name = clean_entity_name.split(" (")[0]
    translator = str.maketrans("", "", string.punctuation)
    clean_entity_name = clean_entity_name.translate(translator)
    clean_entity_name = unidecode(clean_entity_name)

    if remove_stop_words == True:
        # Remove stop words
        stop_words = [
            "limited",
            "ltd",
            "ag",
            "eg",
            "spa",
            "the",
            "sa",
            "ab",
            "llc",
            "llp",
            "plc",
            "inc",
            "ltd",
            "aktiengesellschaft",
            "nv",
            "a/s",
            "oc",
        ]
        clean_entity_name = " ".join(
            word for word in clean_entity_name.split() if word.lower() not in stop_words
        )

    return clean_entity_name


# ------------------------------------
# -- Define threshold function
# ------------------------------------


def dynamic_threshold(matching_scores: list, lower_threshold: float) -> float:

    # Sort the pairs based on the scores in descending order
    sorted_scores = sorted(matching_scores, reverse=True)
    # Remove scores below the lower threshold set in the main function
    sorted_scores = [x for x in sorted_scores if x >= lower_threshold]
    # Compute the ratio between any two consecutive pairs of scores
    score_ratios = [
        sorted_scores[i] / sorted_scores[i + 1] for i in range(len(sorted_scores) - 1)
    ]

    return sorted_scores[(score_ratios.index(max(score_ratios)))]


# ------------------------------------
# -- Define manual input of
# -- threshold function
# ------------------------------------


def threshold_check(
    matched_scores: list, matched_entities: list, current_threshold: float
) -> float:

    # Zip the two lists together
    combined_list = list(zip(matched_scores, matched_entities))
    # Sort the pairs based on the scores in descending order
    sorted_pairs = sorted(combined_list, reverse=True)
    # Separate the sorted pairs back into two lists
    sorted_scores, sorted_matches = zip(*sorted_pairs)

    # Keep only those entities above the threshold
    new_threshold = current_threshold
    while new_threshold != "":
        new_threshold = float(new_threshold)
        scores_to_keep = [x for x in sorted_scores if x >= new_threshold]
        matches_to_keep = sorted_matches[: len(scores_to_keep) + 1]
        first_three_discared_matches = sorted_matches[
            len(scores_to_keep) + 1 : len(scores_to_keep) + 4
        ]
        # matched_entities = [entity for entity, score in zip(matched_entities, matched_scores) if score > fixed_value]
        new_threshold = input(
            f"With a threshold of {calculated_threshold}, \
			the last three retained matches are {matches_to_keep[-3:]}, \
			while the first three discared ones are {first_three_discared_matches}. \
			Please input the new desired threshold (leave blank if current one is acceptable)"
        )

    return new_threshold


# ------------------------------------
# -- Define fuzzy matching function
# ------------------------------------


def run_fuzzy_match(
    entity_to_match: str,
    search_list: list,
    lower_threshold: float,
    clean_names: bool = True,
    multiple_matches: bool = False,
    set_threshold_dynamically: bool = False,
    ) -> list:

    if clean_names == True:  # perform round of cleaning of names
        entity_to_match_clean = clean_entity_name(entity_to_match)
        search_list_clean = [clean_entity_name(x) for x in search_list]
    else:
        entity_to_match_clean = entity_to_match
        search_list_clean = search_list

    # Initialize empty lists
    matched_entities = []
    matched_scores = []

    # Compute a Jaro-Winkler score for each combination of entities
    for i, s in enumerate(search_list_clean):
        score = jaro.jaro_winkler_metric(entity_to_match_clean, s)
        matched_entities.append(search_list[i])
        matched_scores.append(score)

    # Extract matches of interest on the basis of the various parameters
    if multiple_matches == False:
        # Retain highest score only
        max_score = max(matched_scores)
        if max_score >= lower_threshold:
            matched_entities = matched_entities[
                matched_scores.index(max(matched_scores))
            ]
            matched_scores = max_score
        else:
            matched_scores = []
            matched_entities = []

    elif (multiple_matches == True) & (set_threshold_dynamically == False):
        matched_entities = [
            entity
            for entity, score in zip(matched_entities, matched_scores)
            if score >= lower_threshold
        ]
        matched_scores = [x for x in matched_scores if x >= lower_threshold]

    elif (multiple_matches == True) & (set_threshold_dynamically == True):
        # Calculate the dynamic threshold
        calculated_threshold = float(dynamic_threshold(matched_scores, lower_threshold))
        # Zip the two lists together
        combined_list = list(zip(matched_scores, matched_entities))
        # Sort the pairs based on the scores in descending order
        sorted_pairs = sorted(combined_list, reverse=True)
        # Separate the sorted pairs back into two lists
        sorted_scores, sorted_matches = zip(*sorted_pairs)
        # Retain all scores above or equal to the calculated threshold
        matched_scores = [x for x in sorted_scores if x >= calculated_threshold]
        matched_entities = sorted_matches[: len(matched_scores)]

    return matched_scores, matched_entities


# ------------------------------------
# -- Define master function
# ------------------------------------


def fuzzy_match_cpi(
    dataframe_to_match: pd.DataFrame,
    entity_column: str,
    search_list: list,
    clean_names: bool = True,
    multiple_matches: bool = False,
    set_threshold_dynamically: bool = False,
    lower_threshold: float = 0.8,
) -> pd.DataFrame:

    # Apply function
    results = dataframe_to_match[entity_column].apply(
        run_fuzzy_match,
        args=(
            search_list,
            clean_names,
            multiple_matches,
            set_threshold_dynamically,
            lower_threshold,
        ),
    )

    # Create two new columns to store the results
    dataframe_to_match["Matched score"] = results.apply(lambda x: x[0])
    dataframe_to_match["Matched entity"] = results.apply(lambda x: x[1])

    return dataframe_to_match


# Test
# importpath = '/Users/nikitamarini/Desktop/CPI'
# df = pd.read_csv(f'{importpath}/gfanz_entities.csv')
# search_list_test = ['Ageas', 'ABN AMRO', 'Intesa San Paolo']

# df = run_fuzzy_match(df, 'Entity', search_list_test)
# print(df[df['Matched entity'].apply(len) > 0])
