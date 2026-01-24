# Implementation Plan: Context Menu Navigation

## Overview

Este plan implementa menús contextuales (click derecho) para el navegador de columnas estilo Finder, reemplazando los botones del header con una interfaz más intuitiva. La implementación se divide en fases incrementales: primero la detección de contexto y creación de menús, luego la integración con diálogos, y finalmente la limpieza de la UI y testing.

## Tasks

- [x] 1. Create ContextMenuHandler class with context detection
  - Create new file `src/context_menu.py`
  - Implement `ContextMenuHandler` class with `__init__` method
  - Implement `detect_context()` method to identify context type from event
  - Implement `get_hierarchy_info()` helper to parse hierarchy paths
  - Add context type constants: ROOT_COLUMN, CHILD_COLUMN, CATEGORY_ITEM, PROJECT_ITEM
  - _Requirements: 1.1, 1.2, 6.1, 6.2_

- [ ]* 1.1 Write property test for hierarchy path extraction
  - **Property 4: Hierarchy Path Extraction**
  - **Validates: Requirements 6.1, 6.2**

- [ ] 2. Implement context menu creation and display
  - [x] 2.1 Implement `create_context_menu()` method in ContextMenuHandler
    - Create GTK.Menu based on context type
    - Add appropriate menu items for each context type
    - Connect menu item signals to callback methods
    - _Requirements: 2.1, 2.2, 3.1, 3.2, 4.1, 5.1_

  - [ ]* 2.2 Write property test for context-appropriate menu contents
    - **Property 2: Context-Appropriate Menu Contents**
    - **Validates: Requirements 2.1, 2.2, 3.1, 3.2, 4.1, 5.1**

  - [x] 2.3 Implement `show_menu()` method to display menu at cursor position
    - Use `menu.popup()` with event coordinates
    - Handle menu positioning edge cases
    - _Requirements: 1.1, 1.2_

  - [x] 2.4 Implement `on_button_press()` event handler
    - Detect right-click (button == 3)
    - Call detect_context() and create_context_menu()
    - Return True to prevent default GTK menu
    - Add error handling with try-except
    - _Requirements: 1.3, 1.4, 1.5_

- [ ]* 2.5 Write unit tests for menu display behavior
  - Test right-click on empty column area
  - Test right-click on specific items
  - Test Escape key closes menu
  - Test click outside closes menu
  - _Requirements: 1.1, 1.2, 1.4, 1.5_

- [ ] 3. Integrate ContextMenuHandler with ColumnBrowser
  - [x] 3.1 Add context menu setup to ColumnBrowser.__init__
    - Create ContextMenuHandler instance
    - Store reference to parent_window
    - Connect button-press-event signal to handler
    - _Requirements: 1.1, 1.2_

  - [x] 3.2 Add helper methods to ColumnBrowser
    - Implement `get_item_at_position(x, y)` to find item under cursor
    - Implement `is_root_column()` to check if column is root
    - Implement `get_hierarchy_info()` to extract hierarchy from current_path
    - _Requirements: 6.1, 6.2_

  - [ ]* 3.3 Write property test for item position detection
    - Test get_item_at_position with random coordinates
    - Verify correct item or None is returned
    - _Requirements: 6.1, 6.2_

- [x] 4. Checkpoint - Ensure basic context menu functionality works
  - Ensure all tests pass, ask the user if questions arise.

- [ ] 5. Extend Dialogs module for pre-configuration
  - [x] 5.1 Modify show_create_category_dialog signature
    - Add optional `pre_config` parameter (dict)
    - Extract parent_category, force_subcategory, hierarchy_path from pre_config
    - Pre-populate parent category combo if provided
    - Set dialog mode (category vs subcategory) if forced
    - Disable parent selection if pre-configured
    - _Requirements: 7.1, 7.3, 7.4_

  - [x] 5.2 Modify show_add_project_dialog signature
    - Add optional `pre_config` parameter (dict)
    - Extract category, subcategory, hierarchy_path from pre_config
    - Pre-select category combo if provided
    - Pre-select subcategory combo if provided
    - Disable category/subcategory selection if pre-configured
    - _Requirements: 7.2, 7.3, 7.4_

  - [ ]* 5.3 Write property test for dialog pre-configuration
    - **Property 3: Dialog Pre-configuration from Context**
    - **Validates: Requirements 2.3, 2.4, 3.3, 3.4, 5.2, 6.3, 6.4, 7.3**

