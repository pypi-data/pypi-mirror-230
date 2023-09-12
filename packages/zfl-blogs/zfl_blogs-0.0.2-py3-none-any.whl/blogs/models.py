from django.db import models  # type: ignore
from markdownx.models import MarkdownxField  # type: ignore
from markdownx.settings import MARKDOWNX_MARKDOWN_EXTENSIONS as EXTENSIONS  # type: ignore
import markdown


class Category(models.Model):
    """
    カテゴリーモデル

    """
    title = models.CharField(
            'カテゴリー',
            max_length=20,
    )
    thumbnail = models.ImageField(
            'サムネイル（空欄可）',
            upload_to='thumbnail',
            null=True,
            blank=True,
    )

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'ブログカテゴリーリスト'
        verbose_name_plural = 'ブログカテゴリーリスト'


class Blog(models.Model):
    """
    記事作成モデル

    """
    title = models.CharField('タイトル', max_length=150)
    text = MarkdownxField('テキスト', help_text='Markdown形式で書いてください。')
    category = models.ForeignKey(Category, on_delete=models.PROTECT)
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    is_publick = models.BooleanField(
            '選択',
            choices=(
                (True, '公開'),
                (False, '非公開'),
            )
    )

    def to_release(self):
        self.is_publick = True
        self.save()

    def to_private(self):
        self.is_publick = False
        self.save()

    def get_toc(self):
        md = markdown.Markdown(extensions=EXTENSIONS)
        html = md.convert(self.text)
        return md.toc

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'ブログリスト'
        verbose_name_plural = 'ブログリスト'


# class Popular(models.Model):
#     """
#     GoogleAnalytics APIモデル
#     blogsアプリで使用しているので、後にblogsアプリに移行
# 
#     """
#     title = models.CharField('人気記事', max_length=100)
#     path = models.CharField('URL', max_length=100)
#     view = models.IntegerField('閲覧数')
# 
#     def __str__(self):
#         return self.title
# 
#     class Meta:
#         verbose_name = '人気記事リスト'
#         verbose_name_plural = '人気記事リスト'
