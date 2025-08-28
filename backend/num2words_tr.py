# backend/num2words_az.py
import re
import logging
import num2words

logger = logging.getLogger(__name__)


def turkish_number_to_words(text):
    """Convert numbers to Turkish words with advanced formatting."""
    text = text.replace(".", ",")

    def convert_number(match):
        num_str = match.group()

        if re.match(r"^[₺$€£]\s*\d", num_str) or re.match(r"\d\s*[₺$€£]", num_str):
            return handle_currency(num_str)

        if num_str.endswith("%"):
            base_num = num_str[:-1]
            try:
                float_val = float(base_num.replace(",", "."))
                words = num2words.num2words(float_val, lang="tr")
                return f"{words} yüzde"
            except:
                return num_str

        if "/" in num_str:
            try:
                numerator, denominator = map(int, num_str.split("/"))
                if denominator == 2:
                    if numerator == 1:
                        return "yarım"
                    return f"{num2words.num2words(numerator, lang='tr')} buçuk"
                return f"{num2words.num2words(numerator, lang='tr')} bölü {num2words.num2words(denominator, lang='tr')}"
            except:
                return num_str

        try:
            if re.match(r"\d{4}-\d{2}-\d{2}", num_str):
                return date_to_turkish(num_str)
            if re.match(r"\d{1,2}:\d{2}", num_str):
                return time_to_turkish(num_str)

            if "," in num_str:
                whole, decimal = num_str.split(",")
                whole_words = num2words.num2words(int(whole), lang="tr")
                decimal_words = num2words.num2words(int(decimal), lang="tr")
                return f"{whole_words} virgül {decimal_words}"
            else:
                num = int(num_str)
                if 1800 <= num <= 2100:
                    return f"{num2words.num2words(num, lang='tr')} yılı"
                return num2words.num2words(num, lang="tr")
        except Exception as e:
            logger.debug(f"Number conversion failed: {e}")
            return num_str

    return re.sub(r"([₺$€£]?\s*)?\d+([,.]\d+)?(%?)", convert_number, text)


def azerbaijani_number_to_words(text):
    """Convert numbers to Azerbaijani style using Turkish base."""
    text = text.replace(".", ",")

    def convert_number(match):
        num_str = match.group()

        if re.match(r"^[₼$€£]\s*\d", num_str) or re.match(r"\d\s*[₼$€£]", num_str):
            return handle_currency(num_str, azerbaijani=True)

        if num_str.endswith("%"):
            base_num = num_str[:-1]
            try:
                float_val = float(base_num.replace(",", "."))
                words = num2words.num2words(float_val, lang="tr")
                words = turkish_to_azerbaijani_numbers(words)
                return f"{words} faiz"
            except:
                return num_str

        if "/" in num_str:
            try:
                numerator, denominator = map(int, num_str.split("/"))
                if denominator == 2:
                    if numerator == 1:
                        return "yarım"
                    return f"{num2words.num2words(numerator, lang='tr')} buçuk"
                num_words = f"{num2words.num2words(numerator, lang='tr')} bölü {num2words.num2words(denominator, lang='tr')}"
                return turkish_to_azerbaijani_numbers(num_words)
            except:
                return num_str

        try:
            if re.match(r"\d{4}-\d{2}-\d{2}", num_str):
                return date_to_azerbaijani(num_str)
            if re.match(r"\d{1,2}:\d{2}", num_str):
                return time_to_azerbaijani(num_str)

            if "," in num_str:
                whole, decimal = num_str.split(",")
                whole_words = num2words.num2words(int(whole), lang="tr")
                decimal_words = num2words.num2words(int(decimal), lang="tr")
                whole_words = turkish_to_azerbaijani_numbers(whole_words)
                decimal_words = turkish_to_azerbaijani_numbers(decimal_words)
                return f"{whole_words} nöqtə {decimal_words}"
            else:
                num = int(num_str)
                if 1800 <= num <= 2100:
                    words = num2words.num2words(num, lang="tr")
                    words = turkish_to_azerbaijani_numbers(words)
                    return f"{words} ili"
                words = num2words.num2words(num, lang="tr")
                return turkish_to_azerbaijani_numbers(words)
        except Exception as e:
            logger.debug(f"Azerbaijani number conversion failed: {e}")
            return num_str

    return re.sub(r"([₼$€£]?\s*)?\d+([,.]\d+)?(%?)", convert_number, text)


