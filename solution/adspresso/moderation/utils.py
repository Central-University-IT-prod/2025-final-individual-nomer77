from moderation.models import BlackWord
from natasha import Doc, Segmenter, NewsEmbedding, NewsMorphTagger, MorphVocab
import re

segmenter = Segmenter()
emb = NewsEmbedding()
morph_tagger = NewsMorphTagger(emb)
morph_vocab = MorphVocab()


def normalize_word(word):
    doc = Doc(word)
    doc.segment(segmenter)
    doc.tag_morph(morph_tagger)
    for token in doc.tokens:
        token.lemmatize(morph_vocab)
        return token.lemma
    return word

def get_bad_words() -> set:
    return set(BlackWord.objects.values_list('word', flat=True))

def check_bad_words(text, bad_words: None | list = None):
    if bad_words is None:
        bad_words = get_bad_words()
    words = re.findall(r'\w+', text.lower())
    normalized_words = [normalize_word(word) for word in words]
    for word in normalized_words:
        if word in bad_words:
            return True
    return False