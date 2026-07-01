# Итоговая структура для запуска (maps вручную добавляем):

```
/
├── RobotSim.exe              (обычный режим)
├── RobotSim_debug.exe        (дебаг режим)
└── maps/
    └── default.json

```

## Структура проекта перед сборкой

```
robot_simulation/
├── main.py
├── build_normal.spec
├── build_debug.spec
├── debug_hook.py
├── core/
├── gui/
│   └── main_window.py
├── qr/
└── maps/
    └── default.json
```

## Команды сборки

```bash
uv add pyinstaller

pyinstaller build_normal.spec

pyinstaller build_debug.spec
```

## Добавление новых карт

```
python generate_map.py
```

Вручную меняем параметры для генерации карт:

```python
ROWS = 5
COLS = 5

START = [0, 0]  # стартовый узел [row, col]
END = [ROWS - 1, COLS - 1]  # финишный узел  [row, col]
START_DIR = "east"  # начальное направление робота
# ("north" | "south" | "east" | "west")

# Вероятность того, что ребро между соседними узлами СУЩЕСТВУЕТ (0.0 – 1.0)
# При 1.0 - полная сетка
EDGE_PROB = 0.75

# Гарантировать существование пути от START до END?
# Если True - после генерации проверяем BFS и при необходимости
# досыпаем рёбра вдоль одного из кратчайших путей
ENSURE_PATH = True

# Вероятность того, что узел сетки вообще существует (0.0 – 1.0)
# При 1.0 - все клетки сетки заняты узлами
# START и END всегда существуют независимо от этого параметра
NODE_PROB = 0.90

OUTPUT_FILE = "maps/default.json"  # куда сохранить результат

RANDOM_SEED = None  # int для воспроизводимости, None - каждый раз новая карта
```