def turkish_to_azerbaijani_numbers(text):
    replacements = {
        "dört": "dörd",
        "yedi": "yeddi",
        "sekiz": "səkkiz",
        "dokuz": "doqquz",
        "yirmi": "iyirmi",
        "kırk": "qırx",
        "elli": "əlli",
        "yetmiş": "yetmiş",
        "seksen": "səksən",
        "doksan": "doxsan",
        "bin": "min",
    }
    words = text.split()
    converted = []
    for word in words:
        base = word.rstrip("süüıliıööüüüüü")  # Simplified stem
        if base in replacements:
            converted_word = replacements[base]
            if word.endswith("lar") or word.endswith("ler"):
                converted_word += "lar"
            elif word.endswith("da") or word.endswith("de"):
                converted_word += word[-2:]
            converted.append(converted_word)
        else:
            converted.append(word)
    return " ".join(converted)


def handle_currency(amount_str, azerbaijani=False):
    symbol = ""
    amount = ""
    if amount_str[0] in ["$", "€", "£", "₺", "₼"]:
        symbol, amount = amount_str[0], amount_str[1:]
    elif amount_str[-1] in ["$", "€", "£", "₺", "₼"]:
        amount, symbol = amount_str[:-1], amount_str[-1]
    else:
        return amount_str

    try:
        if "," in amount:
            whole, decimal = amount.split(",")
            whole_words = num2words.num2words(int(whole), lang="tr")
            decimal_words = (
                num2words.num2words(int(decimal), lang="tr") if int(decimal) > 0 else ""
            )
            if decimal_words:
                amount_words = f"{whole_words} tam {decimal_words}"
            else:
                amount_words = whole_words
        else:
            amount_words = num2words.num2words(int(amount), lang="tr")

        currency_names = {
            "$": "dolar",
            "€": "avro",
            "£": "sterlin",
            "₺": "lira",
            "₼": "manat",
        }
        currency_name = currency_names.get(symbol, "para")

        if azerbaijani:
            amount_words = turkish_to_azerbaijani_numbers(amount_words)
            currency_name = {"dolar": "dollar", "avro": "evro"}.get(
                currency_name, currency_name
            )
            return f"{amount_words} {currency_name}"
        return f"{amount_words} {currency_name}"
    except:
        return amount_str


def date_to_turkish(date_str):
    try:
        year, month, day = map(int, date_str.split("-"))
        months = {
            1: "ocak",
            2: "şubat",
            3: "mart",
            4: "nisan",
            5: "mayıs",
            6: "haziran",
            7: "temmuz",
            8: "ağustos",
            9: "eylül",
            10: "ekim",
            11: "kasım",
            12: "aralık",
        }
        day_word = num2words.num2words(day, lang="tr")
        month_word = months[month]
        year_word = num2words.num2words(year, lang="tr")
        return f"{day_word} {month_word} {year_word} yılı"
    except:
        return date_str


def date_to_azerbaijani(date_str):
    try:
        year, month, day = map(int, date_str.split("-"))
        months = {
            1: "yanvar",
            2: "fevral",
            3: "mart",
            4: "aprel",
            5: "may",
            6: "iyun",
            7: "iyul",
            8: "avqust",
            9: "sentyabr",
            10: "oktyabr",
            11: "noyabr",
            12: "dekabr",
        }
        day_word = turkish_to_azerbaijani_numbers(num2words.num2words(day, lang="tr"))
        month_word = months[month]
        year_word = turkish_to_azerbaijani_numbers(num2words.num2words(year, lang="tr"))
        return f"{day_word} {month_word} {year_word} ili"
    except:
        return date_str


def time_to_turkish(time_str):
    try:
        hours, minutes = map(int, time_str.split(":"))
        h_word = lambda x: num2words.num2words(x, lang="tr")
        if minutes == 0:
            return f"{h_word(hours)} tam"
        elif minutes == 30:
            return f"{h_word(hours)} buçuk"
        elif minutes < 30:
            return f"{h_word(hours)} {h_word(minutes)} geçiyor"
        else:
            next_h = (hours + 1) % 24
            mins_left = 60 - minutes
            return f"{h_word(mins_left)} var {h_word(next_h)}"
    except:
        return time_str


def time_to_azerbaijani(time_str):
    try:
        hours, minutes = map(int, time_str.split(":"))
        h_word = lambda x: turkish_to_azerbaijani_numbers(
            num2words.num2words(x, lang="tr")
        )
        m_word = lambda x: turkish_to_azerbaijani_numbers(
            num2words.num2words(x, lang="tr")
        )
        if minutes == 0:
            return f"{h_word(hours)} tam"
        elif minutes == 30:
            return f"{h_word(hours)} yarım"
        elif minutes < 30:
            return f"{h_word(hours)} {m_word(minutes)} keçib"
        else:
            next_h = (hours + 1) % 24
            mins_left = 60 - minutes
            return f"{m_word(mins_left)} qalmış {h_word(next_h)}"
    except:
        return time_str
