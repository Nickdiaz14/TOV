from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from datetime import datetime
import psycopg2
import pytz
import os

app = Flask(__name__)

kids_ids = [17, 18, 19, 20] 
adolescent_ids = [14, 15, 16]
adult_ids = [5, 6, 7, 8, 9, 10]
youth_ids = [11, 12, 13]

@app.route('/get_info')
def get_info():
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT * FROM categories;
    """)

    categories = cursor.fetchall()

    cursor.execute("""
    SELECT * FROM guides;
    """)

    guides = cursor.fetchall()

    cursor.execute("""
    SELECT * FROM products;
    """)

    categories_list = [list(category) for category in cursor.fetchall()]

    quantity_kid = float('inf')
    price_kid = 0
    quantity_adult = float('inf')
    price_adult = 0
    quantity_youth = float('inf')
    price_youth = 0
    quantity_adolescent = float('inf')
    price_adolescent = 0

    for i in range(len(categories_list)):
        cat_id = categories_list[i][0]

        if cat_id == 1:
            for category in categories_list:
                if category[0] in kids_ids:
                    quantity_kid = min(quantity_kid, category[4])
                    price_kid += int(category[3])
            categories_list[i][4] = quantity_kid
            categories_list[i][3] = price_kid

        elif cat_id == 2:
            for category in categories_list:
                if category[0] in adolescent_ids:
                    quantity_adolescent = min(quantity_adolescent, category[4])
                    price_adolescent += int(category[3])
            categories_list[i][4] = quantity_adolescent
            categories_list[i][3] = price_adolescent

        elif cat_id == 3:
            for category in categories_list:
                if category[0] in adult_ids:
                    quantity_adult = min(quantity_adult, category[4])
                    price_adult += int(category[3])
            categories_list[i][4] = quantity_adult
            categories_list[i][3] = price_adult

        elif cat_id == 4:
            for category in categories_list:
                if category[0] in youth_ids:
                    quantity_youth = min(quantity_youth, category[4])
                    price_youth += int(category[3])
            categories_list[i][4] = quantity_youth
            categories_list[i][3] = price_youth
                
    cursor.close()
    connection.close()

    return {'categories':categories, 'categories_list':categories_list, 'guides': guides}



@app.route('/')
def index():
    return render_template('menu.html')

@app.route('/add')
def add_page():
    return render_template('add.html')

@app.route('/charge')
def charge_page():
    return render_template('charge.html')

@app.route('/discharge')
def discharge_page():
    return render_template('discharge.html')

@app.route('/table_guide')
def table_guide_page():
    # Aquí podrías obtener los datos de la base de datos
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT * FROM guides
    ORDER BY id ASC;
    """)

    output = cursor.fetchall()
    data = [{"id": row[0], "nombre": row[1]} for row in output]
    return render_template('table_guide.html',data=data)

