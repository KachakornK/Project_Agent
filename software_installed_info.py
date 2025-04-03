import winreg
from datetime import datetime

def get_reg_date(value):
    """Try to convert registry date strings to readable format"""
    try:
        # Try common date formats: YYYYMMDD, DDMMYYYY, Unix timestamp
        if len(value) == 8 and value.isdigit():
            return datetime.strptime(value, "%Y%m%d").strftime("%Y-%m-%d")
        elif len(value) == 8 and value[:2].isdigit():
            return datetime.strptime(value, "%d%m%Y").strftime("%Y-%m-%d")
        elif value.isdigit():
            return datetime.fromtimestamp(int(value)).strftime("%Y-%m-%d")
    except:
        pass
    return value

def get_reg_value(subkey, value_names):
    """Get first available registry value from list of possible names"""
    for name in value_names:
        try:
            value = winreg.QueryValueEx(subkey, name)[0]
            if value:
                return get_reg_date(str(value)) if any(kw in name.lower() for kw in ['date','expiry','time']) else value
        except OSError:
            continue
    return 'N/A'

def get_installed_programs():
    programs = []
    reg_paths = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]

    # Common registry value names for different vendors
    LICENSE_KEYS = ['LicenseExpiry', 'ExpiryDate', 'EndDate', 'SubscriptionEnd', 'LicenseExpirationDate']
    PATCH_KEYS = ['LastPatchDate', 'LastUpdate', 'UpdateDate', 'InstallDate', 'ModifiedDate']

    for hive, path in reg_paths:
        try:
            with winreg.OpenKey(hive, path) as key:
                for i in range(winreg.QueryInfoKey(key)[0]):
                    subkey_name = winreg.EnumKey(key, i)
                    with winreg.OpenKey(key, subkey_name) as subkey:
                        try:
                            name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            if name:
                                programs.append({
                                    'name': name,
                                    'version': get_reg_value(subkey, ['DisplayVersion']),
                                    'publisher': get_reg_value(subkey, ['Publisher']),
                                    'install_date': get_reg_value(subkey, ['InstallDate']),
                                    'license_expiry': get_reg_value(subkey, LICENSE_KEYS),
                                    'last_patch_update': get_reg_value(subkey, PATCH_KEYS)
                                })
                        except OSError:
                            continue
        except FileNotFoundError:
            continue

    return programs

if __name__ == "__main__":
    programs = get_installed_programs()
    for idx, p in enumerate(programs, 1):
        print(f"{idx}. {p['name']}")
        print(f"   Version: {p['version']}")
        print(f"   Publisher: {p['publisher']}")
        print(f"   Installed: {p['install_date']}")
        print(f"   License Expiry: {p['license_expiry']}")
        print(f"   Last Patch: {p['last_patch_update']}\n")