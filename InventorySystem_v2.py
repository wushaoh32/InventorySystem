#os是内置标准库，提供与操作系统交互的函数（创建、删除、重命名）
import os
#内置用于操作SQLite数据库的标准库
import sqlite3
import sys
#thinter创建图形界面的标准库，并简称为tk
import tkinter as tk
#从tkinter库中导入特定的模块，ttk:主体化小部件，messagebox:各种类型的消息框，filedialog:创建文件选择对话框
#若不单独导入，在使用时需要tkinter.messagebox.showinfo这种较长的命名
from tkinter import ttk, messagebox, filedialog
#从datetime模块中导入datetime类（此处模块名与类名相同），获取当前时间，
from datetime import datetime
#pandas是数据处理和分析，读取各种格式的数据文件
import pandas as pd
import pytz
import requests
import json
import time
import hmac
import hashlib
import urllib
import base64
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from database import DBManager

USER_DB = r'\\10.253.62.19\Shares\10.253.62.19\Shares\user.db'

def check_login(user_id: str, user_name: str) -> bool:
    with DBManager(USER_DB) as db:
        result = db.execute(
            "SELECT user_name FROM users WHERE user_id=? AND user_name=?",
            (user_id, user_name)
        )
    return len(result) > 0


import configparser
from pathlib import Path


def get_config():
    """自动定位配置文件"""
    base_path = Path(__file__).parent
    if getattr(

            sys, 'frozen', False):  # 打包后模式
        base_path = Path(sys.executable).parent

    config = configparser.ConfigParser()
    config.read(base_path / 'config.ini')
    return config

