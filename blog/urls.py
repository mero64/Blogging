from django.urls import path

from . import views


urlpatterns = [
    path('', views.StartingPageView.as_view(), name='starting-page'),
    path('blog/<str:username>/', views.UserPageView.as_view(), name='user-page'),
    path('blog/<str:username>/<slug:slug>', views.PostView.as_view(), name='post-view'),
    path('tag/<str:tag>/', views.TagPageView.as_view(), name='tag-view'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.RegisterView.as_view(), name='register'),
]
