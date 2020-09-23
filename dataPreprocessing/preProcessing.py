"""
Pre-process a tweet text and return a cleaned version of it alongside the mentions, the hashtags the URLs and the RT status (defined if it catches a 'RT" at the beginning of a tweet'
"""
import re

import unidecode

from gensim.utils import deaccent

from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from nltk.tokenize import RegexpTokenizer

# Catch the mentions
mention_re = re.compile(r"@([A-Za-z0-9_]+)")

# Catch the hashtags
hashtag_re = re.compile(r"^#\S+|\s#\S+")

# Catch any URL
url_re = re.compile(
    "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)

# Catch the RT
rt_re = re.compile(r"^RT", re.IGNORECASE)

# Tokeniser

to_split_re = re.compile(r"\w+")
tokenizer = RegexpTokenizer(to_split_re)


def remove_accent(sentence):
    # def rmdiacritics(char):
    #     """
    #     Source: https://stackoverflow.com/a/15547803/3193951
    #     Return the base character of char, by "removing" any
    #     diacritics like accents or curls and strokes and the like.
    #     """
    #     desc = unidecode.name(char)
    #     cutoff = desc.find(" WITH ")
    #     if cutoff != -1:
    #         desc = desc[:cutoff]
    #         try:
    #             char = ud.lookup(desc)
    #         except KeyError:
    #             pass  # removing "WITH ..." produced an invalid name
    #     return char
    #
    return deaccent(sentence)


def return_token(txt: str, tokeniser=RegexpTokenizer(to_split_re)):
    """
    Use a tokeniser to return text in a list format
    :params:
        txt str(): text to tokenised
        tokeniser tokenizer(): Which tokeniser is used. Default RegexpTokenizer
    :return:
        list() of tokens
    """
    return tokenizer.tokenize(txt)


def remove_stop(txt, lang="spanish"):
    """
    """
    stop_words = set(stopwords.words(lang))
    stop_words.update([".", ",", '"', "'", ":", ";", "(", ")", "[", "]", "{", "}"])
    stop_words.update(["de", "el", "los", "la", "las", "els", "http", "https"])
    # TODO Remove all first person plural from the set
    # stop_words.update(["MENTION".lower(), "RT".lower(), "URL".lower()])
    if isinstance(txt, str):
        txt = txt.split(" ")
    try:
        return [
            w
            for w in txt
            if str(w).lower().rstrip() not in stop_words and len(str(w).rstrip()) > 0
        ]
    except TypeError:
        return None


def remove_entities(txt: str, compiled_regex: re.compile, substitute: str = ""):
    """
    Replace mentions from the txt tweet and add them into a list to be able to keep them for later
    """
    entities = compiled_regex.findall(txt)
    txt = compiled_regex.sub(substitute, txt)
    return txt, entities


def stem_text(txt: list(), lang: str = "spanish"):
    """
    Return a stemmed version of the input list of words

    :params:
        txt list(): of str to stem
        lang: str(): language of the text to clean. (Default: spanish)
    """
    stemmer = SnowballStemmer(lang)
    try:
        if isinstance(txt, str):
            return [stemmer.stem(w) for w in txt.split(" ") if len(w) > 0]
        elif isinstance(txt, list):
            return [stemmer.stem(w) for w in txt if len(w) > 0]
    except TypeError:  # In case of np.NaN
        return txt


def preprocess_tweet(
    sentence: str,
    remove_hashtag: bool = False,
    remove_url: bool = False,
    remove_mention: bool = False,
    remove_rt: bool = False,
    return_dict: bool = False,
):
    """
    Getting a tweet (string) and regex all the entities and replace them with a
    placeholder. Return all original entities in separated list
    and if the tweet was a RT (contained RT at the beginning)
    :params:
        sentence str(): Tweet text

        remove_hashtags bool(): if removes the hashtags or
            just the symbol to keep it as a word (Default: False)

        remove_url boo(): if removes the URL or replaces it with URL(Default: False)

        remove_mention bool(): if removes the mentions or replaces with MENTION (Default: False)

        remove_rt bool(): if removes the rt or replaces with RT (Default: False)

        return_dict bool() Return separated lists of a dictionary (Default: False)


    :return:
        sentences list(), mentions list(), urls list(), hashtags list(), rt_status bool()
        if return_dict:
            dict(sentence: list(),
                 mentions: list(),
                 urls: list(),
                 hashtags: list(),
                 rt_status: bool())
    """
    mentions = None
    urls = None
    hashtags = None
    rt_status = None
    try:
        # lowering all words
        sentence = sentence.lower()

        # Replace User mentions tags
        if remove_mention is True:
            mention_replace = ""
        else:
            mention_replace = "__MENTION__"
        sentence, mentions = remove_entities(sentence, mention_re, mention_replace)

        # Remove URL
        if remove_url is True:
            url_replace = ""
        else:
            url_replace = "__URL__"
        sentence, urls = remove_entities(sentence, url_re, url_replace)
        # Remove Hashtags
        # We keep the hashtags as they can be normal words
        if remove_hashtag is True:
            sentence, hashtags = remove_entities(sentence, hashtag_re, "__HASHTAG__")
        else:
            hashtags = hashtag_re.findall(sentence)
            sentence = sentence.replace("#", "")

        # Remove RT symbol
        if remove_rt is True:
            rt_replace = ""
        else:
            rt_replace = "RT"
        sentence, rt_status = remove_entities(sentence, rt_re, rt_replace)
        # Transform into boolean to return True or False if catch RT
        rt_status = bool(rt_status)

        # Replace the accents with a normalised version
        sentence = remove_accent(sentence)
        # Remove punctuations and numbers
        sentence = re.sub("[^a-zA-Z]", " ", sentence)

        # Single character removal
        sentence = re.sub(r"\s+[a-zA-Z]\s+", " ", sentence)

        # Removing multiple spaces
        sentence = " ".join(sentence.split())
    except Exception as e:
        print(e)
        print("Sentence: {} - Type {}".format(sentence, type(sentence)))
        raise

    if return_dict is True:
        return {
            "tweet": sentence,
            "mentions": mentions,
            "urls": urls,
            "hashtags": hashtags,
            "rt_status": rt_status,
        }
    else:
        return sentence, mentions, urls, hashtags, rt_status


def main():

    original_tweet = "RT @Toto, this is a sada ter for the @mentions of an #hastags"
    print("Original Tweet")
    print(original_tweet)

    process_tweet = preprocess_tweet(original_tweet)
    print("Preprocess tweet")
    print(process_tweet)

    stop_words = set(stopwords.words("spanish"))
    print(stop_words)
    stop_words.update([".", ",", '"', "'", ":", ";", "(", ")", "[", "]", "{", "}"])


if __name__ == "__main__":
    main()
