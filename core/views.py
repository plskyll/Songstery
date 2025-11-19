from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from .models import *
from .forms import MusicRecommendationForm, PlaylistForm, CommentForm

# Тестові дані (замість API)
books_data = [
    {
        'id': 1,
        'title': 'Шістка воронів',
        'author': 'Лі Бардуго',
        'cover': 'https://static.yakaboo.ua/media/catalog/product/1/1/116_12_1.jpg',
        'genre': 'Фентезі',
        'year': 2015,
    },
    {
        'id': 2,
        'title': 'Тюремна цілителька',
        'author': 'Лінетт Ноні',
        'cover': 'https://static.yakaboo.ua/media/cloudflare/product/webp/600x840/7/_/7_36_2.jpg',
        'genre': 'Фентезі',
        'year': 2021,
    },
    {
        'id': 3,
        'title': 'Золота клітка',
        'author': 'Лінетт Ноні',
        'cover': 'https://static.yakaboo.ua/media/catalog/product/7/9/79_30.jpg',
        'genre': 'Фентезі',
        'year': 2021,
    },
]

popular_music = [
    {
        'id': 1,
        'title': "Trouble",
        'artist': 'Valerie Broussard',
        'book': 'Шістка воронів',
        'meta': 'Valerie Broussard • Шістка воронів',
        'likes': 2458,
    },
    {
        'id': 2,
        'title': 'Survivor',
        'artist': '2WEI',
        'book': 'Тюремна цілителька',
        'meta': '2WEI • Тюремна цілителька',
        'likes': 1892,
    },
]


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Головна'
        context['books_section_title'] = 'Популярні книги'
        context['music_section_title'] = 'Популярна музика'
        context['books'] = books_data
        context['popular_music'] = popular_music

        # Реальні книги з БД
        context['db_books'] = Book.objects.all()[:6]
        return context


class BookDetailView(DetailView):
    model = Book
    template_name = 'core/book_detail.html'
    context_object_name = 'book'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        book = self.object

        book.views_count += 1
        book.save(update_fields=['views_count'])

        context['chapters'] = book.chapters.all()
        context['popular_playlists'] = book.playlists.filter(
            is_public=True
        ).order_by('-likes_count')[:5]

        context['top_music'] = MusicRecommendation.objects.filter(
            chapter__book=book
        ).select_related('user', 'chapter').order_by('-likes_count')[:10]

        context['comments'] = book.comments.filter(parent=None).select_related('user')[:20]

        if self.request.user.is_authenticated:
            context['is_saved'] = SavedBook.objects.filter(
                user=self.request.user,
                book=book
            ).exists()

        return context