from tkinter import messagebox
class SparePartsManager:
    #1主函数
    def __init__(self, master):
        # 动态加载配置文件
        self.config = self.load_config()
        # 初始化数据库连接
        self.user_db = DBManager(self.config['user_db'])
        self.spare_db = DBManager(self.config['spare_db'])
        self.master = master
        self.current_user = None  # 存储当前用户信息
        self.master.withdraw()  # 隐藏主窗口，等待登录
        # 初始化用户数据库
        self.init_user_db()
        # 显示登录窗口
        self.show_login()
        #__init__是类的构造函数，每当创建一个SparePartsManager实例时都会调用
        #初始化时建立连接
        #当调整表结构后需要删除旧表！！！！！！！！！！！！！！
        #self.conn = sqlite3.connect('数据库.db')
        db_path = r'\\10.253.62.19\Shares\spare_parts_system\数据库.db'
        conn = sqlite3.connect(db_path, timeout=3)
        conn.execute("PRAGMA journal_mode=WAL")  # 启用预写日志
        self.cursor = conn.cursor()
        # 钉钉配置（需要用户自行修改）
        self.dingtalk_webhook = "https://oapi.dingtalk.com/robot/send?access_token=ffcf37eb5141ef7d63d5a3918a99e5351f62a86974d4db6f348440693e2d6ae4"
        self.dingtalk_secret = "SEC89bf6db53bdddf7897917f217405a3f67360874018740696bb37e437f17dec62"  
        
        # 在类初始化中添加
        self.enable_dingtalk = True  # 可配置为False关闭通知

        #这行代码将传入构造函数的master参数赋值给实例对象master属性，此处master就指代正在创建的SparePartsManager实例
        self.master = master
        master.title("总装设备科备件库管理系统")
        master.geometry("{0}x{1}+0+0".format(master.winfo_screenwidth(), master.winfo_screenheight()))
        master.configure(bg='white')
        
        self.create_database()
        self.create_widgets()
        self.load_data()
        # 添加管理员按钮（默认隐藏）
        self.manage_btn = tk.Button(
            self.master,
            text="用户管理",
            command=self.manage_users,
            state=tk.DISABLED  # 初始状态不可用
        )
        #调整按钮在上还是在下
        self.manage_btn.pack(side='top', pady=5)

    def load_config(self) -> dict:
        """从配置文件读取路径"""
        config = {
            'user_db': r'\\10.253.62.19\Shares\spare_parts_system\user.db',
            'spare_db': r'\\10.253.62.19\Shares\spare_parts_system\数据库.db'
        }
        return config

    # 钉钉发送方法
    def send_dingtalk_msg(self, content):
        if not self.enable_dingtalk:
            return
    #新加登录界面
    def init_user_db(self):

        db_path = r'\\10.253.62.19\Shares\spare_parts_system\user.db'
        conn = sqlite3.connect(db_path, timeout=3)
        conn.execute("PRAGMA journal_mode=WAL")  # 启用预写日志
        #conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS users
                     (
                         user_id
                         TEXT
                         PRIMARY
                         KEY,
                         user_name
                         TEXT
                     )''')
        # 初始化管理员账号
        try:
            c.execute("INSERT OR IGNORE INTO users VALUES ('admin', '系统管理员')")
            conn.commit()
        except sqlite3.IntegrityError:
            pass
        conn.close()

    def show_login(self):
        """显示登录窗口（修改尺寸和位置）"""
        self.login_window = tk.Toplevel(self.master)
        self.login_window.title("用户登录")
        self.login_window.grab_set()

        # 设置窗口大小和位置
        window_width = 300
        window_height = 180
        screen_width = self.login_window.winfo_screenwidth()
        screen_height = self.login_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.login_window.geometry(f"{window_width}x{window_height}+{x}+{y}")

        # 使用Frame容器优化布局
        main_frame = tk.Frame(self.login_window)
        main_frame.pack(expand=True, padx=20, pady=20)

        # 工号输入
        tk.Label(main_frame, text="工号：").grid(row=0, column=0, sticky='w', pady=5)
        self.user_id_entry = tk.Entry(main_frame, width=20)
        self.user_id_entry.grid(row=0, column=1, pady=5)

        # 姓名输入
        tk.Label(main_frame, text="姓名：").grid(row=1, column=0, sticky='w', pady=5)
        self.user_name_entry = tk.Entry(main_frame, width=20)
        self.user_name_entry.grid(row=1, column=1, pady=5)

        # 登录按钮（居中显示）
        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=2, columnspan=2, pady=15)
        tk.Button(btn_frame, text="登录", command=self.check_login, width=10).pack()

        # 让输入框获得焦点
        self.user_id_entry.focus_set()

    def check_login(self):
        """修改后的登录验证方法"""
        user_id = self.user_id_entry.get().strip()
        user_name = self.user_name_entry.get().strip()

        db_path = r'\\10.253.62.19\Shares\spare_parts_system\user.db'
        conn = sqlite3.connect(db_path, timeout=3)
        conn.execute("PRAGMA journal_mode=WAL")  # 启用预写日志
        #conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute("SELECT user_name FROM users WHERE user_id=? AND user_name=?",
                  (user_id, user_name))
        result = c.fetchone()
        conn.close()

        if result:
            self.current_user = {'id': user_id, 'name': user_name}
            # 如果是管理员，启用管理按钮
            if user_id == 'admin':
                self.manage_btn.config(state=tk.NORMAL)
            self.login_window.destroy()
            self.master.deiconify()
        else:
            messagebox.showerror("登录失败", "工号或姓名错误")

        #在登录验证后更新按钮状态
        if result:
            self.current_user = {'id': user_id, 'name': user_name}
            # 如果是管理员，显示管理按钮和导入按钮
            if user_id == 'admin':
                self.manage_btn.config(state=tk.NORMAL)
                self.buttons['导入'].pack(side='left', padx=15, pady=10)  # 显示导入按钮


    def manage_users(self):
        """用户管理窗口（完整实现）"""
        if self.current_user['id'] != 'admin':
            messagebox.showerror("权限不足", "仅管理员可操作")
            return

        self.manage_window = tk.Toplevel(self.master)
        self.manage_window.title("用户管理")
        self.manage_window.geometry("400x300")

        # 用户列表表格
        self.user_tree = ttk.Treeview(
            self.manage_window,
            columns=('user_id', 'user_name'),
            show='headings'
        )
        self.user_tree.heading('user_id', text='工号')
        self.user_tree.column('user_id', width=100, anchor='center')
        self.user_tree.heading('user_name', text='姓名')
        self.user_tree.column('user_name', width=150, anchor='center')
        self.user_tree.pack(fill='both', expand=True, padx=10, pady=10)

        # 操作按钮
        btn_frame = tk.Frame(self.manage_window)
        btn_frame.pack(pady=5)

        tk.Button(
            btn_frame,
            text="添加用户",
            command=self.show_add_user_dialog
        ).pack(side='left', padx=5)

        tk.Button(
            btn_frame,
            text="删除用户",
            command=self.delete_user
        ).pack(side='left', padx=5)

        # 初始化用户列表
        self.refresh_user_list()

    def refresh_user_list(self):
        """刷新用户列表数据"""
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)

        db_path = r'\\10.253.62.19\Shares\spare_parts_system\user.db'
        conn = sqlite3.connect(db_path, timeout=3)
        conn.execute("PRAGMA journal_mode=WAL")  # 启用预写日志
        #conn = sqlite3.connect('user.db')
        c = conn.cursor()
        c.execute("SELECT user_id, user_name FROM users")
        for row in c.fetchall():
            self.user_tree.insert('', 'end', values=row)
        conn.close()

    def show_add_user_dialog(self):
        """显示添加用户对话框"""
        self.add_window = tk.Toplevel(self.manage_window)
        self.add_window.title("添加用户")
        self.add_window.grab_set()

        tk.Label(self.add_window, text="工号：").grid(row=0, column=0, padx=5, pady=5)
        self.new_id_entry = tk.Entry(self.add_window)
        self.new_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.add_window, text="姓名：").grid(row=1, column=0, padx=5, pady=5)
        self.new_name_entry = tk.Entry(self.add_window)
        self.new_name_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Button(
            self.add_window,
            text="保存",
            command=self.save_user
        ).grid(row=2, columnspan=2, pady=10)

    def save_user(self):
        """保存新用户到数据库"""
        user_id = self.new_id_entry.get().strip()
        user_name = self.new_name_entry.get().strip()

        if not user_id or not user_name:
            messagebox.showerror("错误", "工号和姓名不能为空")
            return

        db_path = r'\\10.253.62.19\Shares\spare_parts_system\user.db'
        conn = sqlite3.connect(db_path, timeout=3)
        conn.execute("PRAGMA journal_mode=WAL")  # 启用预写日志
        #conn = sqlite3.connect('user.db')
        c = conn.cursor()
        try:
            c.execute(
                "INSERT INTO users (user_id, user_name) VALUES (?, ?)",
                (user_id, user_name)
            )
            conn.commit()
            messagebox.showinfo("成功", "用户添加成功")
            self.refresh_user_list()
            self.add_window.destroy()
        except sqlite3.IntegrityError:
            messagebox.showerror("错误", "工号已存在")
        finally:
            conn.close()

    def delete_user(self):
        """删除选中用户"""
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showerror("错误", "请选择要删除的用户")
            return

        user_id = self.user_tree.item(selected[0], 'values')[0]
        if user_id == 'admin':
            messagebox.showerror("错误", "不能删除管理员账号")
            return

        if messagebox.askyesno("确认", f"确定删除用户 {user_id} 吗？"):
            db_path = r'\\10.253.62.19\Shares\spare_parts_system\user.db'
            conn = sqlite3.connect(db_path, timeout=3)
            conn.execute("PRAGMA journal_mode=WAL")  # 启用预写日志
            #conn = sqlite3.connect('user.db')
            c = conn.cursor()
            c.execute("DELETE FROM users WHERE user_id=?", (user_id,))
            conn.commit()
            conn.close()
            self.refresh_user_list()
    #2、数据库创建函数
    def create_database(self):
        #数据库结构
        #当调整表结构后需要删除旧表！！！！！！！！！！！！！！
        #self.conn = sqlite3.connect('数据库.db')
        db_path = r'\\10.253.62.19\Shares\spare_parts_system\数据库.db'
        conn = sqlite3.connect(db_path, timeout=3)
        conn.execute("PRAGMA journal_mode=WAL")  # 启用预写日志
        self.cursor = conn.cursor()
        #通过数据库连接对象创建一个游标对象，游标用于执行SQL语句并处理查询结果,execute是游标对象的方法,用于执行SQL语句
        #新增价格列（REAL类型存储小数）
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS parts
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                             warehouse TEXT,
                             part_number TEXT UNIQUE,
                             part_name TEXT,
                             specification TEXT,
                             category TEXT,
                             unit TEXT,
                             quantity INTEGER,
                             price REAL,
                             shelf_number TEXT,
                             floor INTEGER,
                             last_update TIMESTAMP)''')
        conn.commit()
        #创建日志表
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS operation_logs
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            operation_type TEXT,
                            part_number TEXT,
                            quantity_change INTEGER,
                            operator TEXT,
                            operation_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')

        conn.commit()
   
    #3主界面窗体函数
    def create_widgets(self):
        # 按钮区域，创建窗体部件
        button_frame = tk.Frame(self.master, bg='#DCDCDC', height=self.master.winfo_screenheight()//4)
        button_frame.pack(fill='x', padx=10, pady=5)
        #修改按钮创建方式
        self.buttons = {}
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
            #隐藏按钮
            self.buttons[text] = btn
        #初始化隐藏按钮导入
        self.buttons['导入'].pack_forget()

        # 数据显示区域
        self.tree = ttk.Treeview(self.master, columns=('ID','Warehouse','PartNumber','PartName','Specification',
                                                     'Category','Unit','Quantity','Price','Shelf','Floor','LastUpdate'),
                                                     show='headings')
        
        columns = [
            ('ID', 50), ('库房名称', 100), ('物料编号', 120), ('物料名称', 150),
            ('规格型号', 150), ('物料分类', 100), ('单位', 50), ('库存数量', 80),
            ('价格（元）',80),('货架编号', 80), ('层数', 50), ('最后更新时间', 150)
        ]
        
        for idx, (col, width) in enumerate(columns):
            self.tree.heading(f'#{idx+1}', text=col)
            self.tree.column(f'#{idx+1}', width=width, anchor='center')
            
        vsb = ttk.Scrollbar(self.master, orient="vertical", command=self.tree.yview)
        vsb.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(fill='both', expand=True)

    #4主界面数据载入函数,TreeView是Python库的组件，以树形显示数据
    def load_data(self):
        self.cursor.execute("SELECT *, datetime(last_update, 'localtime') FROM parts")
        for row in self.tree.get_children():
            self.tree.delete(row)

        #获取数据并插入TreeView    
        self.cursor.execute("SELECT * FROM parts")
        for row in self.cursor.fetchall():
            item = self.tree.insert('', 'end', values=row)
            if row[7] == 0:  # quantity=0
                self.tree.item(item, tags=('zero',))
            elif row[7] == 1:
                self.tree.item(item,tags=('low_stock',))
        # 配置零库存样式,数量为0时显示为红色，数据信息不删除，当重新入库时，变为黑色
        self.tree.tag_configure('zero', foreground='red')
        self.tree.tag_configure('low_stock', foreground='#008000')
    
    #5刷新函数
    def refresh_data(self):
        
        self.load_data()
        messagebox.showinfo("系统提示","数据已刷新")

    #6入库函数：入库按钮、耳机弹窗入库信息、自动补全，进行整合（看似只加了一个价格列，结果修改一天）
    def add_part(self): 
        add_window = tk.Toplevel(self.master)
        add_window.title("备件入库")
        
        # 字段配置（调整库房名称为下拉列表）
        fields = [
            ('库房名称', 'combo'),  # 修改为下拉列表
            ('物料编号', 'text'),
            ('物料名称', 'text'),
            ('规格型号', 'combo'),
            ('物料分类', 'text'),
            ('单位', 'text'),
            ('库存数量', 'number'),
            ('价格(元)', 'number'),
            ('货架编号', 'text'),
            ('层数', 'number')
        ]
        
        entries = {}
        
        # 创建输入组件
        for idx, (label, ftype) in enumerate(fields):
            tk.Label(add_window, text=label).grid(row=idx, column=0, padx=5, pady=5)
            
            if ftype == 'combo':
                entry = ttk.Combobox(add_window, width=23)
                entry.grid(row=idx, column=1, padx=5, pady=5)
                # 如果是库房名称，初始化下拉列表
                if label == '库房名称':
                    self.refresh_warehouse_list(entry)
            else:
                entry = tk.Entry(add_window, width=25)
                entry.grid(row=idx, column=1, padx=5, pady=5)
            
            entries[label] = entry

        # 新增刷新库房列表按钮
        refresh_btn = tk.Button(add_window, text="刷新库房列表", 
                            command=lambda: self.refresh_warehouse_list(entries['库房名称']))
        refresh_btn.grid(row=0, column=2, padx=5)

        # 自动填充功能（修改为联合校验）
        def auto_fill(event=None):
            """联合校验库房名称和物料编号"""
            warehouse = entries['库房名称'].get()
            part_number = entries['物料编号'].get()
            
            # 联合查询
            if warehouse and part_number:
                self.cursor.execute("SELECT * FROM parts WHERE warehouse=? AND part_number=?", 
                                (warehouse, part_number))
                existing = self.cursor.fetchone()
                if existing:
                    # 自动填充其他字段
                    entries['物料名称'].delete(0, tk.END)
                    entries['物料名称'].insert(0, existing[3])
                    entries['规格型号'].set(existing[4])
                    entries['物料分类'].delete(0, tk.END)
                    entries['物料分类'].insert(0, existing[5])
                    entries['单位'].delete(0, tk.END)
                    entries['单位'].insert(0, existing[6])
                    entries['价格(元)'].delete(0, tk.END)
                    entries['价格(元)'].insert(0, f"{existing[8]:.1f}")
                    entries['货架编号'].delete(0, tk.END)
                    entries['货架编号'].insert(0, existing[9])
                    entries['层数'].delete(0, tk.END)
                    entries['层数'].insert(0, existing[10])
                    return
            
            # 更新规格型号下拉
            part_name = entries['物料名称'].get()
            if part_name:
                self.cursor.execute("SELECT DISTINCT specification FROM parts WHERE part_name LIKE ?", 
                                (f'%{part_name}%',))
                entries['规格型号']['values'] = [row[0] for row in self.cursor.fetchall()]

        entries['库房名称'].bind('<<ComboboxSelected>>', auto_fill)
        entries['物料编号'].bind('<FocusOut>', auto_fill)
        entries['物料名称'].bind('<KeyRelease>', auto_fill)
        
        # 提交处理
        def submit():
            """整合后的提交处理"""
            try: 
                # 获取所有输入值
                warehouse = entries['库房名称'].get().strip()
                part_number = entries['物料编号'].get().strip()
                part_name = entries['物料名称'].get().strip()  
                quantity = int(entries['库存数量'].get())
                # 查询当前库存
                self.cursor.execute("SELECT quantity FROM parts WHERE part_number=?", (part_number,))
                existing = self.cursor.fetchone()
                current_qty = existing[0] if existing else 0
                
                # 计算新库存
                new_qty = current_qty + quantity
                #入库校验增强
                if not warehouse:
                    raise ValueError("库房名称不能为空")
                if not part_number:
                    raise ValueError("物料编号不能为空")      

                # 校验库房是否存在
                self.cursor.execute("SELECT 1 FROM parts WHERE warehouse=?", (warehouse,))
                warehouse_exists = self.cursor.fetchone()
                
                if not warehouse_exists:
                    # 新库房确认
                    if not messagebox.askyesno("确认", 
                        f"库房 '{warehouse}' 不存在，确认要创建新库房吗？"):
                        messagebox.showinfo("提示", "请检查库房名称")
                        return
                # 数据校验
                required_fields = ['库房名称', '物料编号', '物料名称', '规格型号', 
                                '物料分类', '单位', '库存数量', '价格(元)']
                for field in required_fields:
                    if not entries[field].get().strip():
                        raise ValueError(f"{field}不能为空")
                
                # 数据转换
                data = {
                    'warehouse': entries['库房名称'].get(),
                    'part_number': entries['物料编号'].get(),
                    'part_name': entries['物料名称'].get(),
                    'specification': entries['规格型号'].get(),
                    'category': entries['物料分类'].get(),
                    'unit': entries['单位'].get(),
                    'quantity': int(entries['库存数量'].get()),
                    'price': round(float(entries['价格(元)'].get()), 1),  # 价格处理
                    'shelf': entries['货架编号'].get(),
                    'floor': int(entries['层数'].get() or 0),
                    'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
                
                if data['price'] < 0:
                    raise ValueError("价格不能为负数")
                
                # 数据库操作
                self.cursor.execute('''INSERT INTO parts 
                    (warehouse, part_number, part_name, specification, 
                    category, unit, quantity, price, shelf_number, floor, last_update)
                    VALUES (?,?,?,?,?,?,?,?,?,?,?)
                    ON CONFLICT(part_number) DO UPDATE SET
                        quantity = quantity + excluded.quantity,
                        price = excluded.price,
                        last_update = excluded.last_update''',
                    (data['warehouse'], data['part_number'], data['part_name'],
                    data['specification'], data['category'], data['unit'],
                    data['quantity'], data['price'],  # 新增价格
                    data['shelf'], data['floor'], data['time']))
                
                self.conn.commit()
                
                # 记录日志
                quantity =int(entries['库存数量'].get())
                self.log_operation("入库", part_number, quantity)
                
                add_window.destroy()
                self.load_data()
                messagebox.showinfo("成功", "入库操作已完成")
                # 发送钉钉消息（使用已定义的变量）
                msg = f"**📦 物料入库通知** \n\n" \
                    f"- 库房名称：{warehouse} \n" \
                    f"- 物料编号：{part_number} \n" \
                    f"- 物料名称：{part_name} \n" \
                    f"- 入库数量：{quantity} \n" \
                    f"- 最新库存：{new_qty} \n" \
                    f"- 操作时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
                self.send_dingtalk_msg(msg)
        
                
            except ValueError as e:
                messagebox.showerror("输入错误", str(e))
            except Exception as e:
                messagebox.showerror("系统错误", f"保存失败：{str(e)}")
        
        
        # 提交按钮
        tk.Button(add_window, text="提交入库", command=submit, 
                bg='#4CAF50', fg='white').grid(row=len(fields), columnspan=2, pady=10)
            

    #7出库函数的二级界面函数
    def update_specification(self, entries):
        part_name = entries['物料名称'].get()
        if part_name:
            self.cursor.execute("SELECT DISTINCT specification FROM parts WHERE part_name LIKE ?", 
                              (f'%{part_name}%',))
            specs = [row[0] for row in self.cursor.fetchall()]
            entries['规格型号'].config(values=specs)
       
    #8出库函数      
    def remove_part(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("警告", "请先选择要出库的物料")
            return

        part_info = self.tree.item(selected[0])['values']
        remove_window = tk.Toplevel(self.master)
        remove_window.title("出库操作")

        # === 设置窗口大小和居中 ===
        window_width = 400  # 加宽窗口
        window_height = 250  # 加高窗口
        screen_width = remove_window.winfo_screenwidth()
        screen_height = remove_window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        remove_window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        remove_window.resizable(False, False)  # 禁止调整大小

        # === 使用Frame优化布局 ===
        main_frame = tk.Frame(remove_window)
        main_frame.pack(expand=True, padx=20, pady=20)

        # === 物料信息展示 ===
        info_frame = tk.Frame(main_frame)
        info_frame.pack(fill='x', pady=10)

        tk.Label(info_frame, text="物料编号：", font=('微软雅黑', 10)).grid(row=0, column=0, sticky='w')
        tk.Label(info_frame, text=part_info[2], font=('微软雅黑', 10, 'bold')).grid(row=0, column=1, sticky='w')

        tk.Label(info_frame, text="物料名称：", font=('微软雅黑', 10)).grid(row=1, column=0, sticky='w')
        tk.Label(info_frame, text=part_info[3], font=('微软雅黑', 10, 'bold')).grid(row=1, column=1, sticky='w')

        tk.Label(info_frame, text="当前库存：", font=('微软雅黑', 10)).grid(row=2, column=0, sticky='w', pady=5)
        tk.Label(info_frame, text=str(part_info[7]), font=('微软雅黑', 10, 'bold')).grid(row=2, column=1, sticky='w')

        # === 出库数量输入 ===
        input_frame = tk.Frame(main_frame)
        input_frame.pack(fill='x', pady=15)

        tk.Label(input_frame, text="出库数量：", font=('微软雅黑', 10)).grid(row=0, column=0)
        quantity_entry = tk.Entry(input_frame, width=15, font=('微软雅黑', 10))
        quantity_entry.grid(row=0, column=1, padx=5)
        quantity_entry.focus_set()  # 自动聚焦输入框

        # === 操作按钮 ===
        btn_frame = tk.Frame(main_frame)
        btn_frame.pack(pady=10)
        
        def confirm_remove():

            try:
                qty = int(quantity_entry.get())
                selected = self.tree.selection()
                part_info = self.tree.item(selected[0])['values']
                warehouse = part_info[1]  # 假设物料编号在第3列
                part_number = part_info[2]  # 假设物料编号在第3列
                part_name = part_info[3]  # 假设物料编号在第4列
                current_qty = part_info[7]  # 当前库存数量在第8列
                remaining = current_qty - qty

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
                self.log_operation("出库", part_info[2], -qty)
                
                remove_window.destroy()
                self.load_data()
                messagebox.showinfo("成功", f"成功出库 {qty} 个 {part_info[3]}")
                #钉钉
                msg = f"**🚚 物料出库提醒** \n\n" \
                f"- 库房名称：{warehouse} \n" \
                f"- 物料编号：{part_number} \n" \
                f"- 物料名称：{part_name} \n" \
                f"- 出库数量：{qty} \n" \
                f"- 剩余库存：{remaining} \n" \
                f"- 操作时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"

                self.send_dingtalk_msg(msg)
                
            except ValueError:
                messagebox.showerror("错误", "请输入有效的正整数值")

        tk.Button(btn_frame, text="确认出库", command=confirm_remove,
                  width=10, bg='#FF6666', fg='white').pack(side='left', padx=10)

        tk.Button(btn_frame, text="取消", command=remove_window.destroy,
                  width=10).pack(side='left', padx=10)

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
        
    #9导入函数
    def import_data(self):

        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx")])
        if not file_path:
            return
        
        if not messagebox.askyesno("确认", "此操作将覆盖现有数据，是否继续？"):
            return
        
        try:
            # 读取Excel并处理数据
            df = pd.read_excel(file_path)
            
            # 检查必要列是否存在,新增价格列，修改列数为10列
            required_columns = ['库房名称', '物料编号', '物料名称', '规格型号', 
                            '物料分类', '单位', '库存数量', '价格','货架编号', '层数']
            
            if not all(col in df.columns for col in required_columns):
                missing = [col for col in required_columns if col not in df.columns]
                raise ValueError(f"缺少必要列: {', '.join(missing)}")

            # 对Excel中的数据进行清洗
            df = df[required_columns].copy()
            df['库存数量'] = pd.to_numeric(df['库存数量'], errors='coerce').fillna(0).astype(int)
            df['层数'] = pd.to_numeric(df['层数'], errors='coerce').fillna(1).astype(int)
            #价格的清理，我直接用了一个函数来实现，因为他这个功能需要处理多种异常
            df['价格'] = df['价格'].apply(self.clean_price)

            
            # 添加系统字段
            df['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            # 执行导入
            success_count = 0
            for _, row in df.iterrows():
                try:
                    #原有数据库插入代码
                    self.cursor.execute('''INSERT OR REPLACE INTO parts 
                        (warehouse, part_number, part_name, specification, 
                        category, unit, quantity, price, shelf_number, floor, last_update)
                        VALUES (?,?,?,?,?,?,?,?,?,?,?)''', 
                        #千万记得调整表结构时，对此处的？进行修改，否则报错如“10 values for 11 column”
                        #此处SQL语句中的？是一种占位符，防止SQL注入攻击，用上?之后，无论用户输入什么内容，
                        # 都只会被当做数据来处理，而不会被解析为SQL语句的一部分
                        (row['库房名称'], row['物料编号'], row['物料名称'], row['规格型号'],
                        row['物料分类'], row['单位'], row['库存数量'], row['价格'],
                        row['货架编号'], row['层数'], row['last_update']))
                    success_count += 1
                    #为每条记录添加日志
                    self.log_operation(
                        operation_type="导入",
                        part_number=row['物料编号'],
                        quantity_change=row['库存数量']
                    )
                    success_count += 1
                    self.log_operation("导入", row['物料编号'], row['库存数量'])
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
            messagebox.showinfo("导入说明", "请确保Excel包含以下9列且数据格式正确：\n" "库房名称 | 物料编号 | 物料名称 | 规格型号\n" "物料分类 | 单位 | 库存数量(数字)|价格 | 货架编号 | 层数(数字)")
    
    #10导出函数
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
                'price':'价格（元）',
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
                '物料分类', '单位', '库存数量','价格（元）', '货架编号', '层数', '最后库存变动时间'
            ]]
            
            file_name = f"备件物料表_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            save_path = os.path.join(os.path.expanduser("~"), "Desktop", file_name)
            df.to_excel(save_path, index=False)
            messagebox.showinfo("成功", f"文件已保存到桌面：{file_name}")
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")

    #11搜索函数
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
    
    #12模版生成函数

    def generate_template(self):
        #生成模版的表头
        template_df = pd.DataFrame(columns=[
            '库房名称','物料编号','物料名称','规格型号','物料分类','单位','库存数量','价格','货架编号','层数'
        ])
        #添加实例数据
        template_df.loc[0] = [
            "示例库房","GWGW0101","示例物料","SPEC-001","电气设备","个",10,99.5,"A01",2
        ]
        save_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel文件","*.xlsx")],
            initialfile="备件导入模版.xlsx"
        )
        if save_path:
            template_df.to_excel(save_path,index=False)
            #在原始字符串前加  r  ，可以让字符串中的字符都按照字面意思解析，不会对  \  进行转义处理。
            messagebox.showinfo("成功",f"模版已保存到：{r'C:/Users/admin/Desktop'}") 
    
    #13、日志记录函数
    #日志操作
    def log_operation(self, operation_type, part_number, quantity_change):
        """基础日志记录方法"""
        """操作人"""
        try:
            operator = self.current_user['name'] if self.current_user else 'system'
            self.cursor.execute('''INSERT INTO operation_logs
                                       (operation_type, part_number, quantity_change, operator)
                                   VALUES (?, ?, ?, ?)''',
                                (operation_type, part_number, quantity_change, operator))
            self.conn.commit()
        except Exception as e:
            print(f"日志记录失败: {str(e)}")

    #14创建日志查看窗口
    def show_logs(self):
        log_window = tk.Toplevel(self.master)
        log_window.title("操作日志")

        # 修正列定义（必须与查询字段顺序完全一致）
        columns = [
            ('ID', 50),
            ('操作类型', 80),
            ('物料编号', 120),
            ('数量变化', 80),
            ('操作人', 100),  # 新增操作人列
            ('操作时间', 150)  # 原时间列保持最后
        ]

        tree = ttk.Treeview(log_window, columns=[col[0] for col in columns], show='headings')
        for col, width in columns:
            tree.heading(col, text=col)
            tree.column(col, width=width, anchor='center')

        # 关键修正：查询时显式指定字段顺序
        self.cursor.execute('''SELECT id,
                                      operation_type,
                                      part_number,
                                      quantity_change,
                                      operator,
                                      datetime(operation_time, 'localtime')
                               FROM operation_logs
                               ORDER BY operation_time DESC''')

        # 插入数据（确保顺序与columns定义一致）
        for row in self.cursor.fetchall():
            tree.insert('', 'end', values=row)

        tree.pack(fill='both', expand=True)
        
        # 导出按钮
        tk.Button(log_window, text="导出日志", 
                command=self.export_logs).pack(pady=6)

    #15导出日志函数
    def export_logs(self):
        try:
            # 获取日志数据
            df = pd.read_sql_query('''SELECT 
                                    operation_type AS 操作类型,
                                    part_number AS 物料编号,
                                    quantity_change AS 数量变化,
                                    operator AS 人员操作,
                                    datetime(operation_time, 'localtime') AS 操作时间
                                    FROM operation_logs''', self.conn)
            
            # 生成文件名
            file_name = f"操作日志_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            save_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                initialfile=file_name,
                filetypes=[("Excel文件", "*.xlsx")]
            )
            
            if save_path:
                df.to_excel(save_path, index=False)
                messagebox.showinfo("成功", f"日志已导出到：{save_path}")
                
        except Exception as e:
            messagebox.showerror("错误", f"导出失败：{str(e)}")  

    #16、数据清洗函数,保留2位小数
    #16、数据清洗
    def clean_price(self,price_input):
        try:
            #数据清洗：①去除货币符号、②去除千分位逗号、③保留2位小数、④无效数据默认设为0.0
            #isinstance(object,classinfo)是一个内置函数，用于判断一个对象是否是指定类型的实例
            #strip()是字符串对象的一个方法，用于移除字符串开头和结尾的指定字符（空格、制表、换行）
            #round()是一个内置函数，对数字进行四舍五入操作
            #max()是一个内置函数，用于返回可迭代对象中的最大元素，此处可以处理如果price中产生负数
            if isinstance(price_input,str):
                price_input = price_input.replace('￥','').replace('$','').replace(',','').replace('，','').strip()
            price = round(float(price_input),2)#四舍五入2位
            return max(0.00,price)#确保非负数
        except (ValueError,TypeError):
            return 0.00

    #17新增库房名称管理功能（去重后的库房名称列表、刷新库房下拉列表）
    def get_warehouse_list(self):
        """获取去重后的库房名称列表"""
        self.cursor.execute("SELECT DISTINCT warehouse FROM parts")
        return [row[0] for row in self.cursor.fetchall()]

    def refresh_warehouse_list(self, combobox):
        """刷新库房下拉列表"""
        warehouses = self.get_warehouse_list()
        combobox['values'] = warehouses

    def _get_dingtalk_sign(self):
        """生成钉钉签名（如果启用了加签）"""
        timestamp = str(round(time.time() * 1000))
        secret_enc = self.dingtalk_secret.encode('utf-8')
        string_to_sign = f'{timestamp}\n{self.dingtalk_secret}'
        string_to_sign_enc = string_to_sign.encode('utf-8')
        hmac_code = hmac.new(secret_enc, string_to_sign_enc, digestmod=hashlib.sha256).digest()
        sign = urllib.parse.quote_plus(base64.b64encode(hmac_code))
        return timestamp, sign

    def send_dingtalk_msg(self, content):
        """发送消息到钉钉"""
        try:
            # 获取操作人姓名
            operator_name = self.current_user['name'] if self.current_user else '系统自动操作'

            # 构造完整消息
            full_content = f"**操作人：{operator_name}**\n{content}"

            # 后续钉钉消息发送逻辑保持不变
            headers = {"Content-Type": "application/json"}
            data = {
                "msgtype": "markdown",
                "markdown": {
                    "title": "库存变更通知",
                    "text": full_content  # 使用包含操作人的消息
                }
            }
            
            # 处理加签
            if self.dingtalk_secret:
                timestamp, sign = self._get_dingtalk_sign()
                url = f"{self.dingtalk_webhook}&timestamp={timestamp}&sign={sign}"
            else:
                url = self.dingtalk_webhook
                
            response = requests.post(
                url,
                data=json.dumps(data),
                headers=headers
            )
            
            if response.status_code != 200:
                print("钉钉消息发送失败:", response.text)
        except Exception as e:
            print("钉钉消息发送异常:", str(e))

if __name__ == "__main__":
    root = tk.Tk()
    app = SparePartsManager(root)
    #mainloop是tkinter中Tk类，也就是主窗口对象，mainloop方法会持续监听用户点击按钮、输入文本、移动窗口
    #使GUI程序进入事件循环
    root.mainloop()