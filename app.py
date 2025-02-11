from flask import Flask, render_template, request
import pandas as pd
import numpy as np
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
popular_df = pd.read_csv(os.path.join(BASE_DIR, 'popular.csv'))
pt = pd.read_csv(os.path.join(BASE_DIR, 'pt.csv'), index_col='Book-Title', dtype={'Book-Title': str})
books = pd.read_csv(os.path.join(BASE_DIR, 'book.csv'))
similarity_scores = pd.read_csv(os.path.join(BASE_DIR, 'similarity_scores.csv'), index_col=0)

@app.route('/')
def index():
    return render_template('index.html',
                           book_name=popular_df['Book-Title'].to_list(),
                           author=popular_df['Book-Author'].to_list(),
                           image=popular_df['Image-URL-M'].to_list(),
                           votes=popular_df['num_ratings'].to_list(),
                           rating=popular_df['avg_ratings'].to_list(),
                           )

@app.route('/recommend')
def recommend_ui():
    return render_template('recommend.html')

@app.route('/recommend_books', methods=['POST'])
def recommend():
    user_input = request.form.get('user_input').strip().lower()
    pt.index = pt.index.astype(str).str.strip().str.lower()

    if user_input not in pt.index:
        return "Book not found in the database. Please try another title."

    index = np.where(pt.index == user_input)[0][0]
    book_similarity_scores = similarity_scores.iloc[index]
    similar_items = sorted(list(enumerate(book_similarity_scores)), key=lambda x: x[1], reverse=True)[1:6]

    data = []
    for i in similar_items:
        similar_book_title = pt.index[i[0]]
        temp_df = books[books['Book-Title'].str.strip().str.lower() == similar_book_title]
        if not temp_df.empty:
            data.append([
                temp_df.iloc[0]['Book-Title'],
                temp_df.iloc[0]['Book-Author'],
                temp_df.iloc[0]['Image-URL-M']
            ])

    return render_template('recommend.html', data=data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
