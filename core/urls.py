from django.urls import path
from core import views

app_name = 'core'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),

    path('book/<int:pk>/', views.BookDetailView.as_view(), name='book_detail'),
    path('book/<int:book_id>/save/', views.save_book, name='save_book'),
    path('book/create/', views.create_book, name='create_book'),

    path('book/<int:book_id>/chapter/<int:chapter_num>/', views.ChapterDetailView.as_view(), name='chapter_detail'),
    path('chapter/<int:chapter_id>/add-music/', views.add_music_recommendation, name='add_music'),
    path('music/<int:music_id>/like/', views.like_music, name='like_music'),
    path('music/<int:music_id>/delete/', views.delete_music, name='delete_music'),
    path('book/<int:book_id>/add-chapters/', views.add_chapters, name='add_chapters'),

    path('book/<int:book_id>/create-playlist/', views.create_playlist, name='create_playlist'),
    path('playlist/<int:pk>/', views.PlaylistDetailView.as_view(), name='playlist_detail'),
    path('playlist/<int:playlist_id>/like/', views.like_playlist, name='like_playlist'),
    path('playlist/<int:pk>/add-track/', views.add_track_to_playlist, name='add_track'),

    path('profile/', views.profile, name='profile'),
]
