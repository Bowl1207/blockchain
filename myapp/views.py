from django.shortcuts import render, get_object_or_404
from .models import KeywordGroup, Keyword, Question, GitBookPage

# FAISS 搜尋相關套件
import os
import numpy as np
import faiss
from django.conf import settings
from sentence_transformers import SentenceTransformer
from myapp.models import GitBookPage
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from scrapy.aiAnswer import get_summary_for_keyword


# 載入模型與 index（為提升效能，放外層只初始化一次）
model = SentenceTransformer('BAAI/bge-m3')
index_path = os.path.join(settings.BASE_DIR, "faiss_data", "gitbook_faiss.index")
id_path = os.path.join(settings.BASE_DIR, "faiss_data", "gitbook_ids.npy")
ids = np.load(id_path)
index = faiss.read_index(index_path)

# 假設你有保存 title 對應資訊（以下用假資料代替）
titles = ["頁面1", "頁面2", "頁面3", "頁面4", "頁面5"]


def topic_list(request):
    groups = KeywordGroup.objects.all()
    for group in groups:
        if group.description:
            group.description = group.description.replace("\\n", "\n")

    return render(request, 'searchweb/topic_list.html', {'groups': groups})


def keyword_list(request, group_id):
    group = get_object_or_404(KeywordGroup, pk=group_id)
    keywords = Keyword.objects.filter(group=group)
    return render(request, 'searchweb/keyword_list.html', {'group': group, 'keywords': keywords})


def question_list(request, keyword_id):
    keyword = get_object_or_404(Keyword, pk=keyword_id)
    questions = Question.objects.filter(keywords=keyword)
    gitbook_pages = keyword.gitbook_pages.all()
    return render(request, 'searchweb/question_list.html', {'keyword': keyword, 'questions': questions, 'gitbook_pages': gitbook_pages})


def backend_dashboard(request):
    return render(request, 'searchweb/dashboard.html')


# FAISS 查詢功能
def search_by_faiss(request):
    query = request.GET.get('q')
    results = []

    if query:
        # 1. 產生查詢向量
        embedding = model.encode([query])
        D, I = index.search(np.array(embedding).astype('float32'), k=5)

        # 2. 取出被命中的 GitBookPage id
        matched_ids = [int(ids[i]) for i in I[0] if i != -1]

        # 3. 把 id 對應成 GitBookPage 物件 (dict for 快速查找)
        id_to_obj = {obj.id: obj for obj in GitBookPage.objects.filter(id__in=matched_ids)}

        # 4. 整理結果 (帶 id、title、distance)
        for rank, i in enumerate(I[0]):
            if i != -1:
                page_id = int(ids[i])
                page = id_to_obj.get(page_id)
                if page:
                    results.append({
                        "id": page.id,
                        "title": page.title,
                        "distance": D[0][rank],
                    })

    return render(request, "searchweb/faiss_search.html", {
        "results": results,
        "query": query
    })

'''def gitbookpage(request):
    pages = GitBookPage.objects.order_by("title")
    return render(request, "searchweb/gitbookpage.html", {"pages": pages})'''

def gitbookpage(request, pk):
    page = get_object_or_404(GitBookPage, pk=pk)
    return render(request, "searchweb/gitbookpage.html", {"page": page})

@require_GET
def get_keyword_summary(request):
    keyword = (request.GET.get("keyword") or "").strip()
    if not keyword:
        return JsonResponse({"error": "請提供 keyword 參數"}, status=400)
    summary = get_summary_for_keyword(keyword, k=5)
    return JsonResponse({"keyword": keyword, "summary": summary})