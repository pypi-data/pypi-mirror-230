# from apiclient.discovery import build
# from oauth2client.service_account import ServiceAccountCredentials
# import os
# import datetime
# from dateutil.relativedelta import relativedelta
# from django.conf import settings
# 
# 
# SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
# KEY_FILE_LOCATION = os.path.join(settings.ZEROFROMLIGHT_DIR, 'client_secrets.json')
# VIEW_ID = settings.ZEROFROMLIGHT_KEYS['VIEW_ID']
# 
# def initialize_analyticsreporting():
#     credentials = ServiceAccountCredentials.from_json_keyfile_name(
#                             KEY_FILE_LOCATION, SCOPES)
#     analytics = build('analyticsreporting', 'v4', credentials=credentials)
#     return analytics
# 
# 
# def get_report(analytics):
#     """
#     ブログ閲覧数取得
# 
#     """
#     return analytics.reports().batchGet(
#             body={
#             'reportRequests': [{
#                 'viewId': VIEW_ID,
#                 'pageSize': 10,
#                 'dateRanges': [{"startDate": "3daysAgo", "endDate": "today"}],
#                 'dimensions': [{'name': 'ga:pagePath'}, {'name': 'ga:pageTitle'}],
#                 'dimensionFilterClauses': [{'filters': [{'dimensionName': 'ga:pagePath',
#                                                        'expressions': ['/blogs/detail/']}]
#                                            }],
#                 'metrics': [{'expression': 'ga:pageviews'}],
#                 'orderBys': [{'fieldName': 'ga:pageviews', 'sortOrder': 'DESCENDING'}],
#              }]
#             }
#     ).execute()
# 
# 
# def print_response():
#     """
#     ブログ閲覧数取得処理
# 
#     """
#     analytics = initialize_analyticsreporting()
#     response = get_report(analytics)
#     print('結果---------')
#     print(response['reports'][0]['data'])
# 
#     for row in response['reports'][0]['data']['rows']:
#         row_path = 'https://zerofromlight.com' + row['dimensions'][0]
#         #row_path = row['dimensions'][0][6:]
#         #row_path = row['dimensions'][0].split('/')[3]
#         row_title = row['dimensions'][1]
#         row_view = row['metrics'][0]['values'][0]
#         yield row_title, row_path, row_view


