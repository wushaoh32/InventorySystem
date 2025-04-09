import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import pandas as pd

class SparePartsManager:
    def __init__(self, master):
        self.master = master
        master.title("备件库管理系统")
        master.geometry("{0}x{1}+0+0".format(master.winfo_screenwidth(), master.winfo_screenheight()))
        master.configure(bg='white')
        
        self.create_database()
        self.create_widgets()
        self.load_data()

    def create_database(self):
        self.conn = sqlite3.connect('spare_parts.db')
        self.cursor = self.conn.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS parts
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             warehouse TEXT,
                             part_number TEXT UNIQUE,
                             part_name TEXT,
                             specification TEXT,
                             category TEXT,
                             unit TEXT,
                             quantity INTEGER,
                             shelf_number TEXT,
                             floor INTEGER,
                             last_update TIMESTAMP)''')
        self.conn.commit()

    def create_widgets(self):
        # 按钮区域
        button_frame = tk.Frame(self.master, bg='#DCDCDC', height=self.master.winfo_screenheight()//4)
        button_frame.pack(fill='x', padx=10, pady=5)

        buttons = [
            ('入库', self.add_part),
            ('出库', self.remove_part),
            ('导入', self.import_data),
            ('导出', self.export_data),
            ('搜索', self.search_parts)
        ]
        
        for text, command in buttons:
            btn = tk.Button(button_frame, text=text, command=command, 
                           width=15, height=2, bg='#DCDCDC', fg='black')
            btn.pack(side='left', padx=20, pady=10)

        # 数据显示区域
        self.tree = ttk.Treeview(self.master, columns=('ID','Warehouse','PartNumber','PartName','Specification',
                                                     'Category','Unit','Quantity','Shelf','Floor','LastUpdate'),
                                                     show='headings')
        
        columns = [
            ('ID', 50), ('库房名称', 100), ('物料编号', 120), ('物料名称', 150),
            ('规格型号', 150), ('物料分类', 100), ('单位', 50), ('库存数量', 80),
            ('货架编号', 80), ('层数', 50), ('最后更新时间', 150)
        ]
        
        for idx, (col, width) in enumerate(columns):
            self.tree.heading(f'#{idx+1}', text=col)
            self.tree.column(f'#{idx+1}', width=width, anchor='center')
            
        vsb = ttk.Scrollbar(self.master, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(fill='both', expand=True)

    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        self.cursor.execute("SELECT * FROM parts")
        rows = self.cursor.fetchall()
        for row in rows:
            self.tree.insert('', 'end', values=row)

    def add_part(self):
        add_window = tk.Toplevel(self.master)
        add_window.title("入库管理")
        
        labels = ['库房名称','物料编号','物料名称','规格型号','物料分类',
                 '单位','数量','货架编号','层数']
        entries = {}
        
        for idx, label in enumerate(labels):
            tk.Label(add_window, text=label).grid(row=idx, column=0, padx=5, pady=5)
            entries[label] = tk.Entry(add_window, width=25)
            entries[label].grid(row=idx, column=1, padx=5, pady=5)
            
        # 自动填充规格型号
        entries['物料名称'].bind('<KeyRelease>', lambda e: self.update_specification(entries))
        
        # 自动填充已有信息
        entries['物料编号'].bind('<FocusOut>', lambda e: self.auto_fill_info(entries))
        
        tk.Button(add_window, text="提交", 
                 command=lambda: self.submit_add(entries, add_window)).grid(row=len(labels), columnspan=2)

    def auto_fill_info(self, entries):
        part_number = entries['物料编号'].get()
        if part_number:
            self.cursor.execute("SELECT * FROM parts WHERE part_number=?", (part_number,))
            existing = self.cursor.fetchone()
            if existing:
                entries['物料名称'].insert(0, existing[3])
                entries['规格型号'].insert(0, existing[4])
                entries['物料分类'].insert(0, existing[5])
                entries['单位'].insert(0, existing[6])
                entries['货架编号'].insert(0, existing[8])
                entries['层数'].insert(0, existing[9])

    def update_specification(self, entries):
        part_name = entries['物料名称'].get()
        if part_name:
            self.cursor.execute("SELECT DISTINCT specification FROM parts WHERE part_name LIKE ?", 
                              (f'%{part_name}%',))
            specs = [row[0] for row in self.cursor.fetchall()]
            entries['规格型号'].config(values=specs)

    def submit_add(self, entries, window):
        data = {
            'warehouse': entries['库房名称'].get(),
            'part_number': entries['物料编号'].get(),
            'part_name': entries['物料名称'].get(),
            'specification': entries['规格型号'].get(),
            'category': entries['物料分类'].get(),
            'unit': entries['单位'].get(),
            'quantity': int(entries['数量'].get()),
            'shelf': entries['货架编号'].get(),
            'floor': int(entries['层数'].get()),
            'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        try:
            self.cursor.execute('''INSERT INTO parts VALUES 
                (NULL,?,?,?,?,?,?,?,?,?,?) 
                ON CONFLICT(part_number) DO UPDATE SET 
                quantity=quantity+excluded.quantity,
                last_update=excluded.last_update''',
                (data['warehouse'], data['part_number'], data['part_name'],
                data['specification'], data['category'], data['unit'],
                data['quantity'], data['shelf'], data['floor'], data['time']))
            self.conn.commit()
            window.destroy()
            self.load_data()
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")

    def remove_part(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要出库的物料")
            return
        
        part_info = self.tree.item(selected[0])['values']
        remove_window = tk.Toplevel(self.master)
        
        tk.Label(remove_window, text=f"物料编号：{part_info[2]}").pack()
        tk.Label(remove_window, text=f"物料名称：{part_info[3]}").pack()
        
        tk.Label(remove_window, text="出库数量：").pack()
        quantity_entry = tk.Entry(remove_window)
        quantity_entry.pack()
        
        def confirm_remove():
            try:
                qty = int(quantity_entry.get())
                if qty <= 0:
                    raise ValueError
                    
                self.cursor.execute("UPDATE parts SET quantity=quantity-? WHERE part_number=?",
                                (qty, part_info[2]))
                self.conn.commit()
                
                self.cursor.execute("SELECT quantity FROM parts WHERE part_number=?", (part_info[2],))
                remaining = self.cursor.fetchone()[0]
                
                if remaining <= 0:
                    self.cursor.execute("DELETE FROM parts WHERE part_number=?", (part_info[2],))
                    self.conn.commit()
                    
                remove_window.destroy()
                self.load_data()
            except ValueError:
                messagebox.showerror("错误", "请输入有效的正整数值")

        tk.Button(remove_window, text="确认出库", command=confirm_remove).pack() 

        def import_data(self):
            file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
            if file_path:
                try:
                    df = pd.read_excel(file_path)
                    # 处理导入逻辑...
                    messagebox.showinfo("成功", "数据导入成功！")
                    self.load_data()
                except Exception as e:
                    messagebox.showerror("错误", f"导入失败：{str(e)}")

        def export_data(self):
            file_name = f"备件物料表{datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
            # 导出逻辑...
            messagebox.showinfo("成功", f"文件已保存为：{file_name}")

        def search_parts(self):
            search_window = tk.Toplevel(self.master)
            # 搜索界面逻辑...

    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not file_path:
            return
        
        if not messagebox.askyesno("确认", "此操作将覆盖现有数据，是否继续？"):
            return
        
        try:
            df = pd.read_excel(file_path)
            df['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            self.cursor.executemany('''INSERT OR REPLACE INTO parts VALUES 
                (?,?,?,?,?,?,?,?,?,?,?)''', df.values.tolist())
            self.conn.commit()
            self.load_data()
            messagebox.showinfo("成功", "数据导入完成！")
        except Exception as e:
            messagebox.showerror("错误", f"导入失败：{str(e)}")

    def export_data(self):
        try:
            df = pd.read_sql_query("SELECT * FROM parts", self.conn)
            file_name = f"备件物料表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            save_path = os.path.join(os.path.expanduser("~"), "Desktop", file_name)
            df.to_excel(save_path, index=False)
            messagebox.showinfo("成功", f"文件已保存到桌面：{file_name}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")

    def search_parts(self):
        search_window = tk.Toplevel(self.master)
        search_window.title("搜索物料")
        
        search_type = tk.StringVar(value="part_number")
        tk.Radiobutton(search_window, text="按物料编号", variable=search_type, value="part_number").pack()
        tk.Radiobutton(search_window, text="按物料名称", variable=search_type, value="part_name").pack()
        
        search_entry = tk.Entry(search_window, width=30)
        search_entry.pack(pady=10)
        
        def perform_search():
            search_term = search_entry.get()
            if not search_term:
                return
                
            if search_type.get() == "part_number":
                self.cursor.execute("SELECT * FROM parts WHERE part_number=?", (search_term,))
            else:
                self.cursor.execute("SELECT * FROM parts WHERE part_name LIKE ?", (f"%{search_term}%",))
                
            results = self.cursor.fetchall()
            if not results:
                messagebox.showinfo("提示", "未找到匹配结果")
                return
                
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            for row in results:
                self.tree.insert('', 'end', values=row)
                
            search_window.destroy()

        tk.Button(search_window, text="搜索", command=perform_search).pack()      
          
if __name__ == "__main__":
    root = tk.Tk()
    app = SparePartsManager(root)
    root.mainloop()