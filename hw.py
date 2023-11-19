import redis
from redis_lru import RedisLRU
from models import Author, Quote

client = redis.StrictRedis(host="localhost", port=6379, password=None)
cache = RedisLRU(client)

@cache
def find_by_tag(tag: str) -> list[str | None]:
    print(f"Find by tag: {tag}")
    quotes = Quote.objects(tags__icontains=tag)
    result = [q.quote for q in quotes]
    return result

@cache
def find_by_author(author: str) -> list[str | None]:
    print(f"Find by author: {author}")
    authors = Author.objects(fullname__icontains=author)
    result = {}
    for a in authors:
        quotes = Quote.objects(author=a)
        result[a.fullname] = [q.quote for q in quotes]
    return result

def process_command(command: str):
    parts = command.split(':')
    if len(parts) != 2:
        print("Невірний формат команди. Спробуйте знову.")
        return

    field, value = parts[0].strip(), parts[1].strip()

    if field == 'name':
        result = find_by_author(value)
        print(result)

    elif field == 'tag':
        result = find_by_tag(value)
        print(result)

    elif field == 'tags':
        tag_list = value.split(',')
        result = {}
        for tag in tag_list:
            result[tag] = find_by_tag(tag)
        print(result)

    elif field == 'exit':
        print("Завершення виконання скрипту.")
        exit()

    else:
        print("Невідоме поле. Спробуйте знову.")

if __name__ == "__main__":
    while True:
        command = input("Введіть команду (наприклад, name: Steve Martin): ").strip()
        process_command(command)
