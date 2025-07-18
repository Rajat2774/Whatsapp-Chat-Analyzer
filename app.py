import streamlit as st
import preprocessor, helper
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import matplotlib.dates as mdates
import chardet

# Set Streamlit page config
st.set_page_config(page_title="WhatsApp Chat Analyzer", page_icon="💬", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
    .main {
        background-color: #f9f9f9;
    }
    .stButton>button {
        color: white;
        background: linear-gradient(135deg, #00b4db, #0083b0);
        border-radius: 8px;
        padding: 0.5em 2em;
    }
    /* Remove background override for selectbox text */
    </style>
    """,
    unsafe_allow_html=True
)


# Sidebar
st.sidebar.title("💬 WhatsApp Chat Analyzer")
uploaded_file = st.sidebar.file_uploader("Upload your chat file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()

    # Try to detect encoding
    detected = chardet.detect(bytes_data)
    encoding = detected['encoding'] or 'utf-8'  # fallback to utf-8 if undetected

    try:
        data = bytes_data.decode(encoding)
    except UnicodeDecodeError:
        # Fallbacks if chardet fails
        for enc in ['utf-8', 'utf-8-sig', 'utf-16', 'ISO-8859-1']:
            try:
                data = bytes_data.decode(enc)
                break
            except UnicodeDecodeError:
                data = None

    df = preprocessor.preprocess(data)

    user_list = df['user'].unique().tolist()
    user_list.remove('Group Notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Analyze messages from", user_list)

    if st.sidebar.button("Show Analysis"):
        with st.spinner("Processing... ⏳"):
            num_msg, words, media, links = helper.fetch_stats(selected_user, df)
            if not df.empty:
                st.markdown("---")
                st.title("📊 Chat Statistics")
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Messages", num_msg)
                col2.metric("Words", words)
                col3.metric("Media Shared", media)
                col4.metric("Links Shared", links)

                st.markdown("---")
                st.header("🗓️ Monthly Message Timeline")
                timeline = helper.monthly_timeline(selected_user, df)
                fig, ax = plt.subplots(figsize=(10, 5))
                ax.plot(timeline['time'], timeline['message'], color='#0083b0', marker='o')
                plt.xticks(rotation="vertical")
                st.pyplot(fig)

                st.header("📅 Daily Message Timeline")
                timeline_daily = helper.daily_timeline(selected_user, df)
                
                fig, ax = plt.subplots(figsize=(15, 6))
                ax.plot(timeline_daily['date'], timeline_daily['message'], color='#00b4db', marker='o', markersize=3)

                # Show monthly x-axis ticks only
                ax.xaxis.set_major_locator(mdates.AutoDateLocator())
                ax.xaxis.set_major_formatter(mdates.DateFormatter('%d-%b-%Y'))

                plt.xticks(rotation=45, fontsize=9)
                plt.tight_layout()
                st.pyplot(fig)

                st.markdown("---")
                st.header("🕑 Activity Map")
                col1, col2 = st.columns(2)

                with col1:
                    st.subheader("Most Busy Day")
                    busy_day = helper.week_activity(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.bar(busy_day.index, busy_day.values, color='#ff7f50')
                    plt.xticks(rotation="vertical")
                    st.pyplot(fig)

                with col2:
                    st.subheader("Most Busy Month")
                    busy_month = helper.month_activity(selected_user, df)
                    fig, ax = plt.subplots()
                    ax.bar(busy_month.index, busy_month.values, color='#6a5acd')
                    plt.xticks(rotation="vertical")
                    st.pyplot(fig)

                st.subheader("Weekly Activity Heatmap")
                heatmap = helper.activity_heatmap(selected_user, df)
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.heatmap(heatmap, cmap="YlGnBu", ax=ax)
                st.pyplot(fig)

                if selected_user == 'Overall':
                    st.markdown("---")
                    st.header("🏆 Most Active Users")
                    x, new_df = helper.most_busy_users(df)
                    col1, col2 = st.columns(2)
                    with col1:
                        fig, ax = plt.subplots()
                        ax.bar(x.index, x.values, color='#00b4db')
                        plt.xticks(rotation='vertical')
                        st.pyplot(fig)
                    with col2:
                        st.dataframe(new_df)

                st.markdown("---")
                st.header("☁️ Word Cloud")
                df_wc = helper.create_word_cloud(selected_user, df)
                fig, ax = plt.subplots()
                ax.imshow(df_wc)
                ax.axis('off')
                st.pyplot(fig)

                st.header("🔤 Most Common Words")
                common_word = helper.most_common_words(selected_user, df)
                fig, ax = plt.subplots()
                ax.barh(common_word[0], common_word[1], color='#ffb347')
                ax.set_xlabel("Count")
                st.pyplot(fig)

                st.markdown("---")
                st.header("😊 Emoji Analysis")

                common_emoji = helper.emoji_analysis(selected_user, df)
                col1, col2 = st.columns(2)
                if not common_emoji.empty:
                    with col1:
                        st.dataframe(common_emoji)

                # Emoji font setup
                    mpl.rcParams['font.family'] = 'Segoe UI Emoji'  # Windows
                # mpl.rcParams['font.family'] = 'Apple Color Emoji'  # macOS
                # mpl.rcParams['font.family'] = 'Noto Color Emoji'  # Linux
                    with col2:
                        fig, ax = plt.subplots()
                        ax.pie(common_emoji[1].head(), labels=common_emoji[0].head(), autopct="%0.2f", startangle=140)
                        st.pyplot(fig)
                else:
                    st.write("No emoji data available for this user")
            else:
                st.write("No messages available for this user")

        st.success("✅ Analysis Complete!")

else:
    st.markdown("Upload a WhatsApp chat `.txt` file from your phone export to get started! 📄")
