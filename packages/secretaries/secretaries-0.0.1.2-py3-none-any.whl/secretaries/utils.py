import re
import os
import sys
import math
import glob
import shutil
import warnings
import polars as pl
import urllib.request
from textwrap import wrap
from importlib_resources import files, as_file

def init_folders(wd, lang, tags):
    corpus_folder = os.path.join(wd, tags[lang]['corpus'] + '_' + lang)
    input_folder = os.path.join(wd, 'input_' + lang)
    names_folder = os.path.join(input_folder, tags[lang]['names'])
    non_names_folder = os.path.join(input_folder, tags[lang]['non_names'])
    masks_folder = os.path.join(input_folder, tags[lang]['masks'])
    output_folder = os.path.join(wd, 'output_' + lang)
    starter_kits = {'se': 'startkit_ickenamn_se', 
                    'en': 'starter_kit_safe_words_en'}
    copy_starter_kit = not os.path.exists(non_names_folder)
    folders = [corpus_folder, input_folder, output_folder, names_folder, non_names_folder, masks_folder]
    for f in folders:
        if not os.path.exists(f):
            os.mkdir(f)
    if copy_starter_kit:
        with as_file(files('secretaries').joinpath(starter_kits[lang] + '.csv')) as starter_kit:
            shutil.copy(starter_kit, os.path.join(non_names_folder, starter_kits[lang] + '.csv'))
    return(tuple(folders))


textwidth = 80

def border():
    """Print a border to the console"""

    print("-" * textwidth)

def progress():
    """Print something, for now (might be replaced by some kind of a progress bar)"""

    print("...")

def print_status_(tags, string_id, replacement):
    """Print to the console in a specific language"""

    print('\n'.join(wrap(re.sub('placeholder', str(replacement), tags[string_id]), width = textwidth)))

def unsplit(df, id_column, text_column):
    df = df.select([id_column, id_column + "2", 'sub_id', text_column]) \
            .groupby(id_column) \
            .agg(pl.col(text_column).str.concat(delimiter = ""))
    return(df)
            # .with_columns(pl.col(id_column).str.replace("_\d+$", "").keep_name()) \

def ingest(folder, colname = 'token', sep = ',', drop_duplicates = True, keep_other_columns = False):
    """Read a folder of csv files into a Polars dataframe"""

    folder = re.sub(r"/$", "", folder)
    queries = []
    for file in glob.glob(f"{folder}/*.csv"):
        q = pl.scan_csv(file, separator = sep)
        queries.append(q)

    try:
        tokens = pl.concat(queries)

        if keep_other_columns:
            tokens = tokens.with_columns(pl.col(colname) \
                                 .cast(pl.Utf8) \
                                 .str.replace_all(r'\(|\)', '') \
                                 .str.to_lowercase())
        else:
            tokens = tokens.select(pl.col(colname) \
                                 .cast(pl.Utf8) \
                                 .str.replace_all(r'\(|\)', '') \
                                 .str.to_lowercase())

        if drop_duplicates:
            tokens = tokens.unique(subset = [colname])
    except ValueError:
        tokens = pl.LazyFrame({colname: []})

    return(tokens.collect())


def find_masks_(mask_set, max_sequence_length, null_list, text_column, x):
    """Find tokens to be masked."""

    masks = []
    ngrams = []
    txt = re.sub(r"[.,!?]", "", x[text_column])

    for i in range(1,max_sequence_length + 1)[::-1]:
        matches = re.findall(r"(?:[^a-öA-Ö1-9]|^)(?=((?:[a-öA-Ö1-9]+[^a-öA-Ö1-9]*){1,%s}))" % i, txt)
        ngrams.extend(matches)
    ngrams = [n.rstrip() for n in ngrams]
    # Ensure unique ngrams, sorted descending by string length
    ngrams = sorted(list(set(ngrams)), key = len)[::-1]
    for token in ngrams:
        if token.lower() in mask_set:
            masks.append(token)
    if len(masks) == 0:
        return null_list
    masks = sorted(masks, key = len, reverse = True)
    return(masks)

