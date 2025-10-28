import os
import sys
import django
from django.db import connection

# 讓腳本找到你的 Django 專案
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "searchweb.settings")
django.setup()

from myapp.models import GitBookPage

# ---- 1) 先刪光這個 Model 的資料 ----
GitBookPage.objects.all().delete()

# ---- 2) 依資料庫種類重置自動遞增序號 ----
engine = connection.settings_dict.get("ENGINE", "")
table_name = GitBookPage._meta.db_table  # 例：'myapp_gitbookpage'

with connection.cursor() as cursor:
    if "sqlite" in engine:
        # SQLite（Django 預設在開發常見）
        cursor.execute("DELETE FROM sqlite_sequence WHERE name=%s", [table_name])
    elif "postgresql" in engine:
        # PostgreSQL
        seq_name = f"{table_name}_id_seq"
        cursor.execute(f"ALTER SEQUENCE {seq_name} RESTART WITH 1;")
    elif "mysql" in engine:
        # MySQL / MariaDB
        cursor.execute(f"ALTER TABLE {table_name} AUTO_INCREMENT = 1;")
    else:
        # 其他少見後端：給個提示
        print(f"Unknown DB engine: {engine}. Please handle sequence reset manually.")

print(f"✅ Cleared table '{table_name}' and reset its auto-increment (engine={engine}).")

# ---- 3) 接著再照你原本的流程重新匯入 ----
import re
folder_path = r"D:\website\blockchain_guide"  # 單一路徑

def clean_title(filename):
    return filename.replace(".txt", "").replace("_", " ").strip()

for filename in os.listdir(folder_path):
    if filename.endswith(".txt"):
        filepath = os.path.join(folder_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
        GitBookPage.objects.create(
            title=clean_title(filename),
            content=content
        )
        print(f"已儲存：{filename}")