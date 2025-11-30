from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import *
from .forms import (
    MusicRecommendationForm, PlaylistForm, CommentForm,
    SignUpForm, UserUpdateForm, BookForm, BulkChaptersForm, PlaylistTrackForm
)


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Реєстрація успішна! Ласкаво просимо.')
            return redirect('core:home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Головна'

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

        paginator = Paginator(books_qs, 8)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['db_books'] = page_obj
        context['page_obj'] = page_obj
        context['search_query'] = search_query

        context['top_music_db'] = MusicRecommendation.objects.select_related(
            'user', 'chapter__book'
        ).order_by('-likes_count')[:6]

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

        if self.request.user == book.creator or self.request.user.is_staff:
            context['chapters'] = book.chapters.all()
        else:
            context['chapters'] = book.chapters.filter(is_approved=True)

        context['popular_playlists'] = book.playlists.filter(is_public=True).order_by('-likes_count')[:5]
        context['top_music'] = MusicRecommendation.objects.filter(chapter__book=book).order_by('-likes_count')[:10]

        if self.request.user.is_authenticated:
            context['is_saved'] = SavedBook.objects.filter(user=self.request.user, book=book).exists()
            context['is_owner'] = (self.request.user == book.creator)

        return context


@login_required
def create_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.creator = request.user
            book.save()

            # Створюємо 1 розділ автоматично
            Chapter.objects.create(
                book=book, number=1, title="Розділ 1",
                description="Початок", is_approved=True
            )

            messages.success(request, 'Книгу успішно створено!')
            return redirect('core:book_detail', pk=book.pk)
    else:
        form = BookForm()
    return render(request, 'core/create_book.html', {'form': form})


@login_required
def save_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    saved, created = SavedBook.objects.get_or_create(user=request.user, book=book)
    if not created:
        saved.delete()
        messages.success(request, 'Книгу видалено зі збережених')
    else:
        messages.success(request, 'Книгу додано до збережених')
    return redirect('core:book_detail', pk=book_id)


class ChapterDetailView(DetailView):
    model = Chapter
    template_name = 'core/chapter_detail.html'
    context_object_name = 'chapter'

    def get_object(self):
        return get_object_or_404(Chapter, book_id=self.kwargs['book_id'], number=self.kwargs['chapter_num'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        chapter = self.object
        context['music_recommendations'] = chapter.music_recommendations.select_related('user')
        context['playlists'] = chapter.playlists.filter(is_public=True)

        context['prev_chapter'] = Chapter.objects.filter(book=chapter.book, number=chapter.number - 1).first()
        context['next_chapter'] = Chapter.objects.filter(book=chapter.book, number=chapter.number + 1).first()

        if self.request.user.is_authenticated:
            liked_music_ids = Like.objects.filter(
                user=self.request.user,
                music_recommendation__in=context['music_recommendations']
            ).values_list('music_recommendation_id', flat=True)
            context['liked_music_ids'] = list(liked_music_ids)
        return context


@login_required
def add_chapters(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if request.method == 'POST':
        form = BulkChaptersForm(request.POST)
        if form.is_valid():
            count = form.cleaned_data['number_of_chapters']
            last_chapter = book.chapters.order_by('-number').first()
            start_num = (last_chapter.number + 1) if last_chapter else 1

            is_owner = (request.user == book.creator) or request.user.is_staff
            approved_status = True if is_owner else False

            chapters_to_create = []
            for i in range(count):
                num = start_num + i
                chapters_to_create.append(Chapter(
                    book=book, number=num, title=f"Розділ {num}",
                    is_approved=approved_status
                ))

            Chapter.objects.bulk_create(chapters_to_create)

            if is_owner:
                messages.success(request, f'Успішно додано {count} розділів!')
            else:
                messages.warning(request, f'Додано {count} розділів. Вони з\'являться після перевірки.')

            return redirect('core:book_detail', pk=book.pk)
    else:
        form = BulkChaptersForm()

    return render(request, 'core/add_chapters.html', {'form': form, 'book': book})


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
            return redirect('core:chapter_detail', book_id=chapter.book.id, chapter_num=chapter.number)
    else:
        form = MusicRecommendationForm()
    return render(request, 'core/add_music.html', {'form': form, 'chapter': chapter})


@login_required
def like_music(request, music_id):
    music = get_object_or_404(MusicRecommendation, id=music_id)
    like, created = Like.objects.get_or_create(user=request.user, music_recommendation=music)
    if created:
        music.likes_count += 1
    else:
        like.delete()
        music.likes_count = max(0, music.likes_count - 1)
    music.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def delete_music(request, music_id):
    music = get_object_or_404(MusicRecommendation, id=music_id)
    if music.user == request.user or request.user.is_staff:
        url = music.chapter.get_absolute_url()
        music.delete()
        messages.success(request, 'Рекомендацію видалено')
        return redirect(url)
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

    chapters = book.chapters.all()
    return render(request, 'core/create_playlist.html', {
        'form': form,
        'book': book,
        'chapters': chapters
    })


@login_required
def add_track_to_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)

    if request.user != playlist.creator:
        messages.error(request, "Тільки автор плейлиста може додавати треки")
        return redirect('core:playlist_detail', pk=pk)

    if request.method == 'POST':
        form = PlaylistTrackForm(request.POST)
        if form.is_valid():
            track = form.save(commit=False)
            track.playlist = playlist

            # Визначаємо порядок (ставимо в кінець)
            last_track = playlist.tracks.order_by('-order').first()
            track.order = (last_track.order + 1) if last_track else 1

            track.save()
            messages.success(request, 'Трек додано!')
            return redirect('core:playlist_detail', pk=pk)
    else:
        form = PlaylistTrackForm()

    return render(request, 'core/add_track.html', {'form': form, 'playlist': playlist})

class PlaylistDetailView(DetailView):
    model = Playlist
    template_name = 'core/playlist_detail.html'
    context_object_name = 'playlist'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracks'] = self.object.tracks.all()
        if self.request.user.is_authenticated:
            context['is_liked'] = Like.objects.filter(user=self.request.user, playlist=self.object).exists()
        return context


@login_required
def like_playlist(request, playlist_id):
    playlist = get_object_or_404(Playlist, id=playlist_id)
    like, created = Like.objects.get_or_create(user=request.user, playlist=playlist)
    if created:
        playlist.likes_count += 1
    else:
        like.delete()
        playlist.likes_count = max(0, playlist.likes_count - 1)
    playlist.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def add_comment(request):
    # Тут можна реалізувати логіку коментарів, поки що заглушка
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профіль оновлено!')
            return redirect('core:profile')
    else:
        form = UserUpdateForm(instance=request.user)

    saved_books = SavedBook.objects.filter(user=request.user).select_related('book')
    my_playlists = Playlist.objects.filter(creator=request.user).select_related('book')
    my_recommendations = MusicRecommendation.objects.filter(user=request.user).select_related('chapter__book')

    return render(request, 'core/profile.html', {
        'form': form,
        'saved_books': saved_books,
        'my_playlists': my_playlists,
        'my_recommendations': my_recommendations
    })