import logging
import datetime

import pytz
import fasttext
import numpy as np
import pandas as pd

from tqdm import tqdm
from dataPreprocessing import preProcessingText

logging.basicConfig(format="%(asctime)s %(message)s", level=logging.INFO)


def get_lang(txt, lang_model_path=None):

    if lang_model_path is None:
        lang_model_path = "./models/lid.176.bin"

    lang_model = fasttext.load_model(lang_model_path)
    try:
        label, proba = lang_detector(txt)

        if len(label) == 1:  # Only one language detected
            label = label[0].replace("__label__", "")
            proba = proba[0]
        elif len(label) > 1:  # Several language detected
            label = "multilangue"
            proba = np.mean(proba)  # Get the mean of the proba as not interested in it

    except Exception as e:
        label, proba = None, None
    return label, proba


def process_tweet(tweet, lang_model=None):
    """
    Need
    # Source: https://amitness.com/2019/07/identify-text-language-python/
    #!wget -O ./models/lid.176.bin https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
    PRETRAINTED_MODEL_PATH = "./models/lid.176.bin"
    lang_model = fasttext.load_model(PRETRAINTED_MODEL_PATH)
    """

    tweet_to_return = dict()

    # Add the tweet id
    tweet_to_return["id"] = tweet["id"]

    # Add the userid
    tweet_to_return["user_id"] = tweet["user"]["id"]

    # Try to get the full text in either the case of a retweet or a normal tweet
    # Seems to have the key 'truncated': bool() that can be used
    try:
        if (
            tweet["retweeted_status"] is None
        ):  # used in case parse the pandas document after 1.export. In that case the key exists == None. Raise KeyError to ensure compatibility
            raise KeyError
        tweet_to_return["rt_status"] = True
        tweet_to_return["text"] = tweet["retweeted_status"]["extended_tweet"][
            "full_text"
        ]
    except KeyError:
        tweet_to_return["rt_status"] = False
        try:
            tweet_to_return["text"] = tweet["extended_tweet"]["full_text"]
        except KeyError:
            tweet_to_return["text"] = tweet["text"]

    try:
        tweet_to_return["lang_twitter"] = tweet.pop("lang")
    except KeyError:
        tweet_to_return["lang_twitter"] = np.NaN
    tweet_to_return["screen_name"] = tweet["user"]["screen_name"].lower()

    tweet_to_return["user_mentions"] = [
        x["screen_name"].lower() for x in tweet["entities"]["user_mentions"]
    ]
    tweet_to_return["user_mentions_ids"] = [
        x["id"] for x in tweet["entities"]["user_mentions"]
    ]

    tweet_to_return["hashtags"] = [
        x["text"].lower() for x in tweet["entities"]["hashtags"]
    ]

    tweet_to_return["urls"] = [x["expanded_url"] for x in tweet["entities"]["urls"]]

    tweet_to_return["created_at"] = datetime.datetime.strptime(
        tweet["created_at"], "%a %b %d %H:%M:%S +0000 %Y"
    ).replace(tzinfo=pytz.UTC)

    # tweet_to_return["created_at"] = str(tweet["created_at"])

    remove_entities = preProcessingText.preprocess_text(
        tweet_to_return["text"],
        remove_mention=True,
        remove_url=True,
        remove_rt=True,
        return_dict=True,
    )
    tweet_to_return["txt_wo_entities"] = remove_entities["tweet"]

    # tweet_to_return["txt_wo_entities"] = tweet_to_return["clean_text"]
    # Check if the rt has not been set up as true earlier
    if tweet_to_return["rt_status"] is False:
        tweet_to_return["rt_status"] = remove_entities["rt_status"]
    # tweet["clean_text"] = preProcessing.remove_accent(tweet["clean_text"])
    if lang_model:
        tweet_to_return["lang_label"], tweet_to_return["lang_proba"] = get_lang(
            tweet_to_return["txt_wo_entities"], lang_model.predict
        )
        tweet_to_return["lang_proba"] = float(
            tweet_to_return["lang_proba"]
        )  # Need to transform float32 into str for json
    tweet_to_return["token_txt"] = preProcessingText.return_token(
        tweet_to_return["txt_wo_entities"]
    )
    # tweet_to_return["clean_text"] = preProcessing.remove_stop(
    #     tweet_to_return["clean_text"], "spanish"
    # )
    # tweet_to_return["clean_stemmed_text"] = preProcessing.stem_text(
    #     tweet_to_return["clean_text"]
    # )
    tweet_to_return["word_count"] = len(tweet_to_return["token_txt"])

    return tweet_to_return


def main():
    # Source: https://amitness.com/2019/07/identify-text-language-python/
    #!wget -O ./models/lid.176.bin https://dl.fbaipublicfiles.com/fasttext/supervised-models/lid.176.bin
    PRETRAINTED_MODEL_PATH = "./models/lid.176.bin"
    lang_model = fasttext.load_model(PRETRAINTED_MODEL_PATH)

    all_tweets = list()
    n = 0
    # root_filename = tweet_filename.split("/")[-1].split(".")[0]
    root_filename = "01-2020_09-2020"
    tweet_filename = "./{}/data/{}.ftr".format(root_filename, root_filename)

    # Load dataset:
    df = pd.read_feather(tweet_filename)
    # df = df.sample(1000)
    # drop previous index column
    df = df.drop(df.columns[0], axis=1)
    # Load tweets
    for index, tweet in tqdm(df.iterrows(), total=df.shape[0]):
        processed_tweet = process_tweet(tweet, lang_model)

        all_tweets.append(processed_tweet)


if __name__ == "__main__":
    main()
