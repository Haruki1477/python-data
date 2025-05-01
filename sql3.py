import tkinter as tk
from tkinter import ttk, messagebox
import psycopg2
from datetime import datetime, date
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# DB接続情報
DB_PARAMS = {
    "host": "localhost",
    "dbname": "test",
    "user": "postgres",
    "password": "haru0707"
}

# 勤怠記録（出勤 or 退勤）
def record_attendance(type_):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        employee_id = int(entry_id.get())
        today = date.today()
        now = datetime.now().time()

        cur.execute("SELECT * FROM 勤怠 WHERE 社員ID = %s AND 日付 = %s", (employee_id, today))
        result = cur.fetchone()

        if type_ == "出勤":
            if result:
                messagebox.showinfo("情報", "本日はすでに出勤済みです")
            else:
                cur.execute("INSERT INTO 勤怠 (社員ID, 日付, 出勤時刻) VALUES (%s, %s, %s)",
                            (employee_id, today, now))
                conn.commit()
                messagebox.showinfo("成功", "出勤記録を登録しました")
        else:  # 退勤
            if not result:
                messagebox.showerror("エラー", "出勤記録がありません")
            elif result[4]:  # 退勤時刻がある
                messagebox.showinfo("情報", "すでに退勤済みです")
            else:
                cur.execute("UPDATE 勤怠 SET 退勤時刻 = %s WHERE 勤怠ID = %s", (now, result[0]))
                conn.commit()
                messagebox.showinfo("成功", "退勤記録を更新しました")

        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("エラー", str(e))

# 勤怠一覧表示
def show_attendance():
    try:
        for row in tree.get_children():
            tree.delete(row)

        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        employee_id = int(entry_id.get())
        cur.execute("""
            SELECT 日付, 出勤時刻, 退勤時刻
            FROM 勤怠
            WHERE 社員ID = %s
            ORDER BY 日付 DESC
            LIMIT 30
        """, (employee_id,))

        rows = cur.fetchall()
        for row in rows:
            # 出勤時刻と退勤時刻の差を勤務時間として計算
            if row[1] and row[2]:  # 両方の時刻がある場合
                work_start = datetime.combine(date.today(), row[1])
                work_end = datetime.combine(date.today(), row[2])
                work_duration = work_end - work_start
                hours_worked = work_duration.total_seconds() / 3600  # 時間に換算
                hours_worked = round(hours_worked, 2)  # 小数点以下2桁に丸める
            else:
                hours_worked = 0

            tree.insert("", "end", values=(row[0], row[1], row[2], hours_worked))

        cur.close()
        conn.close()
    except Exception as e:
        messagebox.showerror("エラー", str(e))

# ダッシュボード情報を取得
def fetch_employee_dashboard(employee_id, start_date, end_date):
    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        # 勤務時間や勤務日数の集計（例：月ごとの勤務時間）
        query = """
            SELECT 
                SUM(勤務時間) AS total_hours,
                COUNT(DISTINCT 日付) AS work_days  -- 日付で集計
            FROM 勤怠
            WHERE 社員ID = %s AND 日付 BETWEEN %s AND %s;
        """
        cur.execute(query, (employee_id, start_date, end_date))
        row = cur.fetchone()

        # 結果を辞書として返す
        result = {
            "total_hours": row[0] if row[0] is not None else 0,  # Noneの場合0に変換
            "work_days": row[1] if row[1] is not None else 0,  # Noneの場合0に変換
        }

        cur.close()
        conn.close()
        return result
    except Exception as e:
        messagebox.showerror("エラー", str(e))
        return None

# ダッシュボード画面の表示
def show_dashboard():
    employee_id = int(entry_id.get())
    start_date = "2025-04-01"  # 例: 2025年4月1日から
    end_date = "2025-04-30"    # 例: 2025年4月30日まで

    dashboard_data = fetch_employee_dashboard(employee_id, start_date, end_date)

    if dashboard_data:
        total_hours = dashboard_data["total_hours"]
        work_days = dashboard_data["work_days"]

        dashboard_window = tk.Toplevel(root)
        dashboard_window.title(f"社員 {employee_id} のダッシュボード")
        dashboard_window.geometry("400x400")

        label_total_hours = tk.Label(dashboard_window, text=f"総勤務時間: {total_hours} 時間")
        label_total_hours.pack(pady=10)

        label_work_days = tk.Label(dashboard_window, text=f"出勤日数: {work_days} 日")
        label_work_days.pack(pady=10)

# 勤怠一覧の表示
def plot_attendance_chart():
    employee_id = int(entry_id.get())
    start_date = "2025-04-01"  # 例: 2025年4月1日から
    end_date = "2025-04-30"    # 例: 2025年4月30日まで

    try:
        conn = psycopg2.connect(**DB_PARAMS)
        cur = conn.cursor()

        query = """
            SELECT 日付, 勤務時間
            FROM 勤怠
            WHERE 社員ID = %s AND 日付 BETWEEN %s AND %s;
        """
        cur.execute(query, (employee_id, start_date, end_date))
        rows = cur.fetchall()

        dates = []
        work_hours = []

        for row in rows:
            dates.append(row[0])
            work_hours.append(row[1] if row[1] else 0)

        # グラフの作成
        plt.figure(figsize=(10, 6))
        plt.plot(dates, work_hours, marker="o", color="b")
        plt.xlabel("日付")
        plt.ylabel("勤務時間(時間)")
        plt.title(f"社員 {employee_id} の勤務時間 ({start_date}〜{end_date})")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.show()

        cur.close()
        conn.close()

    except Exception as e:
        messagebox.showerror("エラー", str(e))

# GUI構築
root = tk.Tk()
root.title("社員勤怠管理")
root.geometry("600x400")

tk.Label(root, text="社員ID").pack()
entry_id = tk.Entry(root)
entry_id.pack(pady=5)

btn_frame = tk.Frame(root)
btn_frame.pack()

tk.Button(btn_frame, text="出勤", command=lambda: record_attendance("出勤")).pack(side=tk.LEFT, padx=10, pady=5)
tk.Button(btn_frame, text="退勤", command=lambda: record_attendance("退勤")).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="勤怠一覧表示", command=show_attendance).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="ダッシュボード", command=show_dashboard).pack(side=tk.LEFT, padx=10)
tk.Button(btn_frame, text="勤務時間グラフ", command=plot_attendance_chart).pack(side=tk.LEFT, padx=10)

# Treeviewで勤怠履歴表示（勤務時間を追加）
tree = ttk.Treeview(root, columns=("日付", "出勤", "退勤", "勤務時間(時間)"), show="headings")
tree.heading("日付", text="日付")
tree.heading("出勤", text="出勤時刻")
tree.heading("退勤", text="退勤時刻")
tree.heading("勤務時間(時間)", text="勤務時間(時間)")
tree.pack(expand=True, fill=tk.BOTH, pady=10)

root.mainloop()
