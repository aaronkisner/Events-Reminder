from datetime import datetime
from convertdate import hebrew
from pyluach.dates import HebrewDate



hebrew_months_nisan = {
    1: "ניסן", 2: "אייר", 3: "סיון", 4: "תמוז", 5: "אב", 6: "אלול",
    7: "תשרי", 8: "חשוון", 9: "כסלו", 10: "טבת", 11: "שבט", 12: "אדר",
    62: "אדר ב'"
}

# מיפוי שמות חודשים לפי תשרי כחודש ראשון
hebrew_months = {
    1: "תשרי", 2: "חשוון", 3: "כסלו", 4: "טבת", 5: "שבט", 6: "אדר",
    62: "אדר ב'", 7: "ניסן", 8: "אייר", 9: "סיון",
    10: "תמוז", 11: "אב", 12: "אלול"
}

def clean_month_value(month):
    try:
        month = int(month)
        return month
    except ValueError:
        print(f"Invalid month value: {month}. Defaulting to 0.")
        return 0

def map_hebrew_month(year, month):
    """
    ממפה את החודשים העבריים למיספור תואם לספרייה convertdate
    """
    if month == 62:  # אדר ב'
        if hebrew.leap(year):
            return 13  # חודש 13 בשנה מעוברת
        else:
            raise ValueError(f"Invalid month 62 for a non-leap year: {year}")
    elif month == 6:  # אדר רגיל או אדר א'
        if hebrew.leap(year):
            return 12  # אדר א' בשנה מעוברת
        else:
            return 12  # אדר רגיל בשנה רגילה
    else:
        # מיפוי חודשים רגילים מתשרי לניסן
        if month >= 7:  # תשרי עד אדר
            return month - 6
        else:  # ניסן עד אלול
            return month + 6

def hebrew_to_gregorian_fixed(year, month, day):
    print(f"Converting Hebrew date: year={year}, month={month}, day={day}...")
    try:
        corrected_month = map_hebrew_month(year, month)
        print(f"Corrected month for conversion: {corrected_month}")
        gregorian_date = datetime(*hebrew.to_gregorian(year, corrected_month, day))
        print(f"Converted Gregorian date: {gregorian_date}")
        return gregorian_date

    except Exception as e:
        print(f"Error converting Hebrew date: year={year}, month={month}, day={day} -> {e}")
        raise



def next_anniversary(original_year, original_month, original_day):
    """
    מחשבת את יום השנה הקרוב לתאריך עברי מקורי
    """
    today = datetime.today()
    current_hebrew_year = hebrew.from_gregorian(today.year, today.month, today.day)[0]

    # נסה את השנה הנוכחית
    for offset in range(2):  # בודק גם את השנה הנוכחית וגם את השנה הבאה
        try:
            year_to_check = current_hebrew_year + offset
            # אם אדר ב' ואין שנה מעוברת, תרגם לאדר
            month_to_check = original_month
            if original_month == 62 and not hebrew.leap(year_to_check):
                month_to_check = 6  # תרגם לאדר רגיל

            gregorian_date = hebrew_to_gregorian_fixed(year_to_check, month_to_check, original_day)
            if gregorian_date.date() == today.date():
                days_until = 0  # התאריך הוא היום
                next_hebrew = f"{original_day} {hebrew_months.get(month_to_check)} {year_to_check}"
                return gregorian_date, next_hebrew, days_until
            elif gregorian_date > today:
                days_until = (gregorian_date - today).days + 1
                next_hebrew = f"{original_day} {hebrew_months.get(month_to_check)} {year_to_check}"
                return gregorian_date, next_hebrew, days_until
        except ValueError:
            pass  # נסה שנה הבאה אם יש שגיאה (לדוגמה, חודש לא תקף)

    raise ValueError(f"Could not calculate next anniversary for Hebrew date: {original_year}-{original_month}-{original_day}")


#def hebrew_date_in_words(day, month, year):
#    hebrew_date = HebrewDate(year, month, day)
#    return hebrew_date.hebrew



def hebrew_date_in_words(day, month, year):
    """
    ממיר תאריך עברי לפורמט מילולי מלא בעברית (למשל: ח' בשבט תשפ"ה)
    """
    # המרת היום לפורמט מילולי
    hebrew_day_letters = {
        1: 'א', 2: 'ב', 3: 'ג', 4: 'ד', 5: 'ה', 6: 'ו', 7: 'ז', 8: 'ח', 9: 'ט',
        10: 'י', 11: "י\"א", 12: "י\"ב", 13: "י\"ג", 14: "י\"ד", 15: "ט\"ו", 16: "ט\"ז",
        17: "י\"ז", 18: "י\"ח", 19: "י\"ט", 20: "כ", 21: "כ\"א", 22: "כ\"ב",
        23: "כ\"ג", 24: "כ\"ד", 25: "כ\"ה", 26: "כ\"ו", 27: "כ\"ז", 28: "כ\"ח",
        29: "כ\"ט", 30: "ל"
    }
    day_word = hebrew_day_letters.get(day, str(day))
    
    # שמות החודשים
    hebrew_months_names = {
        1: "תשרי", 2: "חשוון", 3: "כסלו", 4: "טבת", 5: "שבט", 6: "אדר",
        7: "ניסן", 8: "אייר", 9: "סיון", 10: "תמוז", 11: "אב", 12: "אלול", 13: "אדר ב'"
    }
    
    # בדיקת חודש אדר ב'
    if month == 62 and not hebrew.leap(year):
        month = 6  # בשנה לא מעוברת, אדר ב' הופך לאדר רגיל
    
    month_name = hebrew_months_names.get(month, "לא ידוע")
    
    # חישוב השנה העברית
    hundreds_map = {
        800: "תת", 700: "תש", 600: "תר", 500: "תק", 400: "ת"
    }
    
    # שלוש הספרות האחרונות של השנה
    last_three_digits = year % 1000
    
    # מציאת המאות
    hundreds = (last_three_digits // 100) * 100
    hundreds_word = hundreds_map.get(hundreds, "")
    
    # חישוב העשרות והיחידות
    remainder = last_three_digits % 100
    tens_and_units_map = {
        15: "ט\"ו", 16: "ט\"ז"
    }
    if remainder in tens_and_units_map:
        tens_and_units_word = tens_and_units_map[remainder]
    else:
        # עשרות
        tens = (remainder // 10) * 10
        units = remainder % 10
        tens_word = {
            10: "י", 20: "כ", 30: "ל", 40: "מ",
            50: "נ", 60: "ס", 70: "ע", 80: "פ", 90: "צ"
        }.get(tens, "")
        units_word = {
            1: "א", 2: "ב", 3: "ג", 4: "ד", 5: "ה",
            6: "ו", 7: "ז", 8: "ח", 9: "ט"
        }.get(units, "")
        tens_and_units_word = tens_word + units_word
    
    # שילוב המאות עם העשרות והיחידות
    year_word = hundreds_word + tens_and_units_word
    
    return f"{day_word} ב{month_name} {year_word}"
