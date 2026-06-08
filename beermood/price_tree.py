class PriceNode:
    """Представить узел бинарного дерева поиска по цене.

    Один узел хранит все напитки с одинаковой ценой.

    Attributes:
        price: Цена напитков в данном узле.
        beers: Список напитков с этой ценой.
        left: Левое поддерево (цены строго меньше).
        right: Правое поддерево (цены строго больше).
    """

    def __init__(self, price, beer):
        """Инициализировать узел с первым напитком.

        Args:
            price: Цена напитка.
            beer: Первый объект Beer, добавляемый в узел.
        """

        # Сохраняем цену и первый напиток с такой ценой
        self.price = price
        self.beers = [beer]

        # Ссылки на узлы с меньшей и большей ценой
        self.left = None
        self.right = None


def insert_price_node(root, beer):
    """Добавить напиток в бинарное дерево поиска по цене.

    Если напиток с такой ценой уже есть, добавляет его в существующий узел.

    Args:
        root: Корень текущего поддерева или None.
        beer: Объект Beer для вставки.

    Returns:
        Обновлённый корень поддерева.
    """

    # Если ветка пустая, создаём новый узел
    if root is None:
        return PriceNode(beer.price, beer)

    # Напитки с одинаковой ценой храним в одном узле
    if beer.price == root.price:
        root.beers.append(beer)

    # Меньшую цену отправляем в левую ветку
    elif beer.price < root.price:
        root.left = insert_price_node(root.left, beer)

    # Большую цену отправляем в правую ветку
    else:
        root.right = insert_price_node(root.right, beer)

    return root


def build_price_tree(catalog):
    """Построить бинарное дерево поиска по ценам из каталога.

    Args:
        catalog: Список объектов Beer.

    Returns:
        Корневой узел PriceNode или None, если каталог пуст.
    """

    # В начале дерево пустое
    root = None

    # По очереди добавляем все напитки из каталога
    for beer in catalog:
        root = insert_price_node(root, beer)

    return root


def search_price_range(root, min_price, max_price):
    """Найти все напитки в диапазоне цен [min_price, max_price].

    Args:
        root: Корневой узел дерева.
        min_price: Нижняя граница диапазона (включительно).
        max_price: Верхняя граница диапазона (включительно).

    Returns:
        Список объектов Beer, цена которых попадает в заданный диапазон.
    """

    # В этот список собираем найденные напитки
    result = []
    _search_price_range_recursive(root, min_price, max_price, result)

    return result


def _search_price_range_recursive(root, min_price, max_price, result):
    """Рекурсивно обойти дерево и собрать напитки в диапазоне цен.

    Ветка обходится только если она может содержать подходящие цены:
    влево — если текущая цена строго больше min_price,
    вправо — если текущая цена строго меньше max_price.

    Args:
        root: Текущий узел или None.
        min_price: Нижняя граница диапазона (включительно).
        max_price: Верхняя граница диапазона (включительно).
        result: Список для накопления найденных напитков.
    """

    # Пустую ветку дальше не обходим
    if root is None:
        return

    # В левой ветке могут быть подходящие более дешёвые напитки
    if root.price > min_price:
        _search_price_range_recursive(root.left, min_price, max_price, result)

    # Добавляем все напитки из узла, если цена подходит
    if min_price <= root.price <= max_price:
        result.extend(root.beers)

    # В правой ветке могут быть подходящие более дорогие напитки
    if root.price < max_price:
        _search_price_range_recursive(root.right, min_price, max_price, result)
