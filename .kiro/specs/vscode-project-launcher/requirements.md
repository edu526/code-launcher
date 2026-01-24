# Documento de Requisitos

## Introducción

VSCode Project Launcher es una aplicación de escritorio para Linux/GNOME que proporciona un lanzador visual de proyectos para Visual Studio Code. La aplicación utiliza una interfaz de navegación por columnas estilo Finder (macOS) que permite a los usuarios organizar sus proyectos en una jerarquía de categorías y subcategorías, facilitando el acceso rápido a proyectos mediante búsqueda inteligente y navegación visual.

## Glosario

- **Sistema**: VSCode Project Launcher
- **Usuario**: Desarrollador que utiliza la aplicación para gestionar y abrir proyectos
- **Proyecto**: Directorio en el sistema de archivos que contiene código fuente
- **Categoría**: Agrupación lógica que puede contener subcategorías y proyectos
- **Columna**: Panel vertical en la interfaz que muestra categorías o proyectos
- **Navegación_Finder**: Estilo de navegación por columnas donde cada selección expande una nueva columna a la derecha
- **ConfigManager**: Componente que gestiona la persistencia de configuración en archivos JSON
- **ColumnBrowser**: Componente visual que representa una columna individual en la interfaz
- **FinderStyleWindow**: Ventana principal de la aplicación
- **VSCode**: Visual Studio Code, el editor de código que se lanza desde la aplicación

## Requisitos

### Requisito 1: Navegación por Categorías

**Historia de Usuario:** Como usuario, quiero navegar por mis proyectos organizados en categorías jerárquicas, para poder encontrar proyectos de manera intuitiva.

#### Criterios de Aceptación

1. CUANDO el usuario inicia la aplicación, EL Sistema DEBERÁ mostrar la primera columna con las categorías principales
2. CUANDO el usuario selecciona una categoría, EL Sistema DEBERÁ cargar una nueva columna a la derecha mostrando sus subcategorías y proyectos
3. CUANDO el usuario selecciona una categoría diferente en una columna anterior, EL Sistema DEBERÁ eliminar todas las columnas posteriores y cargar el nuevo contenido
4. EL Sistema DEBERÁ permitir navegación ilimitada en profundidad de categorías
5. CUANDO una categoría tiene un icono personalizado, EL Sistema DEBERÁ mostrar el icono del sistema junto al nombre de la categoría

### Requisito 2: Gestión de Proyectos

**Historia de Usuario:** Como usuario, quiero añadir, editar y eliminar proyectos, para mantener mi lista de proyectos actualizada.

#### Criterios de Aceptación

1. CUANDO el usuario hace clic en "Añadir Proyecto", EL Sistema DEBERÁ mostrar un diálogo para seleccionar el directorio del proyecto y asignarlo a una categoría
2. CUANDO el usuario proporciona un path de proyecto, EL Sistema DEBERÁ validar que el directorio existe
3. CUANDO el usuario proporciona un path relativo con `~`, EL Sistema DEBERÁ expandirlo a la ruta absoluta del home del usuario
4. CUANDO el usuario guarda un proyecto, EL Sistema DEBERÁ persistir la información en el archivo projects.json
5. EL Sistema DEBERÁ permitir editar el nombre y categoría de proyectos existentes
6. EL Sistema DEBERÁ permitir eliminar proyectos de la configuración

### Requisito 3: Gestión de Categorías

**Historia de Usuario:** Como usuario, quiero crear y organizar categorías jerárquicas, para estructurar mis proyectos de manera lógica.

#### Criterios de Aceptación

1. CUANDO el usuario hace clic en "Crear Categoría", EL Sistema DEBERÁ mostrar un diálogo para ingresar nombre, categoría padre e icono
2. CUANDO el usuario selecciona un icono, EL Sistema DEBERÁ mostrar iconos disponibles del tema del sistema
3. CUANDO el usuario guarda una categoría, EL Sistema DEBERÁ persistir la información en el archivo categories.json
4. EL Sistema DEBERÁ permitir crear categorías sin padre (categorías raíz)
5. EL Sistema DEBERÁ permitir crear subcategorías asignando una categoría padre
6. CUANDO el usuario elimina una categoría, EL Sistema DEBERÁ reasignar o eliminar proyectos y subcategorías asociadas

### Requisito 4: Lanzamiento de Proyectos en VSCode

**Historia de Usuario:** Como usuario, quiero abrir proyectos en VSCode con un doble clic o botón, para comenzar a trabajar rápidamente.

#### Criterios de Aceptación

1. CUANDO el usuario hace doble clic en un proyecto, EL Sistema DEBERÁ lanzar VSCode con el directorio del proyecto
2. CUANDO el usuario selecciona un proyecto y hace clic en "Abrir en VSCode", EL Sistema DEBERÁ lanzar VSCode con el directorio del proyecto
3. CUANDO el path del proyecto no existe, EL Sistema DEBERÁ mostrar un mensaje de error y no intentar lanzar VSCode
4. EL Sistema DEBERÁ utilizar el comando `code` para lanzar VSCode
5. CUANDO VSCode no está instalado, EL Sistema DEBERÁ manejar el error apropiadamente

### Requisito 5: Búsqueda de Proyectos

**Historia de Usuario:** Como usuario, quiero buscar proyectos por nombre en tiempo real, para acceder rápidamente sin navegar por categorías.

#### Criterios de Aceptación

