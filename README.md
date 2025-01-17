# Тестовое задание для Infotecs

Приложение на FastApi для просмотра погоды

---

## Установка

Запустить скрипт, как сказано в условиях задания
```bash
python script.py
```
Скрипт создаст виртуально окружение, если его нет и активирует. Потом уставновит все зависимости из файла requrements.txt и запустит сервер uvicorn на localhost:8000

## Альтернативная установка (не из архива)
Загрузить проект с гитхаба 
```bash
git clone https://github.com/ISSSSA/weather_api.git
cd weather_api
python script.py
```
## Запуск тестов
Для запуска тестов надо выполнить следующие команды
```bash
cd test
pytest tests.py 
```

## Описание endpoints
**_Важно!!!! Для упрощения проверки задания я прикрепил OpenAPI документацию, которая после запуска сервера доступна по адресу localhost:8000/docs_**

Так вернемся к нашим эндпоинтам:  
* /register - для создания пользователя по username, как указано в задании, я как понял из заданий, полноценная регистарция не нужна (подробнее смотрите в документации)
* /weather - для получения погоды по координатам (подробнее смотрите в документации)
* /city - для добавления юзеру города по координатам (подробнее смотрите в документации)
* /cities - города по user_id (подробнее смотрите в документации)
* /weather_at_time - погода среди добавленных для юзера городов, по времени (подробнее смотрите в документации)
* /docs - документация OpenAPI, настоятельно прошу воспользоваться для вашего же удобства
* /redoc - тоже документация
Обновляется, вся погода хранящаяся в БД каждые 15 минут

## О задании
Задание интересное и не тяжелое, но местами была не понятна формулировка, например про форму отправки ответа, я до сих пор не уверен, что правильно его предоставил. Думал вообще Отправить просто скрипт, который бы подтягивал все с моего Гитахаба.

## Заключение
Спасибо большое, за уделенное время, очень надеюсь на продолжение диалога, и всего хорошего!!!