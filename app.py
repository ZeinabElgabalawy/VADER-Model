import sqlite3
from flask import Flask, render_template
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

app = Flask(__name__)

# اسم قاعدة البيانات
DB_NAME = "cleaned_tweets_database (2).db"

# دالة لإنشاء الجدول إذا لم يكن موجودًا
def create_sentiment_table():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sentiment_summary (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            positive_percentage REAL,
            negative_percentage REAL,
            neutral_percentage REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# دالة لحفظ النتائج في الجدول
def save_sentiment_results(positive, negative, neutral):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sentiment_summary (positive_percentage, negative_percentage, neutral_percentage)
        VALUES (?, ?, ?)
    ''', (positive, negative, neutral))
    conn.commit()
    conn.close()

# دالة لجلب التغريدات من قاعدة البيانات
def get_data_from_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, tweet_id, tweet_text FROM tweets")
    rows = cursor.fetchall()
    conn.close()
    return rows

# دالة لتحليل المشاعر باستخدام VADER
def analyze_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    sentiment_score = analyzer.polarity_scores(text)
    if sentiment_score['compound'] >= 0.05:
        sentiment = 'Positive'
    elif sentiment_score['compound'] <= -0.05:
        sentiment = 'Negative'
    else:
        sentiment = 'Neutral'
    return sentiment

@app.route('/')
def index():
    # تأكد من إنشاء الجدول
    create_sentiment_table()
    
    raw_data = get_data_from_db()
    positive_count = 0
    negative_count = 0
    neutral_count = 0
    
    for row in raw_data:
        tweet_text = row[2]
        sentiment = analyze_sentiment(tweet_text)
        if sentiment == 'Positive':
            positive_count += 1
        elif sentiment == 'Negative':
            negative_count += 1
        else:
            neutral_count += 1
    
    total_count = len(raw_data)
    positive_percentage = (positive_count / total_count) * 100 if total_count > 0 else 0
    negative_percentage = (negative_count / total_count) * 100 if total_count > 0 else 0
    neutral_percentage = (neutral_count / total_count) * 100 if total_count > 0 else 0

    # حفظ النسب في قاعدة البيانات
    save_sentiment_results(positive_percentage, negative_percentage, neutral_percentage)
    
    # عرض النسب في الصفحة
    return render_template('sentiment_results.html', 
                           positive_percentage=positive_percentage, 
                           neutral_percentage=neutral_percentage, 
                           negative_percentage=negative_percentage)

if __name__ == '__main__':
    app.run(debug=True)
