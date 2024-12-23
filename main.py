from csv_handler import load_csv
from date_converter import hebrew_to_gregorian_fixed, hebrew_months, next_anniversary, hebrew_date_in_words
from alert_handler import add_need_to_send_column, send_alerts_from_df
import pandas as pd

# הגדרת המייל והסיסמה
from_email = "hebrew.events.reminder@gmail.com"
from_password = "nkbk bvkl czqh fwdf"

# חישוב גיל האירוע (AGE)
def calculate_event_age(df):
    """
    מחשב את גיל האירוע בין התאריך המקורי לתאריך יום השנה הבא
    """
    # ווידוא שהעמודות הן בפורמט datetime
    df['Original_Gregorian_Date'] = pd.to_datetime(df['Original_Gregorian_Date'], errors='coerce')
    df['Next_Anniversary_Gregorian'] = pd.to_datetime(df['Next_Anniversary_Gregorian'], errors='coerce')

    # חישוב גיל האירוע
    df['AGE'] = df.apply(
        lambda row: int(row['Next_Anniversary_Gregorian'].year - row['Original_Gregorian_Date'].year)
        if pd.notna(row['Next_Anniversary_Gregorian']) and pd.notna(row['Original_Gregorian_Date'])
        else None,
        axis=1
    )
    df['AGE'] = df['AGE'].fillna(0).astype(int)  # Ensure AGE is an integer
    return df

# טען את ה-CSV
df = load_csv()

# הוסף עמודות חדשות ל-DataFrame
df['Original_Gregorian_Date'] = None
df['Next_Anniversary_Gregorian'] = None
df['Next_Anniversary_Hebrew'] = None
df['Days_Until_Next_Anniversary'] = None

# Debugging CSV data parsing
print("\n--- Debugging CSV Data Parsing ---")
for index, row in df.iterrows():
    try:
        name = row.get('name', 'Unknown')
        email = row.get('Email', 'Unknown')
        event_name = row.get('event_name', 'Unknown')
        year = int(row['Hyear'])
        month = int(row['Hmonth'])
        day = int(row['Hday'])
        month_name = hebrew_months.get(month, "Unknown")
        print(f"Processing row {index}: Name={name}, Email={email}, Event Name={event_name}, Year={year}, Month={month} ({month_name}), Day={day}")

        # Convert Hebrew to Gregorian
        gregorian_date = hebrew_to_gregorian_fixed(year, month, day)
        df.at[index, 'Original_Gregorian_Date'] = gregorian_date
        print(f"Row {index} -> Converted to Gregorian: {gregorian_date}")

        # Calculate next anniversary
        try:
            next_gregorian, next_hebrew_year, days_until = next_anniversary(year, month, day)
            next_hebrew = hebrew_date_in_words(day, month, int(next_hebrew_year.split()[-1]))
            formatted_gregorian = next_gregorian.strftime("%d-%m-%Y") if pd.notna(next_gregorian) else None
            df.at[index, 'Next_Anniversary_Gregorian'] = formatted_gregorian
            df.at[index, 'Next_Anniversary_Hebrew'] = next_hebrew
            print(f"Debug1111111111: days_until for row {index} is {days_until}")

            df.at[index, 'Days_Until_Next_Anniversary'] = int(days_until)

            # Check if the event is within the alert time
            if int(days_until) <= int(row['Alert_Time']):  # Compare days_until to Alert_Time
                print(f"Event happening within alert time: {event_name} -> Sending alert!")
                df.at[index, 'need_to_send'] = 1
            else:
                df.at[index, 'need_to_send'] = 0
        except Exception as calc_error:
            print(f"Error calculating anniversary for row {index}: {calc_error}")
            df.at[index, 'need_to_send'] = 0

        print(f"Row {index} -> Next Anniversary (Gregorian): {formatted_gregorian}")
        print(f"Row {index} -> Next Anniversary (Hebrew): {next_hebrew}")
        print(f"Row {index} -> Days Until Next Anniversary: {days_until} days")

    except Exception as e:
        print(f"Error processing row {index}: {e}")
        df.at[index, 'need_to_send'] = 0



# חישוב גיל האירוע
df = calculate_event_age(df)

#df['Days_Until_Next_Anniversary'] = df['Days_Until_Next_Anniversary'].apply(lambda x: int(x) if pd.notna(x) else None)




# הוספת עמודת need_to_send
try:
    df = add_need_to_send_column(df)
except Exception as e:
    print(f"Error adding 'need_to_send' column: {e}")

# שמירת ה-DataFrame המעודכן
df.to_csv("updated_dates.csv", index=False, encoding='utf-8')

# שליחת המיילים
try:
    send_alerts_from_df(df, from_email=from_email, from_password=from_password)
except Exception as e:
    print(f"Error sending emails: {e}")




# דיבאג DataFrame לאחר העדכון
print("\n--- Updated DataFrame ---")
print(df[['event_name', 'Days_Until_Next_Anniversary', 'need_to_send']])

print(df)
