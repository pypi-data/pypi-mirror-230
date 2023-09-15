import tldextract
import nltk
import re
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

try:
    nltk.data.find("corpora/stopwords")
except LookupError:
    nltk.download("stopwords")

stemmer = PorterStemmer()
stop_words = stopwords.words("english")
stop_words.extend(
    [
        "page",
        "app",
        "user",
        "ltd",
        "co",
        "yes",
        "no",
        "pvt",
        "inc",
        "via",
        "refer",
        "websit",
        "site",
        "facebook",
        "twitter",
        "yahoo",
        "instagram",
        "googl",
        "new",
        "com",
        "org",
        "hi",
        "year",
        "ago",
        "wonder",
    ]
)
punctuation_translator = str.maketrans(
    dict.fromkeys("\"#$%&'()*+,-/:;<=>@[\\]^_`{|}~", " ")
)  # .?! removed frpm punctuations
punctuation_mapping = [(" .", "."), (" !", "!"), (" ?", "?")]
remove_parentheses_compile = re.compile(r"""[\(\[].*?[\)\]]""")
remove_trail_space_comma_compile2 = re.compile(r"""\s+,\s+""")
url_compile = r"""(?i)\b((?:https?://|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'\".,<>?«»""'']))"""
email_compile = r"""(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])"""
phone_compile = r"""(?:(?:\+?([1-9]|[0-9][0-9]|[0-9][0-9][0-9])\s*(?:[.-]\s*)?)?(?:\(\s*([2-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9])\s*\)|([0-9][1-9]|[0-9]1[02-9]|[2-9][02-8]1|[2-9][02-8][02-9]))\s*(?:[.-]\s*)?)?([2-9]1[02-9]|[2-9][02-9]1|[2-9][02-9]{2})\s*(?:[.-]\s*)?([0-9]{4})(?:\s*(?:#|x\.?|ext\.?|extension)\s*(\d+))?"""
contact_email_compile = r"""Contact Email (?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\]) |Official Facebook account for |home \| \- > """
emoji_pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "]+",
    flags=re.UNICODE,
)


def remove_emoji_patterns(text: str) -> str:
    return emoji_pattern.sub(r"", text)


def restrict_to_ascii(text: str) -> str:
    return text.encode("ascii", "ignore").decode()


def extract_domain(url: str) -> str:
    # get domain from input e.g. all below would output: nantenergy.com
    # www.nantenergy.com - https://nantenergy.com/ - https://nantenergy.com/ - lauren@nantenegery.com - nantenegery.com
    return tldextract.extract(url).registered_domain


def remove_one_characters(text: str) -> str:
    return re.sub(r"\b[a-zA-Z]\b", "", text)


def remove_numbers(text: str) -> str:
    return re.sub(r" \d+", "", text)


def remove_punctuation(text: str) -> str:
    return text.translate(punctuation_translator)


def remove_stopwords_and_stem(text: str) -> str:
    paras = [p for p in text.split("\n") if p.strip()]
    processed_paras = []
    for para in paras:
        word_tokens = word_tokenize(para)
        # filtered_text = [word for word in word_tokens if word not in stop_words]
        filtered_text = [stemmer.stem(word) for word in word_tokens]
        filtered_text = [word for word in filtered_text if word not in stop_words]
        temp = " ".join(filtered_text)
        processed_paras.append(temp)

    return " \n ".join(processed_paras)


def remove_sub_super_scripts(text: str) -> str:
    return "".join([i for i in text if ord(i) < 128])


def remove_non_ascii(text: str) -> str:
    return "".join(
        char for char in text if ord(char) < 128 and ord(char) not in [8364, 163]
    )


def remove_parantheses(text: str) -> str:
    return re.sub(remove_parentheses_compile, "", text)


def remove_trail_space_comma(text: str) -> str:
    return re.sub(remove_trail_space_comma_compile2, ", ", text)


def replace_sentence_seperators(text: str) -> str:
    for k, v in punctuation_mapping:
        text = text.replace(k, v)
    return text


def detect_urls(text: str) -> list:
    try:
        url = re.findall(url_compile, text)
        urls = [x[0] for x in url]
    except:
        pass
    return urls


def detect_emails(text: str) -> list:
    try:
        email = re.findall(email_compile, text)
        emails = [x[0] for x in email]
    except:
        pass
    return emails


def detect_contact_emails(text: str) -> list:
    try:
        contact_email = re.findall(contact_email_compile, text)
        contact_emails = [x[0] for x in contact_email]
    except:
        pass
    return contact_emails


def detect_phones(text: str) -> list:
    try:
        phone = re.findall(phone_compile, text)
        phones = [x[0] for x in phone]
    except:
        pass
    return phones
