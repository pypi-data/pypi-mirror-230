import unicodedata

from tqdm.auto import tqdm
from rapidfuzz.distance import Levenshtein

from vina2vi.util import normalize


def get_avg_sim(
    preds,
    gts,
    *args,
    n_strings: int|None = None,
):
    """
    args
        preds
            a sequence of strings, predictions of some model
        gts
            a sequence of groundtruth strings (i.e. with diacritics)
        n_strings
            the number of strings contained in preds (or gts)
    """
    norm_preds = (normalize(s) for s in preds)
    norm_gts = (normalize(s) for s in gts)
    sims = []
    if n_strings is None and "__len__" in dir(gts):
        n_strings = len(gts)
    for i, (p, g) in tqdm(enumerate(zip(norm_preds, norm_gts)), total=n_strings):
        sims.append(Levenshtein.normalized_similarity(p, g))

    if not "i" in locals():
        print("Cannot compute avg_sim. Maybe you have an empty preds or gts?")
        return None

    # n_instances and n_strings are synonyms in this function
    n_instances = i+1
    avg_sim = sum(sims)/n_instances
    return avg_sim


