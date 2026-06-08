from dataclasses import dataclass


@dataclass
class Beer:
    """Представить сорт пива из каталога.

    Attributes:
        name: Название напитка.
        beer_type: Стиль или сорт пива.
        price: Цена в рублях.
        strength: Крепость в процентах.
        rating: Пользовательский рейтинг.
        taste_tags: Теги вкусового профиля.
        mood_tags: Теги подходящего настроения.
        weather_tags: Теги подходящей погоды.
    """

    # Основная информация о напитке
    name: str
    beer_type: str
    price: int
    strength: float
    rating: float

    # Теги для фильтрации и рекомендаций
    taste_tags: list[str]
    mood_tags: list[str]
    weather_tags: list[str]
