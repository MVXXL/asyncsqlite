# AsyncSQLite

## Введение

AsyncSQLite - это библиотека Python, предоставляющая асинхронный интерфейс для взаимодействия с базами данных SQLite. Она использует модули asyncio и sqlite3 для эффективного выполнения операций с базами данных в асинхронных приложениях. Это делает ее идеальным выбором для сценариев, где необходимо выполнять ввод-выводные операции, такие как запросы к базе данных, без блокировки цикла событий.

## Установка

Установить AsyncSQLite можно с помощью pip:

```bash
pip install asyncsqlite
```

## Особенности

* **Асинхронный API** - Все методы взаимодействия с базой данных являются асинхронными, что позволяет легко интегрировать их в асинхронные рабочие процессы.
* **Пул соединений** - Эффективно управляет пулом соединений для снижения накладных расходов, связанных с созданием и закрытием соединений для каждой операции.
* **Обработка ошибок** - Встроена обработка ошибок с автоматическими повторными попытками для некоторых ошибок базы данных.
* **Кэширование запросов** - Опционально кэширует результаты запросов для повышения производительности часто выполняемых запросов.
* **Групповые операции** - Поддерживает групповую вставку данных для эффективной вставки данных.
* **Управление таблицами** - Позволяет проверять существование таблицы, создавать таблицы с указанными столбцами и типами данных, а также удалять или очищать таблицы.

## Использование

### 1. Импортируйте и инициализируйте класс **AsyncSQLite**:
```py
import asyncsqlite

async def main():
    async with asyncsqlite.AsyncSQLite("my_database.db") as db:
        # Выполняйте операции с базой данных здесь
        pass

if __name__ == "__main__":
    asyncio.run(main())
```
### 2. Выполняйте запросы:

* `await db.execute(query, params=None)`: Выполняет запрос (без извлечения результатов).
* `await db.fetchall(query, params=None)`: Извлекает все строки из запроса и возвращает их в виде списка словарей.
* `await db.fetchone(query, params=None)`: Извлекает первую строку из запроса и возвращает ее в виде словаря.

### 3. Вставляйте данные:

* `await db.insert(table, values)`: Вставляет одну строку в таблицу.
* `await db.bulk_insert(table, columns, values)`: Эффективно вставляет несколько строк данных.

### 4. Обновляйте и удаляйте данные:

* `await db.update(table, values, where, params)`: Обновляет строки в таблице.
* `await db.delete(table, where, params)`: Удаляет строки из таблицы.

### 5. Управление транзакциями:

* `await db.transaction(queries)`: Выполняет список запросов в одной транзакции с автоматическими повторными попытками при возникновении ошибок.

### 6. Управление таблицами:

* `await db.table_exists(table_name)`: Проверяет, существует ли таблица.
* `await db.create_table(table_name, columns)`: Создает новую таблицу с указанными столбцами.
* `await db.drop_table(table_name)`: Удаляет существующую таблицу.
* `await db.clear_table(table_name)`: Очищает все данные из таблицы.

## Конфигурация (опционально)

* `max_workers (int, по умолчанию 10)`: Максимальное количество рабочих в пуле потоков.
* `initial_pool_size (int, по умолчанию 5)`: Начальный размер пула соединений.
* `max_pool_size (int, по умолчанию 20)`: Максимальный размер пула соединений.
* `retry_attempts (int, по умолчанию 3)`: Максимальное количество попыток повтора для транзакций при возникновении ошибок.

## Дополнительные примечания

* Рекомендуется использовать асинхронный менеджер контекста (async with) для автоматического управления пулом соединений.
* Кэш запросов можно отключить, установив self._query_cache = {} в конструкторе.

## Вклад

Мы приветствуем ваш вклад в улучшение AsyncSQLite! Не стесняйтесь отправлять запросы на слияние или сообщать о проблемах в репозитории проекта (ссылка будет предоставлена при наличии).