@app.route('/table_ped')
def table_ped_page():
    # Aquí podrías obtener los datos de la base de datos
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT r.id, g.name, r.date, p.name, r.quantity, r.price, r.delivered, r.paid, r.charged, r.consigned
    FROM registers r
    JOIN guides g ON r.name_id = g.id
    JOIN products p ON r.product_id = p.id
    ORDER BY r.id ASC;
    """)

    output = cursor.fetchall()
    data = [{"id": row[0], "nombre": row[1], "fecha": row[2], "producto": row[3], "cantidad": row[4], "precio": f"{int(row[5]):,}".replace(",", "."), "entregado": "" if row[6] == False else "X", "pagado": "" if row[7] == False else "X", "cargado": "" if row[8] == False else "X", "consignado": "" if row[9] == False else "X"} for row in output]
    return render_template('table_ped.html',data=data)

@app.route('/table_inv')
def table_inv_page():
    # Aquí podrías obtener los datos de la base de datos
    connection = connect_db()
    cursor = connection.cursor()

    cursor.execute("""
    SELECT p.id, c.category, p.name, p.price, p.quantity FROM products p
    JOIN categories c ON p.category_id = c.id
    ORDER BY id ASC;
    """)

    categories_list = [list(category) for category in cursor.fetchall()]

    quantity_kid = float('inf')
    price_kid = 0
    quantity_adult = float('inf')
    price_adult = 0
    quantity_youth = float('inf')
    price_youth = 0
    quantity_adolescent = float('inf')
    price_adolescent = 0

    for i in range(len(categories_list)):
        cat_id = categories_list[i][0]

        if cat_id == 1:
            for category in categories_list:
                if category[0] in kids_ids:
                    quantity_kid = min(quantity_kid, category[4])
                    price_kid += int(category[3])
            categories_list[i][4] = quantity_kid
            categories_list[i][3] = price_kid

        elif cat_id == 2:
            for category in categories_list:
                if category[0] in adolescent_ids:
                    quantity_adolescent = min(quantity_adolescent, category[4])
                    price_adolescent += int(category[3])
            categories_list[i][4] = quantity_adolescent
            categories_list[i][3] = price_adolescent

        elif cat_id == 3:
            for category in categories_list:
                if category[0] in adult_ids:
                    quantity_adult = min(quantity_adult, category[4])
                    price_adult += int(category[3])
            categories_list[i][4] = quantity_adult
            categories_list[i][3] = price_adult

        elif cat_id == 4:
            for category in categories_list:
                if category[0] in youth_ids:
                    quantity_youth = min(quantity_youth, category[4])
                    price_youth += int(category[3])
            categories_list[i][4] = quantity_youth
            categories_list[i][3] = price_youth

    data = [{"id": row[0], "categoria": row[1], "producto": row[2], "precio": f"{int(row[3]):,}".replace(",", "."), "cantidad": row[4]} for row in categories_list]
    return render_template('table_inv.html',data=data)

def connect_db():
    load_dotenv()
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port="5432"
    )

@app.route('/charge/submit', methods=['POST'])
def charge_submit():
    try:
        connection = connect_db()
        cursor = connection.cursor()

        # Procesar los datos}
        producto = int(request.form['producto'])
        cantidad = int(request.form['cantidad'])

        if producto == 1:
            for i in [17, 18, 19, 20]:
                cursor.execute("""
                    UPDATE products
                    SET quantity = quantity + %s
                    WHERE id = %s;""", (cantidad, i))
                
        elif producto == 2:
            for i in [14, 15, 16]:
                cursor.execute("""
                    UPDATE products
                    SET quantity = quantity + %s
                    WHERE id = %s;""", (cantidad, i))
            
        elif producto == 3:
            for i in [5, 6, 7, 8]:
                cursor.execute("""
                    UPDATE products
                    SET quantity = quantity + %s
                    WHERE id = %s;""", (cantidad, i))
            
        elif producto == 4:
            for i in [11, 12, 13]:
                cursor.execute("""
                    UPDATE products
                    SET quantity = quantity + %s
                    WHERE id = %s;""", (cantidad, i))
        
        else:
            cursor.execute("""
                UPDATE products
                SET quantity = quantity + %s
                WHERE id = %s;""", (cantidad, producto))

        connection.commit()
        cursor.close()
        connection.close()  
        return jsonify({'success': True})
    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False})
    
@app.route('/guide/submit', methods=['POST'])
def guide_submit():
    try:
        connection = connect_db()
        cursor = connection.cursor()

        # Procesar los datos}
        nombre = request.form['nombre']

        cursor.execute("""
            INSERT INTO guides (name) VALUES (%s);
        """, (nombre,))

        connection.commit()
        cursor.close()
        connection.close()  
        return jsonify({'success': True})
    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False})

@app.route('/discharge/submit', methods=['POST'])
def discharge_submit():
    try:
        connection = connect_db()
        cursor = connection.cursor()

        # Procesar los datos
        name = request.form['guia']
        categoria = request.form['categoria']
        producto = int(request.form['producto'])
        cantidad = request.form['cantidad']
        valor_total = int(request.form['valor_total'][2:].replace('.', ''))
        timezone = pytz.timezone('America/Bogota')
        now = datetime.now(timezone)
        fecha_corta = now.strftime('%Y/%m/%d')
        fecha_larga = now.strftime('%Y/%m/%d %H:%M')
        cursor.execute("""
                INSERT INTO registers 
                (created_at, date, name_id, category_id, product_id, price, quantity)
                VALUES (%s, %s, %s, %s, %s, %s, %s);
            """, (fecha_larga, fecha_corta, name, categoria, producto, valor_total, cantidad))
        
        if producto == 1:
            for i in [17, 18, 19, 20]:
                cursor.execute("""
                    UPDATE products
                    SET quantity = quantity - %s
                    WHERE id = %s;""", (cantidad, i))
                
        elif producto == 2:
            for i in [14, 15, 16]:
                cursor.execute("""
                    UPDATE products
                    SET quantity = quantity - %s
                    WHERE id = %s;""", (cantidad, i))
            
        elif producto == 3:
            for i in [5, 6, 7, 8]:
                cursor.execute("""
                    UPDATE products
                    SET quantity = quantity - %s
                    WHERE id = %s;""", (cantidad, i))
            
        elif producto == 4:
            for i in [11, 12, 13]:
                cursor.execute("""
                    UPDATE products
                    SET quantity = quantity - %s
                    WHERE id = %s;""", (cantidad, i))
        
        else:
            cursor.execute("""
                UPDATE products
                SET quantity = quantity - %s
                WHERE id = %s;""", (cantidad, producto))

        connection.commit()
        cursor.close()
        connection.close()  
        return jsonify({'success': True})
    except Exception as e:
        print("Error:", e)
        return jsonify({'success': False})
    
@app.route("/guardar_guide", methods=["POST"])
def guardar_guide():
    datos_actualizados = request.get_json()
    connection = connect_db()
    cursor = connection.cursor()

    for dato in datos_actualizados:
        id = dato['id']
        nombre = dato['nombre']

        cursor.execute("""
            UPDATE guides
            SET name = %s
            WHERE id = %s;
        """, (nombre, id))
    connection.commit()
    cursor.close()
    return jsonify({"status": "ok"})

@app.route("/guardar_ped", methods=["POST"])
def guardar_ped():
    datos_actualizados = request.get_json()
    connection = connect_db()
    cursor = connection.cursor()

    for dato in datos_actualizados:
        id = dato['id']
        entregado = dato['entregado'] == 'X'
        pagado = dato['pagado'] == 'X'
        cargado = dato['cargado'] == 'X'
        consignado = dato['consignado'] == 'X'

        cursor.execute("""
            UPDATE registers
            SET delivered = %s, paid = %s, charged = %s, consigned = %s
            WHERE id = %s;
        """, (entregado, pagado, cargado, consignado, id))
    connection.commit()
    cursor.close()
    return jsonify({"status": "ok"})

@app.route("/guardar_inv", methods=["POST"])
def guardar_inv():
    datos_actualizados = request.get_json()
    connection = connect_db()
    cursor = connection.cursor()

    for dato in datos_actualizados:
        id = dato['id']
        precio = int(dato['precio'][2:].replace('.', ''))
        cantidad = dato['cantidad']

        cursor.execute("""
            UPDATE products
            SET price = %s, quantity = %s
            WHERE id = %s;
        """, (precio, cantidad, id))
    connection.commit()
    cursor.close()
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run()
