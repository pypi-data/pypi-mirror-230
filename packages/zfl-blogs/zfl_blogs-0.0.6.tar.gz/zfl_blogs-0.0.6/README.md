# zfl-blogs

[![PyPI - Version](https://img.shields.io/pypi/v/zfl-blogs.svg)](https://pypi.org/project/zfl-blogs)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/zfl-blogs.svg)](https://pypi.org/project/zfl-blogs)

-----

**目次**

- [詳細](#詳細)
- [インストール](#インストール)
- [設定](#設定)
- [実行](#実行)
- [License](#license)

## 詳細

zfl-blogs

## インストール

```console
$ pip install zfl-blogs
```

## 設定

`settings.py`の編集

```python
INSTALLED_APPS = [
    ...
    'django.forms',
    'django_cleanup',
    'markdownx',
    'blogs',
]

FORM_RENDERER = 'django.forms.renderers.TemplatesSetting'

...

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                ...
                'blogs.context.common',
            ],
            'libraries': {
                'mark': 'templatetags.mark',
            }
        },
    },
]

...

STATIC_URL = '/static/'


MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")

MARKDOWNX_IMAGE_MAX_SIZE = {'size': (800, 500), 'quality': 100}

MARKDOWNX_UPLOAD_MAX_SIZE = 1000 * 1024 # 最大1MBまで可能

MARKDOWNX_UPLOAD_CONTENT_TYPES = ['image/jpeg', 'image/png', 'image/gif']

MARKDOWNX_MARKDOWN_EXTENSIONS = [
        'extra',
        'admonition', # 訓戒・忠告
        'sane_lists', # 正常なリスト
        'toc',    # 目次
        'nl2br',  # 改行
]

MARKDOWNX_MARKDOWN_EXTENSION_CONFIGS = {
        'toc': {
            'title': '目次',
            'permalink': True
        }
}

```

`urls.py`の編集

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('markdownx/', include("markdownx.urls")),
    path('blogs/', include("blogs.urls")),
]

# 開発環境での設定
if settings.DEBUG == True:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

`settings.py`の`FORM_RENDERER`で`django.forms.renderers.TemplatesSetting`に設定しているので、プロジェクト直下に`templates`ディレクトリを作成し、`blogs`アプリの`templates`ディレクトリから`markdownx`ディレクトリをコピーしてきます。

そうすることで、記事を書く際のマークダウンプレビューを横並びにすることができます。

```console
$ python3 -c "import blogs; print(blogs.__path__)"
```

## 実行

データベースの作成

```console
$ python3 manage.py migrate
```

スーパーユーザーの作成

```console
$ python3 manage.py createsuperuser
```

グーグルアナリティスクすAPIからブログの閲覧数を取得するコマンドの実行

```console
$ python3 manage.py access_ranking
```

## License

`zfl-blogs` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
