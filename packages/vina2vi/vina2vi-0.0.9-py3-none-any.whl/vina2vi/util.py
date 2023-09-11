import string
import unicodedata
from dataclasses import dataclass, field

import unidecode
import torch
#from datasets import Dataset, DatasetDict
from tokenizers import normalizers


@dataclass(frozen=True)
class Vietnamese:
    ambiguous_chars = {
        "a": "aáảãàạâấẩẫầậăắẳẵằặ",
        "d": "dđ",
        "e": "eéẻẽèẹêếểễềệ",
        "i": "iíỉĩìị",
        "o": "oóỏõòọôôốổỗồộơớởỡờợ",
        "u": "uúủũùụưứửữừự",
        "y": "yýỷỹỳỵ",
    }
    for k, v in ambiguous_chars.items():
        ambiguous_chars[k] = unicodedata.normalize("NFC", v)
    lowers = "".join(ambiguous_chars.values()) + string.ascii_lowercase
    uppers = lowers.upper()
    lowers = set(lowers)
    uppers = set(uppers)
    chars = lowers.union(uppers)
    puncs = ",.!?_()[]-'\": \t\n"
    puncs = unicodedata.normalize("NFC", puncs)
    puncs = set(puncs)

    vowels = set()
    for c in "aeiouy":
        vowels.update(ambiguous_chars[c])
    consonants = "bcdđghklmnprstvx" + "fjwz" # ph, th?
    consonants = set(consonants)

    @staticmethod
    def is_foreign(string):
        string = string.strip()
        if string == "":
            print("empty string!!!")
            return False

        string = unicodedata.normalize("NFC", string)
        char_set = set(string)
        intersection = char_set.intersection(Vietnamese.chars | Vietnamese.puncs)
        return len(intersection) < len(char_set)


def rm_diacritics(s):
    return unidecode.unidecode(s)


def normalize(s, form:str="NFD"):
    return unicodedata.normalize(form ,s)


cased_vi_normalizer = normalizers.Sequence([
    normalizers.NFC(),
    normalizers.StripAccents(),
])
uncased_vi_normalizer = normalizers.Sequence([
    normalizers.Lowercase(),
    cased_vi_normalizer,
])
cased_vina_normalizer = normalizers.Sequence([
    normalizers.NFD(),
    normalizers.StripAccents(),
    normalizers.Replace("đ", "d"),
    normalizers.Replace("Đ", "D"),
])
uncased_vina_normalizer = normalizers.Sequence([
    normalizers.Lowercase(),
    normalizers.NFD(),
    normalizers.StripAccents(),
    normalizers.Replace("đ", "d"),
])

ansi_code = {
    #"red":    "\033[91m",
    "red":    "\x1b[91m",
    "green":  "\033[92m",
    "yellow": "\033[93m",
    "blue":   "\033[94m",
    "pink":   "\033[95m",
    "teal":   "\033[96m",
    "grey":   "\033[97m",
    #"reset":    "\x1b[0m",
    "reset":    "\033[0m",
}


