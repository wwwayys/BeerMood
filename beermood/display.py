def show_beer(beer):
    """Вывести подробную информацию об одном напитке в консоль.

    Args:
        beer: Объект Beer для отображения.
    """

    # Отделяем карточку напитка от остального вывода
    print("----------------------------------------")
    print(f"Название: {beer.name}")
    print(f"Сорт: {beer.beer_type}")
    print(f"Цена: {beer.price} руб.")
    print(f"Крепость: {beer.strength}%")
    print(f"Рейтинг: {beer.rating}")
    print(f"Вкус: {', '.join(beer.taste_tags)}")
    print(f"Настроение: {', '.join(beer.mood_tags)}")
    print(f"Погода: {', '.join(beer.weather_tags)}")


def show_beer_list(beers):
    """Вывести список напитков в консоль.

    Если список пуст, выводит сообщение «Ничего не найдено.»

    Args:
        beers: Список объектов Beer для отображения.
    """

    # Сразу сообщаем пользователю, если список пуст
    if not beers:
        print("Ничего не найдено.")
        return

    # Показываем количество результатов и каждую карточку отдельно
    print(f"\nНайдено напитков: {len(beers)}")

    for beer in beers:
        show_beer(beer)
