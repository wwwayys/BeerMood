from collections import deque

from data_loader import load_catalog_from_json
from price_tree import build_price_tree, search_price_range
from indexes import build_taste_index
from filters import (
    normalize,
    parse_filter_values,
    filter_by_ranked_tags,
    remove_duplicates,
    intersect_with_current
)
from display import show_beer, show_beer_list
from input_utils import input_int


def make_recommendation_queue(beers):
    """Создать очередь рекомендаций из списка напитков.

    Args:
        beers: Список объектов Beer.

    Returns:
        Объект deque с напитками в том же порядке.
    """

    # deque позволяет быстро получать следующую рекомендацию слева
    return deque(beers)


def get_available_tags(catalog, field_name):
    """Собрать отсортированный список уникальных тегов из каталога.

    Args:
        catalog: Список объектов Beer.
        field_name: Имя атрибута Beer (taste_tags, mood_tags, weather_tags).

    Returns:
        Отсортированный список нормализованных уникальных тегов.
    """

    # Множество автоматически убирает повторяющиеся теги
    tags = set()

    # Собираем теги из указанного поля каждого напитка
    for beer in catalog:
        beer_tags = getattr(beer, field_name)

        for tag in beer_tags:
            normalized_tag = normalize(tag)

            if normalized_tag:
                tags.add(normalized_tag)

    # Возвращаем варианты в алфавитном порядке
    return sorted(tags)


def print_options(title, options):
    """Вывести нумерованный список доступных вариантов.

    Args:
        title: Заголовок списка.
        options: Список строк для отображения.
    """

    print(f"\n{title}")

    # Нумерацию начинаем с единицы для удобства пользователя
    for index, option in enumerate(options, start=1):
        print(f"{index}. {option}")


def ask_valid_tags(message, available_options):
    """Запросить один или несколько тегов из предложенного списка.

    Повторяет запрос до тех пор, пока все введённые значения
    не окажутся в available_options.

    Args:
        message: Текст приглашения к вводу.
        available_options: Список допустимых нормализованных значений.

    Returns:
        Строка с введёнными тегами через запятую.
    """

    # Запрашиваем ввод повторно, пока все теги не будут корректными
    while True:
        user_input = input(message)

        # Разбиваем строку на отдельные нормализованные значения
        values = parse_filter_values(user_input)

        if not values:
            print("Ошибка: нужно ввести хотя бы одно значение из предложенного списка.")
            continue

        # Собираем значения, которых нет среди доступных вариантов
        invalid_values = []

        for value in values:
            if value not in available_options:
                invalid_values.append(value)

        if invalid_values:
            print("Ошибка: нужно выбрать только значения из предложенного списка.")
            print(f"Неподходящие значения: {', '.join(invalid_values)}")
            print("Попробуйте ещё раз.")
            continue

        # Возвращаем проверенные значения в едином формате
        return ", ".join(values)


def show_main_menu():
    """Вывести основное меню программы.

    Команды идут по порядку:
    1–9 и 0 для выхода.
    """

    print("\n========== BeerMood ==========")
    print("1. Показать текущий список напитков")
    print("2. Сортировать напитки")
    print("3. Фильтр по бюджету")
    print("4. Фильтр по настроению")
    print("5. Фильтр по погоде")
    print("6. Поиск по вкусовому ключевому слову")
    print("7. Перейти в режим подбора рекомендаций")
    print("8. Отменить последнее действие")
    print("9. Сбросить все фильтры")
    print("0. Выйти")


def show_recommendation_menu():
    """Вывести меню режима подбора рекомендаций.

    Здесь есть только фильтры,
    команда показа рекомендации
    и команда возврата в основное меню.
    """

    print("\n========== BeerMood: подбор рекомендаций ==========")
    print("1. Фильтр по бюджету")
    print("2. Фильтр по настроению")
    print("3. Фильтр по погоде")
    print("4. Поиск по вкусовому ключевому слову")
    print("5. Показать следующую рекомендацию")
    print("0. Вернуться в основное меню")


def print_filter_result(filter_name, current_results, recommendation_mode):
    """Вывести результат применения фильтра в зависимости от режима.

    В обычном режиме показывает полный список напитков.
    В режиме рекомендаций — только количество подходящих вариантов.

    Args:
        filter_name: Название применённого фильтра для вывода.
        current_results: Текущий отфильтрованный список напитков.
        recommendation_mode: True, если активен режим рекомендаций.
    """

    # В режиме рекомендаций не выводим длинный список напитков
    if recommendation_mode:
        print(f"{filter_name} запомнен.")
        print(f"Подходящих вариантов: {len(current_results)}")
        print("Чтобы получить рекомендацию, выберите команду 5.")
    else:
        # В основном режиме сразу показываем результат фильтра
        print(f"{filter_name} применён.")
        show_beer_list(current_results)