1. CUANDO el usuario escribe en el campo de búsqueda, EL Sistema DEBERÁ filtrar proyectos en tiempo real
2. CUANDO hay resultados de búsqueda, EL Sistema DEBERÁ mostrar solo los proyectos que coinciden con el término de búsqueda
3. CUANDO el usuario borra el término de búsqueda, EL Sistema DEBERÁ restaurar la vista de navegación por categorías
4. EL Sistema DEBERÁ realizar búsqueda insensible a mayúsculas/minúsculas
5. EL Sistema DEBERÁ buscar coincidencias parciales en el nombre del proyecto

### Requisito 6: Persistencia de Configuración

**Historia de Usuario:** Como usuario, quiero que mis proyectos y categorías se guarden automáticamente, para no perder mi configuración al cerrar la aplicación.

#### Criterios de Aceptación

1. CUANDO el usuario añade o modifica un proyecto, EL Sistema DEBERÁ guardar los cambios en projects.json inmediatamente
2. CUANDO el usuario añade o modifica una categoría, EL Sistema DEBERÁ guardar los cambios en categories.json inmediatamente
3. CUANDO la aplicación inicia, EL Sistema DEBERÁ cargar la configuración desde los archivos JSON
4. CUANDO los archivos de configuración no existen, EL Sistema DEBERÁ crear archivos con configuración por defecto
5. EL Sistema DEBERÁ validar la estructura JSON al cargar la configuración

### Requisito 7: Instancia Única de Aplicación

**Historia de Usuario:** Como usuario, quiero que solo se ejecute una instancia de la aplicación, para evitar conflictos y confusión.

#### Criterios de Aceptación

1. CUANDO el usuario intenta lanzar la aplicación, EL Sistema DEBERÁ verificar si ya existe una instancia en ejecución
2. CUANDO ya existe una instancia, EL Sistema DEBERÁ enfocar la ventana existente y no crear una nueva instancia
3. EL Sistema DEBERÁ utilizar un mecanismo de lock de archivo para detectar instancias en ejecución
4. CUANDO la aplicación se cierra, EL Sistema DEBERÁ liberar el lock de archivo

### Requisito 8: Autostart en GNOME

**Historia de Usuario:** Como usuario, quiero que la aplicación se inicie automáticamente al iniciar sesión, para tener acceso inmediato a mis proyectos.

#### Criterios de Aceptación

1. CUANDO el usuario instala la aplicación, EL Sistema DEBERÁ crear un archivo .desktop en ~/.config/autostart/
2. CUANDO el usuario inicia sesión en GNOME, EL Sistema DEBERÁ lanzarse automáticamente
3. EL Sistema DEBERÁ permitir deshabilitar el autostart mediante configuración
4. EL archivo .desktop DEBERÁ contener la ruta correcta al ejecutable de la aplicación

### Requisito 9: Actualización Automática con Git

**Historia de Usuario:** Como usuario, quiero que la aplicación se actualice automáticamente desde el repositorio, para tener siempre la última versión.

#### Criterios de Aceptación

1. CUANDO hay cambios en el repositorio Git, EL Sistema DEBERÁ detectarlos mediante hooks de Git
2. CUANDO se detectan cambios, EL Sistema DEBERÁ ejecutar `git pull` para actualizar el código
3. CUANDO la actualización es exitosa, EL Sistema DEBERÁ reiniciar la aplicación automáticamente
4. CUANDO la actualización falla, EL Sistema DEBERÁ registrar el error y continuar con la versión actual

### Requisito 10: Interfaz Gráfica GTK3

**Historia de Usuario:** Como usuario, quiero una interfaz gráfica nativa de GNOME, para una experiencia consistente con mi entorno de escritorio.

#### Criterios de Aceptación

1. EL Sistema DEBERÁ utilizar GTK3 para todos los componentes de interfaz
2. EL Sistema DEBERÁ utilizar TreeView para mostrar listas de categorías y proyectos
3. EL Sistema DEBERÁ utilizar diálogos nativos de GTK para selección de archivos y confirmaciones
4. EL Sistema DEBERÁ respetar el tema GTK del sistema
5. CUANDO el usuario redimensiona la ventana, EL Sistema DEBERÁ ajustar los componentes apropiadamente

### Requisito 11: Validación de Paths

**Historia de Usuario:** Como usuario, quiero que la aplicación valide los paths de proyectos, para evitar errores al intentar abrir proyectos inexistentes.

#### Criterios de Aceptación

1. CUANDO el usuario añade un proyecto, EL Sistema DEBERÁ validar que el path existe en el sistema de archivos
2. CUANDO el usuario intenta abrir un proyecto, EL Sistema DEBERÁ verificar que el path sigue existiendo
3. CUANDO un path contiene `~`, EL Sistema DEBERÁ expandirlo a la ruta absoluta del home
4. CUANDO un path es relativo, EL Sistema DEBERÁ resolverlo a ruta absoluta
5. CUANDO un path no es válido, EL Sistema DEBERÁ mostrar un mensaje de error descriptivo

### Requisito 12: Instalación y Dependencias

**Historia de Usuario:** Como usuario, quiero instalar la aplicación fácilmente con todas sus dependencias, para comenzar a usarla rápidamente.

#### Criterios de Aceptación

1. EL Sistema DEBERÁ proporcionar un script de instalación (install.sh)
2. CUANDO el usuario ejecuta el script de instalación, EL Sistema DEBERÁ verificar e instalar dependencias de Python
3. CUANDO el usuario ejecuta el script de instalación, EL Sistema DEBERÁ verificar la presencia de GTK3 y AppIndicator3
4. EL Sistema DEBERÁ requerir Python 3, GTK3, AppIndicator3 y VSCode como dependencias
5. CUANDO faltan dependencias, EL Sistema DEBERÁ informar al usuario qué paquetes instalar
