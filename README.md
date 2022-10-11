# Публикация комиксов

Проект написан с целью публикаций комиксов с сайта [xkcd.com](https://xkcd.com/) в группе сайта [vk.com](https://vk.com/).

## Создаём группу и приложение на сайте [vk.com](https://vk.com/)
Авторизуйтесь/зарегистрируйтесь в [vk.com](https://vk.com/).

Создайте группу по ссылке [vk.com.groups](https://vk.com/groups?tab=admin).

Создайте приложение [dev.vk.com](https://dev.vk.com/). В качестве типа приложения следует указать `standalone` — это подходящий тип для приложений, которые просто запускаются на компьютере.

## Получаем нужные ключи/токены
В настройках созданного приложения найдите `ID приложения`. Он вам понадобится для получения `личного ключа`. 

С помощью данной процедуры [implicit-flow](https://dev.vk.com/api/access-token/implicit-flow-user) вы получите тот самый ключ. Выполните данные условия:
* Убрать параметр redirect_uri у запроса на ключ
* В параметре scope указать через запятую данные права: photos, groups, wall и offline, вот так: scope=photos,groups,wall,offline.

У вас получиться такая строка, но только вместо client_id=`1` подставить `ID` своего приложения.
```
https://oauth.vk.com/authorize?client_id=1&display=page&scope=photos,groups,wall,offline&response_type=token&v=5.131&state=123456
```
Передаём её в адресную строку браузера, разрешаем доступ приложения к нашему аккаунту и получаем ответ:
```
https://oauth.vk.com/blank.html#access_token=vk1.a.Qg5KUJbNlVtk8e4l0tf12Q5n-sv01CiuKox04yxxsCIlrsO2V9aZkWo_IxoB2YjcEJuuNVG2QyrGchqpKRY7BdsHlumFQ4D4OyZSHitA52NEDnVDKbGQRnEmF_p7O31Rt5MYPByb0y3qaJe8Auc6IT9fvbu-sKGcN2XcuvaKu1fDsDdAdUd1nlNUdV&expires_in=0&user_id=1&state=123456
```
Копируем только значение нашего `access_token`, исключая `&expires_in=0&user_id=1&state=123456`. Получится ключ вида:
```
vk1.a.Qg5KUJbNlVtk8e4l0tf12Q5n-sv01CiuKox04yxxsCIlrsO2V9aZkWo_IxoB2YjcEJuuNVG2QyrGchqpKRY7BdsHlumFQ4D4OyZSHitA52NEDnVDKbGQRnEmF_p7O31Rt5MYPByb0y3qaJe8Auc6IT9fvbu-sKGcN2XcuvaKu1fDsDdAdUd1nlNUdV
```
Сохраняем ключ в коревой директории проекта в файле `.env` под именем `COMICS_ACCESS_TOKEN=`

Также в `.env` потребуется записать `id` нашей группы. Чтобы его получить можно воспользоваться сайтом [regvk.com](https://regvk.com/id/). Сохраняем его под именем `COMICS_GROUP_ID=`

## Как установить

Для запуска проекта понадобится Python3. Устанавливаем необходимые сторонние библиотеки:
```
pip install -r requirements.txt
```
Запускаем скрипт:
```
python main.py
```
Скрипт будет публиковать посты с комиксами один раз в сутки.