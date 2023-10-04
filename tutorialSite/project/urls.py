from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login', views.login, name='login'),
    path('signup', views.signup, name='signup'),
    path('logout', views.logout, name="logout"),
    path('dashboard', views.dashboard, name="dashboard"),
    path('write-post', views.writePost, name="write-post"),
    path('view-post/<int:post_id>/', views.viewPost, name="view-post"),
    path('search', views.search, name="search"),
    path('comments/<int:post_id>/', views.comment, name="comment"),
    path('staffPage', views.staff, name="staff"),
    path('request', views.request, name="request"),
]