import math
import json
import re
import os
import itertools

from notification_classes import Notification
from printer import Printer


class Menu:
    """Класс меню с паттерном state machine."""

    def __init__(self, printer: Printer, notifier: Notification):
        self.printer = printer
        self.notifier = notifier

        self.current_section = 'main'
        self.exit_program = False

        self.edges = []              # [(u, v), ...] — введённые рёбра
        self.isolated_nodes = set()  # Изолированные вершины
        self.input_mode = 'include'  # ★ ИЗМЕНЕНО: INCLUDE по умолчанию
        self.nodes = set()           # Уникальные вершины (включая изолированные)
        self.graph_edges = set()     # Итоговый граф (нормализованные рёбра)

    # ============================================================
    # Хелперы уведомлений
    # ============================================================
    def _ts(self):
        return self.printer.last_input_time or self.printer.now()

    def notify_error(self, msg: str):
        self.notifier.add_error(msg, self._ts())

    def notify_warning(self, msg: str):
        self.notifier.add_warning(msg, self._ts())

    def notify_message(self, msg: str):
        self.notifier.add_message(msg, self._ts())

    def notify_note(self, msg: str):
        self.notifier.add_note(msg, self._ts())

    def show_notifications(self):
        self.printer.print_notifications_block(self.notifier.get_all())

    # ============================================================
    # Парсинг и построение графа
    # ============================================================
    def _parse_token(self, token: str):
        """
        Парсит один токен: число или строка в кавычках.
        Возвращает int, str или None (если ошибка).
        """
        token = token.strip()
        if not token:
            return None
        # Строка в кавычках
        if token.startswith('"') and token.endswith('"') and len(token) >= 2:
            return token[1:-1]
        # Число
        try:
            return int(token)
        except ValueError:
            return None

    def _parse_edge_string(self, raw: str):
        """
        Парсит строку вида '(1 2) ("a" "b") (1) ("x", "y", "z")'.
        Возвращает (edges, isolated_nodes, errors).
        - 1 вершина в скобках → изолированная
        - 2 вершины → ребро
        - 3+ вершин → клика (все попарные рёбра)
        """
        pattern = re.compile(r'\(\s*([^)]+?)\s*\)')
        parsed_edges = []
        parsed_isolated = []
        errors = []

        matches = list(pattern.finditer(raw))
        if not matches:
            errors.append(self.printer.fmt_no_edge_groups())
            return parsed_edges, parsed_isolated, errors

        for match in matches:
            content = match.group(1)
            # Разделяем по пробелам и запятым
            tokens = re.split(r'[\s,]+', content)
            tokens = [t for t in tokens if t]

            parsed_tokens = []
            for t in tokens:
                val = self._parse_token(t)
                if val is None:
                    errors.append(self.printer.fmt_invalid_token(t))
                else:
                    parsed_tokens.append(val)

            if not parsed_tokens:
                continue

            if len(parsed_tokens) == 1:
                # Изолированная вершина
                parsed_isolated.append(parsed_tokens[0])
            elif len(parsed_tokens) == 2:
                # Ребро
                u, v = parsed_tokens
                parsed_edges.append((u, v))
            else:
                # Клика — добавляем все попарные рёбра
                for i in range(len(parsed_tokens)):
                    for j in range(i + 1, len(parsed_tokens)):
                        parsed_edges.append((parsed_tokens[i], parsed_tokens[j]))

        return parsed_edges, parsed_isolated, errors

    def _normalize_edge(self, u, v):
        """Нормализует ребро для хранения (меньший элемент первый)."""
        if str(u) <= str(v):
            return (u, v)
        return (v, u)

    def _detect_duplicates_and_loops(self, new_edges, new_isolated):
        """
        Проверяет новые рёбра и изолированные вершины на петли и кратность.
        Учитывает как уже существующие, так и дубликаты внутри новой порции.
        """
        seen_edges = set()
        for u, v in self.edges:
            seen_edges.add(self._normalize_edge(u, v))

        seen_nodes = set(self.nodes)
        seen_nodes.update(self.isolated_nodes)

        for u, v in new_edges:
            if u == v:
                self.notify_warning(self.printer.fmt_loop_detected(u, v))
            key = self._normalize_edge(u, v)
            if key in seen_edges:
                self.notify_warning(self.printer.fmt_multiple_edge(u, v))
            seen_edges.add(key)

        for v in new_isolated:
            if v in seen_nodes:
                self.notify_warning(self.printer.fmt_duplicate_isolated(v))
            seen_nodes.add(v)

    def _build_graph(self):
        """
        Строит итоговый граф на основе режима.
        - INCLUDE: граф = введённые рёбра
        - EXCLUDE: граф = полный граф на всех вершинах минус введённые рёбра
        """
        normalized = set()
        for u, v in self.edges:
            normalized.add(self._normalize_edge(u, v))

        self.nodes = set()
        for u, v in self.edges:
            self.nodes.add(u)
            self.nodes.add(v)
        for v in self.isolated_nodes:
            self.nodes.add(v)

        if self.input_mode == 'exclude':
            all_edges = set()
            nodes_list = sorted(self.nodes, key=str)
            for i in range(len(nodes_list)):
                for j in range(i + 1, len(nodes_list)):
                    all_edges.add(self._normalize_edge(nodes_list[i], nodes_list[j]))
            self.graph_edges = all_edges - normalized
        else:
            self.graph_edges = normalized

    def _count_cliques_of_size(self, k: int) -> int:
        """Считает количество клик размера k в графе."""
        if k == 0:
            return 1
        if k == 1:
            return len(self.nodes)

        count = 0
        for subset in itertools.combinations(self.nodes, k):
            is_clique = True
            for i in range(k):
                for j in range(i + 1, k):
                    key = self._normalize_edge(subset[i], subset[j])
                    if key not in self.graph_edges:
                        is_clique = False
                        break
                if not is_clique:
                    break
            if is_clique:
                count += 1
        return count

    def _get_combination_name(self, k):
        names = {
            1: ("units", "единицы"), 2: ("pairs", "пары"),
            3: ("triples", "тройки"), 4: ("quadruples", "четверки"),
            5: ("quintuples", "пятерки"), 6: ("sextuples", "шестерки"),
            7: ("septuples", "семерки"), 8: ("octuples", "восьмерки"),
            9: ("nonuples", "девятки"), 10: ("decuples", "десятки"),
        }
        return names.get(k, (f"{k}-tuples", f"по {k}"))

    def _format_node(self, v):
        """Форматирует вершину для вывода: строки в кавычках, числа как есть."""
        if isinstance(v, str):
            return f'"{v}"'
        return str(v)

    def _ask_yes_no(self) -> bool:
        while True:
            r = self.printer.ask("\n➕ Continue? (y/n) / Продолжить? (y/n): ").strip().lower()
            if r in ['y', 'yes', 'да']:
                return True
            if r in ['n', 'no', 'нет']:
                return False
            self.printer.print_invalid_y_n()

    # ============================================================
    # Пункты меню
    # ============================================================
    def section_main(self):
        self.printer.print_main_menu_header()
        self.printer.print_main_menu_stats(len(self.edges), len(self.graph_edges), len(self.nodes))
        self.printer.print_main_menu_mode(self.input_mode)
        self.printer.print_main_menu_items()

        while True:
            choice = self.printer.ask_main_menu_choice()
            if choice == '0':
                self.exit_program = True
                return None
            if choice == '1': return 'input_mode'
            if choice == '2': return 'manual_input'
            if choice == '3': return 'json_input'
            if choice == '4': return 'view_graph'
            if choice == '5': return 'calculate'
            if choice == '6': return 'reset'
            self.notify_error(self.printer.fmt_invalid_choice(choice))
            self.printer.print_invalid_input_retry()

    def section_input_mode(self):
        self.printer.print_mode_selection_header()
        self.printer.print_mode_selection_items()

        while True:
            choice = self.printer.ask_mode_choice()
            if choice == '0':
                return 'main'
            if choice == '1':
                self.input_mode = 'include'
                self._build_graph()
                self.notify_message(self.printer.fmt_mode_set_msg('include'))
                self.printer.print_mode_set('include')
                return 'main'
            if choice == '2':
                self.input_mode = 'exclude'
                self._build_graph()
                self.notify_message(self.printer.fmt_mode_set_msg('exclude'))
                self.printer.print_mode_set('exclude')
                return 'main'
            self.notify_error(self.printer.fmt_invalid_mode_choice(choice))
            self.printer.print_invalid_input_retry()

    def section_manual_input(self):
        self.printer.print_manual_input_header()
        self.printer.print_manual_input_format()
        self.printer.print_manual_input_example()
        self.printer.print_manual_input_hints()

        if not self.edges and not self.isolated_nodes:
            self.notify_note(self.printer.fmt_note_json_alternative())

        while True:
            raw = self.printer.ask_edges_input()

            if raw in ['0', 'back', 'назад']:
                self.show_notifications()
                return 'main'

            if raw == 'clear':
                self.edges = []
                self.isolated_nodes = set()
                self._build_graph()
                self.notifier.clear_all()
                self.notify_message(self.printer.fmt_all_cleared_msg())
                self.printer.print_all_cleared()
                continue

            if not raw:
                self.notify_error(self.printer.fmt_empty_input())
                self.printer.print_cannot_be_empty()
                continue

            parsed_edges, parsed_isolated, errors = self._parse_edge_string(raw)

            if errors:
                self.printer.print_parsing_errors_header()
                for e in errors:
                    self.notify_error(e)
                    self.printer.print_error_line(e)
                if not parsed_edges and not parsed_isolated:
                    self.printer.print_no_valid_edges()
                    continue

            # ★ ИСПРАВЛЕНО: сначала детект, потом добавление
            self._detect_duplicates_and_loops(parsed_edges, parsed_isolated)
            self.edges.extend(parsed_edges)
            self.isolated_nodes.update(parsed_isolated)
            self._build_graph()

            total_new = len(parsed_edges) + len(parsed_isolated)
            self.notify_message(self.printer.fmt_edges_added_msg(
                total_new, len(self.edges) + len(self.isolated_nodes), len(self.graph_edges)))
            self.printer.print_edges_added(total_new, len(self.edges) + len(self.isolated_nodes), len(self.graph_edges))
            self.printer.print_unique_nodes(len(self.nodes))

            if not self._ask_yes_no():
                self.show_notifications()
                return 'main'

    def section_json_input(self):
        self.printer.print_json_input_header()
        self.printer.print_json_format()

        while True:
            path = self.printer.ask_json_path()
            if path.lower() in ['0', 'back', 'назад']:
                self.show_notifications()
                return 'main'

            if not path:
                self.notify_error(self.printer.fmt_empty_path())
                self.printer.print_cannot_be_empty()
                continue

            if not os.path.exists(path):
                self.notify_error(self.printer.fmt_file_not_found(path))
                self.printer.print_file_not_found_warning(path)
                continue

            try:
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except json.JSONDecodeError as e:
                self.notify_error(self.printer.fmt_invalid_json(path, e))
                self.printer.print_invalid_json_warning(e)
                continue
            except Exception as e:
                self.notify_error(self.printer.fmt_read_error(path, e))
                self.printer.print_read_error_warning(e)
                continue

            if 'edges' not in data or not isinstance(data['edges'], list):
                self.notify_error(self.printer.fmt_no_edges_array(path))
                self.printer.print_no_edges_array_warning()
                continue

            parsed_edges = []
            parsed_isolated = []
            local_errors = []
            
            for i, edge in enumerate(data['edges'], 1):
                try:
                    # ★ ИСПРАВЛЕНО: поддержка петли как изолированной вершины
                    if 'node' in edge:
                        v = edge['node']
                        if isinstance(v, (int, str)):
                            parsed_isolated.append(v)
                        else:
                            local_errors.append(self.printer.fmt_edge_invalid(i, "invalid node type"))
                    elif 'from' in edge and 'to' in edge:
                        u = edge['from']
                        v = edge['to']
                        if isinstance(u, (int, str)) and isinstance(v, (int, str)):
                            # ★ ИСПРАВЛЕНО: петля → изолированная вершина
                            if u == v:
                                parsed_isolated.append(u)
                            else:
                                parsed_edges.append((u, v))
                        else:
                            local_errors.append(self.printer.fmt_edge_invalid(i, "invalid types"))
                    else:
                        local_errors.append(self.printer.fmt_edge_invalid(i, "missing 'from'/'to' or 'node'"))
                except (KeyError, ValueError, TypeError) as e:
                    local_errors.append(self.printer.fmt_edge_invalid(i, e))

            if local_errors:
                self.printer.print_some_edges_had_errors()
                for e in local_errors:
                    self.notify_error(e)
                    self.printer.print_error_line(e)

            if not parsed_edges and not parsed_isolated:
                self.printer.print_no_json_edges()
                continue

            # ★ ИСПРАВЛЕНО: сначала детект, потом добавление
            self._detect_duplicates_and_loops(parsed_edges, parsed_isolated)
            self.edges.extend(parsed_edges)
            self.isolated_nodes.update(parsed_isolated)
            self._build_graph()

            total_new = len(parsed_edges) + len(parsed_isolated)
            self.notify_message(self.printer.fmt_json_loaded_msg(len(parsed_edges), path))
            self.printer.print_json_loaded(
                total_new, path, len(self.edges) + len(self.isolated_nodes), 
                len(self.graph_edges), len(self.nodes))

            if not self._ask_yes_no():
                self.show_notifications()
                return 'main'

    def section_view_graph(self):
        self.printer.print_view_header()
        self.printer.print_graph_stats(
            self.input_mode, len(self.edges), len(self.graph_edges), len(self.nodes))

        if self.edges or self.isolated_nodes:
            # Вывод рёбер
            if self.edges:
                self.printer.print_edges_list(
                    [(self._format_node(u), self._format_node(v)) for u, v in self.edges])
            
            # Вывод изолированных вершин
            if self.isolated_nodes:
                self.printer.print_isolated_nodes(
                    [self._format_node(v) for v in sorted(self.isolated_nodes, key=str)])

            # Степени узлов
            degree = {}
            for node in self.nodes:
                degree[node] = 0
            for u, v in self.graph_edges:
                degree[u] = degree.get(u, 0) + 1
                degree[v] = degree.get(v, 0) + 1
            self.printer.print_node_degrees(
                {self._format_node(k): v for k, v in sorted(degree.items(), key=lambda x: str(x[0]))})
        else:
            self.printer.print_no_edges_yet()

        self.show_notifications()
        self.printer.print_press_enter()
        return 'main'

    def section_calculate(self):
        if not self.nodes:
            self.printer.print_nothing_to_calculate()
            self.printer.print_press_enter()
            return 'main'

        N = len(self.nodes)
        groups = list(range(1, N + 1))

        self.printer.print_calculate_header(N, self.input_mode)

        cliques = {}
        total_sum = 0
        for k in groups:
            c = self._count_cliques_of_size(k)
            cliques[k] = c
            total_sum += c

        if N <= 8:
            terms = [f"\\omega_{{{k}}}={cliques[k]}" for k in groups]
            latex = "S = " + " + ".join(terms)
        else:
            start = [f"\\omega_{{{k}}}" for k in groups[:3]]
            end = [f"\\omega_{{{k}}}" for k in groups[-2:]]
            latex = "S = " + " + ".join(start) + " + \\dots + " + " + ".join(end)
        self.printer.print_latex(latex)

        self.printer.print_table_header()
        for k in groups:
            en, ru = self._get_combination_name(k)
            self.printer.print_table_row(k, en, ru, cliques[k])
        self.printer.print_table_sum(total_sum)

        max_edges = N * (N - 1) // 2
        is_complete = len(self.graph_edges) == max_edges
        if is_complete:
            fast = 2**N - 1
            self.printer.print_check_formula(fast)
            self.notify_note(self.printer.fmt_note_full_range_check())

        degree = {}
        for node in self.nodes:
            degree[node] = 0
        for u, v in self.graph_edges:
            degree[u] = degree.get(u, 0) + 1
            degree[v] = degree.get(v, 0) + 1
        self.printer.print_graph_statistics(
            N, len(self.graph_edges),
            {self._format_node(k): v for k, v in sorted(degree.items(), key=lambda x: str(x[0]))})

        self.printer.print_press_enter()
        return 'main'

    def section_reset(self):
        """Сбрасывает все данные программы."""
        self.edges = []
        self.isolated_nodes = set()
        self.nodes = set()
        self.graph_edges = set()
        self.input_mode = 'include'  # ★ Возвращаем INCLUDE по умолчанию
        self.notifier.clear_all()

        self.notify_message(self.printer.fmt_reset_msg())
        self.printer.print_reset_done()
        return 'main'


# ============================================================
# Главная функция
# ============================================================
def main():
    printer = Printer()
    notifier = Notification()
    printer.set_notifier(notifier)
    menu = Menu(printer, notifier)

    menu_graph = {
        'main':         menu.section_main,
        'input_mode':   menu.section_input_mode,
        'manual_input': menu.section_manual_input,
        'json_input':   menu.section_json_input,
        'view_graph':   menu.section_view_graph,
        'calculate':    menu.section_calculate,
        'reset':        menu.section_reset,
    }

    printer.print_program_start()

    while not menu.exit_program:
        current = menu.current_section
        if current not in menu_graph:
            menu.current_section = 'main'
            continue
        next_section = menu_graph[current]()
        if next_section is not None:
            menu.current_section = next_section

    printer.print_program_end()


if __name__ == "__main__":
    main()