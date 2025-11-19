from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import MusicRecommendation, Playlist, Comment, Book, PlaylistTrack


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'year', 'genre', 'description', 'cover_image', 'cover_url']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Назва книги'}),
            'author': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Автор'}),
            'year': forms.NumberInput(attrs={'class': 'form-input', 'placeholder': 'Рік видання'}),
            'genre': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Жанр'}),
            'description': forms.Textarea(
                attrs={'class': 'form-textarea', 'rows': 4, 'placeholder': 'Про що ця книга?'}),
            'cover_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://... (якщо немає файлу)'}),
        }


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']


class MusicRecommendationForm(forms.ModelForm):
    class Meta:
        model = MusicRecommendation
        fields = ['track_title', 'artist', 'link_type', 'link_url', 'embed_code', 'comment']
        widgets = {
            'track_title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Назва треку'}),
            'artist': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Виконавець'}),
            'link_type': forms.Select(attrs={'class': 'form-select'}),
            'link_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://...'}),
            'embed_code': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Для YouTube: ID відео'}),
            'comment': forms.Textarea(
                attrs={'class': 'form-textarea', 'placeholder': 'Чому саме ця музика?', 'rows': 3})
        }


# Оновіть цей клас
class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['title', 'description', 'mood', 'external_link', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Назва плейлиста'}),
            'description': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Опис плейлиста', 'rows': 3}),
            'mood': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'атмосферний, епічний...'}),
            'external_link': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://open.spotify.com/playlist/...'}),
        }


class PlaylistTrackForm(forms.ModelForm):
    class Meta:
        model = PlaylistTrack
        fields = ['track_title', 'artist', 'link_url']
        widgets = {
            'track_title': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Назва пісні'}),
            'artist': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Виконавець'}),
            'link_url': forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'Посилання на трек'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'class': 'form-textarea', 'placeholder': 'Ваш коментар...', 'rows': 3})
        }


class BulkChaptersForm(forms.Form):
    number_of_chapters = forms.IntegerField(
        min_value=1,
        max_value=100,
        label="Кількість розділів",
        widget=forms.NumberInput(attrs={
            'class': 'form-input',
            'placeholder': 'Наприклад: 10'
        })
    )
