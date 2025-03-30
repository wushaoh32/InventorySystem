import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import pandas as pd
from datetime import datetime

class WarehouseApp:
    def __init__(self, root):
        self.root = root
        self.root.title("备件仓库管理系统")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        self.create_widgets()
        self.create_db()
        self.refresh_table()

        # 窗口自适应配置
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=1)

    def create_db(self):
        conn = sqlite3.connect('warehouse.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS inventory
                     (序号 INTEGER PRIMARY KEY AUTOINCREMENT,
                     库房名称 TEXT, 物料编号 TEXT, 物料名称 TEXT,
                     规格型号 TEXT, 物料分类 TEXT, 单位 TEXT,
                     库存数量 INTEGER, 货架编号 TEXT, 层数 INTEGER,
                     最后库存变动时间 TIMESTAMP)''')
        conn.commit()
        conn.close()

    def create_widgets(self):
        # 上部操作区域
        top_frame = tk.Frame(self.root, bg='#DCDCDC', height=200)
        top_frame.grid(row=0, column=0, sticky='nsew')

        # 按钮布局
        btn_style = {'width': 12, 'height': 2, 'font': ('微软雅黑', 12)}
        tk.Button(top_frame, text="入库", command=self.add_item, **btn_style).grid(row=0, column=0, padx=20, pady=20)
        tk.Button(top_frame, text="出库", command=self.remove_item, **btn_style).grid(row=0, column=1, padx=20, pady=20)
        tk.Button(top_frame, text="导入", command=self.import_data, **btn_style).grid(row=0, column=2, padx=20, pady=5)
        tk.Button(top_frame, text="导出", command=self.export_data, **btn_style).grid(row=0, column=3, padx=20, pady=5)

        # 下部表格区域
        columns = ("序号", "库房名称", "物料编号", "物料名称", "规格型号", 
                 "物料分类", "单位", "库存数量", "货架编号", "层数", "最后库存变动时间")
        
        self.tree = ttk.Treeview(self.root, columns=columns, show='headings', height=20)
        vsb = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(self.root, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=1, column=0, sticky='nsew')
        vsb.grid(row=1, column=1, sticky='ns')
        hsb.grid(row=2, column=0, sticky='ew')

        # 配置列
        col_widths = [50, 100, 100, 120, 120, 100, 60, 80, 80, 60, 150]
        for col, width in zip(columns, col_widths):
            self.tree.heading(col, text=col)
            self.tree.column(col, width=width, anchor='center')

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        
        conn = sqlite3.connect('warehouse.db')
        c = conn.cursor()
        c.execute("SELECT * FROM inventory")
        rows = c.fetchall()
        for row in rows:
            self.tree.insert('', 'end', values=row)
        conn.close()

    def add_item(self, is_remove=False):
        self.input_window("入库操作" if not is_remove else "出库操作", is_remove)

    def remove_item(self):
        self.add_item(is_remove=True)

    def input_window(self, title, is_remove=False):
        window = tk.Toplevel(self.root)
        window.title(title)
        window.geometry("600x800")

        labels = ["库房名称", "物料编号", "物料名称", "规格型号", "物料分类",
                 "单位", "库存数量", "货架编号", "层数"]
        entries = {}
        
        for i, label in enumerate(labels):
            tk.Label(window, text=label).grid(row=i, column=0, padx=10, pady=5)
            if label == "规格型号":
                entries[label] = ttk.Combobox(window, width=25)
                entries[label].grid(row=i, column=1, padx=10, pady=5)
            else:
                entries[label] = tk.Entry(window, width=27)
                entries[label].grid(row=i, column=1, padx=10, pady=5)

        # 自动填充规格型号
        def update_spec(*args):
            material_name = entries["物料名称"].get()
            if material_name:
                conn = sqlite3.connect('warehouse.db')
                c = conn.cursor()
                c.execute("SELECT DISTINCT 规格型号 FROM inventory WHERE 物料名称=?", (material_name,))
                specs = [spec[0] for spec in c.fetchall()]
                entries["规格型号"].config(values=specs)
                conn.close()

        entries["物料名称"].bind("<KeyRelease>", update_spec)

        def submit():
            values = [e.get() if not isinstance(e, ttk.Combobox) else e.get() for e in entries.values()]
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                quantity = int(values[6])
                if is_remove:
                    quantity = -quantity
                
                conn = sqlite3.connect('warehouse.db')
                c = conn.cursor()
                c.execute('''INSERT INTO inventory VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                         (*values[:6], quantity, *values[7:9], current_time))
                conn.commit()
                conn.close()
                messagebox.showinfo("成功", "操作已提交！")
                window.destroy()
                self.refresh_table()
            except Exception as e:
                messagebox.showerror("错误", f"输入错误: {str(e)}")

        tk.Button(window, text="提交", command=submit).grid(row=len(labels)+1, columnspan=2, pady=20)

    def import_data(self):
        filepath = filedialog.askopenfilename(title="选择Excel文件", 
                                           filetypes=[("Excel文件", "*.xlsx")])
        if not filepath:
            return
            
        if messagebox.askyesno("确认", "将会覆盖现有数据，是否继续？"):
            try:
                df = pd.read_excel(filepath)
                df["最后库存变动时间"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                conn = sqlite3.connect('warehouse.db')
                df.to_sql('inventory', conn, if_exists='replace', index=False)
                conn.commit()
                conn.close()
                self.refresh_table()
                messagebox.showinfo("成功", "数据导入成功！")
            except Exception as e:
                messagebox.showerror("错误", f"导入失败: {str(e)}")

    def export_data(self):
        filename = f"备件物料表{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        filepath = filedialog.asksaveasfilename(
            title="保存文件", 
            initialfile=filename,
            defaultextension=".xlsx",
            filetypes=[("Excel文件", "*.xlsx")])
        
        if filepath:
            try:
                conn = sqlite3.connect('warehouse.db')
                df = pd.read_sql("SELECT * FROM inventory", conn)
                df.to_excel(filepath, index=False)
                conn.close()
                messagebox.showinfo("成功", f"文件已保存到：{filepath}")
            except Exception as e:
                messagebox.showerror("错误", f"导出失败: {str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = WarehouseApp(root)
    root.mainloop()