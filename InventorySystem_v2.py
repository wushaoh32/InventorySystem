import os
import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import pandas as pd

class SparePartsManager:

    #主函数
    def __init__(self, master):
        #初始化时建立连接
        self.conn = sqlite3.connect('spare_parts.db')
        self.cursor = self.conn.cursor()

        self.master = master
        master.title("总装设备科备件库管理系统")
        master.geometry("{0}x{1}+0+0".format(master.winfo_screenwidth(), master.winfo_screenheight()))
        master.configure(bg='white')
        
        self.create_database()
        self.create_widgets()
        self.load_data()

    #数据库创建函数
    def create_database(self):
        #数据库结构
        self.conn = sqlite3.connect('InventorySystem.db')
        self.cursor = self.conn.cursor()
        #通过数据库连接对象创建一个游标对象，游标用于执行SQL语句并处理查询结果,execute是游标对象的方法,用于执行SQL语句
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
        #创建日志表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS operation_logs
                        (id INTEGER PRIMARY KEY AUTOINCREMENT,
                         operation_type TEXT,
                         part_number TEXT,
                         quantity_change INTEGER,
                         operator TEXT DEFAULT 'system',
                         operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        self.conn.commit()
   
    #主界面窗体函数
    def create_widgets(self):
        # 按钮区域，创建窗体部件
        button_frame = tk.Frame(self.master, bg='#DCDCDC', height=self.master.winfo_screenheight()//4)
        button_frame.pack(fill='x', padx=10, pady=5)

        buttons = [
            ('入库', self.add_part),
            ('出库', self.remove_part),
            ('导入', self.import_data),
            ('导出', self.export_data),
            ('搜索', self.search_parts),
            ('刷新',self.refresh_data),
            ('生成模版',self.generate_template),
            ('日志',self.show_logs)
        ]
        
        for text, command in buttons:
            #主界面的大按钮
            btn = tk.Button(button_frame, text=text, command=command, 
                           width=10, height=2, bg='#DCDCDC', fg='black')
            #大按钮的间距
            btn.pack(side='left', padx=10, pady=10)

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

    #主界面数据载入函数,TreeView是Python库的组件，以树形显示数据
    def load_data(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
            
        self.cursor.execute("SELECT * FROM parts")
        for row in self.cursor.fetchall():
            item = self.tree.insert('', 'end', values=row)
            if row[7] == 0:  # quantity=0
                self.tree.item(item, tags=('zero',))
        
        # 配置零库存样式,数量为0时显示为红色，数据信息不删除，当重新入库时，变为黑色
        self.tree.tag_configure('zero', foreground='red')
    #刷新函数
    def refresh_data(self):
        
        self.load_data()
        messagebox.showinfo("系统提示","数据已刷新")

    #主界面数据添加函数
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

    #自动填充补全函数
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

    #出库函数的二级界面函数
    def update_specification(self, entries):
        part_name = entries['物料名称'].get()
        if part_name:
            self.cursor.execute("SELECT DISTINCT specification FROM parts WHERE part_name LIKE ?", 
                              (f'%{part_name}%',))
            specs = [row[0] for row in self.cursor.fetchall()]
            entries['规格型号'].config(values=specs)

    #入库函数
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
            # 获取所有输入值，日志功能的大哥
            part_number = entries['物料编号'].get()
            quantity = int(entries['数量'].get())

            #确保在入库的方法中不删除零库存记录
            self.cursor.execute('''UPDATE parts SET 
                quantity=quantity+?, 
                last_update=?
                WHERE part_number=?''',
                (quantity, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), part_number))
            self.conn.commit()

            # 在提交成功后添加日志记录
            self.log_operation(
                operation_type="入库",
                part_number=part_number,
                quantity_change=quantity
            )

            window.destroy()
            self.load_data()
            
        except Exception as e:
            messagebox.showerror("错误", f"保存失败：{str(e)}")
            
    #出库函数      
    def remove_part(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要出库的物料")
            return
        
        part_info = self.tree.item(selected[0])['values']
        remove_window = tk.Toplevel(self.master)
        remove_window.title("出库操作")
        
        # 显示物料信息（不可编辑）
        tk.Label(remove_window, text=f"物料编号：{part_info[2]}").pack()
        tk.Label(remove_window, text=f"物料名称：{part_info[3]}").pack()
        tk.Label(remove_window, text=f"当前库存：{part_info[7]}").pack()
        
        tk.Label(remove_window, text="出库数量：").pack()
        quantity_entry = tk.Entry(remove_window)
        quantity_entry.pack()
        
        def confirm_remove():
            try:
                qty = int(quantity_entry.get())
                current_qty = int(part_info[7])  # 当前库存数量
                
                # 验证出库数量
                if qty <= 0:
                    messagebox.showerror("错误", "出库数量必须大于0")
                    return
                    
                if qty > current_qty:
                    messagebox.showerror("出库失败", "已有备件数量不足")
                    return
                
                # 更新库存数量（不再删除记录）
                new_qty = current_qty - qty
                self.cursor.execute("UPDATE parts SET quantity=?, last_update=? WHERE part_number=?",
                                (new_qty, datetime.now().strftime('%Y-%m-%d %H:%M:%S'), part_info[2]))
                self.conn.commit()
                
                # 记录出库日志
                self.log_operation(
                    operation_type="出库",
                    part_number=part_info[2],
                    quantity_change=-qty
                )
                
                remove_window.destroy()
                self.load_data()
                messagebox.showinfo("成功", f"成功出库 {qty} 个 {part_info[3]}")
                
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
        
    #导入函数
    def import_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not file_path:
            return
        
        if not messagebox.askyesno("确认", "此操作将覆盖现有数据，是否继续？"):
            return
        
        try:
            # 读取Excel并处理数据
            df = pd.read_excel(file_path)
            
            # 检查必要列是否存在
            required_columns = ['库房名称', '物料编号', '物料名称', '规格型号', 
                            '物料分类', '单位', '库存数量', '货架编号', '层数']
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                raise ValueError(f"缺少必要列: {', '.join(missing)}")

            # 数据清洗
            df = df[required_columns].copy()
            df['库存数量'] = pd.to_numeric(df['库存数量'], errors='coerce').fillna(0).astype(int)
            df['层数'] = pd.to_numeric(df['层数'], errors='coerce').fillna(1).astype(int)
            
            # 添加系统字段
            df['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 执行导入
            success_count = 0
            for _, row in df.iterrows():
                try:
                    #原有数据库插入代码
                    self.cursor.execute('''INSERT OR REPLACE INTO parts 
                        (warehouse, part_number, part_name, specification, 
                        category, unit, quantity, shelf_number, floor, last_update)
                        VALUES (?,?,?,?,?,?,?,?,?,?)''', 
                        (row['库房名称'], row['物料编号'], row['物料名称'], row['规格型号'],
                        row['物料分类'], row['单位'], row['库存数量'], 
                        row['货架编号'], row['层数'], row['last_update']))
                    success_count += 1
                    #为每条记录添加日志
                    self.log_operation(
                        operation_type="导入",
                        part_number=row['物料编号'],
                        quantity_change=row['库存数量']
                    )
                    success_count += 1
                except Exception as e:
                    print(f"导入失败记录: {row['物料编号']} - 错误: {str(e)}")
            
            self.conn.commit()
            self.load_data()
            
            if success_count == len(df):
                messagebox.showinfo("成功", f"全部{success_count}条数据导入成功！")
            else:
                messagebox.showwarning("部分成功", 
                    f"成功导入{success_count}/{len(df)}条数据，失败记录请查看控制台日志")
                
        except Exception as e:
            messagebox.showerror("导入错误", f"导入失败: {str(e)}\n\n请检查：\n1. 数值列是否包含非数字\n2. 是否缺少必要列\n3. 数据格式是否符合要求")
            messagebox.showinfo("导入说明", "请确保Excel包含以下9列且数据格式正确：\n" "库房名称 | 物料编号 | 物料名称 | 规格型号\n" "物料分类 | 单位 | 库存数量(数字) | 货架编号 | 层数(数字)")
    
    #导出函数
    def export_data(self):
        try:
            # 添加字段映射关系
            column_mapping = {
                'id': '序号',
                'warehouse': '库房名称',
                'part_number': '物料编号',
                'part_name': '物料名称',
                'specification': '规格型号',
                'category': '物料分类',
                'unit': '单位',
                'quantity': '库存数量',
                'shelf_number': '货架编号',
                'floor': '层数',
                'last_update': '最后库存变动时间'
            }
            #导出的数据包含零库存记录
            df = pd.read_sql_query("SELECT * FROM parts", self.conn)
            # 重命名列
            df.rename(columns=column_mapping, inplace=True)
            
            # 重新排列列顺序（与界面显示一致）
            df = df[[
                '序号', '库房名称', '物料编号', '物料名称', '规格型号',
                '物料分类', '单位', '库存数量', '货架编号', '层数', '最后库存变动时间'
            ]]
            
            file_name = f"备件物料表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            save_path = os.path.join(os.path.expanduser("~"), "Desktop", file_name)
            df.to_excel(save_path, index=False)
            messagebox.showinfo("成功", f"文件已保存到桌面：{file_name}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")

    #搜索函数
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
        def cancel_search():#关闭时自动刷新
            search_window.destroy()
            self.refresh_data()
        tk.Button(search_window,text="取消",command=cancel_search,width=6).pack(side='left',padx=35)
        tk.Button(search_window, text="搜索", command=perform_search,width=6).pack(side='right',padx=35)      
    
    #模版生成函数    
    def generate_template(self):
        #生成模版的方法
        template_df = pd.DataFrame(columns=[
            '库房名称','物料编号','物料名称','规格型号','物料分类','单位','库存数量','货架编号','层数'
        ])
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件","*.xlsx")],
            initialfile="备件导入模版.xlsx"
        )
        if save_path:
            template_df.to_excel(save_path,index=False)
            messagebox.showinfo("成功",f"模版已保存到：{C:/Users/admin/Desktop}")
    
    #日志记录函数
    def log_operation(self, operation_type, part_number, quantity_change, operator="system"):
        """记录操作日志"""
        try:
            self.cursor.execute('''INSERT INTO operation_logs 
                            (operation_type, part_number, quantity_change, operator)
                            VALUES (?,?,?,?)''',
                            (operation_type, part_number, quantity_change, operator))
            self.conn.commit()
        except Exception as e:
            print(f"日志记录失败：{str(e)}")

    #创建日志查看窗口
    def show_logs(self):
        log_window = tk.Toplevel(self.master)
        log_window.title("操作日志")
        log_window.geometry("800x600")
        
        # 日志表格
        tree = ttk.Treeview(log_window, columns=('ID','操作类型','物料编号','数量变化','操作人','操作时间'), show='headings')
        
        columns = [
            ('ID', 50), ('操作类型', 80), ('物料编号', 120), 
            ('数量变化', 80), ('操作人', 80), ('操作时间', 150)
        ]
        
        for col, width in columns:
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor='center')
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(log_window, orient="vertical", command=tree.yview)
        scrollbar.pack(side='right', fill='y')
        tree.configure(yscrollcommand=scrollbar.set)
        
        # 查询并显示日志
        self.cursor.execute("SELECT * FROM operation_logs ORDER BY operation_time DESC")
        for row in self.cursor.fetchall():
            tree.insert('', 'end', values=row)
        
        tree.pack(fill='both', expand=True)
        
        # 添加导出按钮
        tk.Button(log_window, text="导出日志", 
                command=lambda: self.export_logs()).pack(pady=5)

    def export_logs(self):
        """导出日志到Excel"""
        df = pd.read_sql_query("SELECT * FROM operation_logs ORDER BY operation_time DESC", self.conn)
        file_name = f"备件操作日志_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            initialfile=file_name,
            filetypes=[("Excel文件", "*.xlsx")]
        )
        if save_path:
            df.to_excel(save_path, index=False)
            messagebox.showinfo("成功", f"日志已导出到: {save_path}")    
if __name__ == "__main__":
    root = tk.Tk()
    app = SparePartsManager(root)
    root.mainloop()