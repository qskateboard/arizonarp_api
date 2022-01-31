# arizonarp_api
ArizonaRP Forum API w/o XenForo API keys

Для работы скрипта, необходимо скопировать из браузера юзер агент и полные куки в скрипт. 
Найти их можно, нажав Ctrl+Shift+I, затем перейти во вкладку Network и обновить страницу. В запросах выбрать текущую страницу и там в заголовках будут нужные параметры.

## Пример: 

```python
import api 

user_agent = "Mozilla/5.0..."
cookies = "_ym_uid=162..."
api.setup(user_agent, cookies)
for thread in api.get_threads("https://forum.arizona-rp.com/forums/1583/"):
    print("{} by {}".format(thread['title'], thread['creator']))
```


### Список всех методов: 

- get_categories(url) - Вывести все категории в разделе
- get_category(url) - Вывести название категории
- get_threads(url) - Вывести все темы в разделе
- get_post(url) - Вывести всю информацию по посту
- edit_post(url, html) - Редактирование поста (HTML)
- set_unread(url) - Установить все темы в выбранном разделе прочитанными
- send_message(url, message) - Отправить сообщение в тему (BB Codes)
- get_thread(url) - Вывести название темы и содержание первого поста
- close_thread(url) - Закрыть тему
- pin_thread(url) - Закрепить тему
- make_reaction(url, reaction_id) - Установить реакцию на пост
