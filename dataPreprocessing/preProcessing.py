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
rt_re = re.compile("^RT", re.IGNORECASE)


def remove_entities(txt, compiled_regex, substitute=""):
    """
    Replace mentions from the txt tweet and add them into a list to be able to keep them for later
    """
    entities = compiled_regex.findall(txt)
    txt = compiled_regex.sub(substitute, txt)
    print(entities)
    return txt, entities


def preprocess_tweet(sentence):
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
        sentence, rt_status = remove_entities(sentence, rt_re, " ")
        # Transform into boolean to return True or False if catch RT
        rt_status = bool(rt_status)

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
    return {
        "tweet": sentence,
        "mentions": mentions,
        "urls": urls,
        "hashtags": hashtags,
        "rt_status": rt_status,
    }


def main():

    print(
        preprocess_tweet(
            "RT: test for checking the return of @mention_1 and #Hasthags_321"
        )
    )


if __name__ == "__main__":
    main()
