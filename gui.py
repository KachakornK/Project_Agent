import tkinter as tk
from tkinter import ttk, messagebox
from discord_webhook import send_to_discord
from datetime import datetime
import json

class SystemInfoGUI:
    def __init__(self, system_info):
        self.system_info = system_info
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
        
        # สร้างปุ่มควบคุม
        self._create_buttons()
        
        # กำหนดสไตล์ทั่วไป
        self._configure_styles()
    
    def _configure_styles(self):
        style = ttk.Style()
        style.configure('TLabel', font=('Tahoma', 10))
        style.configure('Bold.TLabel', font=('Tahoma', 10, 'bold'))
        style.configure('TButton', font=('Tahoma', 10))
        style.configure('Accent.TButton', font=('Tahoma', 10, 'bold'), foreground='white', background='#4CAF50')
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
            
            # ส่งข้อมูลไปยัง Discord (ถ้ามี)
            discord_success = True
            if hasattr(self, 'send_to_discord'):
                discord_success = send_to_discord(all_data)
            
            if discord_success:
                messagebox.showinfo(
                    "สำเร็จ", 
                    "บันทึกข้อมูลเรียบร้อย\n" +
                    "ไฟล์ output.txt ถูกสร้างแล้ว\n" +
                    "ส่งข้อมูลไปยัง Discord เรียบร้อย"
                )
            else:
                messagebox.showinfo(
                    "สำเร็จบางส่วน", 
                    "บันทึกข้อมูลเรียบร้อย\n" +
                    "ไฟล์ output.txt ถูกสร้างแล้ว\n" +
                    "แต่ไม่สามารถส่งข้อมูลไปยัง Discord ได้"
                )
                
        except Exception as e:
            messagebox.showerror(
                "ข้อผิดพลาด", 
                f"เกิดข้อผิดพลาดขณะบันทึกข้อมูล:\n{str(e)}"
            )
    
    def run(self):
        self.root.mainloop()