class ChapterDetailView(DetailView):
    model = Chapter
    template_name = 'core/chapter_detail.html'
    context_object_name = 'chapter'

    def get_object(self):
        return get_object_or_404(
            Chapter,
            book_id=self.kwargs['book_id'],
            number=self.kwargs['chapter_num']
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chapter = self.object

        context['music_recommendations'] = chapter.music_recommendations.select_related('user')
        context['playlists'] = chapter.playlists.filter(is_public=True)
        context['comments'] = chapter.comments.filter(parent=None).select_related('user')

        context['prev_chapter'] = Chapter.objects.filter(
            book=chapter.book,
            number=chapter.number - 1
        ).first()

        context['next_chapter'] = Chapter.objects.filter(
            book=chapter.book,
            number=chapter.number + 1
        ).first()

        # Перевірка лайків користувача
        if self.request.user.is_authenticated:
            liked_music_ids = Like.objects.filter(
                user=self.request.user,
                music_recommendation__in=context['music_recommendations']
            ).values_list('music_recommendation_id', flat=True)
            context['liked_music_ids'] = list(liked_music_ids)

        return context


@login_required
def save_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    saved, created = SavedBook.objects.get_or_create(
        user=request.user,
        book=book
    )

    if not created:
        saved.delete()
        messages.success(request, 'Книгу видалено зі збережених')
    else:
        messages.success(request, 'Книгу додано до збережених')

    return redirect('core:book_detail', pk=book_id)


@login_required
def add_music_recommendation(request, chapter_id):
    chapter = get_object_or_404(Chapter, id=chapter_id)

    if request.method == 'POST':
        form = MusicRecommendationForm(request.POST)
        if form.is_valid():
            music = form.save(commit=False)
            music.chapter = chapter
            music.user = request.user
            music.save()
            messages.success(request, 'Музичну рекомендацію додано!')
            return redirect('core:chapter_detail',
                            book_id=chapter.book.id,
                            chapter_num=chapter.number)
    else:
        form = MusicRecommendationForm()

    return render(request, 'core/add_music.html', {
        'form': form,
        'chapter': chapter
    })


@login_required
def like_music(request, music_id):
    music = get_object_or_404(MusicRecommendation, id=music_id)

    like, created = Like.objects.get_or_create(
        user=request.user,
        music_recommendation=music
    )

    if created:
        music.likes_count += 1
        music.save()
    else:
        like.delete()
        music.likes_count = max(0, music.likes_count - 1)
        music.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def delete_music(request, music_id):
    music = get_object_or_404(MusicRecommendation, id=music_id)

    if music.user == request.user or request.user.is_staff:
        chapter_url = music.chapter.get_absolute_url()
        music.delete()
        messages.success(request, 'Рекомендацію видалено')
        return redirect(chapter_url)

    messages.error(request, 'Ви не можете видалити цю рекомендацію')
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def create_playlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = PlaylistForm(request.POST)
        if form.is_valid():
            playlist = form.save(commit=False)
            playlist.book = book
            playlist.creator = request.user

            chapter_id = request.POST.get('chapter_id')
            if chapter_id:
                playlist.chapter_id = chapter_id

            playlist.save()
            messages.success(request, 'Плейлист створено!')
            return redirect('core:playlist_detail', pk=playlist.pk)
    else:
        form = PlaylistForm()

    return render(request, 'core/create_playlist.html', {
        'form': form,
        'book': book,
        'chapters': book.chapters.all()
    })


class PlaylistDetailView(DetailView):
    model = Playlist
    template_name = 'core/playlist_detail.html'
    context_object_name = 'playlist'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        playlist = self.object

        context['tracks'] = playlist.tracks.all()
        context['comments'] = playlist.comments.filter(parent=None).select_related('user')

        if self.request.user.is_authenticated:
            context['is_liked'] = Like.objects.filter(
                user=self.request.user,
                playlist=playlist
            ).exists()

        return context


@login_required
def like_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)

    like, created = Like.objects.get_or_create(
        user=request.user,
        playlist=playlist
    )

    if created:
        playlist.likes_count += 1
        playlist.save()
    else:
        like.delete()
        playlist.likes_count = max(0, playlist.likes_count - 1)
        playlist.save()

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def add_comment(request):
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user

            # Визначаємо до чого коментар
            book_id = request.POST.get('book_id')
            chapter_id = request.POST.get('chapter_id')
            playlist_id = request.POST.get('playlist_id')
            parent_id = request.POST.get('parent_id')

            if book_id:
                comment.book_id = book_id
            if chapter_id:
                comment.chapter_id = chapter_id
            if playlist_id:
                comment.playlist_id = playlist_id
            if parent_id:
                comment.parent_id = parent_id

            comment.save()
            messages.success(request, 'Коментар додано!')

    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def profile(request):
    saved_books = SavedBook.objects.filter(
        user=request.user
    ).select_related('book')

    my_playlists = Playlist.objects.filter(
        creator=request.user
    ).select_related('book')

    my_recommendations = MusicRecommendation.objects.filter(
        user=request.user
    ).select_related('chapter__book')

    return render(request, 'core/profile.html', {
        'saved_books': saved_books,
        'my_playlists': my_playlists,
        'my_recommendations': my_recommendations
    })


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Головна'

        # Пошук
        search_query = self.request.GET.get('search', '')

        if search_query:
            books_qs = Book.objects.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(genre__icontains=search_query)
            )
            context['books_section_title'] = f'Результати пошуку: "{search_query}"'
        else:
            books_qs = Book.objects.all()
            context['books_section_title'] = 'Популярні книги'

        context['db_books'] = books_qs[:12]
        context['search_query'] = search_query

        # Статичні дані для демо
        context['books'] = books_data
        context['popular_music'] = popular_music
        context['music_section_title'] = 'Популярна музика'

        # Топ музика з БД
        context['top_music_db'] = MusicRecommendation.objects.select_related(
            'user', 'chapter__book'
        ).order_by('-likes_count')[:10]

        return context
