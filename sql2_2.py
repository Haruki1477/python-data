import tkinter as tk
from tkinter import messagebox, filedialog
import psycopg2
import csv
import customtkinter as ctk

# DB接続情報
DB_PARAMS = {
    "host": "localhost",
    "database": "test",  # データベース名「test」
    "user": "postgres",
    "password": "haru0707"
}

# カラーパレット
ctk.set_appearance_mode("System")  # ダーク/ライトモード
ctk.set_default_color_theme("blue")  # テーマを変更（blue, dark, light）

root = ctk.CTk()
root.title("社員管理アプリ")
root.geometry("1000x900")

# CSVインポートの関数
def import_from_csv():
    try:
        # ファイルダイアログでCSVファイルを選択
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if not file_path:
            return  # ファイルが選択されなかった場合は終了
        
        # CSVファイルを読み込み
        with open(file_path, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # ヘッダーをスキップ

            # データベースに挿入
            conn = psycopg2.connect(**DB_PARAMS)
            cur = conn.cursor()
            for row in reader:
                # row[0]がID, row[1]が名前, row[2]が部署
                cur.execute("INSERT INTO 社員 (名前, 部署) VALUES (%s, %s)", (row[1], row[2]))
            conn.commit()
            cur.close()
            conn.close()

        messagebox.showinfo("成功", "社員データをインポートしました！")
    except Exception as e:
        messagebox.showerror("エラー", str(e))

# グローバル変数（並び順を管理）
sort_order = tk.StringVar(value="ASC")  # デフォルトで昇順

# ラジオボタンで昇順降順を切り替える
def update_sort_order():
    fetch_employees(search_name=entry_search_name.get(), search_dept=entry_search_dept.get(), order=sort_order.get())

def fetch_employees(search_name=None, search_dept=None):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # 並び順を直接変数から取得
        order_clause = sort_order.get()  # ASC or DESC

        if search_name and search_dept:
            cur.execute(f"SELECT * FROM 社員 WHERE 名前 LIKE %s AND 部署 LIKE %s ORDER BY ID {order_clause}", (f"%{search_name}%", f"%{search_dept}%"))
        elif search_name:
            cur.execute(f"SELECT * FROM 社員 WHERE 名前 LIKE %s ORDER BY ID {order_clause}", (f"%{search_name}%",))
        elif search_dept:
            cur.execute(f"SELECT * FROM 社員 WHERE 部署 LIKE %s ORDER BY ID {order_clause}", (f"%{search_dept}%",))
        else:
            cur.execute(f"SELECT * FROM 社員 ORDER BY ID {order_clause}")

        rows = cur.fetchall()
        listbox.delete(0, tk.END)
        for row in rows:
            listbox.insert(tk.END, f"{row[0]}: {row[1]}（{row[2]}）")

        cur.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("エラー", str(e))


# CSVエクスポートの関数
def export_to_csv():
    try:
        # 社員データをデータベースから取得
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute("SELECT * FROM 社員")
        rows = cur.fetchall()
        cur.close()
        conn.close()

        # CSVファイルに書き込む
        with open("社員データ.csv", mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["ID", "名前", "部署"])  # ヘッダー
            writer.writerows(rows)  # データを書き込む

        messagebox.showinfo("成功", "社員データをCSVファイルにエクスポートしました！")
    except Exception as e:
        messagebox.showerror("エラー", str(e))

# 検索ボタンを押したときの処理
def search_employees():
    search_name = entry_search_name.get()
    search_dept = entry_search_dept.get()

    fetch_employees(search_name, search_dept, sort_order.get())

# 社員情報を追加する関数
def add_employee():
    name = entry_name.get()  # entry_name が正しく定義されているか確認
    name = entry_name.get()
    dept = entry_dept.get()

    if not name or not dept:
        messagebox.showwarning("入力エラー", "名前と部署を入力してください")
        return

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute("INSERT INTO 社員 (名前, 部署) VALUES (%s, %s)", (name, dept))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("成功", "社員を追加しました")
        entry_name.delete(0, tk.END)
        entry_dept.delete(0, tk.END)
        fetch_employees()  # 一覧を更新
    except Exception as e:
        messagebox.showerror("エラー", str(e))

# 社員情報を削除する関数
def delete_employee():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("選択エラー", "削除する社員を選択してください")
        return
    
    employee_id = listbox.get(selected[0]).split(":")[0]  # IDを取得

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute("DELETE FROM 社員 WHERE id = %s", (employee_id,))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("成功", "社員を削除しました")
        fetch_employees()  # 一覧を更新
    except Exception as e:
        messagebox.showerror("エラー", str(e))

# 社員情報を編集する関数
def edit_employee():
    selected = listbox.curselection()
    if not selected:
        messagebox.showwarning("選択エラー", "編集する社員を選択してください")
        return

    # IDと現在の名前・部署を取得
    employee_id = listbox.get(selected[0]).split(":")[0]
    current_name = listbox.get(selected[0]).split(":")[1].split("（")[0].strip()
    current_dept = listbox.get(selected[0]).split("（")[1].replace("）", "").strip()

    # 入力フォームに現在の情報をセット
    entry_name.delete(0, tk.END)
    entry_name.insert(0, current_name)
    entry_dept.delete(0, tk.END)
    entry_dept.insert(0, current_dept)

    # 編集を保存する関数
    def save_edits():
        new_name = entry_name.get()
        new_dept = entry_dept.get()

        if not new_name or not new_dept:
            messagebox.showwarning("入力エラー", "名前と部署を入力してください")
            return

        try:
            conn = psycopg2.connect(**DB_PARAMS)
            cur = conn.cursor()
            cur.execute("UPDATE 社員 SET 名前 = %s, 部署 = %s WHERE id = %s", (new_name, new_dept, employee_id))
            conn.commit()
            cur.close()
            conn.close()
            messagebox.showinfo("成功", "社員情報を更新しました")
            fetch_employees()  # 一覧を更新
        except Exception as e:
            messagebox.showerror("エラー", str(e))

    # 保存ボタンを表示
    save_button = tk.Button(root, text="保存", command=save_edits)
    save_button.pack(pady=5)

# ここで、エントリーフィールドが定義されていないため追加しました

# 社員情報を追加する関数
def add_employee():
    name = entry_name.get()  # entry_name が正しく定義されているか確認
    dept = entry_dept.get()

    if not name or not dept:
        messagebox.showwarning("入力エラー", "名前と部署を入力してください")
        return

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()
        cur.execute("INSERT INTO 社員 (名前, 部署) VALUES (%s, %s)", (name, dept))
        conn.commit()
        cur.close()
        conn.close()
        messagebox.showinfo("成功", "社員を追加しました")
        entry_name.delete(0, tk.END)
        entry_dept.delete(0, tk.END)
        fetch_employees()  # 一覧を更新
    except Exception as e:
        messagebox.showerror("エラー", str(e))

    
if root.winfo_exists():
    # ウィンドウが存在していれば操作を行う
    root.destroy()  # 例: アプリ終了処理

def check_window(window):
    try:
        # ウィンドウが存在しているかをチェック
        if window.winfo_exists():
            print("ウィンドウはまだ存在しています")
        else:
            print("ウィンドウは破棄されています")
    except Exception as e:
        print(f"エラーが発生しました: {str(e)}")

root = tk.Tk()
root.title("社員管理アプリ")
root.geometry("1000x900")
root.configure(bg="#f9f9f9")

# フォントとスタイル
LABEL_FONT = ("Arial", 10)
ENTRY_WIDTH = 150
PADY = 5

def update_sort_order():
    fetch_employees(
        search_name=entry_search_name.get(),
        search_dept=entry_search_dept.get()
    )


# スクロール可能なキャンバス作成
canvas = tk.Canvas(root, borderwidth=0, background="#f9f9f9")
scroll_frame = tk.Frame(canvas, background="#f9f9f9")  # 中身を詰めるためのFrame
scrollbar = tk.Scrollbar(root, orient="vertical", command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.create_window((0, 0), window=scroll_frame, anchor="nw")

# サイズ変化時にスクロール範囲を調整
def on_frame_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))

