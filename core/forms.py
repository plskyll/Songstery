from django import forms
from .models import MusicRecommendation, Playlist, PlaylistTrack, Comment


class MusicRecommendationForm(forms.ModelForm):
    class Meta:
        model = MusicRecommendation
        fields = ['track_title', 'artist', 'link_type', 'link_url', 'embed_code', 'comment']
        widgets = {
            'track_title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Назва треку'
            }),
            'artist': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Виконавець'
            }),
            'link_type': forms.Select(attrs={'class': 'form-select'}),
            'link_url': forms.URLInput(attrs={
                'class': 'form-input',
                'placeholder': 'https://...'
            }),
            'embed_code': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Для YouTube: dQw4w9WgXcQ'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Чому саме ця музика підходить до розділу?',
                'rows': 3
            })
        }


class PlaylistForm(forms.ModelForm):
    class Meta:
        model = Playlist
        fields = ['title', 'description', 'mood', 'is_public']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Назва плейлиста'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Опис плейлиста',
                'rows': 3
            }),
            'mood': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'атмосферний, епічний, спокійний'
            })
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Ваш коментар...',
                'rows': 3
            })
        }
