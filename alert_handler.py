import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import pandas as pd


def should_send_alert(days_until_next_anniversary, alert_time):
    """
    בודקת אם מספר הימים עד התאריך הבא תואם לאחד מהמספרים ב-Alert_Time
    """
    try:
        if not alert_time or pd.isna(alert_time):  # אם השדה ריק
            return False

        # טיפול במקרה שבו יש ערך בודד או ערכים מופרדים בפסיקים
        alert_days = [int(alert_time)] if isinstance(alert_time, int) or alert_time.isdigit() else list(map(int, str(alert_time).split(',')))

        print(f"Parsed Alert_Time: {alert_days}, Days Until: {days_until_next_anniversary}")
        return days_until_next_anniversary == 0 or int(days_until_next_anniversary) in alert_days
    except Exception as e:
        print(f"Error parsing Alert_Time: {alert_time}. Error: {e}")
        return False





# פונקציה להוספת עמודת need_to_send
def add_need_to_send_column(df):
    """
    מוסיפה עמודת need_to_send ל-DataFrame
    """
    def check_row(row):
        days_until_next = row['Days_Until_Next_Anniversary']
        alert_time = row['Alert_Time']
        print(f"Checking row: Days={days_until_next}, Alert_Time={alert_time}")
        return 1 if should_send_alert(days_until_next, alert_time) else 0

    df['need_to_send'] = df.apply(
        lambda row: 1 if should_send_alert(row['Days_Until_Next_Anniversary'], row['Alert_Time']) else 0,
        axis=1
    )
    return df


# פונקציה לשליחת מיילים
def send_email(to_email, subject, body, from_email="your_email@example.com", from_password="your_password"):
    """
    שולחת מייל התראה
    """
    try:
        # הגדרת המייל
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))

        # חיבור לשרת SMTP ושליחת המייל
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(from_email, from_password)
        server.send_message(msg)
        server.quit()
        print(f"Email sent to {to_email}")
    except smtplib.SMTPAuthenticationError:
        print("Authentication error: Please check your email credentials.")
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")


# פונקציה לשליחת מיילים משורות עם need_to_send == 1
def send_alerts_from_df(df, from_email="your_email@example.com", from_password="your_password"):
    """
    שולחת מיילים רק עבור שורות שבהן need_to_send == 1
    """
    alerts_to_send = df[df['need_to_send'] == 1]

    for index, row in alerts_to_send.iterrows():
        email = row['Email']
        event_name = row['event_name']
        days_until_next = row['Days_Until_Next_Anniversary']
        age = row['AGE']
        formatted_grigorian_date = row['Next_Anniversary_Gregorian']
        hebrew_date = row['Next_Anniversary_Hebrew'] 

        # הודעה מיוחדת אם האירוע הוא היום
        if days_until_next == 0:
            body = f"{event_name} ({age}) הוא היום! - {hebrew_date}, {formatted_grigorian_date}"
        else:
            body = f"{event_name} ({age}), בעוד {days_until_next} ימים - {hebrew_date}, {formatted_grigorian_date}"
        
        subject = f"{event_name} מתקרב!"
        send_email(
            to_email=email,
            subject=subject,
            body=body,
            from_email=from_email,
            from_password=from_password
        )
