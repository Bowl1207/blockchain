import os
import sys
import django
import re

# ✅ 加入專案根目錄到 sys.path（與 manage.py 同層）
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)

#設定 Django 環境
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "searchweb.settings")
django.setup()

from myapp.models import GitBookPage

# 指定資料夾路徑
folder_path = os.path.join(os.path.dirname(__file__), "blockchain_guide")

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
