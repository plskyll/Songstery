from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Book, Chapter, MusicRecommendation, Playlist, Like, SavedBook, Comment
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
            messages.success(request, 'Welcome to Songstery!')
            return redirect('core:home')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get('search', '').strip()
        active_genre = self.request.GET.get('genre', '').strip()

        books_qs = Book.objects.all()

        if search_query:
            books_qs = books_qs.filter(
                Q(title__icontains=search_query) |
                Q(author__icontains=search_query) |
                Q(genre__icontains=search_query)
            )

        if active_genre:
            books_qs = books_qs.filter(genre__iexact=active_genre)

        if search_query:
            section_title = f'Search results: "{search_query}"'
        elif active_genre:
            section_title = active_genre
        else:
            section_title = 'All Books'

        paginator = Paginator(books_qs, 8)
        page_obj = paginator.get_page(self.request.GET.get('page'))

        context['db_books'] = page_obj
        context['page_obj'] = page_obj
        context['search_query'] = search_query
        context['active_genre'] = active_genre
        context['books_section_title'] = section_title
        context['genres'] = (
            Book.objects
            .exclude(genre='')
            .values_list('genre', flat=True)
            .distinct()
            .order_by('genre')
        )
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
        context['top_music'] = MusicRecommendation.objects.filter(
            chapter__book=book
        ).order_by('-likes_count')[:10]
        context['comments'] = book.comments.filter(
            parent=None
        ).select_related('user').prefetch_related('replies__user')
        context['comment_form'] = CommentForm()

        if self.request.user.is_authenticated:
            context['is_saved'] = SavedBook.objects.filter(user=self.request.user, book=book).exists()
            context['is_owner'] = (self.request.user == book.creator)

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
        context['comments'] = chapter.comments.filter(
            parent=None
        ).select_related('user').prefetch_related('replies__user')
        context['comment_form'] = CommentForm()
        context['prev_chapter'] = Chapter.objects.filter(
            book=chapter.book, number=chapter.number - 1
        ).first()
        context['next_chapter'] = Chapter.objects.filter(
            book=chapter.book, number=chapter.number + 1
        ).first()

        if self.request.user.is_authenticated:
            context['liked_music_ids'] = list(
                Like.objects.filter(
                    user=self.request.user,
                    music_recommendation__in=context['music_recommendations']
                ).values_list('music_recommendation_id', flat=True)
            )

        return context


class PlaylistDetailView(DetailView):
    model = Playlist
    template_name = 'core/playlist_detail.html'
    context_object_name = 'playlist'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tracks'] = self.object.tracks.all()
        context['comments'] = self.object.comments.filter(
            parent=None
        ).select_related('user').prefetch_related('replies__user')
        context['comment_form'] = CommentForm()
        if self.request.user.is_authenticated:
            context['is_liked'] = Like.objects.filter(
                user=self.request.user, playlist=self.object
            ).exists()
        return context


@login_required
def add_comment(request):
    if request.method != 'POST':
        return redirect(request.META.get('HTTP_REFERER', '/'))

    form = CommentForm(request.POST)
    if not form.is_valid():
        return redirect(request.META.get('HTTP_REFERER', '/'))

    comment = form.save(commit=False)
    comment.user = request.user

    book_id = request.POST.get('book_id')
    chapter_id = request.POST.get('chapter_id')
    playlist_id = request.POST.get('playlist_id')
    parent_id = request.POST.get('parent_id')

    if book_id:
        comment.book = get_object_or_404(Book, id=book_id)
    if chapter_id:
        comment.chapter = get_object_or_404(Chapter, id=chapter_id)
    if playlist_id:
        comment.playlist = get_object_or_404(Playlist, id=playlist_id)
    if parent_id:
        comment.parent = get_object_or_404(Comment, id=parent_id)

    comment.save()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if comment.user == request.user or request.user.is_staff:
        comment.delete()
    return redirect(request.META.get('HTTP_REFERER', '/'))


@login_required
def create_book(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.creator = request.user
            book.save()
            Chapter.objects.create(
                book=book, number=1, title='Chapter 1', is_approved=True
            )
            messages.success(request, 'Book added successfully.')
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
        messages.success(request, 'Book removed from saved.')
    else:
        messages.success(request, 'Book saved.')
    return redirect('core:book_detail', pk=book_id)


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

            Chapter.objects.bulk_create([
                Chapter(
                    book=book,
                    number=start_num + i,
                    title=f'Chapter {start_num + i}',
                    is_approved=is_owner,
                )
                for i in range(count)
            ])

            if is_owner:
                messages.success(request, f'{count} chapters added.')
            else:
                messages.warning(request, f'{count} chapters submitted for review.')

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
            messages.success(request, 'Recommendation added.')
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
        messages.success(request, 'Recommendation removed.')
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
            messages.success(request, 'Playlist created.')
            return redirect('core:playlist_detail', pk=playlist.pk)
    else:
        form = PlaylistForm()

    return render(request, 'core/create_playlist.html', {
        'form': form,
        'book': book,
        'chapters': book.chapters.all(),
    })


@login_required
def add_track_to_playlist(request, pk):
    playlist = get_object_or_404(Playlist, pk=pk)

    if request.user != playlist.creator:
        messages.error(request, 'Only the playlist creator can add tracks.')
        return redirect('core:playlist_detail', pk=pk)

    if request.method == 'POST':
        form = PlaylistTrackForm(request.POST)
        if form.is_valid():
            track = form.save(commit=False)
            track.playlist = playlist
            last = playlist.tracks.order_by('-order').first()
            track.order = (last.order + 1) if last else 1
            track.save()
            messages.success(request, 'Track added.')
            return redirect('core:playlist_detail', pk=pk)
    else:
        form = PlaylistTrackForm()

    return render(request, 'core/add_track.html', {'form': form, 'playlist': playlist})


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
def profile(request):
    if request.method == 'POST':
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated.')
            return redirect('core:profile')
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, 'core/profile.html', {
        'form': form,
        'saved_books': SavedBook.objects.filter(user=request.user).select_related('book'),
        'my_playlists': Playlist.objects.filter(creator=request.user).select_related('book'),
        'my_recommendations': MusicRecommendation.objects.filter(
            user=request.user
        ).select_related('chapter__book'),
    })