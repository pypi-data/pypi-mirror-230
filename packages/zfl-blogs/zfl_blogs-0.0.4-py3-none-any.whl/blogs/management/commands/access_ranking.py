# from django.core.management.base import BaseCommand
# from blogs.models import Popular
# from .analytics_api import print_response
# 
# 
# class Command(BaseCommand):
#     def handle(self, *args, **options):
# 
#         # ブログ閲覧数取得処理
#         Popular.objects.all().delete()
#         for title, path, view in print_response():
#             Popular.objects.create(
#                         title=title, path=path, view=view
#             )
# 
#         self.stdout.write(self.style.SUCCESS('更新完了'))
