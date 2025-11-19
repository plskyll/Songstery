from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),

    # Книги
    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/<int:book_id>/save/', views.save_book, name='save_book'),

    # Розділи
    path('book/<int:book_id>/chapter/<int:chapter_num>/',
         views.ChapterDetailView.as_view(), name='chapter_detail'),

    # Музика
    path('chapter/<int:chapter_id>/add-music/',
         views.add_music_recommendation, name='add_music'),
    path('music/<int:music_id>/like/', views.like_music, name='like_music'),
    path('music/<int:music_id>/delete/', views.delete_music, name='delete_music'),

    # Плейлисти
    path('book/<int:book_id>/create-playlist/',
         views.create_playlist, name='create_playlist'),
    path('playlist/<int:pk>/', views.PlaylistDetailView.as_view(), name='playlist_detail'),
    path('playlist/<int:playlist_id>/like/', views.like_playlist, name='like_playlist'),

    # Коментарі
    path('comment/add/', views.add_comment, name='add_comment'),

    # Профіль
    path('profile/', views.profile, name='profile'),
]