def find_long_masks_(long_mask_set, x):
    """Find multi-word masks"""

    long_masks = [token for token in long_mask_set if token in x]
    long_masks = sorted(long_masks, key = len, reverse = True)
    return(long_masks)


def mask_(text_column, x):
    """Replace masked tokens with numbered placeholders."""

    txt = x[text_column]
    for i,token in enumerate(x['masks']):
        txt = re.sub(r'(?i)\b' + re.escape(token) + r'\b', '<' + str(i) + '>', txt)
    return(txt)


def unmask_(text_column, x):
    """Re-substitute the original masked words for the numbered placeholders."""

    txt = x[text_column]
    for i,token in enumerate(x['masks']):
        txt = re.sub(r'(?i)\<' + re.escape(str(i)) + r'\>', token, txt)
    return(txt)


def remove_entities_(text_column, tags, x):
    """Remove names, ie entities flagged as people, from the text and replace these with placeholders."""

    txt = x[text_column]
    name_tag = '[' + tags['name'] + ']'
    for entity in x['entities']:
        if entity['entity_group'] == "PER":  
            # remove names and trailing characters (such as genitive -s)
            pattern = re.compile("".join([r"(?i)\b", entity["word"], r"'?s?\b"]))
            txt = pattern.sub(' ' + name_tag, txt)
    return(txt)

def corpus_collect_names_(name_set, null_list, x):
    """Find tokens that are names according to the corpus."""

    # TODO: genitiv-s!
    names = [token for token in x if (token.lower() in name_set) or (re.sub(r"s$", "", token.lower()) in name_set)]
    if len(names) == 0:
        names = null_list
    return(names)

def corpus_replace_names_(text_column, tags, x):
    """Replace names with placeholders in text using the corpus."""

    txt = x[text_column]
    name_tag = '[ ' + tags['name'] + ' ]'
    for token in x['names_from_corpus']:
        txt = re.sub(r'(?i)\b' + re.escape(token) + r'\b', name_tag, txt)
    return txt

def insert_splits_(split_length, split_token, text):
    """Splits a text into chunks of at most split_length tokens. Useful for constraints like the 512 word limit of BERT models."""

    tokens = re.split(pattern = r'\b', string = text)
    # If the number of tokens is less than split_length, do nothing
    if len(tokens) <= split_length:
        return(text)

    is_punctuation = list(map(bool, [re.search(r"^[?.!]+\s?", t) for t in tokens]))
    if not any(is_punctuation):
        # If no [?.!] present, split by comma.
        is_comma = list(map(bool, [re.search(r"^,+\s?", t) for t in tokens]))
        print(sum(is_comma))
        if any(is_comma):
            is_punctuation = is_comma
            warnings.warn('No punctuations in text, splitting by comma instead.')
            print(is_punctuation)
        else:
            # If no punctuation present, do not split text
            sys.exit('No punctuations or comma in text - exiting.')
    punctuation_indices = [0] + [i for i,v in enumerate(is_punctuation) if v]

    # Find intervals that are smaller than the specified split_length
    split_indices = []
    previous_index = 0
    target = split_length
    while target < len(tokens):
        # print('target: ' + str(target))
        checkpoints = [i - target for i in punctuation_indices]
        closest_index = len(list(filter(lambda x: x <= 0, checkpoints))) - 1
        # print('closest_index: ' + str(closest_index) + ' >> ' + str(punctuation_indices[closest_index]))
        split_indices.append(punctuation_indices[closest_index])
        # print('difference at closest_index: ' + str(target - punctuation_indices[closest_index]))
        if closest_index == previous_index:
            sys.exit('Loop failed. Cannot split the text, since two adjacent punctuations are more than split_length tokens apart. Increase the split_length parameter. ')
        else:
            target += split_length - (target - punctuation_indices[closest_index])
        # print('split_indices: ' + str(split_indices))
        previous_index = closest_index

    # Insert split token after punctuation at the computed indices, 
    # then glue the text back together
    offset = 1
    for s in split_indices:
        tokens.insert(s+offset, split_token)
        offset += 1

    return ''.join(tokens)



