# Telegram_bot

Телеграмм-бот предназначен для поиска вакансий по специальности Data Scientist на сайте hh.ru.

1. На вход принимает от пользователя следующие параметры: желаемые опыт работы, размер зарплаты, график работы, город.
![parameters](/images/telebot.PNG)
2. Выдает первые 5 вакансий, удовлетворяющих заданным параметрам, с ссылкой на страницу вакансии на hh.ru.
![parameters](/images/telebot2.PNG)
3. В случае если подходящих вакансий нет, предлагает искать снова.

Для реализации проекта использовался HeadHunter API- https://api.hh.ru/.
Бот запущен на Heroku. 
