# План розробки: Впровадження надійної бази MCP (v2.3.2)

Цей документ фіксує статус, архітектурні вимоги та покроковий план реалізації стандарту **Model Context Protocol (MCP)** і супутніх компонентів стійкості та безпеки в **Locus AI Assistant**.

---

## 🏛️ 4 Стовпи "Надійної бази"

1. **Стандартизована архітектура MCP**:
   - `MCP Host/Client`: Ядро асистента (LLM / процесор), яке формує контекст та ініціює дії.
   - `MCP Gateway (Mediation Layer)`: Централізований диспетчер з'єднань, автентифікації, політик доступу та маршрутизації між клієнтом і багатьма MCP-серверами (Filesystem, Web, System, Custom).
   - `MCP Servers`: Модульні ізольовані провайдери інструментів.

2. **Подолання "MCP Tax" (Tool Attention & Intent Routing)**:
   - Уникнення перевантаження контекстного вікна (>70% веде до галюцинацій та втрати міркувань).
   - Двоетапна активація: легкий Intent Router відбирає лише релевантні сервери/інструменти для поточного завдання перед передачею промпту в основну LLM.

3. **Відмовостійкість та керування виконанням**:
   - **ATBA (Adaptive Timeout Budget Allocation)**: Розподіл глобального ліміту часу завдання між кроками/інструментами з градуальною деградацією.
   - **SERF (Structured Error Recovery Framework)**: Машиночитний формат помилок із підказками відновлення для self-healing агента.

4. **Безпека Zero Trust та ізоляція**:
   - **Sandboxing**: Запуск сторонніх/недовірених MCP-серверів в ізольованих середовищах (Docker / обмежені процеси).
   - **Skill Trust Governance & HITL**: Чотириетапна верифікація довіри з обов'язковим підтвердженням користувача (Human-in-the-Loop) у UI перед деструктивними операціями (запис/видалення/відправка).

---

## 📊 Матриця прогресу

### Статус: В роботі (Гілка `v2.3.2`)

| Етап | Компонент | Статус | Примітки |
| :--- | :--- | :---: | :--- |
| **0** | **Стабілізація бази** | ✅ Виконано | Тести (44/44) пройдено, створено тег `v2.3.1.safe` |
| **1** | **MCP Gateway & Mediation Layer** | ✅ Виконано | Пакет `src/mcp/`, `MCPGateway`, `ServerRegistry`, тести (51/51) пройдено |
| **2** | **ATBA & SERF** | ⏳ Очікує | Адаптивні тайм-аути та структуровані помилки |
| **3** | **Intent Router (Tool Attention)** | ⏳ Очікує | Динамічна фільтрація інструментів для уникнення MCP Tax |
| **4** | **Trust Governance & HITL (UI)** | ⏳ Очікує | Інтеграція підтверджень через WebSocket/FastAPI в React UI |
| **5** | **Sandboxing (Docker / Isolation)** | ⏳ Очікує | Контейнеризація серверів та політики ізоляції |

---

## 📝 Детальний план реалізації (Roadmap)

