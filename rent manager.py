import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os
from datetime import datetime, timedelta

# 数据文件路径
DATA_FILE = "data.json"

class RentManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("租赁管理系统")
        self.root.geometry("1200x800")
        
        # 加载数据
        self.data = self.load_data()
        
        # 创建标签页
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # 创建各个标签页
        self.create_items_tab()
        self.create_rentals_tab()
        self.create_report_tab()
        self.create_customers_tab()
        
        # 刷新数据
        self.refresh_all()
    
    def load_data(self):
        """加载数据"""
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {"items": {}, "rentals": []}
        return {"items": {}, "rentals": []}
    
    def save_data(self):
        """保存数据"""
        try:
            with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("错误", f"保存数据失败: {e}")
    
    def get_rented_quantity(self, item_name):
        """获取已租出的数量"""
        rented = 0
        for rental in self.data["rentals"]:
            if rental["item"] == item_name and rental["status"] == "未返还":
                rented += rental["quantity"]
        return rented
    
    def create_items_tab(self):
        """创建物品管理标签页"""
        self.items_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.items_frame, text="物品管理")
        
        # 输入区域
        input_frame = ttk.LabelFrame(self.items_frame, text="物品信息", padding=10)
        input_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(input_frame, text="物品名称:").grid(row=0, column=0, sticky='w')
        self.item_name_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.item_name_var, width=30).grid(row=0, column=1, padx=5)
        
        ttk.Label(input_frame, text="总数量:").grid(row=0, column=2, sticky='w')
        self.item_total_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.item_total_var, width=15).grid(row=0, column=3, padx=5)
        
        ttk.Label(input_frame, text="单价日租金:").grid(row=0, column=4, sticky='w')
        self.item_price_var = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.item_price_var, width=15).grid(row=0, column=5, padx=5)
        
        # 按钮区域
        btn_frame = ttk.Frame(input_frame)
        btn_frame.grid(row=1, column=0, columnspan=6, pady=10)
        
        ttk.Button(btn_frame, text="添加", command=self.add_item).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="更新", command=self.update_item).pack(side='left', padx=5)
        ttk.Button(btn_frame, text="删除", command=self.delete_item).pack(side='left', padx=5)
        
        # 表格区域
        table_frame = ttk.Frame(self.items_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('name', 'total', 'available', 'price')
        self.items_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        self.items_tree.heading('name', text='物品名称')
        self.items_tree.heading('total', text='总数量')
        self.items_tree.heading('available', text='在库数量')
        self.items_tree.heading('price', text='单价日租金')
        
        self.items_tree.column('name', width=200)
        self.items_tree.column('total', width=100)
        self.items_tree.column('available', width=100)
        self.items_tree.column('price', width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.items_tree.yview)
        self.items_tree.configure(yscrollcommand=scrollbar.set)
        
        self.items_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 绑定选择事件
        self.items_tree.bind('<<TreeviewSelect>>', self.on_item_select)
    
    def create_rentals_tab(self):
        """创建租赁管理标签页"""
        self.rentals_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.rentals_frame, text="租赁管理")
        
        # 租出区域
        rent_frame = ttk.LabelFrame(self.rentals_frame, text="租出物品", padding=10)
        rent_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(rent_frame, text="客户名称:").grid(row=0, column=0, sticky='w')
        self.rental_customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(rent_frame, textvariable=self.rental_customer_var, width=25)
        self.customer_combo.grid(row=0, column=1, padx=5)
        self.customer_combo.bind('<KeyRelease>', self.on_customer_input)
        
        ttk.Label(rent_frame, text="选择物品:").grid(row=0, column=2, sticky='w')
        self.rental_item_var = tk.StringVar()
        self.item_combo = ttk.Combobox(rent_frame, textvariable=self.rental_item_var, width=25)
        self.item_combo.grid(row=0, column=3, padx=5)
        
        ttk.Label(rent_frame, text="数量:").grid(row=0, column=4, sticky='w')
        self.rental_quantity_var = tk.StringVar()
        ttk.Entry(rent_frame, textvariable=self.rental_quantity_var, width=15).grid(row=0, column=5, padx=5)
        
        ttk.Label(rent_frame, text="日期:").grid(row=0, column=6, sticky='w')
        self.rental_date_var = tk.StringVar(value=datetime.now().strftime("%Y-%m-%d"))
        ttk.Entry(rent_frame, textvariable=self.rental_date_var, width=15).grid(row=0, column=7, padx=5)
        
        ttk.Button(rent_frame, text="租出", command=self.rent_out).grid(row=1, column=0, columnspan=8, pady=10)
        
        # 返还区域
        return_frame = ttk.LabelFrame(self.rentals_frame, text="返还物品", padding=10)
        return_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Label(return_frame, text="返还数量:").grid(row=0, column=0, sticky='w')
        self.return_quantity_var = tk.StringVar()
        self.return_entry = ttk.Entry(return_frame, textvariable=self.return_quantity_var, width=15, state='disabled')
        self.return_entry.grid(row=0, column=1, padx=5)
        
        ttk.Button(return_frame, text="返还", command=self.return_item).grid(row=0, column=2, padx=20)
        ttk.Button(return_frame, text="取消选择", command=self.clear_rental_selection).grid(row=0, column=3)
        ttk.Button(return_frame, text="删除记录", command=self.delete_rental).grid(row=0, column=4, padx=20)
        
        # 租赁记录表格
        table_frame = ttk.Frame(self.rentals_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('customer', 'item', 'quantity', 'rent_date', 'return_date', 'status')
        self.rentals_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        self.rentals_tree.heading('customer', text='客户名称')
        self.rentals_tree.heading('item', text='物品名称')
        self.rentals_tree.heading('quantity', text='数量')
        self.rentals_tree.heading('rent_date', text='租出日期')
        self.rentals_tree.heading('return_date', text='返还日期')
        self.rentals_tree.heading('status', text='状态')
        
        self.rentals_tree.column('customer', width=120)
        self.rentals_tree.column('item', width=150)
        self.rentals_tree.column('quantity', width=80)
        self.rentals_tree.column('rent_date', width=100)
        self.rentals_tree.column('return_date', width=100)
        self.rentals_tree.column('status', width=80)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.rentals_tree.yview)
        self.rentals_tree.configure(yscrollcommand=scrollbar.set)
        
        self.rentals_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 绑定选择事件
        self.rentals_tree.bind('<<TreeviewSelect>>', self.on_rental_select)
    
    def create_report_tab(self):
        """创建租金报表标签页"""
        self.report_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.report_frame, text="租金报表")
        
        # 选择客户
        select_frame = ttk.Frame(self.report_frame)
        select_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Label(select_frame, text="选择客户:").pack(side='left', padx=5)
        self.report_customer_var = tk.StringVar()
        self.report_customer_combo = ttk.Combobox(select_frame, textvariable=self.report_customer_var, width=30)
        self.report_customer_combo.pack(side='left', padx=5)
        ttk.Button(select_frame, text="生成报表", command=self.generate_report).pack(side='left', padx=20)
        
        # 报表表格
        table_frame = ttk.Frame(self.report_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        columns = ('item', 'quantity', 'rent_date', 'return_date', 'days', 'price', 'total')
        self.report_tree = ttk.Treeview(table_frame, columns=columns, show='headings')
        
        self.report_tree.heading('item', text='物品名称')
        self.report_tree.heading('quantity', text='数量')
        self.report_tree.heading('rent_date', text='租出日期')
        self.report_tree.heading('return_date', text='返还日期')
        self.report_tree.heading('days', text='租赁天数')
        self.report_tree.heading('price', text='单价日租金')
        self.report_tree.heading('total', text='租金总计')
        
        self.report_tree.column('item', width=150)
        self.report_tree.column('quantity', width=80)
        self.report_tree.column('rent_date', width=100)
        self.report_tree.column('return_date', width=100)
        self.report_tree.column('days', width=80)
        self.report_tree.column('price', width=100)
        self.report_tree.column('total', width=100)
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.report_tree.yview)
        self.report_tree.configure(yscrollcommand=scrollbar.set)
        
        self.report_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # 总租金
        self.total_label = ttk.Label(self.report_frame, text="总租金: 0.00 元", font=('Arial', 14, 'bold'))
        self.total_label.pack(pady=10)
    
    def create_customers_tab(self):
        """创建客户管理标签页"""
        self.customers_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.customers_frame, text="客户管理")
        
        # 按钮区域
        btn_frame = ttk.Frame(self.customers_frame)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        ttk.Button(btn_frame, text="删除客户", command=self.delete_customer).pack(side='left', padx=5)
        
        # 客户表格
        table_frame = ttk.Frame(self.customers_frame)
        table_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.customers_tree = ttk.Treeview(table_frame, show='headings')
        
        scrollbar = ttk.Scrollbar(table_frame, orient='vertical', command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        
        self.customers_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def refresh_all(self):
        """刷新所有数据"""
        self.refresh_items()
        self.refresh_rentals()
        self.refresh_customer_lists()
        self.refresh_customers_tab()
    
    def refresh_items(self):
        """刷新物品列表"""
        for item in self.items_tree.get_children():
            self.items_tree.delete(item)
        
        for name, info in self.data["items"].items():
            self.items_tree.insert('', 'end', values=(name, info['total'], info['available'], info['price']))
        
        # 更新物品下拉框
        self.item_combo['values'] = list(self.data["items"].keys())
    
    def refresh_rentals(self):
        """刷新租赁记录"""
        for item in self.rentals_tree.get_children():
            self.rentals_tree.delete(item)
        
        for rental in self.data["rentals"]:
            self.rentals_tree.insert('', 'end', values=(
                rental['customer'],
                rental['item'],
                rental['quantity'],
                rental['rent_date'],
                rental.get('return_date', ''),
                rental['status']
            ))
    
    def refresh_customer_lists(self):
        """刷新客户列表"""
        customers = set()
        for rental in self.data["rentals"]:
            customers.add(rental['customer'])
        
        customer_list = sorted(list(customers))
        self.customer_combo['values'] = customer_list + ['其他']
        self.report_customer_combo['values'] = customer_list
    
    def refresh_customers_tab(self):
        """刷新客户管理标签页"""
        # 清空表格
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)
        
        # 获取所有客户和物品
        customers = set()
        for rental in self.data["rentals"]:
            if rental['status'] == '未返还':
                customers.add(rental['customer'])
        
        item_names = sorted(list(self.data["items"].keys()))
        
        # 设置表头
        self.customers_tree['columns'] = ['customer'] + item_names
        self.customers_tree.heading('customer', text='客户名称')
        self.customers_tree.column('customer', width=120)
        
        for item in item_names:
            self.customers_tree.heading(item, text=item)
            self.customers_tree.column(item, width=100)
        
        # 填充数据
        for customer in sorted(customers):
            values = [customer]
            for item in item_names:
                quantity = 0
                for rental in self.data["rentals"]:
                    if (rental['customer'] == customer and 
                        rental['item'] == item and 
                        rental['status'] == '未返还'):
                        quantity += rental['quantity']
                values.append(quantity)
            self.customers_tree.insert('', 'end', values=values)
    
    def on_item_select(self, event):
        """物品选择事件"""
        selection = self.items_tree.selection()
        if selection:
            item = self.items_tree.item(selection[0])
            values = item['values']
            self.item_name_var.set(values[0])
            self.item_total_var.set(values[1])
            self.item_price_var.set(values[3])
    
    def on_rental_select(self, event):
        """租赁记录选择事件"""
        selection = self.rentals_tree.selection()
        if selection:
            item = self.rentals_tree.item(selection[0])
            values = item['values']
            if values[5] == '未返还':
                self.return_entry.config(state='normal')
                self.selected_rental_index = self.rentals_tree.index(selection[0])
            else:
                self.return_entry.config(state='disabled')
    
    def on_customer_input(self, event):
        """客户输入事件"""
        current = self.customer_combo.get()
        if current != '其他':
            self.return_entry.config(state='disabled')
        else:
            self.return_entry.config(state='normal')
    
    def clear_rental_selection(self):
        """清除租赁选择"""
        self.rentals_tree.selection_remove(self.rentals_tree.selection())
        self.return_entry.config(state='disabled')
        self.return_quantity_var.set('')
    
    def add_item(self):
        """添加物品"""
        name = self.item_name_var.get().strip()
        total = self.item_total_var.get().strip()
        price = self.item_price_var.get().strip()
        
        if not all([name, total, price]):
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        try:
            total = int(total)
            price = float(price)
        except ValueError:
            messagebox.showerror("错误", "数量和价格必须是数字")
            return
        
        if name in self.data["items"]:
            messagebox.showerror("错误", "物品已存在")
            return
        
        self.data["items"][name] = {
            "total": total,
            "available": total,
            "price": price
        }
        
        self.save_data()
        self.refresh_items()
        self.clear_item_form()
        messagebox.showinfo("成功", "物品添加成功")
    
    def update_item(self):
        """更新物品"""
        name = self.item_name_var.get().strip()
        if not name:
            messagebox.showerror("错误", "请先选择要更新的物品")
            return
        
        if name not in self.data["items"]:
            messagebox.showerror("错误", "物品不存在")
            return
        
        total = self.item_total_var.get().strip()
        price = self.item_price_var.get().strip()
        
        try:
            total = int(total)
            price = float(price)
        except ValueError:
            messagebox.showerror("错误", "数量和价格必须是数字")
            return
        
        old_total = self.data["items"][name]["total"]
        rented = old_total - self.data["items"][name]["available"]
        
        if total < rented:
            messagebox.showerror("错误", "总数量不能小于已租出数量")
            return
        
        self.data["items"][name]["total"] = total
        self.data["items"][name]["available"] = total - rented
        self.data["items"][name]["price"] = price
        
        self.save_data()
        self.refresh_items()
        self.clear_item_form()
        messagebox.showinfo("成功", "物品更新成功")
    
    def delete_item(self):
        """删除物品"""
        name = self.item_name_var.get().strip()
        if not name:
            messagebox.showerror("错误", "请先选择要删除的物品")
            return
        
        if name not in self.data["items"]:
            messagebox.showerror("错误", "物品不存在")
            return
        
        # 检查是否有未返还的租赁
        for rental in self.data["rentals"]:
            if rental["item"] == name and rental["status"] == "未返还":
                messagebox.showerror("错误", "该物品还有未返还的租赁，无法删除")
                return
        
        if messagebox.askyesno("确认", "确定要删除该物品吗？"):
            del self.data["items"][name]
            self.save_data()
            self.refresh_items()
            self.clear_item_form()
            messagebox.showinfo("成功", "物品删除成功")
    
    def clear_item_form(self):
        """清空物品表单"""
        self.item_name_var.set('')
        self.item_total_var.set('')
        self.item_price_var.set('')
    
    def rent_out(self):
        """租出物品"""
        customer = self.rental_customer_var.get().strip()
        item = self.rental_item_var.get().strip()
        quantity = self.rental_quantity_var.get().strip()
        rent_date = self.rental_date_var.get().strip()
        
        if not all([customer, item, quantity, rent_date]):
            messagebox.showerror("错误", "请填写所有字段")
            return
        
        try:
            quantity = int(quantity)
            datetime.strptime(rent_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("错误", "数量必须是数字，日期格式必须是YYYY-MM-DD")
            return
        
        if item not in self.data["items"]:
            messagebox.showerror("错误", "物品不存在")
            return
        
        if quantity <= 0:
            messagebox.showerror("错误", "数量必须大于0")
            return
        
        if quantity > self.data["items"][item]["available"]:
            messagebox.showerror("错误", "库存不足")
            return
        
        rental = {
            "customer": customer,
            "item": item,
            "quantity": quantity,
            "rent_date": rent_date,
            "return_date": None,
            "status": "未返还"
        }
        
        self.data["rentals"].append(rental)
        self.data["items"][item]["available"] -= quantity
        
        self.save_data()
        self.refresh_all()
        self.clear_rental_form()
        messagebox.showinfo("成功", "物品租出成功")
    
    def return_item(self):
        """返还物品"""
        if not hasattr(self, 'selected_rental_index'):
            messagebox.showerror("错误", "请先选择要返还的租赁记录")
            return
        
        return_quantity = self.return_quantity_var.get().strip()
        return_date = self.rental_date_var.get().strip()
        
        if not return_quantity:
            messagebox.showerror("错误", "请输入返还数量")
            return
        
        try:
            return_quantity = int(return_quantity)
            datetime.strptime(return_date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("错误", "数量必须是数字，日期格式必须是YYYY-MM-DD")
            return
        
        rental = self.data["rentals"][self.selected_rental_index]
        
        if return_quantity > rental["quantity"]:
            messagebox.showerror("错误", "返还数量不能超过租出数量")
            return
        
        if return_quantity < rental["quantity"]:
            # 部分返还
            rental["quantity"] -= return_quantity
            returned_rental = {
                "customer": rental["customer"],
                "item": rental["item"],
                "quantity": return_quantity,
                "rent_date": rental["rent_date"],
                "return_date": return_date,
                "status": "已返还"
            }
            self.data["rentals"].append(returned_rental)
        else:
            # 全部返还
            rental["return_date"] = return_date
            rental["status"] = "已返还"
        
        self.data["items"][rental["item"]]["available"] += return_quantity
        
        self.save_data()
        self.refresh_all()
        self.clear_rental_form()
        messagebox.showinfo("成功", "物品返还成功")
    
    def clear_rental_form(self):
        """清空租赁表单"""
        self.rental_customer_var.set('')
        self.rental_item_var.set('')
        self.rental_quantity_var.set('')
        self.return_quantity_var.set('')
        self.return_entry.config(state='disabled')
        if hasattr(self, 'selected_rental_index'):
            delattr(self, 'selected_rental_index')
    
    def delete_rental(self):
        """删除租赁记录"""
        if not hasattr(self, 'selected_rental_index'):
            messagebox.showerror("错误", "请先选择要删除的租赁记录")
            return
        
        rental = self.data["rentals"][self.selected_rental_index]
        
        # 确认删除
        if messagebox.askyesno("确认", f"确定要删除该租赁记录吗？\n客户: {rental['customer']}\n物品: {rental['item']}\n数量: {rental['quantity']}"):
            # 恢复库存（仅当未返还时）
            if rental["status"] == "未返还":
                if rental["item"] in self.data["items"]:
                    self.data["items"][rental["item"]]["available"] += rental["quantity"]
            
            # 删除记录
            del self.data["rentals"][self.selected_rental_index]
            
            self.save_data()
            self.refresh_all()
            self.clear_rental_form()
            messagebox.showinfo("成功", "租赁记录删除成功")
    
    def delete_customer(self):
        """删除客户"""
        selection = self.customers_tree.selection()
        if not selection:
            messagebox.showerror("错误", "请先选择要删除的客户")
            return
        
        item = self.customers_tree.item(selection[0])
        customer = item['values'][0]
        
        # 检查客户是否有未返还的租赁记录
        has_unreturned = False
        for rental in self.data["rentals"]:
            if rental["customer"] == customer and rental["status"] == "未返还":
                has_unreturned = True
                break
        
        # 确认删除
        if has_unreturned:
            if not messagebox.askyesno("确认", f"该客户有未返还的租赁记录，确定要删除吗？\n删除后将恢复相关物品的库存。"):
                return
        else:
            if not messagebox.askyesno("确认", f"确定要删除客户 {customer} 及其所有租赁记录吗？"):
                return
        
        # 恢复库存并删除租赁记录
        rentals_to_delete = []
        for i, rental in enumerate(self.data["rentals"]):
            if rental["customer"] == customer:
                # 恢复库存（仅当未返还时）
                if rental["status"] == "未返还" and rental["item"] in self.data["items"]:
                    self.data["items"][rental["item"]]["available"] += rental["quantity"]
                rentals_to_delete.append(i)
        
        # 从后向前删除，避免索引变化
        for i in reversed(rentals_to_delete):
            del self.data["rentals"][i]
        
        self.save_data()
        self.refresh_all()
        messagebox.showinfo("成功", f"客户 {customer} 及其所有租赁记录已删除")
    
    def generate_report(self):
        """生成报表"""
        customer = self.report_customer_var.get().strip()
        
        if not customer:
            messagebox.showerror("错误", "请选择客户")
            return
        
        # 清空表格
        for item in self.report_tree.get_children():
            self.report_tree.delete(item)
        
        total_rent = 0
        
        for rental in self.data["rentals"]:
            if rental["customer"] == customer:
                rent_date = datetime.strptime(rental["rent_date"], "%Y-%m-%d")
                
                if rental["status"] == "已返还" and rental.get("return_date"):
                    return_date = datetime.strptime(rental["return_date"], "%Y-%m-%d")
                    days = (return_date - rent_date).days
                else:
                    days = (datetime.now() - rent_date).days
                
                if days < 0:
                    days = 0
                
                price = self.data["items"].get(rental["item"], {}).get("price", 0)
                total = days * price * rental["quantity"]
                total_rent += total
                
                self.report_tree.insert('', 'end', values=(
                    rental["item"],
                    rental["quantity"],
                    rental["rent_date"],
                    rental.get("return_date", ""),
                    days,
                    price,
                    f"{total:.2f}"
                ))
        
        self.total_label.config(text=f"总租金: {total_rent:.2f} 元")

if __name__ == "__main__":
    root = tk.Tk()
    app = RentManagerApp(root)
    root.mainloop()
