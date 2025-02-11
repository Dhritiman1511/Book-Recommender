from flask import Flask, render_template, request
import pandas as pd
import numpy as np

popular_df = pd.read_csv('popular.csv')
pt = pd.read_csv('pt.csv', index_col='Book-Title', dtype={'Book-Title': str})
books = pd.read_csv('book.csv')
similarity_scores = pd.read_csv('similarity_scores.csv', index_col=0)

app = Flask(__name__)


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
    user_input = request.form.get('user_input').strip().lower()  # Normalize user input
    pt.index = pt.index.astype(str).str.strip().str.lower()  # Normalize the index

    # Check if the user_input exists in the pt.index
    if user_input not in pt.index:
        return "Book not found in the database. Please try another title."

    # Proceed with the recommendation logic
    index = np.where(pt.index == user_input)[0][0]  # Get the index of the book

    # Get similarity scores for the book
    book_similarity_scores = similarity_scores.iloc[index]

    # Sort and get top 5 similar books (excluding the book itself)
    similar_items = sorted(list(enumerate(book_similarity_scores)), key=lambda x: x[1], reverse=True)[1:6]

    data = []
    for i in similar_items:
        item = []
        similar_book_title = pt.index[i[0]]  # Get the title of the similar book

        # Find the book details in the books DataFrame
        temp_df = books[books['Book-Title'].str.strip().str.lower() == similar_book_title]
        if not temp_df.empty:
            item.extend(temp_df.drop_duplicates('Book-Title')['Book-Title'].to_list())
            item.extend(temp_df.drop_duplicates('Book-Title')['Book-Author'].to_list())
            item.extend(temp_df.drop_duplicates('Book-Title')['Image-URL-M'].to_list())
            data.append(item)
        else:
            print(f"Book not found in books DataFrame: {similar_book_title}")  # Debugging

    print(data)  # Debugging
    return render_template('recommend.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)