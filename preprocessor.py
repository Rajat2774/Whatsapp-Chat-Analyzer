import pandas as pd
import re


def preprocess(data):
    pattern = r"\d{1,2}/\d{1,2}/\d{2,4},\s\d{1,2}:\d{2}(?:\s?[apAP][mM])?\s-\s"

    # Find dates
    dates = re.findall(pattern, data)

    # Split messages
    messages = re.split(pattern, data)[1:]  # skip first empty string if present

    # Remove trailing " - " from dates
    dates = [date.rstrip(" - ") for date in dates]

    # Create DataFrame
    df = pd.DataFrame({'message_date': dates, 'user_message': messages})
    df['message_date'] = df['message_date'].str.strip(" - ")
    df['message_date'] = pd.to_datetime(df['message_date'], dayfirst=True)
    users = []
    messages_clean = []

    for msg in df['user_message']:
        entry = re.split(r':\s', msg, 1) #1 in re.split(..., 1) means split only once, so even if the message has extra colons, it only splits on the first one.
        if len(entry) == 2:
            users.append(entry[0])
            messages_clean.append(entry[1])
        else:
            users.append('Group Notification')
            messages_clean.append(entry[0])

    df['user'] = users
    df['message'] = messages_clean
    df = df[['message_date', 'user', 'message']]

    df['year']=df['message_date'].dt.year
    df['month']=df['message_date'].dt.month_name()
    df['month_num']=df['message_date'].dt.month
    df['day']=df['message_date'].dt.day
    df['hour']=df['message_date'].dt.hour
    df['minute']=df['message_date'].dt.minute
    df['date']=df['message_date'].dt.date
    df['day_name']=df['message_date'].dt.day_name()

    period = []
    for hour in df[['day_name', 'hour']]['hour']:
        if hour == 23:
            period.append(str(hour) + "-" + str('00'))
        elif hour == 0:
            period.append(str('00') + "-" + str(hour + 1))
        else:
            period.append(str(hour) + "-" + str(hour + 1))

    df['period'] = period

    return df
