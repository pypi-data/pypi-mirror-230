from django import template # type: ignore
from django.utils.safestring import mark_safe # type: ignore
from markdownx.utils import markdownify # type: ignore
from markdown.extensions import Extension


register = template.Library()

@register.filter
def markdown_to_html(text):
    return mark_safe(markdownify(text))


# class EscapeHtml(Extension):
#     def extendMarkdown(self, md):
#         md.preprocessors.deregister('html_block')
#         md.inlinePatterns.deregister('html')

