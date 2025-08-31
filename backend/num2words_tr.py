import re
import logging
import num2words

logger = logging.getLogger(__name__)


def turkish_number_to_words(text):
    """Convert numbers to Turkish words with proper grammar rules"""

    # FIRST handle special date formats (YYYY-MM-DD)
    def convert_date_hyphen(match):
        date_str = match.group()
        return date_to_turkish_hyphen(date_str)
    
    text = re.sub(r"\b\d{4}-\d{2}-\d{2}\b", convert_date_hyphen, text)

    # Then handle time expressions
    def convert_time(match):
        time_str = match.group()
        return time_to_turkish(time_str)

    text = re.sub(r"\b(?:0?[0-9]|1[0-9]|2[0-3]):[0-5][0-9]\b", convert_time, text)

    def convert_date(match):
        date_str = match.group()
        return date_to_turkish(date_str)

    text = re.sub(r"\b\d{2}\.\d{2}\.\d{4}\b", convert_date, text)

    # Handle numbers with proper context detection
    def convert_number(match):
        num_str = match.group().strip()

        # Skip if already handled as time
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
            # CRITICAL FIX 1: Handle English-style decimals FIRST (15.5)
            if "." in num_str and "," not in num_str and not re.match(r"\d{1,3}(\.\d{3})+", num_str):
                try:
                    whole, decimal = num_str.split(".")
                    # CRITICAL FIX: Handle .5 as "buçuk" (2.5 → iki buçuk)
                    if decimal == "5" and len(decimal) == 1:  # Only exact .5 cases
                        whole_num = int(whole)
                        if whole_num == 0:
                            result = "yarım"  # 0.5 → yarım
                        else:
                            whole_words = num2words.num2words(whole_num, lang="tr")
                            result = f"{whole_words} buçuk"
                    else:
                        whole_words = num2words.num2words(int(whole), lang="tr")
                        decimal_words = num2words.num2words(int(decimal), lang="tr")
                        result = f"{whole_words} nokta {decimal_words}"
                except Exception as e:
                    logger.debug(f"English decimal conversion failed: {e}")
                    result = num_str

            # Handle Turkish formatting (thousand separators)
            elif "." in num_str and "," in num_str:
                parts = num_str.split(",")
                whole_part = parts[0].replace(".", "")
                decimal_part = parts[1]
                whole_words = num2words.num2words(int(whole_part), lang="tr")
                decimal_words = num2words.num2words(int(decimal_part), lang="tr")
                result = f"{whole_words} virgül {decimal_words}"

            # Handle other formats
            else:
                # Handle fractions (like 1/2)
                if "/" in num_str:
                    try:
                        numerator, denominator = map(int, num_str.split("/"))
                        if denominator == 2:
                            if numerator == 1:
                                result = "yarım"
                            else:
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

                # Handle Turkish decimal (comma)
                elif "," in num_str:
                    whole, decimal = num_str.split(",")
                    whole_words = num2words.num2words(int(whole), lang="tr")
                    decimal_words = num2words.num2words(int(decimal), lang="tr")
                    result = f"{whole_words} virgül {decimal_words}"

                # Handle Turkish thousand separators
                elif "." in num_str and re.match(r"\d{1,3}(\.\d{3})+", num_str):
                    whole_part = num_str.replace(".", "")
                    result = num2words.num2words(int(whole_part), lang="tr")

                # Handle regular integers
                else:
                    num = int(num_str)
                    if 1800 <= num <= 2100:
                        result = f"{num2words.num2words(num, lang='tr')} yılı"
                    else:
                        result = num2words.num2words(num, lang="tr")

            # Add currency/percentage
            if is_currency:
                currency_names = {"₺": "lira", "$": "dolar", "€": "avro", "£": "sterlin"}
                currency_name = currency_names.get(currency_symbol, "para")
                result = f"{result} {currency_name}"
            if is_percentage:
                result = f"{result} yüzde"

            return result

        except Exception as e:
            logger.debug(f"Number conversion failed for '{num_str}': {str(e)}")
            return match.group()

    # CRITICAL FIX 2: Regex priority order - fractions → English decimals → Turkish numbers
    text = re.sub(
        r"\b[₺$€£]?\s*(?:\d+/\d+|\d+\.\d+|\d{1,3}(?:\.\d{3})*(?:,\d+)?)\s*[₺$€£]?\b", 
        convert_number, 
        text
    )

    return text


def date_to_turkish_hyphen(date_str):
    """Handle YYYY-MM-DD format dates"""
    try:
        year, month, day = map(int, date_str.split("-"))
        months = {
            1: "ocak", 2: "şubat", 3: "mart", 4: "nisan", 5: "mayıs", 6: "haziran",
            7: "temmuz", 8: "ağustos", 9: "eylül", 10: "ekim", 11: "kasım", 12: "aralık"
        }
        day_word = num2words.num2words(day, lang="tr")
        month_word = months[month]
        year_word = num2words.num2words(year, lang="tr")
        return f"{day_word} {month_word} {year_word}"
    except Exception as e:
        logger.debug(f"Hyphen date conversion failed: {e}")
        return date_str


def date_to_turkish(date_str):
    """Handle DD.MM.YYYY format dates"""
    try:
        day, month, year = map(int, date_str.split("."))
        months = {
            1: "ocak", 2: "şubat", 3: "mart", 4: "nisan", 5: "mayıs", 6: "haziran",
            7: "temmuz", 8: "ağustos", 9: "eylül", 10: "ekim", 11: "kasım", 12: "aralık"
        }
        day_word = num2words.num2words(day, lang="tr")
        month_word = months[month]
        year_word = num2words.num2words(year, lang="tr")
        return f"{day_word} {month_word} {year_word}"
    except Exception as e:
        logger.debug(f"Dot date conversion failed: {e}")
        return date_str


def time_to_turkish(time_str):
    """Convert time string to natural Turkish time expressions"""
    try:
        hours, minutes = map(int, time_str.split(":"))
        hours = hours % 24

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
            hour_word = num2words.num2words(hours, lang="tr")
            minute_word = num2words.num2words(minutes, lang="tr")
            return f"{hour_word} {minute_word} geçiyor"

        else:
            minutes_to_next = 60 - minutes
            next_hour = (hours + 1) % 24
            hour_word = num2words.num2words(next_hour, lang="tr")
            minute_word = num2words.num2words(minutes_to_next, lang="tr")
            return f"{hour_word}e {minute_word} var"

    except Exception as e:
        logger.debug(f"Time conversion failed: {e}")
        return time_str
