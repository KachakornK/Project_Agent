import winreg
from datetime import datetime

def get_reg_date(value):
    """แปลงค่าวันที่จากรูปแบบต่างๆ เป็นรูปแบบมาตรฐาน YYYY-MM-DD"""
    if not value:
        return ''
    
    value = str(value).strip()
    
    # ลองรูปแบบวันที่ต่างๆ
    date_formats = [
        "%Y%m%d",    # 20231231
        "%d%m%Y",    # 31122023
        "%m/%d/%Y",  # 12/31/2023
        "%Y-%m-%d",  # 2023-12-31
        "%d-%m-%Y",  # 31-12-2023
        "%Y%m%d%H%M%S",  # 20231231120000 (timestamp แบบบางโปรแกรม)
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(value, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    
    # ลองแปลงจาก timestamp ถ้าเป็นตัวเลข
    if value.isdigit():
        try:
            return datetime.fromtimestamp(int(value)).strftime("%Y-%m-%d")
        except:
            pass
    
    return value  # คืนค่าต้นฉบับถ้าแปลงไม่ได้

def get_reg_value(subkey, value_names):
    """ดึงค่าจาก registry และแปลงรูปแบบถ้าเป็นวันที่"""
    for name in value_names:
        try:
            value = winreg.QueryValueEx(subkey, name)[0]
            if value:
                # ตรวจสอบว่าเป็นฟิลด์วันที่หรือไม่
                if any(kw in name.lower() for kw in ['date', 'expiry', 'time', 'patch', 'update']):
                    return get_reg_date(str(value))
                return str(value)
        except (OSError, ValueError):
            continue
    return ''

def get_installed_software():
    """ดึงข้อมูลโปรแกรมที่ติดตั้งตามโครงสร้างฐานข้อมูล"""
    software_list = []
    
    # รายการ registry paths ที่อาจมีข้อมูลการติดตั้งโปรแกรม
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    
    # คีย์ที่เป็นไปได้สำหรับแต่ละฟิลด์
    field_mapping = {
        'name': ['DisplayName'],
        'version': ['DisplayVersion', 'Version'],
        'publisher': ['Publisher', 'CompanyName'],
        'install_date': ['InstallDate', 'InstallTime', 'DateInstalled'],
        'license_expiry': ['LicenseExpiry', 'ExpiryDate', 'EndDate', 'SubscriptionEnd', 'LicenseEndDate'],
        'last_patch_update': ['LastPatchDate', 'LastUpdate', 'UpdateDate', 'PatchDate', 'LastMaintenanceDate']
    }

    for hive, path in reg_paths:
        try:
            with winreg.OpenKey(hive, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, subkey_name) as subkey:
                            # ดึง DisplayName ก่อนเพื่อตรวจสอบว่าเป็นโปรแกรมจริงหรือไม่
                            name = get_reg_value(subkey, field_mapping['name'])
                            if not name:
                                continue
                            
                            # สร้าง dictionary ข้อมูลโปรแกรม
                            program_info = {
                                'name': name,
                                'version': get_reg_value(subkey, field_mapping['version']),
                                'publisher': get_reg_value(subkey, field_mapping['publisher']),
                                'install_date': get_reg_value(subkey, field_mapping['install_date']),
                                'license_expiry': get_reg_value(subkey, field_mapping['license_expiry']),
                                'last_patch_update': get_reg_value(subkey, field_mapping['last_patch_update'])
                            }
                            
                            software_list.append(program_info)
                    except (OSError, ValueError):
                        continue
        except (FileNotFoundError, OSError):
            continue
    
    return software_list