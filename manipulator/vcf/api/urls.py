from django.urls import path

from vcf.api.views import *

app = 'vcf'

urlpatterns = [
    path('get-paginated-data/', GetDataAPIView.as_view(), name="get-paginated-data-api-view"),
    path('append-data/', AppendDataAPIView.as_view(), name="append-data-api-view"),
    path('update-data/', UpdateDataAPIView.as_view(), name="update-data-api-view"),
    path('delete-data/', DeleteDataAPIView.as_view(), name="delete-data-api-view"),
]