### Етап 0: Базова фіксація (Завершено)
- [x] Виправлено сумісність `audioop` для нових версій Python у [src/processor.py](file:///d:/GitFile/Locus_AI_Assistant/src/processor.py).
- [x] Налаштовано [pytest.ini](file:///d:/GitFile/Locus_AI_Assistant/pytest.ini) та успішно прогнано всі 44 тести.
- [x] Зафіксовано стабільну точку: збережено коміт та тег `v2.3.1.safe`.
- [x] Створено робочу гілку `v2.3.2` та підготовлено даний трекер.

---

### Етап 1: MCP Gateway & Реєстр серверів (Завершено)
- [x] Створено модульний пакет `src/mcp/`:
  - [x] `src/mcp/models.py`: dataclass'и `MCPTool`, `ServerConfig`, `ToolExecutionResult`, енами `RiskLevel`, `ServerStatus`, `ServerTransport`.
  - [x] `src/mcp/exceptions.py`: структурована ієрархія помилок `MCPConnectionError`, `MCPTimeoutError`, `MCPToolNotFoundError`, `MCPExecutionError`.
  - [x] `src/mcp/client.py`: потокобезпечний stdio-клієнт з RLock та ізольованим життєвим циклом.
  - [x] `src/mcp/registry.py`: `ServerRegistry` з підтримкою завантаження з файлів (`data/mcp_servers.json`) та словників.
  - [x] `src/mcp/gateway.py`: `MCPGateway` (Mediation Layer) з агрегацією каталогів інструментів, просторами імен (`server__tool` / `server:tool`) та ізоляцією помилок виконання.
  - [x] `src/mcp/__init__.py`: глобальний синглтон `get_gateway()`, автоматичне підключення серверів.
  - [x] `src/mcp_client.py`: 100% зворотна сумісність для існуючого коду.
- [x] Конфігурація серверів у [data/mcp_servers.json](file:///d:/GitFile/Locus_AI_Assistant/data/mcp_servers.json).
- [x] Unit-тести для `MCPGateway` у [tests/test_mcp_gateway.py](file:///d:/GitFile/Locus_AI_Assistant/tests/test_mcp_gateway.py).
- [x] Усі 51 тест успішно пройдено.

---

### Етап 2: Відмовостійкість (ATBA + SERF)
- [ ] **ATBA (Adaptive Timeout Budget Allocation)**:
  - [ ] Впровадити `BudgetManager(total_budget_seconds, deadline)` у шлюзі.
  - [ ] Динамічне обчислення `per_tool_timeout` на основі типу інструменту та залишку бюджету.
  - [ ] Обробка `TimeoutExpired` без зависання головного потоку асистента.
- [ ] **SERF (Structured Error Recovery Framework)**:
  - [ ] Стандартизувати dataclass `ToolExecutionResult` та `ToolErrorResponse`:
    ```json
    {
      "ok": false,
      "error_code": "RESOURCE_UNAVAILABLE",
      "recoverable": true,
      "suggested_action": "Try fallback tool or ask user for alternative path",
      "raw_message": "..."
    }
    ```
  - [ ] Інтеграція SERF відповідей у контекст моделі для самовідновлення (self-healing).
- [ ] Unit-тести для перевірки поведінки при тайм-аутах та обробці помилок.

---

### Етап 3: Вирішення "MCP Tax" (Intent Router / Tool Attention)
- [ ] Створити `src/brain/tool_router.py`:
  - [ ] Легка семантична класифікація або fast-LLM routing запиту користувача.
  - [ ] Відбір топ-N релевантних інструментів (Dynamic Tool Pruning).
  - [ ] Формування оптимізованого списку `tools` для запиту до основної моделі (Gemini).
- [ ] Метрика: порівняння кількості переданих токенів інструментів (очікуване скорочення 50-80%).

---

### Етап 4: Zero Trust Governance & Human-in-the-Loop (HITL)
- [ ] Класифікація рівнів ризику інструментів:
  - `READ_ONLY` (безпечні: читання файлів, пошук).
  - `DESTRUCTIVE_WRITE` (модифікація, видалення файлів).
  - `SYSTEM_EXEC` (запуск процесів/команд).
  - `NETWORK_TRANSMIT` (надсилання конфіденційних даних назовні).
- [ ] Інтеграція з WebSocket API ([src/ws_protocol.py](file:///d:/GitFile/Locus_AI_Assistant/src/ws_protocol.py) та [main.py](file:///d:/GitFile/Locus_AI_Assistant/main.py)):
  - [ ] Подія `tool_permission_request` до фронтенду.
  - [ ] UI-модалка підтвердження дії користувачем ("Дозволити раз", "Дозволити завжди", "Заборонити").
  - [ ] Блокуюче очікування рішення користувача з тайм-аутом ATBA.
- [ ] Журнал аудиту викликів у [logs/](file:///d:/GitFile/Locus_AI_Assistant/logs/).

---

### Етап 5: Sandboxing & Ізоляція
- [ ] Підтримка запуску зовнішніх серверів у Docker-контейнерах:
  - [ ] Шаблони `Dockerfile` для типових MCP серверів.
  - [ ] Налаштування монтування volumes (read-only за замовчуванням).
  - [ ] Обмеження мережі (`--network none` де це можливо).
- [ ] Fallback-ізоляція для систем без Docker (обмежені робочі директорії, заборона виходу за межі дозволеного workspace).

---

## 📌 Як оновлювати цей документ
Під час виконання завдань розробник/асистент позначає виконані пункти відміткою `[x]` та оновлює статус у зведеній таблиці із зазначенням відповідного коміту.
