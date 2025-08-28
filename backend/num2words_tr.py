# backend/num2words_az.py
import re
import logging
import num2words

logger = logging.getLogger(__name__)


def turkish_number_to_words(text):
    """Convert numbers to Turkish words with proper grammar rules"""
    text = text.replace(".", ",")  # Standardize to Turkish decimal format

    # First handle fractions (a/b)
    def convert_fraction(match):
        num_str = match.group()
        try:
            if "/" in num_str:
                parts = num_str.split("/")
                if len(parts) == 2:
                    numerator = float(parts[0])
                    denominator = float(parts[1])

                    # Special cases
                    if numerator == 1 and denominator == 2:
                        return "yarım"
                    if numerator == 1 and denominator == 4:
                        return "çeyrek"

                    # Convert to decimal value to determine proper speech form
                    decimal_value = numerator / denominator

                    # If it's a simple half (x.5), use "buçuk" form
                    if decimal_value % 1 == 0.5 and decimal_value >= 1:
                        whole_part = int(decimal_value)
                        return f"{num2words.num2words(whole_part, lang='tr')} buçuk"

                    # Otherwise use fraction format
                    return f"{num2words.num2words(numerator, lang='tr')} bölü {num2words.num2words(denominator, lang='tr')}"
        except:
            pass
        return num_str

    # Handle fractions first
    text = re.sub(r"\d+\s*/\s*\d+", convert_fraction, text)

    # Then handle decimals and other numbers
    def convert_number(match):
        num_str = match.group().strip()

        # Skip if this was already handled as a fraction
        if "/" in num_str:
            return num_str

        # Handle currency
        if re.match(r"^[₺$€£]\s*\d", num_str) or re.match(r"\d\s*[₺$€£]", num_str):
            return handle_currency(num_str)

        # Handle percentage
        if num_str.endswith("%"):
            base_num = num_str[:-1].strip()
            try:
                float_val = float(base_num.replace(",", "."))
                words = num2words.num2words(float_val, lang="tr")
                return f"{words} yüzde"
            except:
                return num_str

        try:
            # Handle dates (keep as-is for date_to_turkish to process later)
            if re.match(r"\d{4}-\d{2}-\d{2}", num_str):
                return num_str

            # Handle time (keep as-is for time_to_turkish to process later)
            if re.match(r"\d{1,2}:\d{2}", num_str):
                return num_str

            # Process decimal numbers
            if "," in num_str or "." in num_str:
                num_value = float(num_str.replace(",", "."))

                # Special case: 0.5 with following noun becomes "yarım"
                if num_value == 0.5:
                    # Check if followed by a noun (simplified check)
                    next_chars = text[
                        text.find(num_str)
                        + len(num_str) : text.find(num_str)
                        + len(num_str)
                        + 10
                    ]
                    if re.search(r"^\s*[a-zA-Z]", next_chars):
                        return "yarım"
                    return "sıfır virgül beş"

                # X.5 becomes "X buçuk" in speech
                if num_value % 1 == 0.5 and num_value >= 1:
                    whole = int(num_value)
                    return f"{num2words.num2words(whole, lang='tr')} buçuk"

                # Standard decimal format
                whole, decimal = str(num_value).split(".")
                whole_words = num2words.num2words(int(whole), lang="tr")
                decimal_words = num2words.num2words(int(decimal), lang="tr")
                return f"{whole_words} virgül {decimal_words}"

            # Regular integers
            num = int(num_str)

            # Special handling for years
            if 1800 <= num <= 2100:
                return f"{num2words.num2words(num, lang='tr')} yılı"

            return num2words.num2words(num, lang="tr")

        except Exception as e:
            logger.debug(f"Number conversion failed for '{num_str}': {str(e)}")
            return num_str

    return re.sub(r"([₺$€£]?\s*)?\d+([,.]\d+)?(%?)", convert_number, text)


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
