# Проект "Интеграция с Региональной витриной данных"

## Описание концепции

## Принцип работы

## Требования к окружению

## Разворачивание

## Параметры конфигурационного файла


В разных проектах существуют различные способы добавления настроек, где-то через плагины, где-то напрямую в settings.py.
Будет рассмотрен подход указания настроек в settings.py и указания параметров в конфигурационном файле.

Для возможности конфигурирования необходимо проделать ряд действий. В settings.py нужно добавить:

- Определение значений по умолчанию настроек:
    ```
    PROJECT_DEFAULT_CONFIG.update({
        # Настройки РВД
        ('rdm_general', 'EXPORT_ENTITY_ID_PREFIX'): '', # Дефолтное значение нужно изменить на специфическое системе
        ('rdm_general', 'COLLECT_CHUNK_SIZE'): 500,
        ('rdm_general', 'EXPORT_CHUNK_SIZE'): 500,
        ('rdm_transfer_task', 'MINUTE'): '0',
        ('rdm_transfer_task', 'HOUR'): '*/4',
        ('rdm_transfer_task', 'TRANSFER_TASK_DAY_OF_WEEK'): '*',
        ('rdm_transfer_task', 'TIMEDELTA'): 3600,
        ('rdm_upload_status_task', 'MINUTE'): '*/30',
        ('rdm_upload_status_task', 'HOUR'): '*',
        ('rdm_upload_status_task', 'DAY_OF_WEEK'): '*',
        ('uploader_client', 'URL'): 'http://localhost:8090',
        ('uploader_client', 'DATAMART_NAME'): '',
        ('uploader_client', 'REQUEST_RETRIES'): 10,
        ('uploader_client', 'REQUEST_TIMEOUT'): 10,
        ('uploader_client', 'ENABLE_REQUEST_EMULATION'): False,
    })
    ```
- Получение значений настроек из конфигурационного файла:

    ```
    # Ссылка на каталог с файлами для загрузки
    UPLOADS = 'uploads'
  
    # =============================================================================
    # Интеграция с Региональной витриной данных (РВД)
    # =============================================================================
    
    # Префикс идентификаторов записей сущностей специфический для продукта
    RDM_EXPORT_ENTITY_ID_PREFIX = conf.get('rdm_general', 'EXPORT_ENTITY_ID_PREFIX') 
  
    # Количество записей моделей ЭШ обрабатываемых за одну итерацию сбора данных
    RDM_COLLECT_CHUNK_SIZE = conf.get_int('rdm_general', 'COLLECT_CHUNK_SIZE')
    
    # Количество записей моделей обрабатываемых за одну итерацию экспорта данных
    RDM_EXPORT_CHUNK_SIZE = conf.get_int('rdm_general', 'EXPORT_CHUNK_SIZE')
    
    # Настройка запуска периодической задачи выгрузки данных:
    RDM_TRANSFER_TASK_MINUTE = conf.get('rdm_transfer_task', 'MINUTE')
    RDM_TRANSFER_TASK_HOUR = conf.get('rdm_transfer_task', 'HOUR')
    RDM_TRANSFER_TASK_DAY_OF_WEEK = conf.get('rdm_transfer_task', 'DAY_OF_WEEK')
    RDM_TRANSFER_TASK_TIMEDELTA = conf.get_int('rdm_transfer_task', 'TIMEDELTA')
    
    # Настройка запуска периодической задачи статуса загрузки данных в витрину:
    RDM_UPLOAD_STATUS_TASK_MINUTE = conf.get('rdm_upload_status_task', 'MINUTE')
    RDM_UPLOAD_STATUS_TASK_HOUR = conf.get('rdm_upload_status_task', 'HOUR')
    RDM_UPLOAD_STATUS_TASK_DAY_OF_WEEK = conf.get('rdm_upload_status_task', 'DAY_OF_WEEK')
    
    # Загрузка данных в Региональную витрину данных (РВД)
    # Адрес витрины (schema://host:port)
    RDM_UPLOADER_CLIENT_URL = conf.get('uploader_client', 'URL')
    
    # Мнемоника Витрины
    RDM_UPLOADER_CLIENT_DATAMART_NAME = conf.get('uploader_client', 'DATAMART_NAME')
    
    # Количество повторных попыток запроса
    RDM_UPLOADER_CLIENT_REQUEST_RETRIES = conf.get_int('uploader_client', 'REQUEST_RETRIES')
    
    # Таймаут запроса, сек
    RDM_UPLOADER_CLIENT_REQUEST_TIMEOUT = conf.get_int('uploader_client', 'REQUEST_TIMEOUT')
    
    # Включить эмуляцию отправки запросов
    RDM_UPLOADER_CLIENT_ENABLE_REQUEST_EMULATION = conf.get_bool('uploader_client', 'ENABLE_REQUEST_EMULATION')
    
    ```

