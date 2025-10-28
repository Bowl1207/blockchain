import os, sys
import faiss
import django
import numpy as np
from sentence_transformers import SentenceTransformer
import google.generativeai as genai

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))


# ====== Django 初始化 ======
project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "searchweb.settings")
django.setup()

from myapp.models import GitBookPage

# ====== 載入 FAISS 索引與 ID 對照 ======
index_path = os.path.join(project_path, "faiss_data", "gitbook_faiss.index")
ids_path = os.path.join(project_path, "faiss_data", "gitbook_ids.npy")

index = faiss.read_index(index_path)
ids = np.load(ids_path)

# 初始化模型
embedding_model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")

# 設定 Gemini API
os.environ["GOOGLE_API_KEY"] = "AIzaSyBzZ3_CM_eUgjX8xrBHKmqLCQZ68tPrG7A"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
llm = genai.GenerativeModel("gemini-2.5-flash")

# ====== 使用者查詢 ======
while True:
    query = input("\n 請輸入你的問題（或輸入 q 離開）：")
    if query.lower() in ["q", "quit", "exit"]:
        print(" 結束對話。")
        break

    query_vector = embedding_model.encode([query])
    D, I = index.search(query_vector, k=3)

    # 取得對應的資料庫內容
    retrieved_docs = []
    for idx in I[0]:
        page_id = ids[idx]
        try:
            page = GitBookPage.objects.get(id=page_id)
            retrieved_docs.append(page.content)
        except GitBookPage.DoesNotExist:
            continue
    
    # ====== 建立給 Gemini 的 prompt ======
    context = "\n".join(retrieved_docs)
    prompt = f"根據以下內容回答問題：\n{context}\n\n問題：{query}"
    response = llm.generate_content(prompt)

    print("\n AI 回答：\n", response.text)

