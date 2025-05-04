import psycopg2

# DB接続情報
DB_PARAMS = {
    "host": "localhost",
    "dbname": "test",
    "user": "postgres",
    "password": "haru0707"
}

def show_products():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        select_sql = '''
        SELECT id, name, price, stock_quantity, created_at
        FROM products
        ORDER BY id
        '''
        cur.execute(select_sql)
        rows = cur.fetchall()

        print("商品一覧:")
        for row in rows:
            print(f"ID: {row[0]}, 名前: {row[1]}, 価格: ¥{row[2]:,.2f}, 在庫: {row[3]}, 登録日時: {row[4]}")

    except Exception as e:
        print("エラー:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()
def create_orders_table():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        create_sql = '''
        CREATE TABLE IF NOT EXISTS orders (
            id SERIAL PRIMARY KEY,
            product_id INTEGER REFERENCES products(id),
            quantity INTEGER NOT NULL,
            order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        cur.execute(create_sql)
        conn.commit()
        print("テーブル『orders（注文履歴）』を作成しました。")

    except Exception as e:
        print("エラー:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def add_order(product_id, quantity):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # 在庫チェック（商品が存在するか＆在庫が十分か）
        cur.execute("SELECT stock_quantity FROM products WHERE id = %s", (product_id,))
        result = cur.fetchone()
        if not result:
            print("エラー: 指定された商品IDは存在しません。")
            return
        stock = result[0]
        if stock < quantity:
            print(f"エラー: 在庫が不足しています（現在の在庫: {stock}）。")
            return

        # 注文の登録
        insert_sql = '''
        INSERT INTO orders (product_id, quantity)
        VALUES (%s, %s)
        '''
        cur.execute(insert_sql, (product_id, quantity))

        # 在庫を減らす
        update_sql = '''
        UPDATE products
        SET stock_quantity = stock_quantity - %s
        WHERE id = %s
        '''
        cur.execute(update_sql, (quantity, product_id))

        conn.commit()
        print("注文を登録しました。")

    except Exception as e:
        print("エラー:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()

def show_orders():
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        select_sql = '''
        SELECT
            o.id,
            p.name,
            o.quantity,
            o.order_date
        FROM orders o
        JOIN products p ON o.product_id = p.id
        ORDER BY o.id
        '''
        cur.execute(select_sql)
        rows = cur.fetchall()

        if not rows:
            print("注文履歴はまだありません。")
        else:
            print("注文履歴一覧:")
            for row in rows:
                print(f"注文ID: {row[0]}, 商品名: {row[1]}, 数量: {row[2]}, 注文日時: {row[3]}")

    except Exception as e:
        print("エラー:", e)

    finally:
        if cur:
            cur.close()
        if conn:
            conn.close()


# 実行
create_orders_table()

# 実行
show_products()

add_order(1,2)

show_orders()