В дефолтный конфиг проекта необходимо добавить:

```
# Общие настройки интеграции с РВД
[rmd_general]
# Префикс идентификаторов записей сущностей специфический для продукта. Указывается в settings.py и не должен 
# изменяться. Возможность изменения через конфигурационный файл оставлена для экстренных случаев.
# EXPORT_ENTITY_ID_PREFIX = 
# Количество записей моделей обрабатываемых за одну итерацию экспорта данных
EXPORT_CHUNK_SIZE = 500
# Количество записей моделей ЭШ обрабатываемых за одну итерацию сбора данных
COLLECT_CHUNK_SIZE = 500

# Настройка запуска периодической задачи выгрузки данных
[rdm_transfer_task]
MINUTE=*/2
HOUR=*
DAY_OF_WEEK=*
# Дельта между прошлым и текущим запуском, сек
TIMEDELTA=120

# Настройка запуска периодической задачи статуса загрузки данных в витрину
[rdm_upload_status_task]
MINUTE=*/2
HOUR=*
DAY_OF_WEEK=*

[uploader_client]
# Адрес витрины
URL = http://localhost:8090
# Мнемоника Витрины
DATAMART_NAME = test
# Количество повторных попыток запроса
REQUEST_RETRIES = 10
# Таймаут запроса, сек
REQUEST_TIMEOUT = 10
# Включить эмуляцию отправки запросов
ENABLE_REQUEST_EMULATION = True
```

На основе дефолтного конфига произвести конфигурирование приложений.

Перечень настроек в settings.py указан в таблице ниже.

| Название настройки в settings                | Описание                                                                                                                           | Значение по умолчанию   |
|----------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|-------------------------|
| UPLOADS                                      | Основная директория в MEDIA, в которой будет создана директория edu_rdm_integration  для сохранения файлов для дальнейшей выгрузки | 500                     |
| RDM_COLLECT_CHUNK_SIZE                       | Количество записей моделей обрабатываемых за одну итерацию сбора данных                                                            | 500                     |
| RDM_EXPORT_CHUNK_SIZE                        | Количество записей моделей обрабатываемых за одну итерацию экспорта                                                                | 500                     |
| RDM_UPLOADER_CLIENT_URL                      | Адрес витрины (schema://host:port)                                                                                                 | 'http://localhost:8090' |
| RDM_UPLOADER_CLIENT_DATAMART_NAME            | Мнемоника Витрины                                                                                                                  | 'test'                  |
| RDM_UPLOADER_CLIENT_REQUEST_RETRIES          | Количество повторных попыток запроса                                                                                               | 10                      |
| RDM_UPLOADER_CLIENT_REQUEST_TIMEOUT          | Таймаут запроса, сек                                                                                                               | 10                      |
| RDM_UPLOADER_CLIENT_ENABLE_REQUEST_EMULATION | Включить эмуляцию отправки запросов                                                                                                | True                    |
| RDM_TRANSFER_TASK_MINUTE                     | Настройка запуска периодической задачи выгрузки данных. Минута                                                                     | '0'                     |
| RDM_TRANSFER_TASK_HOUR                       | Настройка запуска периодической задачи выгрузки данных. Час                                                                        | '*/4'                   |
| RDM_TRANSFER_TASK_DAY_OF_WEEK                | Настройка запуска периодической задачи выгрузки данных. День недели                                                                | '*'                     |
| RDM_TRANSFER_TASK_TIMEDELTA                  | Дельта между предыдущим и следующим запуском периодической задачи в секундах                                                       | 3600                    |
| RDM_UPLOAD_STATUS_TASK_MINUTE                | Настройка запуска периодической задачи статуса загрузки данных в витрину. Минута                                                   | '*/30'                  |
| RDM_UPLOAD_STATUS_TASK_HOUR                  | Настройка запуска периодической задачи статуса загрузки данных в витрину. Час                                                      | '*'                     |
| RDM_UPLOAD_STATUS_TASK_DAY_OF_WEEK           | Настройка запуска периодической задачи статуса загрузки данных в витрину. День недели                                              | '*'                     |


## Сборка и распространение

## Инструкция для разработчика

## Настройка PyCharm для работы

## Запуск в системе

## Запуск в контейнере

## Правила внесения изменений
