from django.views.generic import TemplateView

books = [
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
    {
        'id': 3,
        'title': 'Castle',
        'artist': 'Halsey',
        'book': 'Золота клітка',
        'meta': 'Halsey • Золота клітка',
        'likes': 1673,
    },
    {
        'id': 4,
        'title': 'Way Down We Go',
        'artist': 'KALEO',
        'book': 'Шістка воронів',
        'meta': 'KALEO • Шістка воронів',
        'likes': 1521,
    },
    {
        'id': 5,
        'title': 'Lovely',
        'artist': 'Billie Eilish, Khalid',
        'book': 'Тюремна цілителька',
        'meta': 'Billie Eilish, Khalid • Тюремна цілителька',
        'likes': 1384,
    },
    {
        'id': 6,
        'title': 'Everybody Wants To Rule The World',
        'artist': 'Lorde',
        'book': 'Золота клітка',
        'meta': 'Lorde • Золота клітка',
        'likes': 1256,
    },
]


class HomeView(TemplateView):
    template_name = 'core/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Головна'
        context['books_section_title'] = 'Популярні книги'
        context['music_section_title'] = 'Популярна музика'
        context['books'] = books
        context['popular_music'] = popular_music
        return context