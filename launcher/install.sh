#!/bin/bash
#
# Script de instalación para VSCode Launcher
# Este script instala y configura el lanzador de proyectos de VSCode
#

set -e

echo "================================================"
echo "   Instalador de VSCode Launcher"
echo "================================================"
echo ""

# Colores para output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Función para imprimir mensajes
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Verificar si estamos en el directorio correcto
if [ ! -f "vscode-launcher.py" ]; then
    print_error "Error: No se encuentra vscode-launcher.py en el directorio actual"
    exit 1
fi

# 1. Instalar dependencias
echo "1. Verificando dependencias..."

if ! command -v python3 &> /dev/null; then
    print_error "Python3 no está instalado. Por favor, instálalo primero."
    exit 1
fi
print_status "Python3 instalado"

# Verificar e instalar dependencias de GTK
if ! python3 -c "import gi; gi.require_version('Gtk', '3.0'); from gi.repository import Gtk" &> /dev/null; then
    print_warning "python3-gi no está instalado. Instalando..."
    
    if command -v apt &> /dev/null; then
        sudo apt update
        sudo apt install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
    elif command -v dnf &> /dev/null; then
        sudo dnf install -y python3-gobject gtk3 libappindicator-gtk3
    elif command -v pacman &> /dev/null; then
        sudo pacman -S --noconfirm python-gobject gtk3 libappindicator-gtk3
    else
        print_error "No se pudo detectar el gestor de paquetes. Instala manualmente:"
        print_error "  - python3-gi"
        print_error "  - python3-gi-cairo"
        print_error "  - gir1.2-gtk-3.0"
        print_error "  - gir1.2-appindicator3-0.1"
        exit 1
    fi
fi
print_status "Dependencias GTK instaladas"

# Verificar VSCode
if ! command -v code &> /dev/null; then
    print_warning "VSCode no está instalado o no está en PATH"
    print_warning "Asegúrate de tener VSCode instalado para usar el lanzador"
fi

# 2. Crear directorios necesarios
echo ""
echo "2. Creando directorios..."

CONFIG_DIR="$HOME/.config/vscode-launcher"
AUTOSTART_DIR="$HOME/.config/autostart"

mkdir -p "$CONFIG_DIR"
mkdir -p "$AUTOSTART_DIR"

print_status "Directorios creados"

# 3. Copiar archivos
echo ""
echo "3. Instalando archivos..."

# Hacer el script ejecutable
chmod +x vscode-launcher.py

# Copiar el script principal
INSTALL_DIR="$HOME/.local/bin"
mkdir -p "$INSTALL_DIR"
cp vscode-launcher.py "$INSTALL_DIR/"

# Crear script de actualización automática
cat > "$HOME/update-launcher.sh" << 'EOF'
#!/bin/bash
# Script de actualización automática

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE_FILE="$SCRIPT_DIR/vscode-launcher.py"
TARGET_FILE="$HOME/.local/bin/vscode-launcher.py"

echo "🔄 Actualizando VSCode Launcher..."

if [ -f "$SOURCE_FILE" ]; then
    cp "$SOURCE_FILE" "$TARGET_FILE"
    chmod +x "$TARGET_FILE"
    echo "✅ VSCode Launcher actualizado correctamente"
else
    echo "❌ Error: No se encuentra el archivo fuente"
    exit 1
fi
EOF

chmod +x "$HOME/update-launcher.sh"

# Crear hook de git para actualización automática (si es un repo git)
SCRIPT_DIR="$(pwd)"
if [ -d "$SCRIPT_DIR/.git" ]; then
    echo "🔧 Configurando hooks de Git para actualización automática..."
    
    cat > "$SCRIPT_DIR/.git/hooks/post-commit" << 'EOF'
#!/bin/bash
# Hook post-commit: actualizar automáticamente el launcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$HOME/update-launcher.sh"
EOF
    
    chmod +x "$SCRIPT_DIR/.git/hooks/post-commit"
    
    cat > "$SCRIPT_DIR/.git/hooks/post-checkout" << 'EOF'
#!/bin/bash
# Hook post-checkout: actualizar automáticamente el launcher

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
"$HOME/update-launcher.sh"
EOF
    
    chmod +x "$SCRIPT_DIR/.git/hooks/post-checkout"
    
    print_status "Hooks de Git configurados para actualización automática"
