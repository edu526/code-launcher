# Requirements Document

## Introduction

Este documento especifica los requisitos para implementar menús contextuales (click derecho) en el navegador de columnas estilo Finder del VSCode Project Launcher. El sistema actualmente utiliza botones en el header para crear categorías y proyectos. Esta funcionalidad será reemplazada por menús contextuales que aparecen según el contexto de la columna o item seleccionado, proporcionando una experiencia de usuario más intuitiva y similar a navegadores de archivos modernos.

## Glossary

- **Context_Menu**: Menú emergente que aparece al hacer click derecho, mostrando opciones relevantes al contexto
- **Column_Browser**: Widget GTK que representa una columna individual en la navegación estilo Finder
- **Root_Column**: Primera columna que muestra las categorías principales del sistema
- **Child_Column**: Columna que muestra subcategorías y/o proyectos de una categoría padre
- **Category_Item**: Elemento de la interfaz que representa una categoría o subcategoría en la jerarquía
- **Project_Item**: Elemento de la interfaz que representa un proyecto de VSCode
- **Hierarchy_Path**: Cadena de texto que identifica la posición en la jerarquía (ej: "cat:Web:Frontend")
- **Dialog_Manager**: Módulo que gestiona los diálogos de creación de categorías y proyectos (dialogs.py)

## Requirements

### Requirement 1: Context Menu Display

**User Story:** Como usuario, quiero que aparezca un menú contextual al hacer click derecho en una columna o item, para que pueda acceder rápidamente a las acciones disponibles según el contexto.

#### Acceptance Criteria

1. WHEN a user right-clicks on an empty area of a column, THEN THE System SHALL display a context menu at the cursor position
2. WHEN a user right-clicks on a specific item (category or project), THEN THE System SHALL display a context menu at the cursor position
3. WHEN the context menu is displayed, THEN THE System SHALL prevent the default GTK context menu from appearing
4. WHEN a user clicks outside the context menu, THEN THE System SHALL close the context menu without executing any action
5. WHEN a user presses the Escape key while a context menu is open, THEN THE System SHALL close the context menu

### Requirement 2: Root Column Context Menu

**User Story:** Como usuario, quiero opciones específicas al hacer click derecho en la columna raíz, para que pueda crear categorías principales o agregar proyectos sin categoría.

#### Acceptance Criteria

1. WHEN a user right-clicks on the root column (categories column), THEN THE System SHALL display a menu with "Crear categoría" option
2. WHEN a user right-clicks on the root column, THEN THE System SHALL display a menu with "Agregar proyecto" option
3. WHEN a user selects "Crear categoría" from the root column menu, THEN THE System SHALL open the category creation dialog configured for root level
4. WHEN a user selects "Agregar proyecto" from the root column menu, THEN THE System SHALL open the project creation dialog with no category pre-selected

### Requirement 3: Child Column Context Menu

**User Story:** Como usuario, quiero opciones específicas al hacer click derecho en columnas hijas, para que pueda crear subcategorías o agregar proyectos dentro de la categoría actual.

#### Acceptance Criteria

1. WHEN a user right-clicks on a child column (non-root column), THEN THE System SHALL display a menu with "Agregar subcategoría" option
2. WHEN a user right-clicks on a child column, THEN THE System SHALL display a menu with "Agregar proyecto" option
3. WHEN a user selects "Agregar subcategoría" from a child column menu, THEN THE System SHALL open the category creation dialog pre-configured with the current hierarchy path as parent
4. WHEN a user selects "Agregar proyecto" from a child column menu, THEN THE System SHALL open the project creation dialog with the current category pre-selected

### Requirement 4: Project Item Context Menu

**User Story:** Como usuario, quiero una opción para abrir proyectos al hacer click derecho sobre ellos, para que pueda lanzar VSCode directamente desde el menú contextual.

#### Acceptance Criteria

1. WHEN a user right-clicks on a project item, THEN THE System SHALL display a menu with "Abrir en VSCode" option
2. WHEN a user selects "Abrir en VSCode" from a project item menu, THEN THE System SHALL open the project in VSCode using the existing open_vscode_project function
3. WHEN a project is successfully opened in VSCode, THEN THE System SHALL close the launcher window

### Requirement 5: Category Item Context Menu

**User Story:** Como usuario, quiero poder agregar subcategorías al hacer click derecho sobre una categoría, para que pueda expandir la jerarquía desde cualquier nivel.

#### Acceptance Criteria

1. WHEN a user right-clicks on a category item, THEN THE System SHALL display a menu with "Agregar subcategoría" option
2. WHEN a user selects "Agregar subcategoría" from a category item menu, THEN THE System SHALL open the category creation dialog pre-configured with the selected category as parent
3. WHEN a new subcategory is created from a category item menu, THEN THE System SHALL refresh the interface to show the new subcategory

### Requirement 6: Hierarchy Path Detection

**User Story:** Como desarrollador del sistema, quiero que el sistema detecte automáticamente el nivel de jerarquía actual, para que los menús contextuales puedan pre-configurar correctamente los diálogos de creación.

#### Acceptance Criteria

1. WHEN a context menu is triggered, THE System SHALL determine the current hierarchy path from the column's current_path attribute
2. WHEN a context menu is triggered on a category item, THE System SHALL extract the hierarchy path from the item's full_path attribute
3. WHEN creating a subcategory, THE System SHALL pass the parent hierarchy path to the Dialog_Manager
4. WHEN creating a project, THE System SHALL pass the current category and subcategory information to the Dialog_Manager

### Requirement 7: Dialog Integration

**User Story:** Como usuario, quiero que los diálogos existentes se reutilicen con información pre-configurada, para que la experiencia sea consistente y no tenga que ingresar información redundante.

#### Acceptance Criteria

1. WHEN opening the category creation dialog from a context menu, THE System SHALL reuse the existing show_create_category_dialog function
2. WHEN opening the project creation dialog from a context menu, THE System SHALL reuse the existing show_add_project_dialog function
3. WHEN a context menu pre-configures a dialog, THE Dialog_Manager SHALL populate the parent category field automatically
4. WHEN a context menu pre-configures a dialog, THE Dialog_Manager SHALL disable or hide fields that are already determined by context

### Requirement 8: Header Button Removal

**User Story:** Como usuario, quiero que los botones del header sean removidos, para que la interfaz sea más limpia y toda la gestión se haga mediante menús contextuales.

#### Acceptance Criteria

1. WHEN the application starts, THE System SHALL NOT display the "Crear nueva categoría" button in the header
2. WHEN the application starts, THE System SHALL NOT display the "Añadir nuevo proyecto" button in the header
3. WHEN the application starts, THE System SHALL maintain the configuration button in the header
4. WHEN the application starts, THE System SHALL maintain the "Abrir en VSCode" button in the header for backward compatibility

### Requirement 9: Visual Feedback

**User Story:** Como usuario, quiero retroalimentación visual al interactuar con menús contextuales, para que sepa que el sistema está respondiendo a mis acciones.

#### Acceptance Criteria

1. WHEN a context menu item is hovered, THE System SHALL highlight the menu item
2. WHEN a context menu action is selected, THE System SHALL provide visual feedback before executing the action
3. WHEN a dialog is opened from a context menu, THE System SHALL display the dialog centered on the parent window
4. WHEN an action fails, THE System SHALL display an error dialog with a descriptive message
