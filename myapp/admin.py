from django.contrib import admin
from .models import KeywordGroup, Keyword, Question
from django.contrib.admin.sites import AdminSite
from .models import GitBookPage  #爬蟲資料

# 關鍵字群組表
@admin.register(KeywordGroup)
class KeywordGroupAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')  
    search_fields = ('name',)
    fields = ('name', 'description')

# 關鍵字表
@admin.register(Keyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ('id', 'keyword', 'group', 'created_at', 'updated_at')
    list_filter = ('group',)
    search_fields = ('keyword',)

# 問題表
@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'get_keywords','answer', 'created_at', 'updated_at') 
    search_fields = ('question', 'answer',)
    filter_horizontal = ('keywords',)  # 橫向多選介面

    #展示關聯的關鍵字
    def get_keywords(self, obj):
        return ", ".join([k.keyword for k in obj.keywords.all()])
    get_keywords.short_description = "關鍵字"

#爬蟲資料
@admin.register(GitBookPage)
class GitBookPageAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'group', 'show_keywords')
    search_fields = ('title', 'content')

    # 顯示關聯關鍵字（ManyToManyField）
    def show_keywords(self, obj):
        # 若該文章沒有關鍵字，避免報錯
        if obj.keywords.exists():
            return ", ".join([kw.keyword for kw in obj.keywords.all()])
        else:
            return "（無關鍵字）"
    show_keywords.short_description = "相關關鍵字"  # 設定欄位名稱