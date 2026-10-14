# ANCAP — задание для Cursor: завершение подготовки к инвестору

Повторная проверка локализованной версии: production frontend build успешен, Vitest 6/6, Playwright 8/8, защита демо-БД 6/6. Сохранённый receipt проверен; live-демо и API smoke в этой проверке повторно не запускались. Поиск provider credentials, закончившийся ошибкой, не подтверждает отсутствие ключа — production-конфигурацию проверять отдельно без вывода секретов.

Проверка последней волны (2026-10-14): локализованные данные присутствуют для всех 32 офферов на пяти языках (Vitest 6/6). Сохранённые доказательства подтверждают локальное Ollama-исполнение без fallback и списание 14 тестовых ACP; архив с контрольными суммами: `docs/investors/evidence/2026-10-14-local-ollama/`. Базовый SHA демо относится к незакоммиченному рабочему дереву; новая версия скрипта фиксирует хеши исполняемых исходников, строго ограничивает локальную одноразовую БД и сохраняет каждый запуск в отдельную папку. Проверки защиты БД 6/6 выполняются без доступа к БД. Готовность production-провайдера и наличие клиентских продаж этим демо не подтверждены.

Дата: 2026-10-14.  
Обновление прогресса: 2026-10-14 (после `ddb8785`; локализация offers/budget/demo + live LLM demo).

## Что уже изменено в локальном проекте

- Главная объясняет модель «клиент покупает результат → workflow выполняется → выдаётся материал и квитанция».
- Публичное меню: Workflows, Направления, Авторам, Разработчикам, Инвесторам. Кошелёк, мост, инфраструктура и доказательства исполнения находятся на втором уровне.
- `/projects` объединяет проекты в шесть направлений и показывает создаваемые документы вместо заявления о завершении всего roadmap.
- `/investors` содержит описание модели заработка, продуктовые доказательства, стадию и этапы финансирования; ссылки на бюджет и демо-сценарий.
- Каталог группирует workflow по направлениям и поддерживает поиск.
- Каталог по умолчанию показывает начальный коммерческий фокус; остальные направления доступны через фильтр. Fallback backend-каталога отмечается явно.
- Первые экраны AETERNA, Cryo, Saliva Rx, Galaxy, Lunar и Stardust переосмыслены как AI-брифы; на всех страницах портфеля баннер показывает цепочку покупатель → задача → входы → AI-результат → ограничения → оплата → квитанция (`projectOffers.ts`).
- Новости и погода ограничены соответствующими страницами, анимация фона отключена на главной, портфеле и странице инвестора.
- Основная подача переведена на EN/RU/UK/DE/繁中; `projectOffers` + `/docs/investors/budget-12m` + `/docs/investors/demo-5min` локализованы (EN/RU/UK/DE/zh-Hant).
- Демо на 5 минут: `docs/investors/DEMO_SCRIPT_5MIN.md` + `/docs/investors/demo-5min`.
- Бюджет 12 месяцев (допущения): `docs/investors/BUDGET_12M_ASSUMPTIONS.md` + `/docs/investors/budget-12m`. Сценарии затрат с резервом 15–20%: lean **€129,950–€247,920**, standard **€277,265–€539,760**. Это непроверенные допущения, не окончательная сумма привлечения.
- Smoke платного пути (тестовый ledger, без Stripe/broadcast): `tests/api/test_investor_paid_path_smoke.py`.

## Статус пунктов задания

| # | Пункт | Статус |
| --- | --- | --- |
| 1 | Главная / projects / investors / workflows, 5 языков | [x] презентационная проверка; повторный Playwright после изменений |
| 2 | Цепочка buyer→receipt на страницах портфеля | [x] `projectOffers` + баннер `ProjectWorkflowContext` |
| 3 | Сверка slug с backend-каталогом | [x] тест `test_portfolio_offer_slugs_exist_in_workflow_catalog` |
| 4 | Полный платный путь на тестовой среде + smoke | [x] credits smoke + **live LLM** (`fallback_used=false`, ollama staging) на одноразовой БД |
| 5 | Демо 5 минут | [x] |
| 6 | Инвесторский пакет по фактам | [~] `/investors` + бюджет; выручка/клиенты **не предоставлены владельцем** |
| 7 | Бюджет 12 месяцев → сумма привлечения | [x] допущения EUR; владелец должен подтвердить юрисдикцию и котировки |
| 8 | Проверки, roadmap, отдельные коммиты | [~] WIP кошелька/bridge/SACP **не включался** |

## Проверки выполненной презентационной части

