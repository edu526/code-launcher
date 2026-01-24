# VSCode Project Launcher

Sistema de acceso rápido a proyectos de VSCode desde la barra superior de GNOME en Linux.

## Características

- Icono en la barra superior (system tray) con acceso rápido a tus proyectos
- Soporte para múltiples directorios de proyectos
- Organización por categorías con submenús
- Configuración sencilla mediante archivo JSON
- Inicio automático al iniciar sesión
- Recarga de proyectos sin reiniciar

## Requisitos

- Linux con entorno de escritorio GNOME
- Python 3
- VSCode instalado
- Bibliotecas GTK3 y AppIndicator3

## Instalación

1. Navega al directorio del proyecto:
   ```bash
   cd /home/eduardo/Escritorio/PERSONALES/UTILS
   ```

2. Ejecuta el script de instalación:
   ```bash
   ./install.sh
   ```

   El script instalará automáticamente todas las dependencias necesarias y configurará el sistema.

## Configuración de Proyectos

Edita el archivo de configuración ubicado en `~/.config/vscode-launcher/projects.json`

### Formato Simple

Para proyectos sin categoría:

```json
{
  "Mi Proyecto": "/ruta/completa/al/proyecto"
}
```

### Formato con Categorías

Para organizar proyectos en categorías con submenús:

```json
{
  "Proyecto Personal 1": {
    "path": "/home/usuario/proyectos/personal1",
    "category": "Personal"
  },
  "Proyecto Trabajo 1": {
    "path": "/home/usuario/trabajo/proyecto1",
    "category": "Trabajo"
  },
  "Proyecto Open Source": {
    "path": "/home/usuario/github/proyecto",
    "category": "Open Source"
  }
}
```

### Ejemplo Completo

```json
{
  "Utils": "/home/eduardo/Escritorio/PERSONALES/UTILS",
  "Mi Web Personal": {
    "path": "/home/eduardo/proyectos/web-personal",
    "category": "Personal"
  },
  "API REST": {
    "path": "/home/eduardo/trabajo/api-rest",
    "category": "Trabajo"
  },
  "Cliente Mobile": {
    "path": "/home/eduardo/trabajo/mobile-app",
    "category": "Trabajo"
  },
  "Librería Python": {
    "path": "/home/eduardo/github/mi-libreria",
    "category": "Open Source"
  }
}
```

## Uso

### Iniciar Manualmente

```bash
~/.local/bin/vscode-launcher.py &
```

### Inicio Automático

El script se inicia automáticamente al iniciar sesión. Si no aparece, cierra sesión y vuelve a entrar.

### Acceso a Proyectos

1. Busca el icono de VSCode en la barra superior
2. Haz clic para ver el menú con tus proyectos
3. Si organizaste por categorías, verás submenús
4. Selecciona un proyecto para abrirlo en VSCode

### Recargar Proyectos

Después de editar el archivo de configuración:

1. Haz clic en el icono de VSCode
2. Selecciona "↻ Recargar proyectos"

### Editar Configuración

Desde el menú del icono:
- Selecciona "⚙ Editar configuración"
- Se abrirá el archivo JSON en tu editor predeterminado

## Desinstalación

```bash
# Eliminar archivos instalados
rm ~/.local/bin/vscode-launcher.py
rm ~/.config/autostart/vscode-launcher.desktop
rm -rf ~/.config/vscode-launcher

# Detener el proceso actual
pkill -f vscode-launcher.py
```

## Solución de Problemas

### El icono no aparece

1. Verifica que las dependencias estén instaladas:
   ```bash
   python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk"
   ```

2. Revisa si el proceso está corriendo:
   ```bash
   ps aux | grep vscode-launcher
   ```

3. Inicia manualmente para ver errores:
   ```bash
   ~/.local/bin/vscode-launcher.py
   ```

### VSCode no se abre

- Verifica que VSCode esté instalado:
  ```bash
  which code
  ```

- Si usas VSCode Insiders, edita `vscode-launcher.py` y cambia `'code'` por `'code-insiders'`

### Las rutas no funcionan

- Asegúrate de usar rutas absolutas completas (no rutas relativas)
- Puedes usar `~` para el directorio home, será expandido automáticamente
- Verifica que los directorios existan

## Estructura de Archivos

```
/home/eduardo/Escritorio/PERSONALES/UTILS/
├── vscode-launcher.py          # Script principal
├── vscode-launcher.desktop     # Archivo desktop para autostart
├── projects.json.example       # Ejemplo de configuración
├── install.sh                  # Script de instalación
└── README.md                   # Esta documentación

~/.config/vscode-launcher/
└── projects.json               # Tu configuración de proyectos

~/.config/autostart/
└── vscode-launcher.desktop     # Autostart del launcher

~/.local/bin/
└── vscode-launcher.py          # Script instalado
```

## Personalización

### Cambiar el Icono

Edita `vscode-launcher.py` y modifica la línea:
```python
ICON_NAME = "code"  # Cambia por otro icono del sistema
```

Iconos disponibles: `folder`, `applications-development`, `utilities-terminal`, etc.

### Añadir Funcionalidades

El script es fácilmente extensible. Puedes añadir:
- Comandos personalizados
- Integración con otros editores
- Scripts de inicialización por proyecto
- Notificaciones de escritorio

## Licencia

Libre para uso personal y comercial.
