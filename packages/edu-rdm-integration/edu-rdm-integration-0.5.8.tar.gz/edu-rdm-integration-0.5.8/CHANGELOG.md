# История изменений

Все изменения проекта должны быть отражены в этом файле.

Формат основан на [Keep a Changelog](http://keepachangelog.com/)
и проект следует [Семантическому версионированию](http://semver.org/).

## [x.y.z] - гггг-мм-дд

Здесь должно быть расширенное описание того, что было сделано, какие есть планы у команды по дальнейшему развитию.
Желательно будущие цели привязывать к конкретным задачам. Т.е. на каждую цель нужно поставить отдельную задачу и
отразить ее номер здесь.

### Добавлено

- [ПРОЕКТ-ZZZZ](https://jira.bars.group/browse/ПРОЕКТ-ZZZZ)
  PATCH Название задачи или изменения.

- [ПРОЕКТ-YYYY](https://jira.bars.group/browse/ПРОЕКТ-YYYY)
  MINOR Название задачи или изменения.

- [ПРОЕКТ-XXXX](https://jira.bars.group/browse/ПРОЕКТ-XXXX)
  MAJOR Название задачи или изменения.

### Изменено

### Исправлено

### Удалено


## [0.5.8] - 2023-09-13

Исправлена ошибка добавления в описание асинхронной задачи списка выгруженных сущностей 
BaseExportLatestEntitiesData._set_description_to_async_task.

### Исправлено

- [EDUSCHL-20334](https://jira.bars.group/browse/EDUSCHL-20334)
  PATCH - Баг с обновлением поля description в BaseExportLatestEntitiesData._set_description_to_async_task.

## [0.5.7] - 2023-09-12

Баг фикс и дополнение поведения BaseExportLatestEntitiesData.

### Изменено

- [EDUSCHL-20435](https://jira.bars.group/browse/EDUSCHL-20435)
  PATCH - BaseExportLatestEntitiesData теперь поддерживает выгрузку ни разу невыгруженных сущностей.

### Исправлено

- [EDUSCHL-20435](https://jira.bars.group/browse/EDUSCHL-20435)
  PATCH - Баг с условием в фильтре в BaseExportLatestEntitiesData._update_model_modified_field.


## [0.5.6] - 2023-09-06

Доработаны классы BaseExportLatestEntitiesData и BaseExportEntitiesData.

### Исправлено

- [EDUSCHL-20435](https://jira.bars.group/browse/EDUSCHL-20435)
  PATCH - Исправлено нахождение левой границы в классе ExportLatestEntitiesData;
        - Добавлена проверка на наличие запущенных или готовых к выгрузке сущностей;
        - Добавлен параметр update_modified, который обновляет поле modified у собранных моделей, 
          чтобы выгрузить невыгруженные записи. 


## [0.5.5] - 2023-09-04

Добавление pip в зависимости сборки пакета.

### Добавлено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  PATCH Добавление pip в зависимости сборки пакета.


## [0.5.4] - 2023-09-04

split_by_days_count переименовал в split_by_quantity.

### Изменено

- [EDUSCHL-20302](https://jira.bars.group/browse/EDUSCHL-20302)
  PATCH split_by_days_count переименовал в split_by_quantity.


## [0.5.3] - 2023-09-03

Изменены параметры формирования подпериодов в generate_first_collect_models_data_script.

### Изменено

- [EDUSCHL-20302](https://jira.bars.group/browse/EDUSCHL-20302)
  PATCH Изменены параметры формирования подпериодов в generate_first_collect_models_data_script.


## [0.5.2] - 2023-08-28

Замена базового класса функций.

### Изменено

- [EDUSCHL-20344](https://jira.bars.group/browse/EDUSCHL-20344)
  PATCH Замена базового класса функций на WebEduLazySavingPredefinedQueueFunction.


## [0.5.1] - 2023-08-22

Для BaseFirstCollectModelsDataCommandsGenerator добавлено условие - если не заполнен creating_trigger_models,
то словарь с данными для команды не передается.

### Исправлено

- [EDUSCHL-20227](https://jira.bars.group/browse/EDUSCHL-20227)
  PATCH Если у сущности не заполнен creating_trigger_models, то в генераторе BaseFirstCollectModelsDataCommandsGenerator
  не формируется словарь с параметрами для команды.
  
- [EDUSCHL-20229](https://jira.bars.group/browse/EDUSCHL-20229)
  PATCH Если у сущности не заполнен creating_trigger_models, то в генераторе BaseFirstCollectModelsDataCommandsGenerator
  не формируется словарь с параметрами для команды.


## [0.5.0] - 2023-08-19
 
Дополнительная функциональность WebEduEntityValueCache была перенесена в EntityCache в function_tools.

### Удалено

- [EDUSCHL-20277](https://jira.bars.group/browse/EDUSCHL-20277)
  MINOR Удален WebEduEntityValueCache.

- [EDUSCHL-20277](https://jira.bars.group/browse/EDUSCHL-20277)
  MINOR Удален WebEduEntityCacheExtended.


## [0.4.7] - 2023-08-17

Изменено формирование очередности сбора/экспорта моделей/сущностей. Вместо отдельных перечислений используется существующее поле `order_number` модели-перечисления `TitledModelEnum`. В случае, когда `order_number` не указан, т.е. будет использоваться значение по умолчанию `DEFAULT_ORDER_NUMBER`, модель/сущность будет исключена из сбора/экспорта.

### Изменено

- [EDUSCHL-19164](https://jira.bars.group/browse/EDUSCHL-19164)
  MINOR Изменено формирование очередности сбора/экспорта моделей/сущностей.

## [0.4.6] - 2023-08-16

Удален лишний вызов метода _prepare_logs

### Исправлено

- [EDUSCHL-19991](https://jira.bars.group/browse/EDUSCHL-19991)
  PATCH удален лишний вызов метода ```_prepare_logs``` в методе  ```__init__``` класса ```BaseCollectingCalculatedExportedDataFunctionCacheStorage```

## [0.4.5] - 2023-08-09

Объединение обрабатываемых логов относящихся к одному объекту

### Добавлено

- [EDUSCHL-19991](https://jira.bars.group/browse/EDUSCHL-19991)
 PATCH Новый миксин ```ReformatLogsMixin``` , новое поле is_merge_logs и новый метод _merge_logs у класса ```BaseCollectingExportedDataFunctionCacheStorage```

## [0.4.4] - 2023-08-12

Исправлен баг с timedelta

### Исправлено

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  PATCH Исправлен баг с timedelta.

## [0.4.3] - 2023-08-12

Исправлен баг с timedelta

### Исправлено

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  PATCH Исправлен баг с timedelta.

## [0.4.2] - 2023-08-11

Исправление ошибки учета миллисекунд, при генерации скриптов сбора и выгрузки данных. В текущий момент chunk_size все
равно работает некорректно. Это связано с тем, что при обнулении миллисекунд за одной записью выборки может скрываться
большое количество, например, которые были созданы или обновлены скриптами. Проблему необходимо решить в будущем, но
текущего решения хватает для эксплуатации.
В выборках моделей и логов не должна входить правая граница периода выборки.

### Исправлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Исправлена ошибка учета миллисекунд в выборках при генерации скриптов с командами для сбора и выгрузки данных.

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH В выборках моделей и логов не должна входить правая граница периода выборки.

## [0.4.1] - 2023-08-09

Доработки для реализации принудительного выполнения функций экспорта данных сущностей.

### Добавлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Доработки для реализации принудительного выполнения функций экспорта данных сущностей.

## [0.4.0] - 2023-08-09

Реализованы общие классы для команд сбора/экспорта.

### Добавлено

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  MINOR Добавлены общие модели, методы и классы.

### Изменено

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  MINOR Реализованы общие классы для команд сбора/экспорта.

## [0.3.3] - 2023-08-08

Добавлено принудительное выполнение функций в ранере для экономии памяти.

### Исправлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Добавлено принудительное выполнение функций в ранере для экономии памяти.

## [0.3.2] - 2023-08-08

Откат к спискам необработанных логов. Исправлена ошибка бесконечного создания чанков логов.

### Исправлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Откат к спискам необработанных логов.

## [0.3.1] - 2023-08-08

Организована передача необработанных логов в виде генератора.

### Изменено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Организована передача необработанных логов в виде генератора.

## [0.3.0] - 2023-08-06

Добавление функциональности для отложенного заполнения кешей. Заполнение производится перед началом работы запускаемого
объекта.

### Добавлено

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  PATCH Добавлено отложенное заполнение кешей хелперов функций.

- [EDUSCHL-20235](https://jira.bars.group/browse/EDUSCHL-20235)
  MINOR Добавлено проставление подэтапа выгрузки данных у записей моделей.

## [0.2.2] - 2023-08-06

Для API РВД добавлена поддержка параметра типа операции для загрузки данных.

### Добавлено

- [EDUSCHL-19920](https://jira.bars.group/browse/EDUSCHL-19920)
  PATCH Для API РВД добавлена поддержка параметра типа операции для загрузки данных.

## [0.2.1] - 2023-08-05

Восстановление сборки пакета после ухода с poetry.

### Исправлено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  PATCH Восстановление сборки пакета после миграции с poetry.

## [0.2.0] - 2023-08-04

Перенос стратегий формирования Функций используемых в генерации исходников.

### Добавлено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  MINOR Перенесены стратегии создания Функций из ЭШ.

## [0.1.4] - 2023-08-03

Возвращение ранее удаленных зависимостей миграции

### Изменено

- [EDUSCHL-20209](https://jira.bars.group/browse/EDUSCHL-20209)
  PATCH Возвращение зависимостей миграции.

- [EDUSCHL-20209](https://jira.bars.group/browse/EDUSCHL-20209)
  PATCH Доработки по формированию документации.

- [EDUSCHL-20200](https://jira.bars.group/browse/EDUSCHL-20200)
  Закреплены версии зависимостей, добавлена ссылка на uploader-client

## [0.1.3] - 2023-07-24

Для раскатки миграций на ЭШ, пришлось закомментировать зависимости в initial-миграции.

### Изменено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  PATCH Вынести общую часть для работы с РВД из ЭШ для использования в ЭК.

## [0.1.2] - 2023-07-23

Внесены изменения в кодовую базу после переноса механизма логирования из ЭШ в educommon.

### Изменено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  PATCH Вынести общую часть для работы с РВД из ЭШ для использования в ЭК.

## [0.1.0] - 2023-07-18

Внесены изменения в кодовую базу после переноса механизма логирования из ЭШ в educommon.

### Добавлено

- [EDUSCHL-19919](https://jira.bars.group/browse/EDUSCHL-19919)
  MINOR Перенос базовых компонентов интеграции с РВД из ЭШ.
