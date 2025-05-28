import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from webhook import WebhookManager
from datetime import datetime
import json
import os

class SystemInfoGUI:
    def __init__(self, system_info):
        self.system_info = system_info
        self.webhook_manager = WebhookManager()
        self.root = tk.Tk()
        self.root.title("ระบบตรวจสอบข้อมูลคอมพิวเตอร์")
        self.root.geometry("1000x750")  # ขยายขนาดหน้าต่างเล็กน้อย
        self._setup_ui()
    
    def _setup_ui(self):
        # สร้าง Notebook (แท็บ)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # สร้างแท็บต่างๆ
        self._create_system_tab()
        self._create_location_tab()
        self._create_software_tab()
        self._create_output_tab()  # เพิ่มแท็บสำหรับแสดง output.txt
        self._create_webhook_tab() 
        self._create_buttons()
        self._configure_styles()

    def _create_webhook_tab(self):
        """สร้างแท็บสำหรับเลือก Webhook URL"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="ตั้งค่า Webhook")
        
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Frame สำหรับเลือก URL
        url_frame = ttk.LabelFrame(main_frame, text="เลือก Webhook URL")
        url_frame.pack(fill='x', padx=10, pady=10)
        
        # Combobox สำหรับเลือก URL
        ttk.Label(url_frame, text="URL ที่มีอยู่:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        
        self.url_combobox = ttk.Combobox(
            url_frame,
            values=list(self.webhook_manager.get_webhook_urls().keys()),
            state="readonly",
            font=('Tahoma', 10)
        )
        self.url_combobox.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        self.url_combobox.current(0)  # เลือกค่าแรกเป็นค่าเริ่มต้น
        
        # ปุ่มเพิ่ม URL ใหม่
        add_btn = ttk.Button(
            url_frame,
            text="+ เพิ่ม URL ใหม่",
            command=self._add_new_url,
            style='White.TButton'  # เปลี่ยนจาก 'Accent.TButton' เป็น 'White.TButton'
        )
        add_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Frame สำหรับแสดง URL ที่เลือก
        selected_frame = ttk.LabelFrame(main_frame, text="URL ที่เลือกในปัจจุบัน")
        selected_frame.pack(fill='x', padx=10, pady=10)
        
        self.selected_url_label = ttk.Label(
            selected_frame,
            text=self.webhook_manager.get_webhook_urls()["Default"],
            wraplength=800,
            foreground="#0066CC",
            font=('Tahoma', 10)
        )
        self.selected_url_label.pack(fill='x', padx=10, pady=10)
        
        # ข้อความแนะนำ
        note_frame = ttk.Frame(main_frame)
        note_frame.pack(fill='x', padx=10, pady=10)
        
        note_label = ttk.Label(
            note_frame,
            text="หมายเหตุ: ระบบจะส่งข้อมูลไปยัง URL ที่เลือกเมื่อกดปุ่ม 'บันทึกข้อมูล'",
            foreground="#666666",
            font=('Tahoma', 9)
        )
        note_label.pack()
        
        # อัปเดต URL ที่เลือกเมื่อมีการเปลี่ยนแปลง
        self.url_combobox.bind("<<ComboboxSelected>>", self._update_selected_url)
        self._update_selected_url()

    def _update_selected_url(self, event=None):
        """อัปเดต URL ที่เลือก"""
        selected_key = self.url_combobox.get()
        urls = self.webhook_manager.get_webhook_urls()
        if selected_key in urls:
            url = urls[selected_key]
            self.webhook_manager.set_webhook_url(url)
            self.selected_url_label.config(text=url)

    def _add_new_url(self):
        """เพิ่ม URL ใหม่"""
        dialog = tk.Toplevel(self.root)
        dialog.title("เพิ่ม Webhook URL ใหม่")
        dialog.geometry("500x200")
        dialog.resizable(False, False)
        
        # ทำให้ dialog อยู่กลางหน้าจอ
        self._center_window(dialog)
        
        main_frame = ttk.Frame(dialog)
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        ttk.Label(main_frame, text="ชื่อ URL:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        name_entry = ttk.Entry(main_frame, font=('Tahoma', 10))
        name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")
        
        ttk.Label(main_frame, text="URL:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        url_entry = ttk.Entry(main_frame, font=('Tahoma', 10))
        url_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")
        
        def save_new_url():
            name = name_entry.get().strip()
            url = url_entry.get().strip()
            
            if not name or not url:
                messagebox.showerror("ข้อผิดพลาด", "กรุณากรอกชื่อและ URL ให้ครบถ้วน")
                return
                
            if not url.startswith(('http://', 'https://')):
                messagebox.showerror("ข้อผิดพลาด", "URL ต้องเริ่มต้นด้วย http:// หรือ https://")
                return
                
            self.webhook_manager.get_webhook_urls()[name] = url
            self.url_combobox['values'] = list(self.webhook_manager.get_webhook_urls().keys())
            self.url_combobox.set(name)  # เลือก URL ใหม่ที่เพิ่งเพิ่ม
            dialog.destroy()
            self._update_selected_url()
        
        btn_frame = ttk.Frame(main_frame)
        btn_frame.grid(row=2, column=0, columnspan=2, pady=10)
        
        ttk.Button(
            btn_frame, 
            text="บันทึก", 
            command=save_new_url,
            style='White.TButton'
        ).pack(side="left", padx=10)
        
        ttk.Button(
            btn_frame, 
            text="ยกเลิก", 
            command=dialog.destroy
        ).pack(side="right", padx=10)
        
        main_frame.columnconfigure(1, weight=1)

    def _center_window(self, window):
        """จัดหน้าต่างให้อยู่กลางจอ"""
        window.update_idletasks()
        width = window.winfo_width()
        height = window.winfo_height()
        x = (window.winfo_screenwidth() // 2) - (width // 2)
        y = (window.winfo_screenheight() // 2) - (height // 2)
        window.geometry(f'{width}x{height}+{x}+{y}')
        
        # สร้างปุ่มควบคุม
        # self._create_buttons()
        
        # กำหนดสไตล์ทั่วไป
        self._configure_styles()
    
    def _configure_styles(self):
        
        style = ttk.Style()
        style.configure('TLabel', font=('Tahoma', 10))
        style.configure('Bold.TLabel', font=('Tahoma', 10, 'bold'))
        style.configure('TButton', font=('Tahoma', 10))
        style.configure('Accent.TButton', font=('Tahoma', 10, 'bold'), foreground='white', background='#4CAF50')
        
        # เพิ่ม style ใหม่สำหรับปุ่มสีขาวตัวหนังสือสีดำ
        style.configure('White.TButton', 
                    font=('Tahoma', 10),
                    foreground='black',  # ตัวหนังสือสีดำ
                    background='white',  # พื้นหลังสีขาว
                    borderwidth=1)
        style.map('White.TButton',
                foreground=[('pressed', 'black'), ('active', 'black')],
                background=[('pressed', '!disabled', '#E0E0E0'), ('active', '#F5F5F5')])
        
        style.configure('Treeview', font=('Tahoma', 9), rowheight=25)
        style.configure('Treeview.Heading', font=('Tahoma', 9, 'bold'))
    
    def _create_system_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="ข้อมูลระบบ")
        
        # Main frame สำหรับข้อมูลระบบ
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        # ส่วนข้อมูลระบบพื้นฐาน
        info_frame = ttk.LabelFrame(main_frame, text="ข้อมูลระบบคอมพิวเตอร์")
        info_frame.pack(fill='x', padx=5, pady=5)
        
        system_data = self.system_info.get_all_info()['pc_info']
        info_labels = [
            ("ชื่อเครื่อง:", system_data['host_name']),
            ("ระบบปฏิบัติการ:", system_data['os']),
            ("CPU:", system_data['cpu']),
            ("RAM (GB):", f"{system_data['ram']} GB"),
            ("Hard Disk (GB):", f"{system_data['hard_disk']} GB"),
            ("IP Address:", system_data['ip_address']),
            ("MAC Address:", system_data['mac_address']),
            ("วันที่เก็บข้อมูล:", system_data['created_at'])
        ]
        
        for i, (label, value) in enumerate(info_labels):
            ttk.Label(info_frame, text=label, style='Bold.TLabel').grid(row=i, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(info_frame, text=value).grid(row=i, column=1, sticky="w", padx=5, pady=2)
        
        # ส่วนข้อมูล Disk
        disk_frame = ttk.LabelFrame(main_frame, text="การใช้พื้นที่ดิสก์")
        disk_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        columns = ("ไดรฟ์", "ทั้งหมด (GB)", "ใช้ไป (GB)", "เหลือ (GB)", "การใช้ (%)")
        self.disk_tree = ttk.Treeview(disk_frame, columns=columns, show="headings", height=4)
        
        for col in columns:
            self.disk_tree.heading(col, text=col)
            self.disk_tree.column(col, width=120, anchor='center')
        
        scrollbar = ttk.Scrollbar(disk_frame, orient="vertical", command=self.disk_tree.yview)
        self.disk_tree.configure(yscrollcommand=scrollbar.set)
        
        self.disk_tree.pack(side="left", fill='both', expand=True)
        scrollbar.pack(side="right", fill='y')
        
        # เพิ่มข้อมูล Disk
        disks = self.system_info._get_disk_info()
        for drive, usage in disks.items():
            usage_percent = (usage['used'] / usage['total']) * 100
            self.disk_tree.insert("", "end", values=(
                drive,
                f"{usage['total']:.2f}",
                f"{usage['used']:.2f}",
                f"{usage['free']:.2f}",
                f"{usage_percent:.1f}%"
            ))
    
    def _create_location_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="ข้อมูลตำแหน่ง")
        
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        loc_frame = ttk.LabelFrame(main_frame, text="ข้อมูลตำแหน่งติดตั้ง")
        loc_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        fields = [
            ("สถานที่:", "location"),
            ("ตึก:", "building"),
            ("ชั้น:", "floor"),
            ("แผนก:", "department")
        ]
        
        self.entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(loc_frame, text=label, style='Bold.TLabel').grid(row=i, column=0, sticky="e", padx=10, pady=8)
            entry = ttk.Entry(loc_frame, font=('Tahoma', 10))
            entry.grid(row=i, column=1, sticky="ew", padx=10, pady=8)
            entry.insert(0, self.system_info.get_all_info()['location_info'].get(field, ""))
            self.entries[field] = entry
        
        loc_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(0, weight=1)
    
    def _create_software_tab(self):
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="โปรแกรมที่ติดตั้ง")
        
        main_frame = ttk.Frame(tab)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        prog_frame = ttk.LabelFrame(main_frame, text="รายการโปรแกรมที่ติดตั้ง")
        prog_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # กำหนดคอลัมน์และหัวข้อภาษาไทย
        columns = {
            "name": {"text": "ชื่อโปรแกรม", "width": 250},
            "version": {"text": "เวอร์ชัน", "width": 100},
            "publisher": {"text": "ผู้พัฒนา", "width": 200},
            "license_expiry": {"text": "วันหมดอายุ", "width": 100},
            "install_date": {"text": "วันที่ติดตั้ง", "width": 100},
            "last_patch_update": {"text": "อัปเดตล่าสุด", "width": 100}
        }
        
        self.tree = ttk.Treeview(
            prog_frame, 
            columns=list(columns.keys()), 
            show="headings", 
            height=20,
            selectmode='extended'
        )
        
        # กำหนดหัวข้อและความกว้างคอลัมน์
        for col, config in columns.items():
            self.tree.heading(col, text=config["text"])
            self.tree.column(col, width=config["width"], anchor='center')
        
        # สร้าง Scrollbar
        scrollbar_y = ttk.Scrollbar(prog_frame, orient="vertical", command=self.tree.yview)
        scrollbar_x = ttk.Scrollbar(prog_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)
        
        # จัด Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar_y.grid(row=0, column=1, sticky="ns")
        scrollbar_x.grid(row=1, column=0, sticky="ew")
        
        prog_frame.grid_rowconfigure(0, weight=1)
        prog_frame.grid_columnconfigure(0, weight=1)
        
        # เพิ่มข้อมูลโปรแกรม
        for prog in self.system_info.get_all_info()['installed_software']:
            self.tree.insert("", "end", values=(
                prog.get('name', ''),
                prog.get('version', ''),
                prog.get('publisher', ''),
                prog.get('license_expiry', ''),
                prog.get('install_date', ''),
                prog.get('last_patch_update', '')
            ))
    
    def _create_output_tab(self):
        """สร้างแท็บสำหรับแสดงเนื้อหาของไฟล์ output.txt"""
        tab = ttk.Frame(self.notebook)
        self.notebook.add(tab, text="ข้อมูล Output")
        
        # Frame สำหรับปุ่ม Copy All
        btn_frame = ttk.Frame(tab)
        btn_frame.pack(fill='x', padx=10, pady=5)
        
        # ปุ่มคัดลอกทั้งหมด
        copy_btn = ttk.Button(
        btn_frame, 
        text="📋 คัดลอกทั้งหมด", 
        command=self._copy_all_output
        )
        copy_btn.pack(side="left", padx=5, pady=5)

        # Text widget สำหรับแสดงเนื้อหา
        self.output_text = scrolledtext.ScrolledText(
            tab,
            wrap=tk.WORD,
            font=('Tahoma', 10),
            padx=10,
            pady=10
        )
        self.output_text.pack(fill='both', expand=True, padx=10, pady=5)
        
        # โหลดข้อมูลหากไฟล์มีอยู่แล้ว
        if os.path.exists('output.txt'):
            self._load_output_file()
    
    def _load_output_file(self):
        """โหลดเนื้อหาจากไฟล์ output.txt และแสดงใน Text widget"""
        try:
            with open('output.txt', 'r', encoding='utf-8') as f:
                content = f.read()
                self.output_text.delete(1.0, tk.END)
                self.output_text.insert(tk.END, content)
        except Exception as e:
            messagebox.showerror("ข้อผิดพลาด", f"ไม่สามารถอ่านไฟล์ output.txt: {str(e)}")
    
    def _copy_all_output(self):
        """คัดลอกเนื้อหาทั้งหมดใน Text widget ไปยังคลิปบอร์ด"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.output_text.get(1.0, tk.END))
        messagebox.showinfo("สำเร็จ", "คัดลอกเนื้อหาทั้งหมดไปยังคลิปบอร์ดแล้ว")
    
    def _create_buttons(self):
        btn_frame = ttk.Frame(self.root)
        btn_frame.pack(fill='x', padx=10, pady=10)

        ttk.Button(
            btn_frame, 
            text="บันทึกข้อมูล",
            command=self._save_data,
            style='TButton'
        ).pack(side="left", padx=10, ipadx=20,)
        
        ttk.Button(
            btn_frame, 
            text="ปิดโปรแกรม", 
            command=self.root.quit,
            style='TButton'
        ).pack(side="right", padx=10, ipadx=20)
    
    def _save_data(self):
        # บันทึกข้อมูลตำแหน่ง
        location_info = {field: entry.get() for field, entry in self.entries.items()}
        self.system_info.save_config(location_info)

        try:
            # บันทึกข้อมูลทั้งหมดเป็นไฟล์ JSON
            all_data = self.system_info.get_all_info()
            with open('output.txt', 'w', encoding='utf-8') as f:
                json.dump(all_data, f, ensure_ascii=False, indent=4)

            # โหลดข้อมูลใหม่ในแท็บ output
            self._load_output_file()

            # ส่งข้อมูลไปยัง Webhook โดยใช้ URL ที่เลือก
            webhook_success = self.webhook_manager.send_to_webhook(all_data)

            if webhook_success:
                messagebox.showinfo(
                    "สำเร็จ",
                    "บันทึกข้อมูลเรียบร้อย\n"
                    "ไฟล์ output.txt ถูกสร้างแล้ว\n"
                    "ส่งข้อมูลเรียบร้อย"
                )
            else:
                messagebox.showinfo(
                    "สำเร็จบางส่วน",
                    "บันทึกข้อมูลเรียบร้อย\n"
                    "ไฟล์ output.txt ถูกสร้างแล้ว\n"
                    "แต่ไม่สามารถส่งข้อมูลไปยัง Webhook ได้"
                )

        except Exception as e:
            messagebox.showerror(
                "ข้อผิดพลาด",
                f"เกิดข้อผิดพลาดขณะบันทึกข้อมูล:\n{str(e)}"
            )


    
    def run(self):
        self.root.mainloop()