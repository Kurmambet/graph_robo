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
