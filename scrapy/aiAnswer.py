# aiAnswer.py（改成工具模組，不要有 while 與 django.setup）
import os, numpy as np, faiss
from django.conf import settings
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv
from myapp.models import GitBookPage

INDEX_PATH = os.path.join(settings.BASE_DIR, "faiss_data", "gitbook_faiss.index")
IDS_PATH   = os.path.join(settings.BASE_DIR, "faiss_data", "gitbook_ids.npy")

index = faiss.read_index(INDEX_PATH)
ids = np.load(IDS_PATH)
embedder = SentenceTransformer("BAAI/bge-m3")

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
llm = genai.GenerativeModel("gemini-2.5-flash")

INSTRUCTION = "為此句子產生檢索向量："

def get_summary_for_keyword(keyword: str, k: int = 5) -> str:
    qtext = INSTRUCTION + keyword
    qvec = embedder.encode([qtext], convert_to_numpy=True)
    qvec = qvec / (np.linalg.norm(qvec, axis=1, keepdims=True) + 1e-12)
    qvec = qvec.astype("float32")

    k = min(k, index.ntotal if hasattr(index, "ntotal") else k)
    D, I = index.search(qvec, k=k)

    docs = []
    for idx in I[0]:
        if idx == -1: continue
        page_id = int(ids[int(idx)])
        page = GitBookPage.objects.filter(id=page_id).only("content").first()
        if page and page.content:
            docs.append(page.content)

    if not docs:
        return "目前找不到與此關鍵字相關的內容。"

    context = "\n\n---\n\n".join(docs)
    prompt = f"請統整與「{keyword}」相關內容並摘要：\n{context}"
    resp = llm.generate_content(prompt)
    return (resp.text or "").strip() or "AI 摘要生成失敗：回傳為空。"