def load_corpus(corpus_path, lang, min_n_persons):
    """Load name corpus for a specific language"""
    if lang == 'se':
        svensktext_filer =  "efternamn.csv fornamn-kvinnor.csv fornamn-man.csv tilltalsnamn-kvinnor.csv tilltalsnamn-man.csv".split()
        if os.path.isfile(corpus_path + '/svensktext.csv'): 
            print('Namnen från Svensktext finns redan nedladdade.')
            svensktext = ingest(corpus_path, colname = 'name', 
                                drop_duplicates = False, keep_other_columns = True)
        else:
            # if not os.path.exists(path + '/corpus_se'): 
            print(f'Laddar ner namnen från Svensktext till {corpus_path}') 
            base_url = r"https://raw.githubusercontent.com/peterdalle/svensktext/master/namn/"
            svensktext = pl.DataFrame({'name': list(), 'persons': list()}) \
                              .with_columns(pl.col('name').cast(pl.Utf8),
                                            pl.col('persons').cast(pl.Int64))

            for file in svensktext_filer:
                f = pl.read_csv(base_url + file)
                svensktext.vstack(f, in_place = True)
            # Save locally
            svensktext.write_csv(os.path.join(corpus_path, 'svensktext.csv'))
            # Read Corpus. Sum the number of people over multiple occurrences, since the same token can be used as a forename or a surname. 
        svensktext = svensktext \
            .groupby('name').agg(pl.col('persons').sum()) \
            .filter(pl.col('persons') >= min_n_persons) \
            .with_columns(pl.col('name').str.to_lowercase())

        corpus_names = set(svensktext.select(pl.col('name')).to_series().to_list())
        return(corpus_names)

    if lang == 'en':
        if os.path.isfile(corpus_path + '/corpus_en.csv'): 
            corpus_names = set(ingest(corpus_path, colname = 'name',
                                  drop_duplicates = True, keep_other_columns = False) \
                            .select(pl.col('name')).to_series().to_list())
        else:
            # Download forename corpus by Mark Kantrowitz containing 7579 unique names
            # If used in production, consider constructing your own corpus from 
            # https://datashare.ed.ac.uk/handle/10283/3007 for example
            l = list()
            base_url = r"https://www.cs.cmu.edu/Groups/AI/util/areas/nlp/corpora/names/"
            for file in ['female.txt', 'male.txt']:
                file = base_url + file
                req = urllib.request.Request(file)
                resp = urllib.request.urlopen(req)
                text = resp.read().decode('utf-8')
                l.extend(text.split('\n')[6::])
            forenames = set([item.lower() for item in l if len(item) > 0])

            # Fetch Github user craigh411's list of the 1000 most common American surnames
            # https://gist.github.com/craigh411/19a4479b289ae6c3f6edb95152214efc
            file = r"https://gist.githubusercontent.com/craigh411/19a4479b289ae6c3f6edb95152214efc/raw/d25a1afd3de42f10abdea7740ed098d41de3c330/List%2520of%2520the%25201,000%2520Most%2520Common%2520Last%2520Names%2520(USA)"
            req = urllib.request.Request(file)
            resp = urllib.request.urlopen(req)
            surnames = resp.read().decode('utf-8').split(',\n')
            surnames = set([item.lower() for item in surnames if len(item) > 2])
            corpus_names = forenames.union(surnames)

            # n_unique_corpus = len(corpus_names)

            # Save locally
            pl.DataFrame({'name': list(corpus_names)}).write_csv(corpus_path + '/corpus_en.csv')

        return(corpus_names)
