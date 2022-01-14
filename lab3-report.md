# Лабораторная работа №3
> Цель работы: Поиск и устранение XSS уязвимостей.
> Исходный текст задания: https://github.com/SergeyMirvoda/secure-web-development-21/blob/main/lab3.md

## Выполнение
Те, кто делает лабораторную на своём языке программирования, должны сначала восстановить в точности этот пример
> Выбран язык программирования Python 3.8

## Задание 1
**7.** Войти на сайт и увидеть список книг и авторов

> Исходный код сайта: https://github.com/Tyz3/WebApp/commit/3c4acafdac5f124555d6ba72fe0508ad0f2d2765
> 
![image](https://user-images.githubusercontent.com/21179689/146647887-e0d00329-8b54-4b25-81b9-8dee6b0e85c3.png)


**8.** На странице со списком книг найти

**8.1** Reflected XSS в поиске книг

На странице /books есть поле с выводом имени пользователя, через которого осуществлёна авторизация на сайте. После успешной авторизации, создано поле в хранилище куки со значением имени пользователя в "чистом виде", изменим значение, добавив нужный нам код, например, ``<img src=1 onerror="javascript:alert('Ref XSS')"/>``.

![image](https://user-images.githubusercontent.com/21179689/146649197-d03b9036-ffa4-4bf6-b3fb-90b1f27ff937.png)

Исправление уязвимости: Нужно добавить фильтрацию на специальные символы HTML, чтобы подставленные теги не интерпретировались браузером.

![image](https://user-images.githubusercontent.com/21179689/146649922-4904cbdc-cbac-42bb-b7d6-36cf29b102fc.png)
![image](https://user-images.githubusercontent.com/21179689/146649480-059fdca9-1a31-4a28-a5a0-59b49351b6ed.png)
**Ссылка на исправление**: https://github.com/Tyz3/WebApp/blob/072fa39ca0a399869c649ee99a62c5ffde2a02c7/views/booklist.pug#L44-L45


**8.2** Persisted (Stored) XSS при создании книги и отображении списка книг

На странице /books в форме добавления книги укажем название книги следующим образом: ``Action in <b>Redisка</b>``.

![image](https://user-images.githubusercontent.com/21179689/146648531-27eda928-7870-432a-a357-1116acd4cc9e.png)

и нажмём кнопку **Добавить**.
![image](https://user-images.githubusercontent.com/21179689/146648551-7d2bbfe0-7397-4ff0-8527-6e2798a36fa3.png)

Исправление уязвимости: аналогичным образом что и в Reflected XSS поменяем способ форматирования подстановочных данных в шаблон .pug.

![image](https://user-images.githubusercontent.com/21179689/146648674-d5ed7d3a-885a-44c1-bec8-819fef9f7f5f.png)

**Ссылка на исправление**: https://github.com/Tyz3/WebApp/blob/072fa39ca0a399869c649ee99a62c5ffde2a02c7/views/booklist.pug#L29


**8.3** Потенциальную уязвимость через Cookie Injection

Возможность изменить аккаунт входа на сайт, с помощью изменения куки через DevTools (F12).

![image](https://user-images.githubusercontent.com/21179689/146648898-1b0881ea-ef0d-4077-a8d9-8cf1c883944c.png)

Возможное исправление: добавление в приложение сессионных ID


**8.4** Некорректное создание сессионной cookie, которое приводит к захвату сессии (Session hijacking)

Чтобы не дать возможность злоумышленнику похитить куки, например, через Stored XSS, нужно запретить JS доступ к document.cookie для дальнейшей отправки их куда-либо.
Для этого в куки есть параметр **httpOnly**, добавим этот параметр в куки при авторизации.

![image](https://user-images.githubusercontent.com/21179689/146649861-7be2f6ce-162a-499b-8f02-206f21e8dde8.png)

**Ссылка на исправление**: https://github.com/Tyz3/WebApp/blob/072fa39ca0a399869c649ee99a62c5ffde2a02c7/server.py#L74


Результат (коммит с исправлениями): https://github.com/Tyz3/WebApp/commit/fdc80e23c4d3c9ca1c833826a21183a2720e54aa