def apply_budget_filter(current_results, price_tree):
    """Применить фильтр по бюджету через бинарное дерево поиска.

    Args:
        current_results: Текущий список напитков.
        price_tree: Корневой узел PriceNode.

    Returns:
        Кортеж (filtered, success), где filtered — отфильтрованный список,
        success — False, если диапазон цен некорректен.
    """

    # Получаем границы бюджета от пользователя
    min_price = input_int("Минимальная цена: ")
    max_price = input_int("Максимальная цена: ")

    # Проверяем правильность диапазона
    if min_price > max_price:
        print("Минимальная цена не может быть больше максимальной.")
        return current_results, False

    # Сначала ищем по дереву цен, затем учитываем предыдущие фильтры
    found_by_tree = search_price_range(price_tree, min_price, max_price)
    filtered = intersect_with_current(found_by_tree, current_results)

    return filtered, True


def apply_mood_filter(current_results, mood_options):
    """Запросить настроение у пользователя и отфильтровать напитки.

    Args:
        current_results: Текущий список напитков.
        mood_options: Список допустимых значений из датасета.

    Returns:
        Отфильтрованный список напитков, отсортированный по совпадению тегов.
    """

    # Показываем доступные теги и запрашиваем настроение
    print_options("Доступные варианты настроения:", mood_options)

    mood = ask_valid_tags(
        "\nВведите настроение. Можно несколько через запятую: ",
        mood_options
    )

    # Сортируем результат по количеству совпавших тегов
    filtered = filter_by_ranked_tags(
        current_results,
        mood,
        "mood_tags"
    )

    return filtered


def apply_weather_filter(current_results, weather_options):
    """Запросить погоду у пользователя и отфильтровать напитки.

    Args:
        current_results: Текущий список напитков.
        weather_options: Список допустимых значений из датасета.

    Returns:
        Отфильтрованный список напитков, отсортированный по совпадению тегов.
    """

    # Показываем доступные теги и запрашиваем погоду
    print_options("Доступные варианты погоды:", weather_options)

    weather = ask_valid_tags(
        "\nВведите погоду. Можно несколько через запятую: ",
        weather_options
    )

    # Сортируем результат по количеству совпавших тегов
    filtered = filter_by_ranked_tags(
        current_results,
        weather,
        "weather_tags"
    )

    return filtered


def apply_taste_filter(current_results, taste_index, taste_options):
    """Запросить вкусовые предпочтения и отфильтровать напитки через индекс.

    Сначала ищет кандидатов через инвертированный индекс, потом пересекает
    с current_results и сортирует по числу совпадений.

    Args:
        current_results: Текущий список напитков.
        taste_index: Инвертированный индекс вкусовых тегов.
        taste_options: Список допустимых значений из датасета.

    Returns:
        Отфильтрованный список напитков, отсортированный по совпадению тегов.
    """

    # Показываем доступные вкусы и запрашиваем выбор пользователя
    print_options("Доступные варианты вкуса:", taste_options)

    keyword_input = ask_valid_tags(
        "\nВведите вкус, которого вам сегодня хочется. Можно несколько через запятую: ",
        taste_options
    )

    # Разбираем запрос на отдельные вкусовые теги
    keywords = parse_filter_values(keyword_input)

    # Через индекс быстро собираем всех подходящих кандидатов
    candidates = []

    for keyword in keywords:
        found = taste_index.get(keyword, [])
        candidates.extend(found)

    # Один напиток мог встретиться сразу по нескольким тегам
    candidates = remove_duplicates(candidates)

    # Сортируем кандидатов по точности совпадения
    ranked_candidates = filter_by_ranked_tags(
        candidates,
        keyword_input,
        "taste_tags"
    )

    # Учитываем фильтры, которые были применены раньше
    filtered = intersect_with_current(
        ranked_candidates,
        current_results
    )

    return filtered


