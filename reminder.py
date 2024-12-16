# שימוש בשמות העמודות מהקובץ הקיים

import pandas as pd
from datetime import datetime, timedelta
from convertdate import hebrew
import os

# הגדרת נתיב יחסי לקריאת הקובץ
file_path = os.path.join(os.path.dirname(__file__), 'dates.csv')
df = pd.read_csv(file_path, encoding='utf-8')

# הנחה: עמודות הקובץ הן 'Hebrew Date' ו-'Event Description'
# פורמט התאריך העברי: "יום-חודש-שנה" (לדוגמה: "2-2-5784")

# המרת תאריך עברי ללועזי
def hebrew_to_gregorian(hebrew_date):
    day, month, year = map(int, hebrew_date.split('-'))
    return datetime(*hebrew.to_gregorian(year, month, day))

# חישוב תאריך של מחר
tomorrow = datetime.now() + timedelta(days=1)

# בדיקת כל התאריכים
events_tomorrow = []
for _, row in df.iterrows():
    try:
        hebrew_date = row['Hebrew Date']
        event_description = row['Event Description']
        event_date = hebrew_to_gregorian(hebrew_date)

        # בדיקה אם התאריך תואם למחר
        if event_date.date() == tomorrow.date():
            events_tomorrow.append(event_description)
    except Exception as e:
        print(f"Error processing date: {hebrew_date}, Error: {str(e)}")

# התראה אם יש אירועים למחר
if events_tomorrow:
    print("Alert: There are events scheduled for tomorrow!")
    for event in events_tomorrow:
        print(f"- {event}")
else:
    print("No events scheduled for tomorrow.")
