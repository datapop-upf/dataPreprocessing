"""
Preprocess a tweet text and return a cleaned version of it
Only accept a text string and return a list of words, a list of URLS, a list of hashtags and a list of mentions

Can apply different language stop words
Can return a list of tokens
Can return the entities alongside
"""
import re

# Catch the mentions
mention_re = re.compile(r"@([A-Za-z0-9_]+)")
# Catch the hashtags
hashtag_re = re.compile(r"^#\S+|\s#\S+")
# Catch any URL
url_re = re.compile(
    "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"
)
# url_re = re.compile(r'(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w\.-]*)*\/?\S')

# Catch the RT
rt_re = re.compile("RT")


def remove_entities(txt, compiled_regex, substitute=""):
    """
    Replace mentions from the txt tweet and add them into a list to be able to keep them for later
    """
    entities = compiled_regex.search(txt)
    txt = compiled_regex.sub(substitute, txt)
    return txt


def preprocess_text(sentence):
    mentions = None
    urls = None
    hashtags = None
    rt_status = None
    try:
        # lowering all words
        sentence = sentence.lower()
        # Replace User mentions tags
        sentence, mentions = remove_entities(sentence, mention_re, "__MENTION__")

        # Remove URL
        sentence, urls = remove_entities(sentence, url_re, "__URL__")
        # Resolve the urls
        # urls = [resolve_url(url) for url in urls]
        # Remove Hashtags
        # We keep the hashtags as they can be normal words
        # sentence = remove_entities(sentence, hashtag_re, '__HASHTAG__')

        hashtags = hashtag_re.findall(sentence)

        sentence = sentence.replace("#", "")

        # Remove RT symbol
        # sentence = remove_entities(sentence, rt_re, ' ')

        # Remove punctuations and numbers
        sentence = re.sub("[^a-zA-Z]", " ", sentence)

        # Single character removal
        sentence = re.sub(r"\s+[a-zA-Z]\s+", " ", sentence)

        # Removing multiple spaces
        sentence = re.sub(r"\s+", " ", sentence)
    except Exception as e:
        print(e)
        print("Sentence: {} - Type {}".format(sentence, type(sentence)))
        raise
    return sentence, mentions, urls, hashtags, rt_status
