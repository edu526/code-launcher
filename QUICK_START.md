# Quick Start Guide

## Ejecutar el Proyecto

### Opción 1: Ejecutar directamente
```bash
python3 src/main.py
```

### Opción 2: Ejecutar como módulo
```bash
python3 -m src.main
```

## Verificar la Instalación

### 1. Verificar compilación
```bash
python3 -m py_compile src/**/*.py
```

### 2. Ejecutar tests
```bash
python3 -m pytest tests/
```

## Estructura del Proyecto

```
src/
├── main.py                    # Entry point - ejecutar este archivo
├── core/                      # Lógica de negocio
├── ui/                        # Componentes de interfaz
├── dialogs/                   # Diálogos de usuario
└── context_menu/              # Sistema de menú contextual
```

## Archivos de Configuración

Los archivos de configuración se guardan en:
```
~/.config/vscode-launcher/
├── categories.json            # Categorías y subcategorías
└── projects.json              # Proyectos configurados
```

## Desarrollo

### Agregar un nuevo diálogo
1. Crear archivo en `src/dialogs/`
2. Implementar función `show_*_dialog()`
3. Exportar en `src/dialogs/__init__.py`
4. Importar donde sea necesario

### Agregar una nueva acción de menú
1. Agregar función en `src/context_menu/actions.py`
2. Exportar en `src/context_menu/__init__.py`
3. Usar en `src/context_menu/handler.py`

### Modificar la interfaz
1. Editar `src/ui/column_browser.py` para el navegador
2. Editar `src/main.py` para la ventana principal

## Troubleshooting

### Error: ModuleNotFoundError
```bash
# Asegúrate de estar en el directorio raíz del proyecto
cd /path/to/vscode-launcher
python3 src/main.py
```

### Error: No module named 'gi'
```bash
# Instalar PyGObject
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

### Error: No se encuentra VSCode
```bash
# Verificar que VSCode esté instalado
which code

# Si no está instalado, instalar VSCode
# https://code.visualstudio.com/
```

## Documentación Adicional

- `README.md` - Documentación principal del proyecto
- `PROJECT_STRUCTURE.md` - Estructura detallada del código
- `REFACTORING_SUMMARY.md` - Resumen de la refactorización
- `REFACTORING_COMPLETE.md` - Detalles completos de la refactorización
