from datetime import datetime


class Printer:
    """
    Класс вывода сообщений.
    """

    def __init__(self, output_file: str = "printer_output.txt"):
        self._last_input_time: datetime = None
        self._last_input_value = ""
        self._record_to_file = False
        self._notifier = None
        self._output_file = output_file
        with open(self._output_file, "w", encoding="utf-8"):
            pass

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

    def _print(self, *args, **kwargs):
        print(*args, **kwargs)
        if self._record_to_file:
            with open(self._output_file, "a", encoding="utf-8") as output_file:
                print(*args, file=output_file, **kwargs)

    def _data_print(self, *args, **kwargs):
        print(*args, **kwargs)
        self._file_print(*args, **kwargs)

    def _file_print(self, *args, **kwargs):
        with open(self._output_file, "a", encoding="utf-8") as output_file:
            print(*args, file=output_file, **kwargs)

    def ask(self, prompt: str) -> str:
        self._last_input_time = self.now()
        self._print(prompt, end="", flush=True)
        value = input()
        self._last_input_value = value
        self._print()
        display = value if value else "[пусто / empty]"
        self._print(f"  📝 [{self._fmt_time(self._last_input_time)}] You entered / Вы ввели: {display}")
        return value

    def _line(self, char: str = "=", width: int = 65):
        self._print(char * width)

    def _bi(self, en: str, ru: str = None):
        self._print(f"  {en}")
        if ru:
            self._print(f"  {ru}")

    def _fmt_time(self, t: datetime) -> str:
        return t.strftime("%H:%M:%S") if t else "??:??:??"

    # ============================================================
    # Запуск / завершение
    # ============================================================
    def print_program_start(self):
        self._print()
        self._line()
        self._print(" 🚀 Starting Dependency Graph Calculator...")
        self._print(" 🚀 Запуск Калькулятора Графа Зависимостей...")
        self._line()

    def print_program_end(self):
        self._print()
        self._line()
        self._print(" 👋 Goodbye! / До свидания!")
        self._line()

    def print_press_enter(self):
        self.ask("\n👉 Press Enter to continue / Нажмите Enter для продолжения...")

    # ============================================================
    # Главное меню (★ ИЗМЕНЁН: добавлен пункт 6 "Reset graph")
    # ============================================================
    def print_main_menu_header(self):
        self._print()
        self._line()
        self._print(" 🌐 DEPENDENCY GRAPH CALCULATOR")
        self._print(" 🌐 КАЛЬКУЛЯТОР ГРАФА ЗАВИСИМОСТЕЙ")
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
        self._print(f"\n  Input mode / Режим ввода: {display}")

    # ★ ИЗМЕНЁН: добавлен пункт [6]
    def print_main_menu_items(self):
        self._print()
        self._line("-")
        self._print("  [1] 🎯 Set input mode (INCLUDE / EXCLUDE edges)")
        self._print("      Задать режим ввода (НУЖНЫЕ / НЕНУЖНЫЕ рёбра)")
        self._print("  [2] ✍️  Enter edges MANUALLY")
        self._print("      Ввести рёбра ВРУЧНУЮ")
        self._print("  [3] 📄 Load edges from JSON FILE")
        self._print("      Загрузить рёбра из JSON-ФАЙЛА")
        self._print("  [4] 👁️  View current graph & notifications")
        self._print("      Просмотр текущего графа и уведомлений")
        self._print("  [5] 🧮 CALCULATE graph statistics")
        self._print("      РАССЧИТАТЬ статистику графа")
        self._print("  [6] 🔄 RESET graph (clear all data)")
        self._print("      СБРОСИТЬ граф (очистить все данные)")
        self._print("  [0] 🚪 EXIT program / ВЫЙТИ из программы")
        self._line("-")

    def ask_main_menu_choice(self) -> str:
        choice = self.ask("👉 Your choice / Ваш выбор: ").strip()
        if choice in {"4", "5"}:
            self._file_print("👉 Your choice / Ваш выбор: ")
            display = self._last_input_value or "[пусто / empty]"
            self._file_print(
                f"  📝 [{self._fmt_time(self._last_input_time)}] "
                f"You entered / Вы ввели: {display}")
            self.start_file_recording()
        return choice

    def start_file_recording(self):
        self._record_to_file = True

    def stop_file_recording(self):
        self._record_to_file = False

    # ============================================================
    # Выбор режима ввода
    # ============================================================
    def print_mode_selection_header(self):
        self._print()
        self._line()
        self._print(" 🎯 INPUT MODE SELECTION / ВЫБОР РЕЖИМА ВВОДА")
        self._line()
        self._bi("Choose how to treat the edges you specify:",
                 "Выберите, как обрабатывать указанные рёбра:")
        self._print()

    def print_mode_selection_items(self):
        self._print("  [1] INCLUDE mode / Режим ВКЛЮЧЕНИЯ")
        self._bi("    → Count ONLY the edges you specify.",
                 "    → Учитывать ТОЛЬКО указанные рёбра.")
        self._print()
        self._print("  [2] EXCLUDE mode / Режим ИСКЛЮЧЕНИЯ")
        self._bi("    → Count ALL edges EXCEPT those you specify.",
                 "    → Учитывать ВСЕ рёбра, КРОМЕ указанных.")
        self._print()
        self._print("  [0] ⬅️  BACK / НАЗАД")
        self._line("-")

    def ask_mode_choice(self) -> str:
        return self.ask("👉 Your choice / Ваш выбор: ").strip()

    def print_mode_set(self, mode: str):
        if mode == 'include':
            self._print("✅ Mode set to INCLUDE. / ✅ Режим установлен: ВКЛЮЧЕНИЕ.")
        else:
            self._print("✅ Mode set to EXCLUDE. / ✅ Режим установлен: ИСКЛЮЧЕНИЕ.")

    # ============================================================
    # Ручной ввод рёбер (★ ИЗМЕНЁН: показывает статистику графа)
    # ============================================================
    def print_manual_input_header(self):
        self._print()
        self._line()
        self._print(" ✍️  MANUAL EDGE INPUT / РУЧНОЙ ВВОД РЁБЕР")
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
        self._print()

    def print_manual_input_example(self):
        self._bi("Examples / Примеры:",
                 "  (1 2) (\"a\" \"b\") (3) (\"x\", \"y\", \"z\")")
        self._print()

    def print_manual_input_hints(self):
        self._bi("[0] or 'back' ⬅️  BACK / НАЗАД",
                 "[clear] — clear all edges / очистить все рёбра")
        self._line()

    def ask_edges_input(self) -> str:
        return self.ask("\n👉 Enter edges / Введите рёбра: ").strip().lower()

    # ★ ИЗМЕНЁН: показывает статистику графа, а не только ввода
    def print_edges_added(self, added: int, total_input: int, graph_edges: int):
        self._print(f"\n✅ Added {added} edge(s). Total input: {total_input}.")
        self._print(f"✅ Добавлено {added} ребер. Всего введено: {total_input}.")
        self._print(f"📊 Edges in graph / Рёбер в графе: {graph_edges}")

    def print_unique_nodes(self, count: int):
        self._print(f"📊 Unique nodes / Уникальных узлов: {count}")

    def print_no_valid_edges(self):
        self._print("⚠️ No valid edges added. Try again. / ⚠️ Ни одного корректного ребра не добавлено. Попробуйте снова.")

    def print_all_cleared(self):
        self._print("🗑️ All edges cleared. / 🗑️ Все рёбра очищены.")

    # ============================================================
    # JSON-ввод (★ ИЗМЕНЁН: показывает статистику графа)
    # ============================================================
    def print_json_input_header(self):
        self._print()
        self._line()
        self._print(" 📄 LOAD FROM JSON / ЗАГРУЗКА ИЗ JSON")
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
        self._print(f"\n✅ Loaded {count} edge(s) from {path}.")
        self._print(f"✅ Загружено {count} ребер из {path}.")
        self._print(f"📊 Total input / Всего введено: {total_input}")
        self._print(f"📊 Edges in graph / Рёбер в графе: {graph_edges}")
        self._print(f"📊 Unique nodes / Уникальных узлов: {nodes}")

    def print_no_json_edges(self):
        self._print("⚠️ No valid edges loaded. / ⚠️ Ни одного корректного ребра не загружено.")

    # ============================================================
    # Просмотр графа
    # ============================================================
    def print_view_header(self):
        self._print()
        self._line()
        self._print(" 👁️  CURRENT GRAPH STATE / ТЕКУЩЕЕ СОСТОЯНИЕ ГРАФА")
        self._line()

    def print_graph_stats(self, mode, edges_input: int, graph_edges: int, nodes_count: int):
        mode_str = mode if mode else "not set / не задан"
        self._bi(f"Input mode / Режим ввода: {mode_str}", "")
        self._bi(f"Edges input / Введено рёбер: {edges_input}",
                 f"Edges in graph / Рёбер в графе: {graph_edges}")
        self._bi(f"Unique nodes / Уникальных узлов: {nodes_count}", "")

    def print_edges_list(self, edges):
        self._print("\n  Edges / Рёбра:")
        self._print("  " + "-" * 60)
        for i, (u, v) in enumerate(edges, 1):
            self._print(f"    [{i:>2}] ({u} -> {v})")
        self._print("  " + "-" * 60)

    def print_isolated_nodes(self, nodes):
        self._print("\n  Isolated nodes / Изолированные вершины:")
        self._print("  " + "-" * 60)
        for i, node in enumerate(nodes, 1):
            self._print(f"    [{i:>2}] {node}")
        self._print("  " + "-" * 60)

    def print_node_degrees(self, degrees: dict):
        self._print("\n  Node degrees / Степени узлов:")
        self._print("  " + "-" * 60)
        for node in sorted(degrees.keys()):
            self._bi(f"    Node {node}: degree {degrees[node]}",
                     f"    Узел {node}: степень {degrees[node]}")
        self._print("  " + "-" * 60)

    def print_no_edges_yet(self):
        self._print("\n  ⚠️ No edges yet. Add some via manual input or JSON.")
        self._print("  ⚠️ Рёбер пока нет. Добавьте их через ручной ввод или JSON.")

    # ============================================================
    # Расчёт
    # ============================================================
    def print_nothing_to_calculate(self):
        self._print()
        self._line()
        self._print(" ⚠️ NOTHING TO CALCULATE / НЕЧЕГО СЧИТАТЬ")
        self._line()
        self._bi("No edges loaded. Please add edges first.",
                 "Рёбра не загружены. Сначала добавьте рёбра.")

    def print_calculate_header(self, N: int, mode):
        self._print()
        self._line()
        self._print(f" 🧮 CLIQUE COUNTING / ПОДСЧЁТ КЛИК  (N = {N})")
        self._line()
        self._bi(f"Number of unique types (nodes) / Количество уникальных типов (узлов): {N}", "")
        mode_str = "INCLUDE" if mode == 'include' or mode is None else "EXCLUDE"
        self._bi(f"Mode / Режим: {mode_str}", "")
        self._bi("Counting cliques (complete subgraphs) for all sizes from 1 to N.",
                 "Подсчёт клик (полных подграфов) для всех размеров от 1 до N.")

    def print_latex(self, latex: str):
        self._data_print()
        self._data_print("-" * 65)
        self._data_print("📐 LaTeX formula / LaTeX-формула:")
        self._data_print("-" * 65)
        self._data_print(latex)
        self._data_print("-" * 65)

    # вывод списка клик для одного размера
    def print_clique_list(self, k: int, en_name: str, ru_name: str, 
                          cliques: list, total_possible: int):
        """
        Выводит список клик размера k.
        cliques: список кортежей вершин
        total_possible: общее количество возможных комбинаций размера k
        """
        count = len(cliques)
        self._data_print(f"  {en_name} / {ru_name}: {count} из {total_possible}")
        
        if cliques:
            # Форматируем каждую клику
            formatted = []
            for clique in cliques:
                # Сортируем вершины внутри клики для единообразия
                sorted_clique = sorted(clique, key=str)
                # Форматируем каждую вершину
                parts = [self._format_node_for_list(v) for v in sorted_clique]
                # Соединяем через дефис
                formatted.append("-".join(parts))
            
            # Выводим список через запятую
            self._data_print("  " + ",\n  ".join(formatted))
        self._data_print()

    def _format_node_for_list(self, v):
        """Форматирует вершину для списка: всегда в кавычках."""
        return f'"{v}"'

    def print_total_sum(self, total: int, total_possible: int):
        self._data_print("=" * 65)
        self._data_print(f"  Total sum / Общая сумма: {total}")
        self._data_print(f"  Total possible sum / Общая возможная сумма: {total_possible}")
        self._data_print(f"  % of fillness / % заполнения: {total/(total_possible/100)} %")
        self._data_print("=" * 65)
        self._data_print()

    def print_table_header(self):
        self._data_print(f"\n{'k':<4} | {'EN Name':<12} | {'RU Name':<10} | {'ω_k (cliques)':<15}")
        self._data_print("-" * 53)

    def print_table_row(self, k: int, en: str, ru: str, c: int):
        self._data_print(f"{k:<4} | {en:<12} | {ru:<10} | {c:<15}")

    def print_table_sum(self, total: int):
        self._data_print("-" * 53)
        self._data_print(f"{'SUM':<4} | {'Total':<12} | {'Сумма':<10} | {total:<15}")
        self._data_print("=" * 65)

    def print_check_formula(self, fast: int):
        self._data_print(f"\n✅ Graph is complete! Check (2^N - 1): {fast}")
        self._data_print(f"✅ Граф полный! Проверка (2^N - 1): {fast}")

    def print_graph_statistics(self, N: int, edges_count: int, degrees: dict):
        self._data_print("\n📊 Graph statistics / Статистика графа:")
        self._data_print(f"  N (unique nodes) / N (уникальных узлов): {N}")
        self._data_print(f"  Edges in graph / Рёбер в графе: {edges_count}")
        if degrees:
            self._data_print("  " + "-" * 60)
            self._data_print("  Node degrees / Степени узлов:")
            for node in sorted(degrees.keys()):
                self._data_print(f"    Node {node}: degree {degrees[node]}")
                self._data_print(f"    Узел {node}: степень {degrees[node]}")
            self._data_print("  " + "-" * 60)

    # ============================================================
    # Сброс графа (★ НОВОЕ)
    # ============================================================
    def print_reset_done(self):
        self._print()
        self._line()
        self._print(" 🔄 GRAPH RESET COMPLETE / ГРАФ СБРОШЕН")
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

        self._print()
        self._line()
        self._print(" 📋 Notifications / Уведомления:")
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
            self._print(f"  [{title}]")
            local_idx = 1
            for ts, msg in items:
                self._print(f"    {local_idx:>2}. [{self._fmt_time(ts)}] {msg}")
                local_idx += 1
            self._print()
        self._line()
        self._print()

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
        self._print("⚠️ Invalid input. Try again. / ⚠️ Неверный ввод. Попробуйте снова.")

    def print_invalid_y_n(self):
        self._print("⚠️ Invalid input. Please enter 'y' or 'n'.")
        self._print("⚠️ Неверный ввод. Пожалуйста, введите 'y' или 'n'.")

    def print_parsing_errors_header(self):
        self._print("\n⚠️ Parsing errors / Ошибки разбора:")

    def print_error_line(self, msg: str):
        self._print(f"  ❌ {msg}")

    def print_cannot_be_empty(self):
        self._print("⚠️ Input cannot be empty. / ⚠️ Ввод не может быть пустым.")

    def print_file_not_found_warning(self, path: str):
        self._print(f"⚠️ File not found: {path}. / ⚠️ Файл не найден: {path}.")

    def print_invalid_json_warning(self, err):
        self._print(f"⚠️ Invalid JSON: {err}. / ⚠️ Некорректный JSON: {err}.")

    def print_read_error_warning(self, err):
        self._print(f"⚠️ Error reading file: {err}. / ⚠️ Ошибка чтения файла: {err}.")

    def print_no_edges_array_warning(self):
        self._print("⚠️ JSON must contain 'edges' array. / ⚠️ JSON должен содержать массив 'edges'.")

    def print_some_edges_had_errors(self):
        self._print("\n⚠️ Some edges had errors / Некоторые рёбра с ошибками:")