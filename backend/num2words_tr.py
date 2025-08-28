# backend/num2words_az.py
import re
import logging
import num2words

logger = logging.getLogger(__name__)


def turkish_number_to_words(text):
    """Convert numbers to Turkish words with proper grammar rules"""

    # First handle time expressions (critical to process before individual numbers)
    def convert_time(match):
        time_str = match.group()
        return time_to_turkish(time_str)

    # Match time in HH:MM format (more specific pattern)
    text = re.sub(r"\b(?:0?[0-9]|1[0-9]|2[0-3]):[0-5][0-9]\b", convert_time, text)

    def convert_date(match):
        date_str = match.group()
        return date_to_turkish(date_str)

    text = re.sub(r"\b\d{2}.\d{2}.\d{4}\b", convert_date, text)

    # Handle numbers with Turkish formatting
    def convert_number(match):
        num_str = match.group().strip()

        # Skip if this was already handled as a time
        if ":" in num_str:
            return num_str

        # Handle currency symbols
        is_currency = False
        currency_symbol = ""
        if num_str[0] in ["₺", "$", "€", "£"]:
            currency_symbol = num_str[0]
            num_str = num_str[1:].strip()
            is_currency = True
        elif num_str[-1] in ["₺", "$", "€", "£"]:
            currency_symbol = num_str[-1]
            num_str = num_str[:-1].strip()
            is_currency = True

        # Handle percentage
        is_percentage = False
        if num_str.endswith("%"):
            num_str = num_str[:-1].strip()
            is_percentage = True

        try:
            # Handle numbers with Turkish formatting (thousand separators)
            if "." in num_str and "," in num_str:
                # This is a number with thousand separators and decimal (e.g., 1.234,56)
                parts = num_str.split(",")
                whole_part = parts[0].replace(".", "")  # Remove thousand separators
                decimal_part = parts[1]

                whole_words = num2words.num2words(int(whole_part), lang="tr")
                decimal_words = num2words.num2words(int(decimal_part), lang="tr")
                result = f"{whole_words} virgül {decimal_words}"

            # Handle other number formats
            else:
                # Handle fractions (like 1/2)
                if "/" in num_str:
                    try:
                        numerator, denominator = map(int, num_str.split("/"))
                        if denominator == 2:
                            if numerator == 1:
                                result = "yarım"
                            else:
                                # Critical fix: 3/2 = 1.5, not 3.5
                                decimal_value = numerator / denominator
                                if decimal_value % 1 == 0.5:
                                    whole_part = int(decimal_value)
                                    result = f"{num2words.num2words(whole_part, lang='tr')} buçuk"
                                else:
                                    result = f"{num2words.num2words(numerator, lang='tr')} bölü {num2words.num2words(denominator, lang='tr')}"
                        else:
                            result = f"{num2words.num2words(numerator, lang='tr')} bölü {num2words.num2words(denominator, lang='tr')}"
                    except:
                        result = num_str

                # Handle decimal numbers (with comma as decimal separator)
                elif "," in num_str:
                    whole, decimal = num_str.split(",")
                    whole_words = num2words.num2words(int(whole), lang="tr")
                    decimal_words = num2words.num2words(int(decimal), lang="tr")
                    result = f"{whole_words} virgül {decimal_words}"

                # Handle numbers with thousand separators (no decimal)
                elif "." in num_str and re.match(r"\d{1,3}(\.\d{3})+", num_str):
                    whole_part = num_str.replace(".", "")
                    result = num2words.num2words(int(whole_part), lang="tr")

                # Handle regular integers
                else:
                    num = int(num_str)

                    # Special handling for years
                    if 1800 <= num <= 2100:
                        result = f"{num2words.num2words(num, lang='tr')} yılı"
                    else:
                        result = num2words.num2words(num, lang="tr")

            # Add currency or percentage back if needed
            if is_currency:
                currency_names = {
                    "₺": "lira",
                    "$": "dolar",
                    "€": "avro",
                    "£": "sterlin",
                }
                currency_name = currency_names.get(currency_symbol, "para")
                result = f"{result} {currency_name}"
            if is_percentage:
                result = f"{result} yüzde"

            return result

        except Exception as e:
            logger.debug(f"Number conversion failed for '{num_str}': {str(e)}")
            return match.group()

    # Match numbers in Turkish format (critical improvement to regex)
    text = re.sub(
        r"\b[₺$€£]?\s*\d{1,3}(?:\.\d{3})*(?:,\d+)?\s*[₺$€£]?\b", convert_number, text
    )

    return text


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

        return f"{amount_words} {currency_name}"
    except:
        return amount_str


def date_to_turkish(date_str):
    try:
        day, month, year = map(int, date_str.split("."))
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
        return f"{day_word} {month_word} {year_word}"
    except:
        return date_str


def time_to_turkish(time_str):
    """Convert time string to natural Turkish time expressions (CORRECTED)"""
    try:
        hours, minutes = map(int, time_str.split(":"))
        hours = hours % 24  # Normalize to 0-23

        # CRITICAL FIX: Handle leading zeros in hours properly
        # In Turkish, 07:00 is just "yedi" not "sıfır yedi"

        if minutes == 0:
            hour_word = num2words.num2words(hours, lang="tr")
            return f"{hour_word} tam"

        elif minutes == 15:
            next_hour = (hours + 1) % 24
            next_hour_word = num2words.num2words(next_hour, lang="tr")
            return f"{next_hour_word}e çeyrek var"

        elif minutes == 30:
            hour_word = num2words.num2words(hours, lang="tr")
            return f"{hour_word} buçuk"

        elif minutes == 45:
            next_hour = (hours + 1) % 24
            next_hour_word = num2words.num2words(next_hour, lang="tr")
            return f"{next_hour_word}e çeyrek kala"

        elif minutes < 30:
            # CORRECT TURKISH FORMAT: "yediye beş var" for 07:05
            # NOT "sıfır yedi sıfır beş"
            hour_word = num2words.num2words(hours, lang="tr")
            minute_word = num2words.num2words(minutes, lang="tr")
            return f"{hour_word} {minute_word} "

        else:  # minutes > 30 and not 45
            # CORRECT TURKISH FORMAT: "sekize beş var" for 07:55
            minutes_to_next = 60 - minutes
            next_hour = (hours + 1) % 24
            hour_word = num2words.num2words(next_hour, lang="tr")
            minute_word = num2words.num2words(minutes_to_next, lang="tr")
            return f"{hour_word}e {minute_word} var"

    except Exception as e:
        logger.debug(f"Time conversion failed: {e}")
        return time_str