- [ ] 6. Implement context menu action handlers
  - [x] 6.1 Implement create_category_action in ContextMenuHandler
    - Extract hierarchy info from context
    - Build pre_config dict with parent category
    - Call Dialogs.show_create_category_dialog with pre_config
    - Pass parent_window.on_create_category_callback
    - _Requirements: 2.3, 3.3, 5.2_

  - [x] 6.2 Implement add_project_action in ContextMenuHandler
    - Extract hierarchy info from context
    - Build pre_config dict with category and subcategory
    - Call Dialogs.show_add_project_dialog with pre_config
    - Pass parent_window.on_add_project_callback
    - _Requirements: 2.4, 3.4_

  - [x] 6.3 Implement open_vscode_action in ContextMenuHandler
    - Extract project path from context
    - Call parent_window.open_vscode_project(path)
    - Handle success/failure appropriately
    - _Requirements: 4.2, 4.3_

  - [ ]* 6.4 Write property test for VSCode project opening
    - **Property 5: VSCode Project Opening**
    - **Validates: Requirements 4.2, 4.3**

  - [ ]* 6.5 Write property test for interface refresh after creation
    - **Property 6: Interface Refresh After Creation**
    - **Validates: Requirements 5.3**

- [ ] 7. Add error handling and visual feedback
  - [x] 7.1 Implement error dialog display in ContextMenuHandler
    - Add show_error_dialog method
    - Create GTK.MessageDialog for errors
    - Center dialog on parent window
    - _Requirements: 9.3, 9.4_

  - [x] 7.2 Add error handling to all action handlers
    - Wrap action handlers in try-except blocks
    - Log errors with descriptive messages
    - Show error dialog on failure
    - _Requirements: 9.4_

  - [x] 7.3 Ensure dialogs are centered on parent window
    - Set transient_for property on all dialogs
    - Set window position to CENTER_ON_PARENT
    - _Requirements: 9.3_

  - [ ]* 7.4 Write property test for error dialog display
    - **Property 8: Error Dialog on Failure**
    - **Validates: Requirements 9.4**

  - [ ]* 7.5 Write property test for dialog centering
    - **Property 7: Dialog Centering**
    - **Validates: Requirements 9.3**

- [ ] 8. Remove header buttons from FinderStyleWindow
  - [x] 8.1 Remove "Crear nueva categoría" button from setup_ui
    - Delete create_category_btn creation code
    - Delete button signal connection
    - Delete on_create_category_clicked method
    - _Requirements: 8.1_

  - [x] 8.2 Remove "Añadir nuevo proyecto" button from setup_ui
    - Delete add_project_btn creation code
    - Delete button signal connection
    - Delete on_add_project_clicked method
    - _Requirements: 8.2_

  - [x] 8.3 Verify configuration and open buttons remain
    - Ensure config_btn is still created and functional
    - Ensure open_btn is still created and functional
    - _Requirements: 8.3, 8.4_

  - [ ]* 8.4 Write unit tests for header button state
    - Test "Crear nueva categoría" button is not present
    - Test "Añadir nuevo proyecto" button is not present
    - Test configuration button is present
    - Test "Abrir en VSCode" button is present
    - _Requirements: 8.1, 8.2, 8.3, 8.4_

- [ ] 9. Final integration and testing
  - [x] 9.1 Test complete workflow: root column → create category
    - Right-click on root column
    - Select "Crear categoría"
    - Verify dialog opens with no parent
    - Create category and verify it appears
    - _Requirements: 2.1, 2.3_

  - [x] 9.2 Test complete workflow: child column → create subcategory
    - Navigate to child column
    - Right-click on column
    - Select "Agregar subcategoría"
    - Verify dialog opens with correct parent
    - Create subcategory and verify it appears
    - _Requirements: 3.1, 3.3, 5.3_

  - [x] 9.3 Test complete workflow: category item → add subcategory
    - Right-click on category item
    - Select "Agregar subcategoría"
    - Verify dialog opens with category as parent
    - Create subcategory and verify it appears
    - _Requirements: 5.1, 5.2, 5.3_

  - [x] 9.4 Test complete workflow: project item → open in VSCode
    - Right-click on project item
    - Select "Abrir en VSCode"
    - Verify VSCode opens with correct project
    - Verify launcher window closes
    - _Requirements: 4.1, 4.2, 4.3_

  - [x] 9.5 Test complete workflow: add project from context menu
    - Right-click on child column
    - Select "Agregar proyecto"
    - Verify dialog opens with category pre-selected
    - Add project and verify it appears
    - _Requirements: 3.2, 3.4_

- [x] 10. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Checkpoints ensure incremental validation
- Property tests validate universal correctness properties with minimum 100 iterations
- Unit tests validate specific examples and edge cases
- The implementation reuses existing dialog functions with pre-configuration
- Error handling is integrated throughout to ensure robustness
