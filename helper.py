from urlextract import URLExtract
from wordcloud import WordCloud
from collections import Counter
import pandas as pd
import emoji



def fetch_stats(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user']==selected_user]

    #1. number of messages   
    num_msg=df.shape[0]
    #2. Number of words
    words=[]
    for message in df['message']:
        words.extend(message.split())

    #3. Number of media files
    media=df[df['message']=='<Media omitted>\n']

    #4. Number of Links
    extractor=URLExtract()
    links=[]
    for message in df['message']:
        links.extend(extractor.find_urls(message))
    
    return num_msg,len(words),len(media),len(links)



def most_busy_users(df):
    X=df['user'].value_counts().head()
    new_df=round((df['user'].value_counts()/df.shape[0])*100,2).reset_index().rename(columns={'user':'Name','count':'Percent'})
    return X,new_df


def create_word_cloud(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user']==selected_user]

    temp=df[df['user']!='Group Notification'] #removing group notification
    temp=temp[temp['message']!='<Media omitted>\n'] #removing media omitted

    wc=WordCloud(width=500,height=500,min_font_size=10,background_color='white')
    df_wc=wc.generate(temp['message'].str.cat(sep=" "))
    return df_wc

def most_common_words(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user']==selected_user]
    
    temp=df[df['user']!='Group Notification'] #removing group notification
    temp=temp[temp['message']!='<Media omitted>\n'] #removing media omitted
    f=open('stop_hinglish.txt','r')
    stop_words=f.read()

    words=[]
    for message in temp['message']:
        for word in message.lower().split():
            if word not in stop_words:
                words.append(word)
    
    common_word=pd.DataFrame(Counter(words).most_common(20))
    return common_word


def emoji_analysis(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user']==selected_user]

    emojis = []
    for message in df['message']:
        emojis.extend([c for c in message if c in emoji.EMOJI_DATA])

    common_emoji=pd.DataFrame(Counter(emojis).most_common(len(Counter(emojis))))
    return common_emoji



def monthly_timeline(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user']==selected_user]

    timeline=df.groupby(['year','month_num','month']).count()['message'].reset_index()
    time=[]
    for i in range(timeline.shape[0]):
        time.append(timeline['month'][i]+"-"+str(timeline['year'][i]))

    timeline['time']=time

    return timeline


def daily_timeline(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user']==selected_user]
    
    daily_timeline=df.groupby('date').count()['message'].reset_index()
    return daily_timeline

def week_activity(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user']==selected_user]
    
    return df['day_name'].value_counts() #series

def month_activity(selected_user,df):
    if selected_user!="Overall":
        df=df[df['user']==selected_user]
    
    return df['month'].value_counts() #series


def activity_heatmap(selected_user,df):

    if selected_user != 'Overall':
        df = df[df['user'] == selected_user]

    user_heatmap = df.pivot_table(index='day_name', columns='period', values='message', aggfunc='count').fillna(0)

    return user_heatmap