fi

print_status "Script instalado en $INSTALL_DIR"
print_status "Sistema de actualización automática configurado"

# Copiar archivo de ejemplo de configuración si no existe
if [ ! -f "$CONFIG_DIR/projects.json" ]; then
    if [ -f "projects.json.example" ]; then
        cp projects.json.example "$CONFIG_DIR/projects.json"
        print_status "Archivo de configuración de ejemplo creado en $CONFIG_DIR/projects.json"
    else
        # Crear archivo de ejemplo por defecto
        cat > "$CONFIG_DIR/projects.json" << 'EOF'
{
  "Ejemplo Proyecto 1": "/ruta/al/proyecto1",
  "Ejemplo Proyecto 2": {
    "path": "/ruta/al/proyecto2",
    "category": "Trabajo"
  },
  "Ejemplo Proyecto 3": {
    "path": "/ruta/al/proyecto3",
    "category": "Personal"
  }
}
EOF
        print_status "Archivo de configuración de ejemplo creado"
    fi
else
    print_warning "Ya existe un archivo de configuración, no se sobrescribirá"
fi

# Copiar archivo desktop para autostart y aplicaciones
sed "s|/home/eduardo/Escritorio/PERSONALES/UTILS/vscode-launcher.py|$INSTALL_DIR/vscode-launcher.py|g" \
    vscode-launcher.desktop > "$AUTOSTART_DIR/vscode-launcher.desktop"

# También crear en applications para el menú
APPLICATIONS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPLICATIONS_DIR"
sed "s|/home/eduardo/Escritorio/PERSONALES/UTILS/vscode-launcher.py|$INSTALL_DIR/vscode-launcher.py|g" \
    vscode-launcher.desktop > "$APPLICATIONS_DIR/vscode-launcher.desktop"

# Crear enlace simbólico para acceso directo desde terminal
ln -sf "$INSTALL_DIR/vscode-launcher.py" "$INSTALL_DIR/vscode-launcher"

print_status "Autostart configurado"
print_status "Acceso directo creado en menú de aplicaciones"

# 4. Configuración final
echo ""
echo "4. Configuración final..."

# Asegurarse de que ~/.local/bin está en PATH
if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    print_warning "~/.local/bin no está en tu PATH"
    print_warning "Añade esta línea a tu ~/.bashrc o ~/.zshrc:"
    echo "    export PATH=\"\$HOME/.local/bin:\$PATH\""
fi

print_status "Instalación completada"

echo ""
echo "================================================"
echo "   ¡Instalación completada con éxito!"
echo "================================================"
echo ""
echo "🎯 Características instaladas:"
echo "   • Sistema de categorías para proyectos"
echo "   • Selector visual de iconos"
echo "   • Búsqueda inteligente de proyectos"
echo "   • Actualización automática con Git"
echo ""
echo "📁 Próximos pasos:"
echo ""
echo "1. Edita tu configuración de proyectos:"
echo "   ${YELLOW}nano $CONFIG_DIR/projects.json${NC}"
echo ""
echo "2. O usa la interfaz gráfica para configurar:"
echo "   • Botón ⚙️ para configurar categorías y proyectos"
echo "   • Botón 📁+ para crear nuevas categorías"
echo "   • Botón + para añadir proyectos"
echo ""
echo "3. Formato de configuración:"
echo "   ${YELLOW}Simple{\"NC}: {\"Nombre\": \"/ruta/al/proyecto\"}"
echo "   ${YELLOW}Con categoría${NC}: {\"Nombre\": {\"path\": \"/ruta\", \"category\": \"Trabajo\"}}"
echo ""
echo "4. Inicia el lanzador:"
echo "   ${YELLOW}vscode-launcher.py${NC} (desde terminal)"
echo "   ${YELLOW}$INSTALL_DIR/vscode-launcher.py &${NC} (directo)"
echo ""
echo "5. O busca 'VSCode Launcher' en tu menú de aplicaciones"
echo ""
echo "🔄 Actualización automática:"
echo "   • Cada git commit/checkout actualiza el launcher"
echo "   • Manual: ${YELLOW}./update-launcher.sh${NC}"
echo ""
