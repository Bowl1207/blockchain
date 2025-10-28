# scrapy/build_faiss.py 建立索引端

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

# 使用 BAAI/bge-m3 模型
model = SentenceTransformer("BAAI/bge-m3")

# 將所有內容轉為 list
documents = [page.content for page in pages]
titles = [page.title for page in pages]
ids = [page.id for page in pages]

# 向量化
print("正在使用bge-m3進行向量轉換...")

instruction = "為此句子產生檢索向量："
docs_with_prompt = [instruction + doc for doc in documents]
embeddings = model.encode(docs_with_prompt, convert_to_numpy=True, show_progress_bar=True)
#正規化
embeddings = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-12)


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

