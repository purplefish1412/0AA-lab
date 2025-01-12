from dataclasses import dataclass
from typing import List, Optional, Tuple, Union
import re

@dataclass
class KDNode:
    interval: List[int]
    left: Optional['KDNode'] = None
    right: Optional['KDNode'] = None

class KDTree:
    def __init__(self):
        self.root = None

    def insert(self, interval: List[int]) -> None:
        if not self.root:
            self.root = KDNode(interval)
            return

        current = self.root
        depth = 0

        while True:
            compare_lower = depth % 2 == 0
            
            if compare_lower:
                if interval[0] < current.interval[0]:
                    if not current.left:
                        current.left = KDNode(interval)
                        break
                    current = current.left
                else:
                    if not current.right:
                        current.right = KDNode(interval)
                        break
                    current = current.right
            else:
                if interval[1] < current.interval[1]:
                    if not current.left:
                        current.left = KDNode(interval)
                        break
                    current = current.left
                else:
                    if not current.right:
                        current.right = KDNode(interval)
                        break
                    current = current.right
            
            depth += 1

    def contains(self, interval: List[int]) -> bool:
        def _contains(node: Optional[KDNode], target: List[int]) -> bool:
            if not node:
                return False
            if node.interval == target:
                return True
            return _contains(node.left, target) or _contains(node.right, target)

        return _contains(self.root, interval)

    def search(self, query: Optional[Tuple[str, List[int]]] = None) -> List[List[int]]:
        def _search(node: Optional[KDNode]) -> List[List[int]]:
            if not node:
                return []
            
            results = []
            results.extend(_search(node.left))
            
            if query is None:
                results.append(node.interval)
            else:
                query_type, query_params = query
                if query_type == 'CONTAINED_BY':
                    L, H = query_params
                    if L <= node.interval[0] and node.interval[1] <= H:
                        results.append(node.interval)
                elif query_type == 'INTERSECTS':
                    L, H = query_params
                    if not (node.interval[1] < L or node.interval[0] > H):
                        results.append(node.interval)
                elif query_type == 'RIGHT_OF':
                    x = query_params[0]
                    if x <= node.interval[0]:
                        results.append(node.interval)
            
            results.extend(_search(node.right))
            return results

        return _search(self.root)

    def print_tree(self) -> None:
        def _print_tree(node: Optional[KDNode], prefix: str = '', is_left: bool = True) -> None:
            if not node:
                return

            print(f"{prefix}{'├── ' if is_left else '└── '}{node.interval}")
            
            new_prefix = prefix + ('│   ' if is_left else '    ')
            
            if node.left:
                _print_tree(node.left, new_prefix, True)
            if node.right:
                _print_tree(node.right, new_prefix, False)

        if not self.root:
            print("Empty tree")
            return
        
        print(f"{self.root.interval}")
        if self.root.left:
            _print_tree(self.root.left, '', True)
        if self.root.right:
            _print_tree(self.root.right, '', False)

class IntervalSets:
    def __init__(self):
        self.sets = {}

    def create_set(self, name: str) -> str:
        if not re.match(r'^[a-zA-Z][a-zA-Z0-9_]*$', name):
            raise ValueError("Invalid set name. Must start with a letter and contain only letters, numbers, and underscores")
        if name in self.sets:
            raise ValueError(f"Set '{name}' already exists")
        self.sets[name] = KDTree()
        return f"Set '{name}' has been created"

    def insert(self, set_name: str, interval: List[int]) -> str:
        if set_name not in self.sets:
            raise ValueError(f"Set '{set_name}' does not exist")
        if interval[0] > interval[1]:
            raise ValueError("Lower bound must be less than or equal to upper bound")
        self.sets[set_name].insert(interval)
        return f"Range [{interval[0]}, {interval[1]}] has been added to '{set_name}'"

    def contains(self, set_name: str, interval: List[int]) -> bool:
        if set_name not in self.sets:
            raise ValueError(f"Set '{set_name}' does not exist")
        if interval[0] > interval[1]:
            raise ValueError("Lower bound must be less than or equal to upper bound")
        return self.sets[set_name].contains(interval)

    def search(self, set_name: str, query: Optional[Tuple[str, List[int]]] = None) -> List[List[int]]:
        if set_name not in self.sets:
            raise ValueError(f"Set '{set_name}' does not exist")
        return self.sets[set_name].search(query)

    def print_tree(self, set_name: str) -> None:
        if set_name not in self.sets:
            raise ValueError(f"Set '{set_name}' does not exist")
        self.sets[set_name].print_tree()

