from django.urls import path, re_path
from . import views

app_name = "interpolApp"

urlpatterns = [
    path('', views.interpol, name="interpol"),
    re_path(r'^notice_detail/(?P<notice_id>.+)/$', views.notice_detail, name='notice_detail'),
]