def main():
    """Запустить приложение BeerMood.

    Загружает каталог, строит вспомогательные структуры данных
    и запускает интерактивный цикл обработки команд пользователя.
    """

    # Загружаем данные о напитках из JSON-файла
    catalog = load_catalog_from_json()

    # Без данных программа не сможет продолжить работу
    if not catalog:
        print("Каталог пуст.")
        return

    # Основной список напитков
    current_results = catalog.copy()

    # Бинарное дерево поиска по цене
    price_tree = build_price_tree(catalog)

    # Словарь вкусовых тегов
    taste_index = build_taste_index(catalog)

    # Списки допустимых значений из датасета
    taste_options = get_available_tags(catalog, "taste_tags")
    mood_options = get_available_tags(catalog, "mood_tags")
    weather_options = get_available_tags(catalog, "weather_tags")

    # Очередь рекомендаций
    recommendation_queue = deque()

    # Стек отмены действий
    history_stack = []

    # Режим подбора рекомендаций
    recommendation_mode = False

    # Проверка: применил ли пользователь хотя бы один фильтр после входа в режим рекомендаций
    recommendation_filters_applied = False

    while True:
        if recommendation_mode:
            show_recommendation_menu()
        else:
            show_main_menu()

        choice = input("Выберите действие: ").strip()

        # =================================================
        # РЕЖИМ ПОДБОРА РЕКОМЕНДАЦИЙ
        # =================================================

        if recommendation_mode:

            # ---------------------------------------------
            # 0. Вернуться в основное меню
            # ---------------------------------------------

            if choice == "0":
                recommendation_mode = False
                recommendation_filters_applied = False

                # При выходе из режима возвращаем начальное состояние
                current_results = catalog.copy()
                recommendation_queue.clear()
                history_stack.clear()

                print("Вы вернулись в основное меню.")
                continue

            # ---------------------------------------------
            # 1. Фильтр по бюджету
            # ---------------------------------------------

            elif choice == "1":
                # Сохраняем список, чтобы действие можно было отменить
                previous_results = current_results.copy()

                filtered, success = apply_budget_filter(
                    current_results,
                    price_tree
                )

                if not success:
                    continue

                history_stack.append(("фильтр по бюджету", previous_results))
                current_results = filtered

                # После фильтра заново создаём очередь рекомендаций
                recommendation_filters_applied = True
                recommendation_queue = make_recommendation_queue(current_results)

                print_filter_result(
                    "Фильтр по бюджету",
                    current_results,
                    recommendation_mode
                )

            # ---------------------------------------------
            # 2. Фильтр по настроению
            # ---------------------------------------------

            elif choice == "2":
                previous_results = current_results.copy()

                current_results = apply_mood_filter(
                    current_results,
                    mood_options
                )

                history_stack.append(("фильтр по настроению", previous_results))

                recommendation_filters_applied = True
                recommendation_queue = make_recommendation_queue(current_results)

                print_filter_result(
                    "Фильтр по настроению",
                    current_results,
                    recommendation_mode
                )

            # ---------------------------------------------
            # 3. Фильтр по погоде
            # ---------------------------------------------

            elif choice == "3":
                previous_results = current_results.copy()

                current_results = apply_weather_filter(
                    current_results,
                    weather_options
                )

                history_stack.append(("фильтр по погоде", previous_results))

                recommendation_filters_applied = True
                recommendation_queue = make_recommendation_queue(current_results)

                print_filter_result(
                    "Фильтр по погоде",
                    current_results,
                    recommendation_mode
                )

            # ---------------------------------------------
            # 4. Поиск по вкусу
            # ---------------------------------------------

            elif choice == "4":
                previous_results = current_results.copy()

                current_results = apply_taste_filter(
                    current_results,
                    taste_index,
                    taste_options
                )

                history_stack.append(("поиск по вкусу", previous_results))

                recommendation_filters_applied = True
                recommendation_queue = make_recommendation_queue(current_results)

                print_filter_result(
                    "Поиск по вкусу",
                    current_results,
                    recommendation_mode
                )

            # ---------------------------------------------
            # 5. Показать следующую рекомендацию
            # ---------------------------------------------

            elif choice == "5":
                if not recommendation_filters_applied:
                    print("Сначала примените хотя бы один фильтр: 1, 2, 3 или 4.")
                    continue

                if not current_results:
                    print("По выбранным фильтрам ничего не найдено.")
                    continue

                if not recommendation_queue:
                    print("Рекомендации закончились.")
                    continue

                # Берём первый напиток из очереди и удаляем его из неё
                beer = recommendation_queue.popleft()

                print("\nВаша рекомендация:")
                show_beer(beer)
                print(f"Осталось рекомендаций в очереди: {len(recommendation_queue)}")

            else:
                print("В режиме подбора доступны только команды 1, 2, 3, 4, 5 и 0.")

            continue

        # =================================================
        # ОСНОВНОЙ РЕЖИМ
        # =================================================

        # -------------------------------------------------
        # 1. Показать текущий список
        # -------------------------------------------------

        if choice == "1":
            show_beer_list(current_results)

        # -------------------------------------------------
        # 2. Сортировка списка
        # -------------------------------------------------

        elif choice == "2":
            print("\nСортировать по:")
            print("1. Цене: от дешёвых к дорогим")
            print("2. Крепости: от слабых к крепким")
            print("3. Рейтингу: от лучших к худшим")

            sort_choice = input("Выберите вариант: ").strip()

            # Сохраняем порядок до сортировки для возможной отмены
            history_stack.append(("сортировка", current_results.copy()))

            if sort_choice == "1":
                current_results.sort(key=lambda beer: beer.price)
                print("Список отсортирован по цене.")

            elif sort_choice == "2":
                current_results.sort(key=lambda beer: beer.strength)
                print("Список отсортирован по крепости.")

            elif sort_choice == "3":
                current_results.sort(key=lambda beer: beer.rating, reverse=True)
                print("Список отсортирован по рейтингу.")

            else:
                # Удаляем запись из истории, если сортировка не выполнена
                history_stack.pop()
                print("Нет такого варианта сортировки.")

            recommendation_queue.clear()

        # -------------------------------------------------
        # 3. Фильтр по бюджету
        # -------------------------------------------------

        elif choice == "3":
            previous_results = current_results.copy()

            filtered, success = apply_budget_filter(
                current_results,
                price_tree
            )

            if not success:
                continue

            history_stack.append(("фильтр по бюджету", previous_results))
            current_results = filtered
            recommendation_queue.clear()

            print_filter_result(
                "Фильтр по бюджету",
                current_results,
                recommendation_mode
            )

        # -------------------------------------------------
        # 4. Фильтр по настроению
        # -------------------------------------------------

        elif choice == "4":
            previous_results = current_results.copy()

            current_results = apply_mood_filter(
                current_results,
                mood_options
            )

            history_stack.append(("фильтр по настроению", previous_results))
            recommendation_queue.clear()

            print_filter_result(
                "Фильтр по настроению",
                current_results,
                recommendation_mode
            )

        # -------------------------------------------------
        # 5. Фильтр по погоде
        # -------------------------------------------------

        elif choice == "5":
            previous_results = current_results.copy()

            current_results = apply_weather_filter(
                current_results,
                weather_options
            )

            history_stack.append(("фильтр по погоде", previous_results))
            recommendation_queue.clear()

            print_filter_result(
                "Фильтр по погоде",
                current_results,
                recommendation_mode
            )

        # -------------------------------------------------
        # 6. Поиск по вкусовому ключевому слову
        # -------------------------------------------------

        elif choice == "6":
            previous_results = current_results.copy()

            current_results = apply_taste_filter(
                current_results,
                taste_index,
                taste_options
            )

            history_stack.append(("поиск по вкусу", previous_results))
            recommendation_queue.clear()

            print_filter_result(
                "Поиск по вкусу",
                current_results,
                recommendation_mode
            )

        # -------------------------------------------------
        # 7. Перейти в режим подбора рекомендаций
        # -------------------------------------------------

        elif choice == "7":
            recommendation_mode = True
            recommendation_filters_applied = False

            # В новом режиме начинаем подбор с полного каталога
            current_results = catalog.copy()
            recommendation_queue.clear()
            history_stack.clear()

            print("\nРежим подбора рекомендаций включён.")
            print("Теперь будут показаны только фильтры и команда рекомендации.")
            print("Фильтры будут запоминаться без вывода списка напитков.")

        # -------------------------------------------------
        # 8. Отменить последнее действие
        # -------------------------------------------------

        elif choice == "8":
            if not history_stack:
                print("Нет действий для отмены.")
            else:
                # Достаём последнее сохранённое состояние из стека
                action_name, previous_results = history_stack.pop()
                current_results = previous_results
                recommendation_queue.clear()

                print(f"Отменено действие: {action_name}")
                show_beer_list(current_results)

        # -------------------------------------------------
        # 9. Сбросить все фильтры
        # -------------------------------------------------

        elif choice == "9":
            # Перед сбросом сохраняем текущий список для отмены
            history_stack.append(("сброс фильтров", current_results.copy()))
            current_results = catalog.copy()
            recommendation_queue.clear()

            print("Все фильтры сброшены.")

        # -------------------------------------------------
        # 0. Выход
        # -------------------------------------------------

        elif choice == "0":
            print("До свидания! Хорошего настроения :)")
            break

        else:
            print("Нет такого пункта меню.")


if __name__ == "__main__":
    main()
