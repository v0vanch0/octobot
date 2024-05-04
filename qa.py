import pandas as pd

# Создание пустого DataFrame
df = pd.DataFrame(columns=['questions', 'answers'])

# Добавление вопросов и ответов
df.loc[len(df)] = ['What is your name?', 'My name is Assistant.']
df.loc[len(df)] = ['What is your favorite color?', 'I like all colors equally.']
# ... добавьте больше вопросов и ответов по мере необходимости ...

# Сохранение DataFrame в файл CSV
df.to_csv('database.csv', index=False)
