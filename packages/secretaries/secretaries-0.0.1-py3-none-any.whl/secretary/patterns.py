tags_default = {
    'split_token': '[[split]]',
    'linebreak_placeholder': 'linebreak_placeholder',
        'corpus_names': 'names_corpus',
        'regex_names': 'names_regex',
        'split': 'data_split',
        'unsplit': 'data',
        'masked': 'masked',
    'se': {
        'name': 'namn',
        'names': 'namn',
        'masks': 'masker',
        'non_names': 'tveksamma',
        'events': 'händelser',
        'orgs': 'organisationer',
        'locations': 'platser',
        'masked': 'maskerade',
        'split': 'uppdelad',
        'wd': 'Sökväg: placeholder',
        'gpu': 'Antal tillgängliga GPU:er: placeholder',
        'corpus': 'korpus',
        'started': 'Startade vid placeholder',
        'data_size': 'Datamängden innehåller placeholder rader',
        'found_masked': 'Hittade alla ord att maskera i texterna vid placeholder',
        'started_ner': 'Påbörjade named entity recognition (NER) vid placeholder',
        'elapsed': 'Tog placeholder minuter',
        'found_entities': 'Hittade alla namngivna enheter vid placeholder',
        'replaced_masks_and_entities': 'Maskerade ord och ersatte namngivna enheter vid placeholder',
        'replaced_regex': 'Ersatte enligt mönster (regex) vid placeholder',
        'corpus_count': 'Antal unika namn från Svensktext: placeholder',
        'replaced_corpus': "Ersatte namn från Svensktext vid placeholder",
        'saving': 'Sparar data...',
        'summary_ner': 'Hittade placeholder namn med hjälp av NER',
        'summary_corpus': 'Hittade placeholder namn ur Svensktext',
        'summary_regex': 'Ersatte placeholder potentiella namn från hälsningsfraser',
        'summary_nb': 'Obs. att antalet ersatta ord med respektive metod är färre',
        'summary_masked': 'Maskerade placeholder ord och/eller ordföljder',
        'ended': 'Skriptet klart vid placeholder'
    },
    'en': {
        'name': 'name',
        'names': 'names',
        'masks': 'masks',
        'non_names': 'ambiguous',
        'events': 'events',
        'orgs': 'orgs',
        'locations': 'locations',
        'masked': 'masked',
        'split': 'split',
        'wd': 'Working directory: placeholder',
        'gpu': 'Number of GPUs available: placeholder',
        'corpus': 'corpus',
        'started': 'Started at placeholder',
        'data_size': 'Data has placeholder rows',
        'found_masked': 'Found all the words to mask in the texts at placeholder',
        'started_ner': 'Started named entity recognition (NER) at placeholder',
        'elapsed': 'placeholder minutes elapsed',
        'found_entities': 'Found all the named entities @ placeholder',
        'replaced_masks_and_entities': 'Masked words and replaced named entities at placeholder',
        'replaced_regex': 'Replaced according to regex patterns placeholder',
        'corpus_count': 'Count of unique names from online corpus: placeholder',
        'replaced_corpus': "Replaced names from corpus at placeholder",
        'summary_regex': 'Replaced placeholder potential names from regex patterns',
        'saving': 'Saving data...',
        'summary_ner': 'Found placeholder names using NER',
        'summary_corpus': 'Found placeholder names from the corpus',
        'summary_nb': 'NB: The number of words actually replaced by each method is less',
        'summary_masked': 'Masked placeholder words and/or multi-word tokens',
        'ended': 'Script executed at placeholder'
    }}

gatunr = r"(?i)(gata(n)?|väg(en)?|stig(en)?|gränd(en)?|torg(et)?|esplanad(en)?|boulevard(en)?|allé(n)?|alle(n)?|plan|plats(en)?|promenad(en)?|gång(en)?|bron|kajen|hill|ängen|byn|ringen|stråket|gården|liden|backen|parken|triangeln|dockan|v\.?)(\s*\d+\s?(?:\w{1})?)([\s]?[\-&]+[\s]?\w{1})?\b"
numrerade_klamrar = r"(?i)<+\d+>+"
html_tecken = r"&#\d{1,5};"
html_taggar = r"<[^<>]*>([^<>]*)</[^<>]>"
url = r"(?i)(?:https?://)?(?:www\w*)"
mvh = "((?i)" + r"|".join([r"mvh",
                           r"Om mer information behövs",
                           r"Kontakta anmälare på",
                           r"Med vänlig hälsn[\w]*\b",
                           r"tack från ",
                           r"vänliga hälsn[\w]*\b",
                           r"bästa hälsn[\w]*\b",
                           r"Hälsn[\w]*\b",
                           r"Hälsar[\w]*\b",
                           r"Vänligen",
                           r"Hilsen",
                           r"Regards",
                           r"Best wishes",
                           r"All the best",
                           r"All the very best",
                           ]) + r")([^\w]{1,3})([^.]*)"
snedstreck = r"([/]+[^.]*$)"
initialer = r"|".join([
                 r"(\b)([A-Ö]{2}[^.\w]*$)",
                 r"(?i)([?\.!][\s]?)([\w]{1,2})[\s]?$"
               ])
epost = r"|".join([r"([\w\.-]+@[\w\.-]+)",
                   r"((?:[\w.-]*\s?){1,3}(?:@|\bat\b|snabela|snabel-a|snabel a)\s?(?:[\w.-]*\s?){1,2}(?:\.|punkt|dot)\s?\w{2,3})"])
regnr = r"(\b[A-Ö]{3}\s*\d{2,3}\w?\b)"
nr = r"(([0-9\.\s-]){5,20})"

null_token = "[empty]"
null_list = [null_token]
