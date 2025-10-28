from django.db import models

class KeywordGroup(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="關鍵字群組名稱")
    description = models.TextField(blank=True, verbose_name="主題描述")

    def __str__(self):
        return self.name

class Keyword(models.Model):
    group = models.ForeignKey(KeywordGroup, on_delete=models.CASCADE, related_name='keywords')
    keyword = models.CharField(max_length=100, unique=True, verbose_name="關鍵字") #增加unique限制，關鍵字不可重複
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")
    def __str__(self):
        return self.keyword

class Question(models.Model):
    keywords = models.ManyToManyField(Keyword, related_name='questions') #ManyToManyField讓一個問題可以連到多個關鍵字
    question = models.TextField(verbose_name="問題內容")
    answer = models.TextField(verbose_name="答案內容")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="建立時間")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新時間")

    def __str__(self):
        return self.question[:50]  # 顯示前 50 字
    
    @property #讓模板用keyword_list存取關鍵字
    def keyword_list(self):
        return ", ".join([k.keyword for k in self.keywords.all()])

class GitBookPage(models.Model):
    title = models.CharField(max_length=255)
    content = models.TextField()
    group = models.ForeignKey(
        KeywordGroup,
        on_delete=models.SET_NULL,   # 群組刪掉時，保留文章但設為 null
        null=True,
        blank=True,
        related_name="gitbook_pages",
        verbose_name="文章群組")

    keywords = models.ManyToManyField(
        "Keyword",
        blank=True,
        related_name="gitbook_pages",
        verbose_name="相關關鍵字"
    )

    def __str__(self):
        return self.title
