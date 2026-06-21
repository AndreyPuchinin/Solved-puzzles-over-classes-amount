from datetime import datetime


class Printer:
    """
    Класс вывода сообщений.
    """

    def __init__(self):
        self._last_input_time: datetime = None
        self._notifier = None

    def set_notifier(self, notifier):
        """Привязывает менеджер уведомлений для автоочистки после вывода."""
        self._notifier = notifier

    # ============================================================
    # Базовые примитивы
    # ============================================================
    @property
    def last_input_time(self) -> datetime:
        return self._last_input_time

    def now(self) -> datetime:
        return datetime.now()

    def ask(self, prompt: str) -> str:
        self._last_input_time = self.now()
        value = input(prompt)
        display = value if value else "[пусто / empty]"
        print(f"  📝 [{self._fmt_time(self._last_input_time)}] You entered / Вы ввели: {display}")
        return value

    def _line(self, char: str = "=", width: int = 65):
        print(char * width)

    def _bi(self, en: str, ru: str = None):
        print(f"  {en}")
        if ru:
            print(f"  {ru}")

    def _fmt_time(self, t: datetime) -> str:
        return t.strftime("%H:%M:%S") if t else "??:??:??"

    # ============================================================
    # Запуск / завершение
    # ============================================================
    def print_program_start(self):
        print()
        self._line()
        print(" 🚀 Starting Dependency Graph Calculator...")
        print(" 🚀 Запуск Калькулятора Графа Зависимостей...")
        self._line()

    def print_program_end(self):
        print()
        self._line()
        print(" 👋 Goodbye! / До свидания!")
        self._line()

    def print_press_enter(self):
        self.ask("\n👉 Press Enter to continue / Нажмите Enter для продолжения...")

    # ============================================================
    # Главное меню (★ ИЗМЕНЁН: добавлен пункт 6 "Reset graph")
    # ============================================================
    def print_main_menu_header(self):
        print()
        self._line()
        print(" 🌐 DEPENDENCY GRAPH CALCULATOR")
        print(" 🌐 КАЛЬКУЛЯТОР ГРАФА ЗАВИСИМОСТЕЙ")
        self._line()

    # ★ ИЗМЕНЁН: теперь показывает статистику графа, а не только ввода
    def print_main_menu_stats(self, edges_input: int, graph_edges: int, nodes_count: int):
        self._bi(f"Edges input / Введено рёбер: {edges_input}",
                 f"Edges in graph / Рёбер в графе: {graph_edges}")
        self._bi(f"Unique nodes / Уникальных узлов: {nodes_count}", "")

    def print_main_menu_mode(self, mode):
        if mode is None:
            display = "⚠️ NOT SET / ⚠️ НЕ ЗАДАН"
        elif mode == 'include':
            display = "✅ INCLUDE (ВКЛЮЧЕНИЕ)"
        else:
            display = "✅ EXCLUDE (ИСКЛЮЧЕНИЕ)"
        print(f"\n  Input mode / Режим ввода: {display}")

    # ★ ИЗМЕНЁН: добавлен пункт [6]
    def print_main_menu_items(self):
        print()
        self._line("-")
        print("  [1] 🎯 Set input mode (INCLUDE / EXCLUDE edges)")
        print("      Задать режим ввода (НУЖНЫЕ / НЕНУЖНЫЕ рёбра)")
        print("  [2] ✍️  Enter edges MANUALLY")
        print("      Ввести рёбра ВРУЧНУЮ")
        print("  [3] 📄 Load edges from JSON FILE")
        print("      Загрузить рёбра из JSON-ФАЙЛА")
        print("  [4] 👁️  View current graph & notifications")
        print("      Просмотр текущего графа и уведомлений")
        print("  [5] 🧮 CALCULATE graph statistics")
        print("      РАССЧИТАТЬ статистику графа")
        print("  [6] 🔄 RESET graph (clear all data)")
        print("      СБРОСИТЬ граф (очистить все данные)")
        print("  [0] 🚪 EXIT program / ВЫЙТИ из программы")
        self._line("-")

    def ask_main_menu_choice(self) -> str:
        return self.ask("👉 Your choice / Ваш выбор: ").strip()

    # ============================================================
    # Выбор режима ввода
    # ============================================================
    def print_mode_selection_header(self):
        print()
        self._line()
        print(" 🎯 INPUT MODE SELECTION / ВЫБОР РЕЖИМА ВВОДА")
        self._line()
        self._bi("Choose how to treat the edges you specify:",
                 "Выберите, как обрабатывать указанные рёбра:")
        print()

    def print_mode_selection_items(self):
        print("  [1] INCLUDE mode / Режим ВКЛЮЧЕНИЯ")
        self._bi("    → Count ONLY the edges you specify.",
                 "    → Учитывать ТОЛЬКО указанные рёбра.")
        print()
        print("  [2] EXCLUDE mode / Режим ИСКЛЮЧЕНИЯ")
        self._bi("    → Count ALL edges EXCEPT those you specify.",
                 "    → Учитывать ВСЕ рёбра, КРОМЕ указанных.")
        print()
        print("  [0] ⬅️  BACK / НАЗАД")
        self._line("-")

    def ask_mode_choice(self) -> str:
        return self.ask("👉 Your choice / Ваш выбор: ").strip()

    def print_mode_set(self, mode: str):
        if mode == 'include':
            print("✅ Mode set to INCLUDE. / ✅ Режим установлен: ВКЛЮЧЕНИЕ.")
        else:
            print("✅ Mode set to EXCLUDE. / ✅ Режим установлен: ИСКЛЮЧЕНИЕ.")

    # ============================================================
    # Ручной ввод рёбер (★ ИЗМЕНЁН: показывает статистику графа)
    # ============================================================
    def print_manual_input_header(self):
        print()
        self._line()
        print(" ✍️  MANUAL EDGE INPUT / РУЧНОЙ ВВОД РЁБЕР")
        self._line()

    def print_manual_input_format(self):
        self._bi("Format: (u v) or (u) or (\"name1\" \"name2\") separated by space.",
                 "Формат: (u v) или (u) или (\"имя1\" \"имя2\") через пробел.")
        self._bi("  u, v — positive integer node numbers OR strings in quotes",
                 "  u, v — положительные целые номера узлов ИЛИ строки в кавычках")
        self._bi("  1 node in brackets = isolated vertex",
                 "  1 вершина в скобках = изолированная вершина")
        self._bi("  2 nodes = edge, 3+ nodes = clique (all pairwise edges)",
                 "  2 вершины = ребро, 3+ вершин = клика (все попарные рёбра)")
        print()

    def print_manual_input_example(self):
        self._bi("Examples / Примеры:",
                 "  (1 2) (\"a\" \"b\") (3) (\"x\", \"y\", \"z\")")
        print()

    def print_manual_input_hints(self):
        self._bi("[0] or 'back' ⬅️  BACK / НАЗАД",
                 "[clear] — clear all edges / очистить все рёбра")
        self._line()

    def ask_edges_input(self) -> str:
        return self.ask("\n👉 Enter edges / Введите рёбра: ").strip().lower()

    # ★ ИЗМЕНЁН: показывает статистику графа, а не только ввода
    def print_edges_added(self, added: int, total_input: int, graph_edges: int):
        print(f"\n✅ Added {added} edge(s). Total input: {total_input}.")
        print(f"✅ Добавлено {added} ребер. Всего введено: {total_input}.")
        print(f"📊 Edges in graph / Рёбер в графе: {graph_edges}")

    def print_unique_nodes(self, count: int):
        print(f"📊 Unique nodes / Уникальных узлов: {count}")

    def print_no_valid_edges(self):
        print("⚠️ No valid edges added. Try again. / ⚠️ Ни одного корректного ребра не добавлено. Попробуйте снова.")

    def print_all_cleared(self):
        print("🗑️ All edges cleared. / 🗑️ Все рёбра очищены.")

    # ============================================================
    # JSON-ввод (★ ИЗМЕНЁН: показывает статистику графа)
    # ============================================================
    def print_json_input_header(self):
        print()
        self._line()
        print(" 📄 LOAD FROM JSON / ЗАГРУЗКА ИЗ JSON")
        self._line()

    def print_json_format(self):
        self._bi("Expected JSON format / Ожидаемый формат JSON:",
             """
{
  "edges": [
    {"from": 1, "to": 2},
    {"from": "a", "to": "b"},
    {"node": 3},
    {"node": "isolated"}
  ]
}
            """)
        self._bi("[0] or 'back' ⬅️  BACK / НАЗАД", "")
        self._line()

    def ask_json_path(self) -> str:
        return self.ask("\n👉 Path to JSON file / Путь к JSON-файлу: ").strip()

    # ★ ИЗМЕНЁН: показывает статистику графа
    def print_json_loaded(self, count: int, path: str, total_input: int, graph_edges: int, nodes: int):
        print(f"\n✅ Loaded {count} edge(s) from {path}.")
        print(f"✅ Загружено {count} ребер из {path}.")
        print(f"📊 Total input / Всего введено: {total_input}")
        print(f"📊 Edges in graph / Рёбер в графе: {graph_edges}")
        print(f"📊 Unique nodes / Уникальных узлов: {nodes}")

    def print_no_json_edges(self):
        print("⚠️ No valid edges loaded. / ⚠️ Ни одного корректного ребра не загружено.")

    # ============================================================
    # Просмотр графа
    # ============================================================
    def print_view_header(self):
        print()
        self._line()
        print(" 👁️  CURRENT GRAPH STATE / ТЕКУЩЕЕ СОСТОЯНИЕ ГРАФА")
        self._line()

    def print_graph_stats(self, mode, edges_input: int, graph_edges: int, nodes_count: int):
        mode_str = mode if mode else "not set / не задан"
        self._bi(f"Input mode / Режим ввода: {mode_str}", "")
        self._bi(f"Edges input / Введено рёбер: {edges_input}",
                 f"Edges in graph / Рёбер в графе: {graph_edges}")
        self._bi(f"Unique nodes / Уникальных узлов: {nodes_count}", "")

    def print_edges_list(self, edges):
        print("\n  Edges / Рёбра:")
        print("  " + "-" * 60)
        for i, (u, v) in enumerate(edges, 1):
            print(f"    [{i:>2}] ({u} -> {v})")
        print("  " + "-" * 60)

    def print_isolated_nodes(self, nodes):
        print("\n  Isolated nodes / Изолированные вершины:")
        print("  " + "-" * 60)
        for i, node in enumerate(nodes, 1):
            print(f"    [{i:>2}] {node}")
        print("  " + "-" * 60)

    def print_node_degrees(self, degrees: dict):
        print("\n  Node degrees / Степени узлов:")
        print("  " + "-" * 60)
        for node in sorted(degrees.keys()):
            self._bi(f"    Node {node}: degree {degrees[node]}",
                     f"    Узел {node}: степень {degrees[node]}")
        print("  " + "-" * 60)

    def print_no_edges_yet(self):
        print("\n  ⚠️ No edges yet. Add some via manual input or JSON.")
        print("  ⚠️ Рёбер пока нет. Добавьте их через ручной ввод или JSON.")

    # ============================================================
    # Расчёт
    # ============================================================
    def print_nothing_to_calculate(self):
        print()
        self._line()
        print(" ⚠️ NOTHING TO CALCULATE / НЕЧЕГО СЧИТАТЬ")
        self._line()
        self._bi("No edges loaded. Please add edges first.",
                 "Рёбра не загружены. Сначала добавьте рёбра.")

    def print_calculate_header(self, N: int, mode):
        print()
        self._line()
        print(f" 🧮 CLIQUE COUNTING / ПОДСЧЁТ КЛИК  (N = {N})")
        self._line()
        self._bi(f"Number of unique types (nodes) / Количество уникальных типов (узлов): {N}", "")
        mode_str = "INCLUDE" if mode == 'include' or mode is None else "EXCLUDE"
        self._bi(f"Mode / Режим: {mode_str}", "")
        self._bi("Counting cliques (complete subgraphs) for all sizes from 1 to N.",
                 "Подсчёт клик (полных подграфов) для всех размеров от 1 до N.")

    def print_latex(self, latex: str):
        print()
        self._line("-")
        print("📐 LaTeX formula / LaTeX-формула:")
        self._line("-")
        print(latex)
        self._line("-")

    def print_table_header(self):
        print(f"\n{'k':<4} | {'EN Name':<12} | {'RU Name':<10} | {'ω_k (cliques)':<15}")
        print("-" * 53)

    def print_table_row(self, k: int, en: str, ru: str, c: int):
        print(f"{k:<4} | {en:<12} | {ru:<10} | {c:<15}")

    def print_table_sum(self, total: int):
        print("-" * 53)
        print(f"{'SUM':<4} | {'Total':<12} | {'Сумма':<10} | {total:<15}")
        self._line()

    def print_check_formula(self, fast: int):
        print(f"\n✅ Graph is complete! Check (2^N - 1): {fast}")
        print(f"✅ Граф полный! Проверка (2^N - 1): {fast}")

    def print_graph_statistics(self, N: int, edges_count: int, degrees: dict):
        print("\n📊 Graph statistics / Статистика графа:")
        self._bi(f"  N (unique nodes) / N (уникальных узлов): {N}",
                 f"  Edges in graph / Рёбер в графе: {edges_count}")
        if degrees:
            print("  " + "-" * 60)
            print("  Node degrees / Степени узлов:")
            for node in sorted(degrees.keys()):
                self._bi(f"    Node {node}: degree {degrees[node]}",
                         f"    Узел {node}: степень {degrees[node]}")
            print("  " + "-" * 60)

    # ============================================================
    # Сброс графа (★ НОВОЕ)
    # ============================================================
    def print_reset_done(self):
        print()
        self._line()
        print(" 🔄 GRAPH RESET COMPLETE / ГРАФ СБРОШЕН")
        self._line()
        self._bi("All edges, nodes, mode and notifications have been cleared.",
                 "Все рёбра, узлы, режим и уведомления очищены.")
        self._bi("You can start fresh.",
                 "Можно начинать заново.")
        self._line()

    # ============================================================
    # Вывод уведомлений (★ ИЗМЕНЁН: локальная нумерация по типам)
    # ============================================================
    def print_notifications_block(self, all_notifications: dict):
        has_any = any(items for items in all_notifications.values())
        if not has_any:
            return

        print()
        self._line()
        print(" 📋 Notifications / Уведомления:")
        self._line()

        order = [
            ('error',   '❌ ERRORS / ОШИБКИ'),
            ('warning', '⚠️  WARNINGS / ПРЕДУПРЕЖДЕНИЯ'),
            ('message', '💬 MESSAGES / СООБЩЕНИЯ'),
            ('note',    '📝 NOTES / ЗАМЕТКИ'),
        ]
        # ★ ИЗМЕНЕНИЕ: локальный счётчик для каждого типа
        for key, title in order:
            items = all_notifications.get(key, [])
            if not items:
                continue
            print(f"  [{title}]")
            local_idx = 1
            for ts, msg in items:
                print(f"    {local_idx:>2}. [{self._fmt_time(ts)}] {msg}")
                local_idx += 1
            print()
        self._line()
        print()

        if self._notifier is not None:
            self._notifier.clear_all()

    # ============================================================
    # Форматирование сообщений для уведомлений
    # ============================================================
    def fmt_invalid_token(self, token: str) -> str:
        return (f"Invalid token '{token}'. Expected: number or \"string\". "
                f"Неверный токен '{token}'. Ожидается: число или \"строка\".")
    
    def fmt_duplicate_isolated(self, v) -> str:
        return (f"Duplicate isolated node: {v}. "
                f"Дубликат изолированной вершины: {v}.")
        def fmt_invalid_choice(self, choice: str) -> str:
            return (f"Invalid choice '{choice}'. Please enter 0-6. "
                    f"Неверный выбор '{choice}'. Введите 0-6.")

    def fmt_invalid_mode_choice(self, choice: str) -> str:
        return (f"Invalid choice '{choice}'. Enter 0, 1 or 2. "
                f"Неверный выбор '{choice}'. Введите 0, 1 или 2.")

    def fmt_empty_input(self) -> str:
        return "Empty input. / Пустой ввод."

    def fmt_empty_path(self) -> str:
        return "Empty file path. / Пустой путь к файлу."

    def fmt_no_edge_groups(self) -> str:
        return ("No valid edge groups found. Format: (u v) "
                "Не найдено ни одной корректной группы. Формат: (u v)")

    def fmt_non_positive_nodes(self, u: int, v: int) -> str:
        return (f"Node numbers must be positive: ({u} {v}). "
                f"Номера узлов должны быть положительными: ({u} {v}).")

    def fmt_parse_error(self, raw: str, err) -> str:
        return (f"Failed to parse '{raw}': {err}. "
                f"Не удалось разобрать '{raw}': {err}")

    def fmt_loop_detected(self, u: int, v: int) -> str:
        return (f"Loop detected: edge ({u} {v}). "
                f"Обнаружена петля: ребро ({u} {v}).")

    def fmt_multiple_edge(self, u: int, v: int) -> str:
        return (f"Multiple edge: ({u} {v}) duplicates previous. "
                f"Кратное ребро: ({u} {v}) дублирует предыдущее.")

    def fmt_file_not_found(self, path: str) -> str:
        return f"File not found: {path}. / Файл не найден: {path}."

    def fmt_invalid_json(self, path: str, err) -> str:
        return f"Invalid JSON in {path}: {err}. / Некорректный JSON в {path}: {err}."

    def fmt_read_error(self, path: str, err) -> str:
        return f"Error reading {path}: {err}. / Ошибка чтения {path}: {err}."

    def fmt_no_edges_array(self, path: str) -> str:
        return f"No 'edges' array in {path}. / Нет массива 'edges' в {path}."

    def fmt_edge_invalid(self, i: int, err) -> str:
        return f"Edge #{i} invalid: {err}. / Ребро #{i} некорректно: {err}."

    def fmt_edge_non_positive(self, i: int, u: int, v: int) -> str:
        return (f"Edge #{i}: node numbers must be positive ({u}, {v}). "
                f"Ребро #{i}: номера узлов должны быть положительными ({u}, {v}).")

    def fmt_mode_set_msg(self, mode: str) -> str:
        if mode == 'include':
            return "Mode set to INCLUDE. / Режим установлен: ВКЛЮЧЕНИЕ."
        return "Mode set to EXCLUDE. / Режим установлен: ИСКЛЮЧЕНИЕ."

    def fmt_edges_added_msg(self, count: int, total: int, graph_edges: int) -> str:
        return (f"Added {count} edge(s). Total input: {total}. "
                f"Edges in graph: {graph_edges}. / "
                f"Добавлено {count} ребер. Всего введено: {total}. "
                f"Рёбер в графе: {graph_edges}.")

    def fmt_json_loaded_msg(self, count: int, path: str) -> str:
        return f"Loaded {count} edge(s) from {path}. / Загружено {count} ребер из {path}."

    def fmt_all_cleared_msg(self) -> str:
        return "All edges cleared. / Все рёбра очищены."

    def fmt_reset_msg(self) -> str:
        return "Graph reset. All data cleared. / Граф сброшен. Все данные очищены."

    def fmt_note_json_alternative(self) -> str:
        return ("Tip: For large graphs, consider using JSON input (menu item 3) "
                "instead of manual entry. "
                "Совет: для больших графов используйте JSON-ввод (пункт 3), а не ручной.")

    def fmt_note_full_range_check(self) -> str:
        return ("Graph is complete (all edges present). "
                "Sum equals 2^N - 1. "
                "Граф полный (все рёбра присутствуют). Сумма равна 2^N - 1.")

    # --- Предупреждения интерфейса ---
    def print_invalid_input_retry(self):
        print("⚠️ Invalid input. Try again. / ⚠️ Неверный ввод. Попробуйте снова.")

    def print_invalid_y_n(self):
        print("⚠️ Invalid input. Please enter 'y' or 'n'.")
        print("⚠️ Неверный ввод. Пожалуйста, введите 'y' или 'n'.")

    def print_parsing_errors_header(self):
        print("\n⚠️ Parsing errors / Ошибки разбора:")

    def print_error_line(self, msg: str):
        print(f"  ❌ {msg}")

    def print_cannot_be_empty(self):
        print("⚠️ Input cannot be empty. / ⚠️ Ввод не может быть пустым.")

    def print_file_not_found_warning(self, path: str):
        print(f"⚠️ File not found: {path}. / ⚠️ Файл не найден: {path}.")

    def print_invalid_json_warning(self, err):
        print(f"⚠️ Invalid JSON: {err}. / ⚠️ Некорректный JSON: {err}.")

    def print_read_error_warning(self, err):
        print(f"⚠️ Error reading file: {err}. / ⚠️ Ошибка чтения файла: {err}.")

    def print_no_edges_array_warning(self):
        print("⚠️ JSON must contain 'edges' array. / ⚠️ JSON должен содержать массив 'edges'.")

    def print_some_edges_had_errors(self):
        print("\n⚠️ Some edges had errors / Некоторые рёбра с ошибками:")