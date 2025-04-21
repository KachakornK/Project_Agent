from gui import SystemInfoGUI
from system_info import SystemInfo
def main():
    system_info = SystemInfo()
    SystemInfoGUI(system_info).run()

if __name__ == "__main__":
    main()
    