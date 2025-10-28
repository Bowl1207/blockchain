# scrapy/build_faiss.py

import os
import sys
import django
import numpy as np
import faiss 
from sentence_transformers import SentenceTransformer

# 加入 Django 專案路徑
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(project_path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "searchweb.settings")
django.setup()

from myapp.models import GitBookPage

# 讀出所有內容
pages = GitBookPage.objects.all()

# 使用多語言小型模型（速度快、效果不錯）MiniLM-L12-v2')
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# 將所有內容轉為 list
documents = [page.content for page in pages]
titles = [page.title for page in pages]
ids = [page.id for page in pages]

# 向量化
print("正在進行向量轉換...")
embeddings = model.encode(documents, convert_to_numpy=True, show_progress_bar=True)

# 建立 Faiss 索引
dimension = embeddings.shape[1]
index = faiss.IndexFlatL2(dimension)
index.add(embeddings)

# 儲存向量檔案（.index）
index_path1 = os.path.join(project_path, "scrapy", "gitbook_faiss.index")
index_path2 = os.path.join(project_path, "faiss_data", "gitbook_faiss.index")
faiss.write_index(index, index_path1)
faiss.write_index(index, index_path2)

# 同步儲存 ID 對照（你可以用 numpy 存成 .npy 檔）
ids_path1 = os.path.join(project_path, "scrapy", "gitbook_ids.npy")
ids_path2 = os.path.join(project_path, "faiss_data", "gitbook_ids.npy")
np.save(ids_path1, np.array(ids))
np.save(ids_path2, np.array(ids))

print(" index 已儲存到：", index_path1, "和", index_path2)

