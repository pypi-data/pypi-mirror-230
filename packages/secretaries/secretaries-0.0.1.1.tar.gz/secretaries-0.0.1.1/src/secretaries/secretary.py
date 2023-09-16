import sys
import logging
logging.disable(logging.WARNING) # disable WARNING, INFO and DEBUG logging everywhere
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# import html
import glob
import polars as pl
import re
import warnings
# import urllib.request
from transformers import pipeline, TFBertForTokenClassification, AutoTokenizer
import tensorflow as tf
from datetime import datetime
from functools import partial

from .patterns import *
from .utils import init_folders, border, progress, unsplit, ingest, find_masks_, find_long_masks_, mask_, remove_entities_, corpus_collect_names_, corpus_replace_names_, unmask_, insert_splits_, print_status_, load_corpus

def run(text = [], 
        csv = None, 
        data_delimiter = ",", 
        input_delimiter = ",", 
        id_column = 'id', 
        id_column_as_int = True,
        text_column = 'text', 
        n = None, 
        ner = True,
        corpus = True, 
        lang = 'se',
        names = list(),
        non_names = list(),
        masks = list(),
        single_text_mode = False,
        min_n_persons = 100, 
        max_sequence_length = 3, 
        remove_html = True,
        preserve_linebreaks = True,
        model_name = 'KB/bert-base-swedish-cased-ner'):
    """Main function for running the secretary
    
    Parameters
    ----------
    text : Optional[str | list(str)]
        Optional single text to process
    csv : Optional[str]
        Optional csv file containing the texts
    data_delimiter : Optional[str]
        The csv delimiter of the data (texts)
    input_delimiter : Optional[str]
        The csv delimiter of inputs (tokens)
    id_column : Optional[str]
        Name of the id column in the csv file, containing a unique id for each row
    id_column_as_int : Optional[bool]
        Whether or not to treat the id column as an integer, which helps with sorting
    text_column : Optional[str]
        Name of the column containing the texts
    n : Optional[int]
        Optionally read a subset of n rows of the data
    ner : Optional[bool]
        Whether or not to Run Named Entity Recognition (defaults to True)
    corpus : Optional[bool]
        Whether or not to do search and replace using the corpus (defaults to True)
    lang : str
        Which language to use (defaults to Swedish)
    names : Optional[list]
        Optional runtime list of tokens to add to the corpus as names
    non_names : Optional[list] 
        Optional runtime list of tokens not considered names, to exclude from the corpus
    masks : Optional[list]
        Optional runtime list of single or multi token words to hide from the algorithm and thus preserve from the substitutions
    single_text_mode : Optional[bool]
        Optionally return a single text. May be useful for setting up an api. 
    min_n_persons : Optional[int]
        An optional frequency threshold for corpus tokens. At present only available in Swedish. Defaults to 100. 
    max_sequence_length : Optional[int] 
        Given a list L and a text T, there are two ways of finding which tokens in L are present in T. One is to split T into parts of 1 through n token sequences and check whether each sequence is present in L. This makes sense for shorter sequences, mainly single token words. When searching for longer sequences, you end up with a lot of combinations of 1 through n tokens. It then becomes more efficient to iterate though L and do a literal search for it in T. The max_sequence_length arguments controls at what sequence length the latter method is used. Defaults to 3, meaning sequences of at most 3 tokens will be extracted from each text. You may opt for a lower setting depending on computational resources. A higher setting might make sense if you have a very long list of multi-word masks.  
    remove_html : Optional[bool]
        Whether or not to remove html tags. Defaults to True.
    preserve_linebreaks : Optional[bool]
        Whether or not to preserve linebreaks in the text(s). Defaults to True.
    model_name
        The name of the Transformers model and tokenizer used for Named Entity Recognition.

 """

    if not csv and not text: sys.stderr.write("Inga texter i datamängden... \n"); sys.exit(1)
    if text and type(text) == str: text = [text]
    if single_text_mode: text = [text[0]]
    if lang.lower() in "se swe swedish".split(): lang = 'se'
    if lang.lower() in "en eng english".split(): lang = 'en'
    if lang == 'en':
        # Set default English NER model, if none specified
        # You have the option of using a custom one from the Huggingface hub,
        # for example 'dslim/bert-large-NER' (depending on your hardware resources)
        if model_name == 'KB/bert-base-swedish-cased-ner':
            model_name = "dslim/bert-base-NER"

    tags = tags_default

    textwidth = 80
    print_status = partial(print_status_, tags[lang])

    path = os.getcwd()
    print_status('wd', path)

    corpus_path, input_folder, output_folder, _, _, _ = init_folders(path, lang, tags)

    output_folder = os.path.join(path, '_'.join(['output', lang]))
    if not os.path.exists(output_folder):
        os.mkdir(output_folder)

    input_folder = os.path.join(path, '_'.join(['input', lang]))
    if not os.path.exists(input_folder):
        os.mkdir(input_folder)

    names = list(map(lambda x: x.lower(), names))
    # Merge safe words in function call with safe words from input folder
    non_names = list(map(lambda x: x.lower(), non_names))
    non_names = set(non_names).union(set(ingest(input_folder + '/' + tags[lang]['non_names'], sep = input_delimiter).select(pl.col('token')).to_series().to_list()))

    # Make sure GPU is available
    print_status('gpu', len(tf.config.list_physical_devices('GPU')))

    ts_init = datetime.now()
    print_status('started', ts_init.strftime("%H:%M:%S"))

    if csv:
        df = pl.scan_csv(csv, separator = data_delimiter, 
                         n_rows = int(n) if n else None) \
                .with_columns(pl.col(id_column).cast(pl.Int32)) \
                .unique(subset = [id_column])
    else:
        df = pl.LazyFrame({id_column: range(len(text)), text_column: text})

    # Remove HTML tags before removing brackets in general
    if remove_html: 
        df = df.with_columns(pl.col(text_column) \
                             .str.replace_all(html_taggar, "$1"))
    if preserve_linebreaks: 
        df = df.with_columns(pl.col(text_column) \
                             .str.replace_all(r"\r|\n", tags["linebreak_placeholder"]))

    # Pre-processing in eager mode:
    # Split text into parts of at most 512 tokens (the BERT model word limit)
    # NB: punctuation also counts as tokens
    insert_splits = partial(insert_splits_, 512, tags["split_token"])
    df = df.collect() \
        .with_columns(pl.col(text_column).map_elements(insert_splits).keep_name()) \
        .with_columns(pl.col(text_column).str.split(tags["split_token"]).keep_name()) \
        .with_columns(pl.col(text_column).list.lengths().alias('n_splits')) \
        .lazy()

    # Remove brackets with numbers (eg <1>, <<5>>, <<<<<25>>>>>) so that 
    # they do not interfere with placeholders for masked words
    # Gather potential names from salutations
    # Remove street numbers, before street names are (most likely) masked by the user
    q = (
        df.with_columns(pl.int_ranges(0, 'n_splits').alias('sub_id')) \
        .explode([text_column, 'sub_id']) \
        .with_columns(pl.concat_str([pl.col(id_column),
                                     pl.col('sub_id')],
                                     separator = "_").alias(id_column + "2")) \
      .with_columns(pl.col(text_column).fill_null(pl.lit(null_token)) \
                        .str.replace(r"^$", null_token) \
                        .cast(pl.Utf8) \
                        .str.replace_all(numrerade_klamrar, "")) \
        .with_columns(pl.col(text_column) \
                      # .str.extract(mvh, group_index = 3) \
                      .str.extract_all(mvh) \
                      .alias('names_from_regex')) \
          .with_columns(pl.col('names_from_regex').fill_null([]), \
                        pl.col(text_column) \
                        .str.replace_all(gatunr, "$1").keep_name(), \
                        pl.col(text_column) \
                        .str.extract_all(r'\b[a-öA-Ö]+\b') \
                        .fill_null(null_list).alias('tokens'))
    )
    df = q.collect()

    initial_colnames = df.columns[:-2]

    nrows = df.select(pl.count())[0,0]
    print_status('data_size', nrows)

    masks = pl.DataFrame({'token': masks}).select(pl.col('token').cast(pl.Utf8).str.to_lowercase())
    masks = ingest(input_folder + '/' + tags[lang]['masks'], sep = input_delimiter) \
                        .with_columns(pl.col('token').cast(pl.Utf8)) \
                        .vstack(masks) \
                        .with_columns(pl.col('token') \
                                     .str.to_lowercase()) \
                        .unique(subset = ['token']) \
                        .with_columns(pl.col('token') \
                                     .str.extract_all(r"[a-öA-Ö]+") \
                                     .list.lengths().alias('antal_ord'))

    mask_set = set(masks.filter(pl.col('antal_ord') <= max_sequence_length) \
                   .select(pl.col('token')).to_series().to_list())

    long_mask_set = set(masks.filter(pl.col('antal_ord') > max_sequence_length) \
                   .select(pl.col('token')).to_series().to_list())

    find_masks = partial(find_masks_, mask_set, max_sequence_length, null_list, text_column)
    find_long_masks = partial(find_long_masks_, long_mask_set)


    # MASKING
    df_maskings = df.select(pl.col(id_column + "2"),
                            pl.col(text_column),
                            pl.struct([text_column, 'tokens']) \
                            .map_elements(find_masks) \
                            .alias("_masks")) \
                    .select(pl.col(id_column + "2"),
                            pl.col(text_column) \
                                  .map_elements(find_long_masks) \
                                  .alias('masks') \
                                  .list.concat('_masks')) \
                    .with_columns(pl.col('masks') \
                                    .fill_null([]))

    ts_masklookup = datetime.now()
    border()
    print_status("found_masked", ts_masklookup.strftime("%H:%M:%S"))
    print_status("elapsed", round((ts_masklookup - ts_init).seconds / 60,1))
    print_status("started_ner", datetime.now().strftime("%H:%M:%S"))
    progress()

    # NAMED ENTITY RECOGNITION
    remove_entities = partial(remove_entities_, text_column, tags[lang])
    if ner:
        model = TFBertForTokenClassification.from_pretrained(model_name)
        nlp = pipeline('ner', model=model, tokenizer=AutoTokenizer.from_pretrained(model_name, model_max_length=512), aggregation_strategy='max') 

        texter = df.select(pl.col(text_column).fill_null(pl.lit(null_token))) \
                           .to_series().to_list()

        ner_values = nlp(texter)


        null_entity = {'entity_group': '', 'score': 0, 'word': '', 'start': 0, 'end': 0}
        ner_values = [x if (len(x) > 0) else [null_entity] for x in ner_values]

        df_entities = df.select(pl.col(id_column + "2"),
                                pl.Series(name = 'entities', values = ner_values) \
                                    .fill_null([]))
    else:
        # DeprecationWarning: https://github.com/pola-rs/polars/pull/10461
        # with warnings.catch_warnings():
        #     warnings.simplefilter('ignore')
        df_entities = df.select(pl.col(id_column + "2"),
                                pl.lit([[]]).alias('entities'))

    ts_nerlookup = datetime.now()
    print_status("found_entities", ts_nerlookup.strftime("%H:%M:%S"))
    print_status("elapsed", round((ts_nerlookup - ts_masklookup).seconds / 60,1))
    progress()


    mask = partial(mask_, text_column)


    # Tokenize text once more, after masking
    df = df.join(df_maskings, on = id_column + "2", how = "left") \
                    .join(df_entities, on = id_column + "2", how = "left") \
            .with_columns(pl.col('masks').fill_null([]),
                          pl.col('entities').fill_null([])) \
                    .with_columns(pl.struct([text_column, "masks"]) \
                                    .map_elements(mask).alias(text_column)) \
                    .with_columns(pl.col(text_column) \
                                    .str.extract_all(r'\b[a-öA-Ö]+\b') \
                                    .fill_null(null_list).alias('tokens')) \
                    .with_columns(pl.struct([text_column, "entities"]) \
                                    .map_elements(remove_entities).alias(text_column))


    ts_sub = datetime.now()
    print_status("replaced_masks_and_entities", ts_sub.strftime("%H:%M:%S"))
    print_status("elapsed", round((ts_sub - ts_nerlookup).seconds / 60,1))
    border()


    df = df.with_columns(pl.col(text_column) \
                        .str.strip() \
                        .str.replace_all(r"\s+", " ") \
                        .str.replace_all(html_tecken, "") \
                        .str.replace_all(url, " [url] ") \
                        .str.replace_all(initialer, " [initialer] ") \
                        .str.replace_all(mvh, " [mvh] ") \
                        .str.replace_all(snedstreck, " [mvh] ") \
                        .str.replace_all(epost, " [epost] ") \
                        .str.replace_all(regnr, " [regnr] ") \
                        .str.replace_all(nr, " [nr] "))

    ts_patternsub = datetime.now()
    print_status("replaced_regex", ts_patternsub.strftime("%H:%M:%S"))
    print_status("elapsed", round((ts_patternsub - ts_sub).seconds / 60,1))
    border()

    if corpus:
        # Merge names in function call with names from input folder
        names = set(names).union(set(ingest(input_folder + '/' + tags[lang]['names'], sep = input_delimiter).select(pl.col('token')).to_series().to_list()))

        corpus_names = load_corpus(corpus_path, lang, min_n_persons)

        n_unique_corpus = len(corpus_names)
        print_status('corpus_count', n_unique_corpus)
        names = corpus_names.union(names)


        if lang == 'se' and not os.path.isfile(input_folder + tags[lang]['non_names'] + '/startkit_ickenamn.csv'):
            print('Ladda ner startkit från Github')


        names = names - non_names

        corpus_collect_names = partial(corpus_collect_names_, names, null_list)
        corpus_replace_names = partial(corpus_replace_names_, text_column, tags[lang])

        df = df.with_columns(pl.col("tokens") \
                             .map_elements(corpus_collect_names) \
                             .alias("names_from_corpus")) \
               .with_columns(pl.struct([text_column, 'names_from_corpus']) \
                                .map_elements(corpus_replace_names))

        ts_corpussub = datetime.now()
        print_status("replaced_corpus", ts_corpussub.strftime("%H:%M:%S"))
        print_status("elapsed", round((ts_corpussub - ts_patternsub).seconds / 60,1))
        border()
    else:
        df = df.with_columns(pl.lit([['']]).alias('names_from_corpus'))


    # Unmask the data, ie put the masked tokens back. 
    unmask = partial(unmask_, text_column)

    df = df.with_columns(pl.struct(["masks", text_column]) \
                         .map_elements(unmask).alias(text_column))

    # Remove null value placeholders.
    df = df.with_columns(pl.col(['masks','names_from_corpus']) \
                         .map_elements(lambda l: [x for x in l if x != null_token]))

    # Reinsert line breaks
    if preserve_linebreaks: 
        df = df.with_columns(pl.col(text_column) \
                             .str.replace_all(tags["linebreak_placeholder"], "\n", literal = True))

    print_status("saving", '')

    df_out = df.lazy() \
          .select(pl.col(initial_colnames)) \
          .with_columns(pl.when(pl.col(text_column) == null_token) \
                          .then(pl.lit("")) \
                          .otherwise(pl.col(text_column)).keep_name()) \
                          .sort(id_column + "2")

    if id_column_as_int:
        df_out = df_out.with_columns(pl.col(id_column).cast(pl.Int32))

    # Write data, with long texts split
    df_out.sort([id_column, 'sub_id']) \
          .collect() \
          .write_csv(output_folder + '/data_' + tags[lang]['split'] + '.csv')

    # Write data, with long texts restored
    unsplit(df_out.sort(id_column) \
        .collect(), id_column, text_column) \
        .write_csv(output_folder + '/' + tags['unsplit'] + '.csv')


    # SUMMARIZE AND SAVE: 

    # Names from regex
    df_regex = df.lazy() \
                 .filter(pl.col('names_from_regex').is_not_null()) \
                 .filter(pl.col('names_from_regex').list.lengths() > 0) \
                 .collect()
    if df_regex.shape[0] > 0:
        df_regex = df_regex \
                  .explode('names_from_regex') \
                  .select(pl.col('names_from_regex') \
                          .str.extract(mvh, group_index = 3) \
                          .keep_name()) \
                  .group_by('names_from_regex') \
                  .count().rename({'names_from_regex': 'token'}) \
                  .sort('count', descending = True)

        df_regex.write_csv(output_folder + '/' + tags[lang]['names'] + '_regex.csv')
    else:
        df_regex = pl.DataFrame({'token': '', 'count': 0})

    if corpus:
        # Names from corpus
        df_corpus = df.lazy() \
                      .filter(pl.col('names_from_corpus').is_not_null()) \
                      .filter(pl.col('names_from_corpus').list.lengths() > 0) \
                      .collect()
        if df_corpus.shape[0] > 0:
            df_corpus = df_corpus \
                      .explode('names_from_corpus') \
                      .group_by('names_from_corpus') \
                      .count().rename({'names_from_corpus': 'token'}) \
                      .sort('count', descending = True)
        else:
            df_corpus = pl.DataFrame({'token': '', 'count': 0})
        df_corpus.write_csv(output_folder + '/' + tags[lang]['names'] + 
                                '_' + tags[lang]['corpus'] + '.csv')


    # Named entities
    if ner:
        df_ner = df.lazy() \
                   .filter(pl.col('entities').list.lengths() > 0) \
                   .filter(pl.col('entities').is_not_null()) \
                   .select(pl.col('entities')).explode('entities') \
                   .unnest('entities') \
                   .drop(['score', 'start', 'end']) \
                   .filter(pl.col('word').is_not_null()) \
                   .group_by(['word','entity_group']) \
                   .count().rename({'word': 'token'}) \
                   .sort('count', descending = True)


        # PER - names
        df_ner_per = df_ner.filter(pl.col('entity_group') == 'PER').drop('entity_group').collect()
        df_ner_per.write_csv(output_folder + '/' + tags[lang]['names'] + '_ner.csv')

        # ORG - organizations and corporations
        df_ner.filter(pl.col('entity_group') == 'ORG').drop('entity_group') \
              .collect().write_csv(output_folder + '/' + tags[lang]['orgs'] + '_ner.csv')

        # EVN - events
        df_ner.filter(pl.col('entity_group') == 'EVN').drop('entity_group') \
              .collect().write_csv(output_folder + '/' + tags[lang]['events'] + '_ner.csv')

        # LOC - locations
        df_ner.filter(pl.col('entity_group') == 'LOC').drop('entity_group') \
              .collect().write_csv(output_folder + '/' + tags[lang]['locations'] + '_ner.csv')

    # Save all the maskings found in the text(s), if any
    # DeprecationWarning: https://github.com/pola-rs/polars/pull/10461
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        maskings = df_maskings.select(pl.col('masks')).explode('masks') \
                  .filter(pl.col('masks') != null_list) \
                  .group_by('masks') \
                  .count().rename({'masks': 'token'}) \
                  .sort('count', descending = True)
    maskings.write_csv(output_folder + '/' + tags[lang]['masked'] + '.csv')

    border()
    if ner:
        n_names_ner = df_ner_per.select(pl.sum('count'))[0,0] 
        print_status("summary_ner", n_names_ner)
    if corpus:
        n_names_corpus = df_corpus.select(pl.sum('count'))[0,0]
        print_status("summary_corpus", n_names_corpus)

    n_maskings = maskings.select(pl.count())[0,0]
    print_status('summary_nb', '')
    progress()
    print_status('summary_masked', n_maskings)
    n_names_regex = df_regex.select(pl.sum('count'))[0,0]
    print_status('summary_regex', n_names_regex)

    ts_end = datetime.now()
    print_status('ended', ts_end.strftime("%H:%M:%S"))
    print_status("elapsed", round((ts_end - ts_init).seconds / 60, 1))

    if single_text_mode:
        return unsplit(df, id_column = id_column, 
                       text_column = text_column)[text_column].to_list()[0]
    else:
        return(df)




