import sqlite3

# Подключаемся к базе данных
conn = sqlite3.connect('wedding.db')
cur = conn.cursor()

# Обновляем картинки для конкретных исполнителей
cur.execute("UPDATE vendors SET image = 'arka.jpg' WHERE name = 'Зал Ривьера'")
cur.execute("UPDATE vendors SET image = 'car.jpg' WHERE name = 'Иван Иванов'")

conn.commit()
conn.close()

print("УСПЕХ! Фотографии привязаны к базе данных.")