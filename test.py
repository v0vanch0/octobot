# Создание векторизатора текстовых данных
import pandas as pd
from nltk.corpus import stopwords
from sklearn.feature_extraction.text import TfidfVectorizer
df = pd.read_csv('database.csv')
question = input()
vectorizer = TfidfVectorizer(stop_words=stopwords.words('russian'))
question_vectors = vectorizer.fit_transform(df['questions'])
question_vector = vectorizer.transform([question])
print(question_vector)