def parse_command(command: str) -> Tuple[str, Union[str, Tuple[str, List[int]], Tuple[str, Tuple[str, List[int]]]]]:
    # Удаление комментариев и лишних пробелов
    command = re.sub(r'//.*$', '', command, flags=re.MULTILINE).strip()
    
    # Проверка завершающей точки с запятой
    if not command.endswith(';'):
        raise ValueError("Command must end with ';'")
    command = command[:-1].strip()
    
    # Разбор команд
    create_match = re.match(r'^CREATE\s+([a-zA-Z][a-zA-Z0-9_]*)$', command, re.IGNORECASE)
    if create_match:
        return 'CREATE', create_match.group(1)

    insert_match = re.match(r'^INSERT\s+([a-zA-Z][a-zA-Z0-9_]*)\s*\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\]$', command, re.IGNORECASE)
    if insert_match:
        return 'INSERT', (insert_match.group(1), [int(insert_match.group(2)), int(insert_match.group(3))])

    print_tree_match = re.match(r'^PRINT_TREE\s+([a-zA-Z][a-zA-Z0-9_]*)$', command, re.IGNORECASE)
    if print_tree_match:
        return 'PRINT_TREE', print_tree_match.group(1)

    contains_match = re.match(r'^CONTAINS\s+([a-zA-Z][a-zA-Z0-9_]*)\s*\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\]$', command, re.IGNORECASE)
    if contains_match:
        return 'CONTAINS', (contains_match.group(1), [int(contains_match.group(2)), int(contains_match.group(3))])

    search_match = re.match(
        r'^SEARCH\s+([a-zA-Z][a-zA-Z0-9_]*)(?:\s+WHERE\s+(CONTAINED_BY|INTERSECTS|RIGHT_OF)\s*\[\s*(-?\d+)(?:\s*,\s*(-?\d+))?\s*\])?$',
        command,
        re.IGNORECASE
    )
    if search_match:
        set_name = search_match.group(1)
        query_type = search_match.group(2)
        if not query_type:
            return 'SEARCH', set_name
            
        param1 = int(search_match.group(3))
        param2 = int(search_match.group(4)) if search_match.group(4) else None
        
        if query_type == 'RIGHT_OF':
            return 'SEARCH', (set_name, (query_type, [param1]))
        else:
            if param2 is None:
                raise ValueError(f"Second parameter required for {query_type}")
            return 'SEARCH', (set_name, (query_type, [param1, param2]))

    raise ValueError("Invalid command format")

def main():
    interval_sets = IntervalSets()
    
    print("Interval Sets Management System")
    print("Enter commands ending with ';'. Empty line to process, 'exit;' to quit")
    
    while True:
        try:
            # Считывание многострочной команды
            lines = []
            while True:
                prefix = '> ' if not lines else '... '
                line = input(prefix)
                if not line and not lines:
                    continue
                if not line:
                    break
                lines.append(line)
            
            command = ' '.join(lines)
            if not command:
                continue
            
            if command.strip().lower() == 'exit;':
                break

            # Обработка команды
            cmd_type, params = parse_command(command)
            
            if cmd_type == 'CREATE':
                result = interval_sets.create_set(params)
                print(result)
            
            elif cmd_type == 'INSERT':
                set_name, interval = params
                result = interval_sets.insert(set_name, interval)
                print(result)
            
            elif cmd_type == 'PRINT_TREE':
                interval_sets.print_tree(params)
            
            elif cmd_type == 'CONTAINS':
                set_name, interval = params
                result = interval_sets.contains(set_name, interval)
                print(result)
            
            elif cmd_type == 'SEARCH':
                if isinstance(params, tuple):
                    set_name, query = params
                    results = interval_sets.search(set_name, query)
                else:
                    results = interval_sets.search(params)
                
                if not results:
                    print("No intervals found")
                else:
                    for interval in results:
                        print(interval)
                        
        except ValueError as e:
            print(f"Error: {e}")
        except KeyboardInterrupt:
            print("\nUse 'exit;' to quit")
            continue
        except EOFError:
            break

if __name__ == "__main__":
    main()
