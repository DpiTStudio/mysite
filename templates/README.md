# Шаблоны проекта (Templates)

Этот каталог содержит все HTML-шаблоны сайта, написанные на языке шаблонов Django (Django Template Language).

---

## 📂 Структура и логика организации

### 1. `base.html` — Каркас (Main layout)
Основной файл, определяющий структуру всех страниц сайта. Включает в себя:
- `<!DOCTYPE html>` и Meta-теги.
- Подключение глобальных CSS и JS.
- Главный блок `{% block content %}`, который переопределяется дочерними шаблонами.
- Блоки для дополнительных скриптов и стилей на конкретных страницах.

### 2. `header.html` и `footer.html` — Общие компоненты
- `header.html`: Шапка сайта с навигационным меню, логотипом, телефоном и кнопками входа/регистрации.
- `footer.html`: Подвал сайта с контактами, ссылками на социальные сети и быстрым меню.
- `hero.html`: Блок с большим изображением и заголовком (обычно используется на главных страницах разделов).

### 3. `includes/` — Вспомогательные блоки (Snippets)
Многократно используемые части кода, подключаемые через `{% include %}`:
- `breadcrumbs.html`: Цепочка навигации ("хлебные крошки").
- `pagination.html`: Постраничная навигация для списков контента.
- `forms/`: Шаблоны для отображения полей форм.
- `messages.html`: Блок вывода системных всплывающих уведомлений (success, error).

### 4. Шаблоны приложений (App-specific templates)
Шаблоны конкретных приложений перенесены в соответствующие директории внутри самих приложений для обеспечения модульности (согласно Django Best Practices):
- **`accounts`** ➔ `accounts/templates/accounts/` (например, `login.html`, `register.html`, `profile.html`)
- **`cart`** ➔ `cart/templates/cart/` (например, `detail.html`, `checkout.html`, `order_success.html`)
- **`favorites`** ➔ `favorites/templates/favorites/`
- **`knowledge_base`** ➔ `knowledge_base/templates/knowledge_base/`
- **`mail`** ➔ `mail/templates/mail/`
- **`main`** ➔ `main/templates/main/`
- **`news`** ➔ `news/templates/news/` (например, `list.html`, `detail.html`)
- **`portfolio`** ➔ `portfolio/templates/portfolio/` (например, `list.html`, `detail.html`, `price_list.html`)
- **`reviews`** ➔ `reviews/templates/reviews/`
- **`services`** ➔ `services/templates/services/` (например, `list.html`, `detail.html`)
- **`tickets`** ➔ `tickets/templates/tickets/` (например, `list.html`, `detail.html`, `create.html`)

### 5. Системные шаблоны
- `404.html`: Страница "Ошибка: не найдено".
- `500.html`: Страница "Ошибка сервера".
- `admin/`: Папка для переопределения стандартных шаблонов административной панели (остается глобальной).

---

## 💡 Рекомендации при работе с шаблонами
1. **Наследование**: Всегда начинайте новые страницы с `{% extends "base.html" %}`.
2. **Локализация**: Используйте тег `{% trans %}` или `{% blocktranslate %}` для перевода строк.
3. **Безопасность**: Будьте осторожны с фильтром `|safe`, используйте его только для доверенного HTML (например, контент из TinyMCE).
4. **HTMX**: Для работы без перезагрузки страниц создавайте парциальные шаблоны (например, `_partial.html`), которые рендерят только кусок контента.