scroll_frame.bind("<Configure>", on_frame_configure)

# 入力フォームのウィジェットを定義
frame_entry = ctk.CTkFrame(scroll_frame) # 修正: scroll_frameを指定
frame_entry.pack(pady=10, padx=10, fill="x")

label_name = ctk.CTkLabel(frame_entry, text="社員：")
label_name.pack(side="left", padx=5)

entry_name = ctk.CTkEntry(frame_entry) # 修正: scroll_frameを指定
entry_name.pack(side="left", padx=5)

label_dept = ctk.CTkLabel(frame_entry, text="部署：")
label_dept.pack(side="left", padx=5)

entry_dept = ctk.CTkEntry(frame_entry)
entry_dept.pack(side="left", padx=5)


# ---------- 検索セクション ---------- 
frame_search = ctk.CTkFrame(scroll_frame)
frame_search.pack(padx=10, pady=10, fill="x")

label_search_name = ctk.CTkLabel(frame_search, text="名前：")
label_search_name.pack(side="left", padx=5)

entry_search_name = ctk.CTkEntry(frame_search)
entry_search_name.pack(side="left", padx=5)

label_search_dept = ctk.CTkLabel(frame_search, text="部署：")
label_search_dept.pack(side="left", padx=5)

entry_search_dept = ctk.CTkEntry(frame_search)
entry_search_dept.pack(side="left", padx=5)

button_search = ctk.CTkButton(frame_search, text="検索", command=search_employees)
button_search.pack(side="left", padx=5)

# ラジオボタンで昇順降順を選択する
radio_asc = tk.Radiobutton(root, text="昇順", variable=sort_order, value="ASC", command=update_sort_order)
radio_asc.pack()
radio_desc = tk.Radiobutton(root, text="降順", variable=sort_order, value="DESC", command=update_sort_order)
radio_desc.pack()


# ---------- リストボックス ---------- 
listbox = tk.Listbox(scroll_frame, height=10)
listbox.pack(padx=10, pady=10, fill="x")

# ---------- ボタン ---------- 
button_import = ctk.CTkButton(scroll_frame, text="CSVインポート", command=import_from_csv)
button_import.pack(pady=10)

button_export = ctk.CTkButton(scroll_frame, text="CSVエクスポート", command=export_to_csv)
button_export.pack(pady=10)

button_add = ctk.CTkButton(scroll_frame, text="社員を追加", command=add_employee)
button_add.pack(pady=10)

button_delete = ctk.CTkButton(scroll_frame, text="社員を削除", command=delete_employee)
button_delete.pack(pady=10)

button_edit = ctk.CTkButton(scroll_frame, text="社員を編集", command=edit_employee)
button_edit.pack(pady=10)

# ボタンを作成
btn_check = tk.Button(root, text="ウィンドウ状態確認", command=lambda: check_window(root))
btn_check.pack(pady=20)

# 初回データの表示
fetch_employees()

root.mainloop()
