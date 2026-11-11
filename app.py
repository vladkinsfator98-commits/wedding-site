from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('wedding.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    search_query = request.args.get('search', '').strip()
    conn = get_db()
    
    if search_query:
        # Ищем точное совпадение с названием города (без учета регистра)
        exact_city = conn.execute("SELECT name FROM cities WHERE LOWER(name) = LOWER(?)", (search_query,)).fetchone()
        
        if exact_city:
            # Если город найден, перенаправляем на его страницу
            conn.close()
            return redirect(url_for('city_page', name=exact_city['name']))
        else:
            # Если точного совпадения нет, показываем список найденных городов
            cities = conn.execute("SELECT name FROM cities WHERE name LIKE ? ORDER BY name", ('%' + search_query + '%',)).fetchall()
    else:
        cities = conn.execute("SELECT name FROM cities ORDER BY name LIMIT 30").fetchall()
        
    conn.close()
    return render_template('index.html', cities=cities, search_query=search_query)

@app.route('/city/<name>')
def city_page(name):
    selected_category = request.args.get('category', '')
    sort_by = request.args.get('sort', '')
    
    conn = get_db()
    query = 'SELECT * FROM vendors WHERE city = ?'
    params = [name]
    
    if selected_category:
        query += ' AND category = ?'
        params.append(selected_category)
        
    if sort_by == 'price':
        query += ' ORDER BY price ASC'
    else:
        query += ' ORDER BY id ASC'
        
    vendors = conn.execute(query, params).fetchall()
    conn.close()
    
    return render_template('city.html', city=name, vendors=vendors, selected_category=selected_category, sort_by=sort_by)
# --- НОВАЯ ФУНКЦИЯ ДЛЯ ПОИСКА ПО КАТЕГОРИЯМ ---
@app.route('/search')
def search():
    category = request.args.get('category', '')
    conn = get_db()
    
    if category:
        vendors = conn.execute('SELECT * FROM vendors WHERE category = ?', (category,)).fetchall()
    else:
        vendors = conn.execute('SELECT * FROM vendors').fetchall()
        
    conn.close()
    return render_template('search.html', category=category, vendors=vendors)
@app.route('/submit_order', methods=['POST'])
def submit_order():
    vendor_id = request.form.get('vendor_id')
    client_name = request.form.get('client_name')
    client_phone = request.form.get('client_phone')
    
    conn = get_db()
    conn.execute('INSERT INTO orders (vendor_id, client_name, client_phone) VALUES (?, ?, ?)', 
                 (vendor_id, client_name, client_phone))
    conn.commit()
    conn.close()
    
    return "<h3 style='text-align:center; font-family:sans-serif; color:green; margin-top:50px;'>Спасибо! Ваша заявка отправлена. Мы свяжемся с вами.</h3><p style='text-align:center;'><a href='/'>Вернуться на главную</a></p>"

@app.route('/admin')
def admin():
    conn = get_db()
    orders = conn.execute('''
        SELECT orders.*, vendors.name as vendor_name, vendors.category 
        FROM orders 
        JOIN vendors ON orders.vendor_id = vendors.id 
        ORDER BY orders.created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('admin.html', orders=orders)

@app.route('/register', methods=['GET', 'POST'])
def register():
    conn = get_db()
    cities = conn.execute("SELECT name FROM cities ORDER BY name").fetchall()

    if request.method == 'POST':
        city = request.form.get('city')
        category = request.form.get('category')
        name = request.form.get('name')
        price = request.form.get('price')
        description = request.form.get('description')
        contact = request.form.get('contact')  # Новое поле
        image_name = request.form.get('image_name') 

        conn.execute('INSERT INTO vendors (city, category, name, price, description, contact, image) VALUES (?, ?, ?, ?, ?, ?, ?)',
                     (city, category, name, price, description, contact, image_name))
        conn.commit()
        conn.close()
        
        return "<h3 style='text-align:center; font-family:sans-serif; color:green; margin-top:50px;'>Анкета добавлена! Теперь вы есть на сайте.</h3><p style='text-align:center;'><a href='/'>Вернуться на главную</a></p>"

    conn.close()
    return render_template('register.html', cities=cities)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
