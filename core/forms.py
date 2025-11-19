from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import MusicRecommendation, Playlist, Comment, Book, PlaylistTrack

# Міксін для автоматичного додавання стилів до всіх полів
class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs['class'] = 'form-checkbox'
            else:
                existing_class = field.widget.attrs.get('class', '')
                field.widget.attrs['class'] = f'{existing_class} form-input'.strip()

# --- ФОРМИ ---

class BookForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'year', 'genre', 'description', 'cover_image', 'cover_url']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-textarea', 'placeholder': 'Про що ця книга?'}),
            'cover_url': forms.URLInput(attrs={'placeholder': 'https://...'}),
        }

class SignUpForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class UserUpdateForm(StyledFormMixin, forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class MusicRecommendationForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = MusicRecommendation
        fields = ['track_title', 'artist', 'link_type', 'link_url', 'embed_code', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea', 'placeholder': 'Чому саме ця музика?'}),
            'link_type': forms.Select(attrs={'class': 'form-select'}),
        }

class PlaylistForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['title', 'description', 'mood', 'external_link', 'is_public']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea', 'placeholder': 'Опис плейлиста'}),
        }

class PlaylistTrackForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = PlaylistTrack
        fields = ['track_title', 'artist', 'link_url']
        widgets = {
            'track_title': forms.TextInput(attrs={'placeholder': 'Назва пісні'}),
            'artist': forms.TextInput(attrs={'placeholder': 'Виконавець'}),
            'link_url': forms.URLInput(attrs={'placeholder': 'Посилання на трек'}),
        }

class CommentForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={'rows': 3, 'class': 'form-textarea', 'placeholder': 'Ваш коментар...'})
        }

class BulkChaptersForm(StyledFormMixin, forms.Form):
    number_of_chapters = forms.IntegerField(
        min_value=1,
        max_value=100,
        label="Кількість розділів",
        widget=forms.NumberInput(attrs={'placeholder': 'Наприклад: 10'})
    )