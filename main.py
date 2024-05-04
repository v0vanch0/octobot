import nltk
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.model_selection import train_test_split
from nltk.corpus import stopwords
# Загрузка базы данных
df = pd.read_excel("dataset.xlsx")
# Создание векторизатора текстовых данных
vectorizer = TfidfVectorizer(stop_words=stopwords.words('russian'))
# Векторизация вопросов
question_vectors = vectorizer.fit_transform(df['questions'])
# Кластеризация вопросов
kmeans = KMeans(n_clusters=2)
kmeans.fit(question_vectors)

# Добавление меток кластера в датафрейм
df['cluster_label'] = kmeans.labels_


def answer_question(question, similarity_threshold=0.5):
    question_vector = vectorizer.transform([question])
    print(question_vector)
    cluster_label = kmeans.predict(question_vector)[0]
    if cluster_label not in kmeans.labels_:
        return "I don't know"
    else:
        # Найти наиболее похожий вопрос в кластере
        similar_questions = df[df['cluster_label'] == cluster_label]
        similarities = cosine_similarity(question_vector, vectorizer.transform(similar_questions['questions']))
        max_similarity_index = similarities.argmax()
        max_similarity = similarities[0, max_similarity_index]
        if max_similarity < similarity_threshold:
            return "Я вас не понимаю."
        else:
            most_similar_question = similar_questions.iloc[max_similarity_index]['questions']
            # Вернуть ответ на наиболее похожий вопрос
            return df.loc[df['questions'] == most_similar_question, 'answers'].iloc[0]


# Тестирование функции
print(answer_question("Привет"))