#def roberta_infer_viz(
#    datasets,
#    *,
#    topk: int = 5,
#    device=torch.device("cpu"),
#    tokenizer,
#    model,
#    data_collator,
#):
#    if "test" in datasets:
#        ds = datasets["test"]
#    else:
#        ds = datasets["train"]
#    sample = ds.shuffle().select([0])[0]
#
#    collated = data_collator([sample])
#    collated = {k: v.to(device) for k, v in collated.items()}
#    model.to(device)
#
#    masked_text = tokenizer.decode(collated["input_ids"][0])
#    mask_token_indices = torch.where(collated["input_ids"] == tokenizer.mask_token_id)[1]
#
#    labels = collated["labels"][0]
#    gt_ids = sample["input_ids"][:]
#    #for i, label in enumerate(labels):
#    #    if label != -100:
#    #        gt_ids[i] = label
#    #gt_tokens = tokenizer.convert_ids_to_tokens(
#    #    gt_ids, skip_special_tokens=False,
#    #)
#    #for i, (label, token) in enumerate(zip(labels, gt_tokens)):
#    #    if i in mask_token_indices:
#    #        if token[0] == 'Ġ':
#    #            token = f' {ansi_code["green"]}{token[1:]}{ansi_code["reset"]}'
#    #        else:
#    #            token = f'{ansi_code["green"]}{token}{ansi_code["reset"]}'
#    #    else:
#    #        if token[0] == 'Ġ':
#    #            token = f' {token[1:]}'
#    #        else:
#    #            continue
#    #    gt_tokens[i] = token
#
#    #gt_text = "".join(
#    #    t for t in gt_tokens if t not in tokenizer.special_tokens_map.values())
#
#
#    token_logits = model(**collated).logits
#    mask_token_logits = token_logits[0, mask_token_indices, :]
#    # Pick the <mask> candidates with the highest logits
#    top_k_token_ids = torch.topk(mask_token_logits, topk, dim=1).indices.numpy()
#
#    #print("(masked)")
#    #print(f'"{masked_text}"', end="\n\n")
#
#    #print("(gt)")
#    #print(f'"{gt_text}"', end="\n\n")
#
#    for kk in range(topk):
#        pred_ids = collated["input_ids"][0].numpy()
#        infer_token_ids = top_k_token_ids[:, kk]
#        pred_ids[mask_token_indices] = infer_token_ids
#        pred_tokens = tokenizer.convert_ids_to_tokens(
#            pred_ids, skip_special_tokens=False,)
#        for i, token in enumerate(pred_tokens):
#            if i in mask_token_indices:
#                gt_token_id = sample["labels"][i]
#                gt_token = tokenizer.convert_ids_to_tokens(gt_token_id)
#                if token[0] == 'Ġ':
#                    token = f' {ansi_code["red"]}{token[1:]}{ansi_code["reset"]}{ansi_code["green"]}{gt_token}{ansi_code["reset"]}'
#                else:
#                    token = f'{ansi_code["red"]}{token}{ansi_code["reset"]}{ansi_code["green"]}{gt_token}{ansi_code["reset"]}'
#            else:
#                if token[0] == 'Ġ':
#                    token = f'{token[1:]}'
#                else:
#                    if token in tokenizer.special_tokens_map.values():
#                        token = ""
#                    elif token in string.punctuation:
#                        pass
#                    else:
#                        token = f' {token}'
#            pred_tokens[i] = token
#
#        #for i, (label, token) in enumerate(zip(labels, pred_tokens)):
#        #    if i in mask_token_indices:
#        #        if token[0] == 'Ġ':
#        #            token = f' {ansi_code["red"]}{token[1:]}{ansi_code["reset"]}'
#        #        else:
#        #            token = f'{ansi_code["red"]}{token}{ansi_code["reset"]}'
#        #    else:
#        #        if token[0] == 'Ġ':
#        #            token = f' {token[1:]}'
#        #        else:
#        #            pass
#        #    pred_tokens[i] = token
#
#        pred_text = "".join(t for t in pred_tokens)
#        print(f'(pred {kk})')
#        print(f'"{pred_text}"')
#        print()
#
#
#def bert_infer_viz(
#    datasets,
#    *,
#    topk: int = 5,
#    device=torch.device("cpu"),
#    tokenizer,
#    model,
#    data_collator,
#):
#    """
#    args
#        data_collator, aka collate_fn
#    """
#    if isinstance(datasets, DatasetDict):
#        if "test" in datasets:
#            ds = datasets["test"]
#        else:
#            ds = datasets["train"]
#    elif isinstance(datasets, Dataset):
#        ds = datasets
#    sample = ds.shuffle().select([0])[0]
#    #print(f'tokenizer.decode(sample["labels"]) = "{tokenizer.decode(sample["labels"])}"')
#    collated = data_collator([sample])
#    # Put on the same assigned device
#    collated = {k: v.to(device) for k, v in collated.items()}
#    masked_text = tokenizer.decode(collated["input_ids"][0])
#    #mask_token_indices = torch.where(collated["input_ids"] == tokenizer.mask_token_id)[1]
#    #mask_token_indices = mask_token_indices.cpu().numpy()
#    mask_token_indices = torch.where(collated["input_ids"] == tokenizer.mask_token_id)[1].cpu().numpy()
#
#    labels = sample["labels"]
#    gt_ids = sample["input_ids"][:]
#    #for i, label in enumerate(labels):
#    #    if label != -100:
#    #        gt_ids[i] = label
#    #gt_tokens = tokenizer.convert_ids_to_tokens(
#    #    gt_ids, skip_special_tokens=False,
#    #)
#    #print(f'{gt_tokens = }')
#    #for i in mask_token_indices:
#    #    token = gt_tokens[i]
#    #    if token[:2] == '##':
#    #        token = f'{ansi_code["green"]}{token[2:]}{ansi_code["reset"]}'
#    #    else:
#    #        token = f' {ansi_code["green"]}{token}{ansi_code["reset"]}'
#    #    gt_tokens[i] = token
#    #
#    #gt_text = " ".join(
#    #    t for t in gt_tokens if t not in tokenizer.special_tokens_map.values())
#
#    model.to(device)
#    token_logits = model(**collated).logits
#    mask_token_logits = token_logits[0, mask_token_indices, :]
#    # Pick the <mask> candidates with the highest logits
#    top_k_token_ids = torch.topk(mask_token_logits, topk, dim=1).indices.cpu().numpy()
#
#
#    #print("(masked)")
#    #print(f'"{masked_text}"', end="\n\n")
#
#    #print("(gt)")
#    #print(f'"{gt_text}"', end="\n\n")
#
#    for kk in range(topk):
#        pred_ids = collated["input_ids"].cpu().numpy()[0]
#        infer_token_ids = top_k_token_ids[:, kk]
#        pred_ids[mask_token_indices] = infer_token_ids
#        pred_tokens = tokenizer.convert_ids_to_tokens(
#            pred_ids, skip_special_tokens=False,)
#        #print(f'{pred_tokens = }')
#        for i, token in enumerate(pred_tokens):
#            if i in mask_token_indices:
#                gt_token_id = sample["labels"][i]
#                gt_token = tokenizer.convert_ids_to_tokens(gt_token_id)
#                if token[:2] == '##':
#                    token = f'{ansi_code["red"]}{token[2:]}{ansi_code["reset"]}{ansi_code["green"]}{gt_token}{ansi_code["reset"]}'
#                else:
#                    token = f' {ansi_code["red"]}{token}{ansi_code["reset"]}{ansi_code["green"]}{gt_token}{ansi_code["reset"]}'
#            else:
#                if token[:2] == '##':
#                    token = f'{token[2:]}'
#                else:
#                    if token in tokenizer.special_tokens_map.values():
#                        token = ""
#                    elif token in string.punctuation:
#                        pass
#                    else:
#                        token = f' {token}'
#            pred_tokens[i] = token
#
#        pred_text = "".join(t for t in pred_tokens)
#        print(f'(pred {kk})')
#        print(pred_text)
#        print()
#
#
#def phobert_infer_viz(
#    datasets,
#    *,
#    topk: int = 5,
#    device=torch.device("cpu"),
#    tokenizer,
#    model,
#    data_collator,
#):
#    if "test" in datasets:
#        ds = datasets["test"]
#    else:
#        ds = datasets["train"]
#    sample = ds.shuffle().select([0])[0]
#    collated = data_collator([sample])
#    # Put on the same assigned device
#    collated = {k: v.to(device) for k, v in collated.items()}
#    masked_text = tokenizer.decode(collated["input_ids"][0])
#    mask_token_indices = torch.where(collated["input_ids"] == tokenizer.mask_token_id)[1]
#    #collated["input_ids"][0, mask_token_indices] = tokenizer.mask_token_id
#
#    #labels = sample["labels"]
#    #print(f'{tokenizer.decode(sample["labels"]) = }')
#    #gt_ids = sample["input_ids"][:]
#
#    model.to(device)
#    token_logits = model(**collated).logits
#    mask_token_logits = token_logits[0, mask_token_indices, :]
#    # Pick the <mask> candidates with the highest logits
#    top_k_token_ids = torch.topk(mask_token_logits, topk, dim=1).indices.numpy()
#
#    #print("(masked)")
#    #print(f'"{masked_text}"', end="\n\n")
#
#    print("(gt)")
#    print(f'"{tokenizer.decode(sample["labels"])}"', end="\n\n")
#
#    for kk in range(topk):
#        pred_ids = collated["input_ids"][0].numpy()
#        infer_token_ids = top_k_token_ids[:, kk]
#        pred_ids[mask_token_indices] = infer_token_ids
#        pred_tokens = tokenizer.convert_ids_to_tokens(
#            pred_ids, skip_special_tokens=False,)
#        #print(f'{pred_tokens = }')
#        for i, token in enumerate(pred_tokens):
#            if i in mask_token_indices:
#                gt_token_id = sample["labels"][i]
#                gt_token = tokenizer.convert_ids_to_tokens(gt_token_id)
#                if token[-2:] == '@@':
#                    token = f'{ansi_code["red"]}{token[:-2]}{ansi_code["reset"]}{ansi_code["green"]}{gt_token}{ansi_code["reset"]}'
#                else:
#                    token = f'{ansi_code["red"]}{token}{ansi_code["reset"]}{ansi_code["green"]}{gt_token}{ansi_code["reset"]} '
#            else:
#                if token[-2:] == '@@':
#                    token = f'{token[:-2]}'
#                else:
#                    if token in tokenizer.special_tokens_map.values():
#                        token = ""
#                    elif token in string.punctuation:
#                        token = f'{token} '
#                    else:
#                        token = f'{token} '
#            pred_tokens[i] = token
#
#        pred_text = "".join(t for t in pred_tokens)
#        print(f'(pred {kk})')
#        print(pred_text)
#        print()