# TODO
# Ange dependencies i requirements.txt
# Vid behov: spara ner "startkit" i arbetsmapparna
# Övrig dokumentation?
# Paketera paket
# Utforma test i test-mappen
# Fixa Readme.md-fil
# Pusha till er1kb:s Github, därefter forka från Malmö stads



# KLART
# Paketera startkit med ickenamn
# Se över kommentarer och filnamn och använd ett språk
# Dokumentera huvudfunktionens argument
# Uppdatera till Python 3.9
# Kolla filers existens? - Detta görs redan när korpuset laddas, i övrigt inga obligatoriska filer
# "Peter" maskeras men hamnar ändå under output_se/namn_corpus.csv... Löst: skapar tokens på nytt efter maskering.
# Fixa hjälpfunktion som i tur och ordning går igenom nödvändiga mappar (uppdelat på språk) och skapar vid behov
# Skriv bara maskerade om ord har maskerats, dvs tabellen inte är tom. Nej - skriv fil oavsett. 
# Separera input-mapp (input_se, input_en) + parameterisera mappnamnen + korpus på svenska
# Möjliggör att specificera egna taggar. Separera taggar och övriga inställningar/meningar, så att användaren inte kan mixtra med de senare. Struntar i denna... 
# Flytta ut inläsning av corpus till extern hjälpfunktion
# Dubbelkolla hur dubbelnamn hanteras (Sven-Erik etc.)
# Separera output-mappar (output_se, output_en)
# Se över användandet av platshållare (null_token, null_list)
# Ge återkoppling på svenska eller engelska
# Svenska eller engelska taggar
# Ladda bara ner relevanta filer från Svensktext, inte hela korpuset
# Spara engelskt namnkorpus lokalt
# Ta bort null_token/null_list från corpus_names
# linebreak_placeholder hamnar i regex_names.csv - möjligt att undvika?  
# Möjliggör att mata in namn, icke-namn och maskeringar som argument till funktionen, för att kunna mata in detta manuellt i textrutor i ett webbgränssnitt. Sammanfoga dessa extra inmatningar med underlaget i mapparna (a.union(b))
# Fixa att maskeringar i början eller slutet av texten räknas mångdubbelt
# Dubbelkolla om det blir flera hälsningar per text och i så fall om kolumnen är i rätt format (list(str) istället för str) - names_from_regex behöver skapas med str.extract_all istället för str.extract nu när en text kan innehålla flera hälsningsfraser
# Ge möjlighet att specificera namn under input/names, så att engelskspråkiga användare kan bygga ett eget korpus. Icke-namn trumfar namn om samma ord förekommer i båda mängderna. 
# Fixa fel där df_corpus blir tomt och programmet får panik, dvs garantera att df_corpus inte är tom om inget namn hittas i korpuset
# Om en lång text analyseras - fixa så att hälsningsfraser inte tar bort resten av texten, dvs byt ut (.*$) i hälsnings-regex
# Sätt argument för språk (svenska/engelska)
# Fixa gatunr (ersättning gjordes men resultatet sparades inte)
# single_text_mode - spara ingen data utan returnera en enskild text
# Ge möjlighet att välja bort ner och corpus (t ex för felsökning eller ingen gpu tillgänglig)
# Fixa genitiv-s - Adolf flaggas men inte Adolfs
# Ge användaren möjlighet att välja separator för csv-filer, både för data och underlag
# Ge möjlighet att ta bort eller bevara radbrytningar
# Splitta texter i delar om max 512 ord
# Sortera korrekt på ID-kolumn innan data sparas, om ID är heltal
# Använd paket för att göra line wrap på text

# SKIPPAT
# Ta bort krav på kolumnhuvudet "token" i csv-filer?
# Ev. lägga alla parametrar i en toml-fil? 
# Ev. lägga till smeknamn

# Små bokstäver i mest_flaggade, för att undvika en massa dubbletter.
# Does not remove initials after brackets: "Finns också på [epost]  eb" 
# The cased bert model does not identify lowercase names as such
# --> Use SpaCy to pick up "proper nouns" (PROPN) which have not been flagged as people or locations?! 
# www addresses?! 
# Obfuscate gendered pronouns? 


