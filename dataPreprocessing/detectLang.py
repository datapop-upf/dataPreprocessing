"""
Detect the lang of a text string and return the lang tag and the associated proba.
Use Fasttext
"""
import fasttext
import numpy as np

lang_detector = fasttext.load_model(PRETRAINED_FASTTEXT_MODEL)

# Source: https://amitness.com/2019/07/identify-text-language-python/
def get_lang(txt, lang_detector):
    try:
        label, proba = lang_detector(txt)

        if len(label) == 1:  # Only one language detected
            label = label[0].replace("__label__", "")
            proba = proba[0]
        elif len(label) > 1:  # Several language detected
            label = "multilangue"
            proba = np.mean(proba)  # Get the mean of the proba as not interested in it

    except Exception as e:
        print(e)
        label, proba = None, None
    return label, proba
