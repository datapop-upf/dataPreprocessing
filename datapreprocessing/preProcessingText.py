"""
Pre-process a tweet text and return a cleaned version of it alongside the mentions, the hashtags the URLs and the RT status (defined if it catches a 'RT" at the beginning of a tweet'
"""
import re

import emot

# import unidecode
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
    return deaccent(sentence)


def return_token(txt: str, tokeniser=tokenizer):
    """
    Use a tokenizer to return text in a list format
    :params:
        txt str(): text to tokenised
        tokeniser tokenizer(): Which tokeniser is used. Default RegexpTokenizer
    :return:
        list() of tokens
    """
    return tokenizer.tokenize(txt)


def remove_stop(txt, lang="spanish"):
    """"""
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


def convert_emojis(text):
    def replace_emoji(txt, indexes, replacements):
        for (index, replacement) in zip(indexes, replacements):
            txt[index] = replacement
        return txt

    converted_emojis = emot.emoji(text)
    if converted_emojis["flag"] is True:
        text = [x for x in text]
        idx_emojis = [
            location[0] for location in converted_emojis["location"]
        ]  # Get the first el as it is a single car
        text = replace_emoji(
            text,
            idx_emojis,
            converted_emojis["mean"],
        )
        text = "".join(text)
    return text


def convert_emoticons(text):
    def replace_emoticons(l, id_to_del, replacements):
        for idx, replacement in zip(
            sorted(id_to_del, reverse=True), sorted(replacements, reverse=True)
        ):
            del l[idx[0] : idx[-1]]
            l[idx[0] : idx[0]] = [x for x in replacement]
        return l

    converted_emoticons = emot.emoticons(text)
    if converted_emoticons["flag"] is True:
        text = [x for x in text]
        text = replace_emoticons(
            text, converted_emoticons["location"], converted_emoticons["mean"]
        )
        text = "".join(text)
    return text


def remove_mentions_from_txt(txt, remove_mention, mention_re):
    if remove_mention is True:
        mention_replace = ""
    else:
        mention_replace = "__MENTION__"
    txt, mentions = remove_compiled_regex(txt, mention_re, mention_replace)
    return txt, mentions


def remove_urls_from_txt(txt, remove_url, url_re):

    if remove_url is True:
        url_replace = ""
    else:
        url_replace = "__URL__"
    txt, urls = remove_compiled_regex(txt, url_re, url_replace)
    return txt, urls


def remove_hashtags_from_txt(txt, remove_hashtag, hashtag_re):

    if remove_hashtag is True:
        txt, hashtags = remove_compiled_regex(txt, hashtag_re, "__HASHTAG__")
    else:
        hashtags = hashtag_re.findall(txt)
        txt = txt.replace("#", "")
    return txt, hashtags


def remove_rt_from_txt(txt, remove_rt, rt_re):

    if remove_rt is True:
        rt_replace = ""
    else:
        rt_replace = "RT"
    txt, rt_status = remove_compiled_regex(txt, rt_re, rt_replace)
    # Transform into boolean to return True or False if catch RT
    rt_status = bool(rt_status)

    return txt, rt_status


def remove_compiled_regex(txt: str, compiled_regex: re.compile, substitute: str = ""):
    """
    Search for the compiled regex in the txt and either replace it with the substitute or remove it
    """
    entities = compiled_regex.findall(txt)
    txt = compiled_regex.sub(substitute, txt)
    return txt, entities


def remove_entities(
    txt: str,
    remove_hashtag: bool = False,
    remove_url: bool = False,
    remove_mention: bool = False,
    remove_rt: bool = False,
):

    # Replace User mentions tags
    txt, mentions_lists = remove_mentions_from_txt(txt, remove_mention, mention_re)

    # Remove URL
    txt, ulrs_lists = remove_urls_from_txt(txt, remove_url, url_re)

    # Remove Hashtags
    # We keep the hashtags as they can be normal words
    txt, hashtags_list = remove_hashtags_from_txt(txt, remove_hashtag, hashtag_re)

    # Remove RT symbol
    txt, rt_bool = remove_rt_from_txt(txt, remove_rt, rt_re)

    return txt, mentions_lists, ulrs_lists, hashtags_list, rt_bool


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


def preprocess_text(
    sentence: str,
    remove_hashtag: bool = False,
    remove_url: bool = False,
    remove_mention: bool = False,
    remove_rt: bool = False,
    remove_emoticon: bool = True,
    remove_emoji: bool = True,
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

        remove_emoticon bool(): if remove the emoticons and replace with their value (Default: True)
        remove_emoji bool(): if remove the emojis and replace with their value (Default: True)

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

        # remove entities and get the list of the removed object if need future parsing
        (
            sentence,
            mentions,
            urls,
            hashtags,
            rt_status,
        ) = remove_entities(
            sentence, remove_hashtag, remove_url, remove_mention, remove_rt
        )
        # Single character removal
        # sentence = re.sub(r"\s+[a-zA-Z]\s+", " ", sentence)

        # Replace the accents with a normalised version
        sentence = remove_accent(sentence)

        # Replace emoticon if true
        if remove_emoticon:
            sentence = convert_emoticons(sentence)

        # Replace emojis if True
        if remove_emoji:
            sentence = convert_emojis(sentence)

        # Remove punctuations and numbers
        sentence = re.sub("[^a-zA-Z]", " ", sentence)

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

    process_tweet = preprocess_text(original_tweet)
    print("Preprocess tweet")
    print(process_tweet)

    second_tweet = "__MENTION__ __MENTION__ enserio cuando habeis dicho que los froot loops estan malos me ha dolido..."
    print("Original Tweet")
    print(second_tweet)
    process_tweet = preprocess_text(second_tweet)
    print("Preprocess tweet")
    print(process_tweet)


if __name__ == "__main__":
    main()
