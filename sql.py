import tkinter as tk
from tkinter import messagebox
import psycopg2

def fetch_employees_in_departments():
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="Step7",
            user="postgres",
            password="haru0707"
        )
        cur = conn.cursor()

        # サブクエリを使って特定の部署IDに属する社員を取得
        cur.execute("""
        SELECT *
        FROM customer
        WHERE NOT EXISTS(SELECT * FROM orders WHERE customer.顧客ID = orders.顧客ID)            
        """)
        rows = cur.fetchall()

        # 出力エリアをクリア
        output_text.delete("1.0", tk.END)

        # 結果表示
        for customer_id,customer_name in rows:
            output_text.insert(tk.END, f"顧客ID: {customer_id[0]} - 顧客名:{str(customer_name)}\n")


        cur.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("エラー", f"データベース接続またはクエリ実行中にエラーが発生しました:\n{e}")

# GUIセットアップ
root = tk.Tk()

frame = tk.Frame(root, padx=10, pady=10)
frame.pack()

btn = tk.Button(frame, text="押して表示", command=fetch_employees_in_departments)
btn.pack()

output_text = tk.Text(frame, height=10, width=60)
output_text.pack()

root.mainloop()