- `npm run build` — успешно на волне `2da45fc`; повтор при необходимости после офер-баннера.
- `npx vitest run src/lib/__tests__/solutionPortfolio.test.ts` — portfolio + offer-chain.
- Playwright `e2e/investor-presentation.spec.ts` — языки, портфель, фильтры, research heroes, light theme, ссылки budget/demo.
- `pytest tests/api/test_investor_paid_path_smoke.py -q` — register → pay (credits) → execute → receipt + platform fee.
- Скриншоты: `tmp/investor-preview-2026-10-14/` (локальная презентация, не production proof).

## Зависимости для платного demo на test env

1. Backend test client / local API with ledger deposit enabled.
2. Workflow templates in-process (`WORKFLOW_TEMPLATES`) — no external LLM required for degraded/fallback path; live LLM optional.
3. **Not required / do not use without approval:** Stripe live keys, ACP chain broadcast, production DB.

## Что требуется от владельца перед отправкой инвестору

1. Страна оформления компании, статус регистрации, состав команды и права на код.
2. Подтверждённая выручка и оплаченные запуски либо явная стадия до проверки продаж.
3. Бюджет на 12 месяцев: заменить допущения котировками; выбрать состав команды и вычислить сумму запроса из подтверждённых денежных затрат и обоснованного резерва.
4. Проверенная демонстрация реального исполнения на согласованном staging (не только sample report).
5. Независимая проверка финансовых и криптографических компонентов.

Владелец обозначил цель: финансирование для найма сотрудников и открытия фирмы. Сумма и юрисдикция пока не определены. Бюджетный memo задаёт рамку, не готовый term sheet.

## Вставка (исходное задание)

```text
Заверши подготовку существующего ANCAP к демонстрации инвестору.
Сначала прочитай AGENTS.md, MASTER_ROADMAP.md, STATUS.md,
docs/CURSOR_INVESTOR_FINISH_RU.md и git status.

Сохрани весь существующий WIP мобильного кошелька, consensus,
bridge и SACP. Не откатывай и не включай чужие изменения в коммиты.
Не заменяй новую главную и структуру разделов прежней россыпью проектов.
…
```

## Дополнительная проверка после da4f8b7

Повторная проверка: production frontend build успешен, Vitest 4/4, Playwright 8/8. Устранена ошибка nullable pathname в баннере и неоднозначный селектор Receipt в тесте. API smoke не запускался повторно: для него нужна отдельная одноразовая тестовая БД (conftest допускает пересоздание public schema).

- Исправлены арифметические итоги бюджета и число инженеров в lean-сценарии. Промо-кредиты ACP исключены из денежных EUR-итогов; стоимость inference уже предусмотрена отдельной строкой.
- Ссылки предложений ведут прямо на `/ai/run/{slug}` или `/ai/bundles/{slug}` вместо неработающего фильтра `?q=`.
- Smoke-тест допускает `llm_usage.fallback_used=true` и нулевую комиссию; его успех не доказывает живой LLM, фактический доход или продажу клиенту.
- Перед demo зафиксировать SHA, сеть/среду и источник тестовых средств; сохранить фактический artifact и receipt, проверить provider/model/status, отсутствие fallback, движение средств и комиссию.
- Подтверждение реальной выручки, юрисдикция и котировки остаются открытыми. Мультиязычную готовность новых offer-цепочек не считать закрытой по одним переводам подписей полей.

## Дополнение после ddb8785 (локализация + live LLM)

SHA базы для демо-доказательств: `ddb8785fb5c2de6ca854ac083bd024e703efc097` (рабочее дерево поверх SHA содержит локализацию и demo-скрипт до коммита).

| Артефакт | Путь / результат |
| --- | --- |
| Offer copy EN/RU/UK/DE/zh-Hant | `frontend-app/src/lib/projectOffersCopy.ts` + `offerForRoute(path, lang)` |
| Budget / demo pages i18n | `frontend-app/src/locales/investorDocs.ts` |
| Disposable DB | `ancap_investor_demo_20261014` (только тест; не production) |
| API smoke | `pytest tests/api/test_investor_paid_path_smoke.py -q` → **2 passed** на disposable DB |
| Live LLM demo | `scripts/investors/live_llm_paid_path_demo.py` → `tmp/investor-live-llm-20261014/` |
| Live proof | `fallback_used=false`, provider=`ollama`, model=`qwen2.5:3b`, fee=1.4 ACP (10%), credits 50→36 |

Owner still must supply jurisdiction, quotes, and real revenue metrics before investor send. Live demo used **local Ollama staging**, not Teneta/Anthropic production keys.
