from core.graph import Graph
from core.pathfinder import bfs
from core.robot import Robot, SimulationController

print("=" * 50)
print("ТЕСТ 1: Загрузка карты")
print("=" * 50)

g = Graph()
g.load_from_file("maps/default.json")

print(f"Узлов в графе : {len(g.nodes)}")
print(f"Старт         : {g.start}")
print(f"Финиш         : {g.end}")
print(f"Направление   : {g.start_direction}")
print(f"Соседи (0,0)  : {g.get_neighbors((0, 0))}")
print(f"Соседи (2,2)  : {g.get_neighbors((2, 2))}")


print("\n" + "=" * 50)
print("ТЕСТ 2: Поиск маршрута BFS")
print("=" * 50)

path = bfs(g.session_adjacency, g.start, g.end)

if path:
    print(f"Путь найден! Хопов: {len(path) - 1}")
    print(f"Маршрут: {' -> '.join(str(n) for n in path)}")
else:
    print("Путь не найден!")


print("\n" + "=" * 50)
print("ТЕСТ 3: Движение робота по маршруту")
print("=" * 50)

controller = SimulationController()
robot = Robot(g.start, g.start_direction, controller)
robot.set_path(path)

print(f"Старт: pos={robot.pos}, direction={robot.direction}")
print()

step = 0
while robot.has_next_step():
    new_pos = robot.step()
    step += 1
    print(f"  Шаг {step}: pos={robot.pos}, direction={robot.direction}")

print(f"\nРобот достиг финиша: {robot.is_at_goal(g.end)}")


print("\n" + "=" * 50)
print("ТЕСТ 4: QR блокирует путь - перестройка маршрута")
print("=" * 50)


g.reset_session()
robot = Robot(g.start, g.start_direction, controller)

# Робот делает 3 шага вручную
initial_path = bfs(g.session_adjacency, g.start, g.end)
robot.set_path(initial_path)

print(f"Начальный маршрут: {' -> '.join(str(n) for n in initial_path)}")
print()

for _ in range(3):
    robot.step()
    print(f"  -> pos={robot.pos}, direction={robot.direction}")

print(f"\nРобот в узле {robot.pos}. Считываем QR-код...")


qr_data = {"forward": False, "back": False, "left": True, "right": False}
print(f"QR данные: {qr_data}")

g.apply_qr_command(robot.pos, robot.direction, qr_data)

# Перестраиваем маршрут от текущей позиции
new_path = bfs(g.session_adjacency, robot.pos, g.end)

if new_path:
    print(f"\nНовый маршрут: {' -> '.join(str(n) for n in new_path)}")
    robot.set_path(new_path)
else:
    print("\nПути до финиша нет!")


print("\n" + "=" * 50)
print("ТЕСТ 5: Полный тупик (нет пути до финиша)")
print("=" * 50)

g.reset_session()

# Удаляем все рёбра из стартового узла вручную
neighbors = g.get_neighbors(g.start)[:]  # копия чтобы не мутировать во время итерации
for neighbor in neighbors:
    g.remove_edge(g.start, neighbor)

result = bfs(g.session_adjacency, g.start, g.end)
print(f"Результат BFS: {result}")
print(f"Тупик обнаружен корректно: {result is None}")
