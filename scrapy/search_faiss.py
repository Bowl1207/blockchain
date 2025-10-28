import os
import sys
import faiss
import numpy as np
import django

# 連接 Django 專案
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "searchweb.settings")
django.setup()

from sentence_transformers import SentenceTransformer
from myapp.models import GitBookPage

# 載入模型與 Index
model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
index_path = os.path.join(os.path.dirname(__file__), "gitbook_faiss.index")
index = faiss.read_index(index_path)

# 準備原始資料（查詢完用來對照）
pages = GitBookPage.objects.all()
titles = [page.title for page in pages]
documents = [page.content for page in pages]

# 讓使用者輸入查詢語句
query = input("請輸入查詢文字： ")
query_vec = model.encode([query])

# 查詢 FAISS 最相近的 3 筆結果
k = 5
D, I = index.search(np.array(query_vec).astype("float32"), k)

print("\n🔍 查詢結果：")
for idx, score in zip(I[0], D[0]):
    print(f"\n📘 標題：{titles[idx]}")
    print(f"📄 內容片段：{documents[idx][:500]}...")
    print(f"📏 距離（越小越相近）：{score:.4f}")
