"""
Pre-process a tweet text and return a cleaned version of it alongside the mentions, the hashtags the URLs and the RT status (defined if it catches a 'RT" at the beginning of a tweet'
"""
import re

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


def remove_entities(txt: str, compiled_regex: re.compile, substitute: str = ""):
    """
    Replace mentions from the txt tweet and add them into a list to be able to keep them for later
    """
    entities = compiled_regex.findall(txt)
    txt = compiled_regex.sub(substitute, txt)
    return txt, entities


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
            remove_rt = "RT"
        sentence, rt_status = remove_entities(sentence, rt_re, rt_replace)
        # Transform into boolean to return True or False if catch RT
        rt_status = bool(rt_status)

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


def remove_stop(text, stop_words, lang="spanish"):
    """
    """
    stop_words = set(stopwords.words(lang))
    stop_words.update([".", ",", '"', "'", ":", ";", "(", ")", "[", "]", "{", "}"])
    stop_words.update(["MENTION".lower(), "RT".lower(), "URL".lower()])


def main():

    original_tweet = "RT @Toto, this is a sada ter for the @mentions of an #hastags"
    print("Original Tweet")
    print(original_tweet)

    process_tweet = preprocess_tweet(original_tweet)
    print("Preprocess tweet")
    print(process_tweet)


if __name__ == "__main__":
    main()
