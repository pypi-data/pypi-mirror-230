from django.urls import path
# from django.views.generic import TemplateView
from .views import IndexView, TestMenuView

urlpatterns = [
    # path('', TemplateView.as_view(template_name="about.html")),
    path('', IndexView.as_view(), name='index_view'),
    path('menu/', TestMenuView.as_view(), name='test_menu_view'),
]