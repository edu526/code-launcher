# Flujo de Trabajo para Releases

## Resumen

Este documento explica el flujo de trabajo recomendado para crear releases automáticos de Code Launcher.

## Filosofía del Sistema

**El tag es la única fuente de verdad para la versión.**

Los archivos de versión en el repositorio (setup.py, build scripts) son informativos, pero el workflow siempre usa la versión del tag para construir los paquetes.

## Proceso de Release (Paso a Paso)

### 1. Preparar el Código

Asegúrate de que todo el código esté listo y testeado en la rama `main`:

```bash
# Asegúrate de estar en main
git checkout main
git pull origin main

# Verifica que todo funciona
python3 -m pytest tests/
```

### 2. Actualizar Versiones (Opcional pero Recomendado)

Puedes actualizar las versiones en los archivos para mantener consistencia:

```bash
# Usa el script de actualización de versión
.github/scripts/update_version.sh 1.0.3

# Revisa los cambios
git diff

# Haz commit de los cambios
git add setup.py packaging/*.sh README.md
git commit -m "chore: bump version to 1.0.3"
git push origin main
```

**Nota:** Este paso es opcional. Si no actualizas los archivos, el workflow mostrará advertencias pero funcionará perfectamente usando la versión del tag.

### 3. Crear y Pushear el Tag

```bash
# Crea el tag con la versión deseada
git tag v1.0.3

# Pushea el tag a GitHub
git push origin v1.0.3
```

### 4. Monitorear el Workflow

1. Ve a tu repositorio en GitHub
2. Click en la pestaña "Actions"
3. Verás un nuevo workflow "Release Build" ejecutándose
4. Click en él para ver el progreso

### 5. Verificar el Release

Una vez que el workflow termine (5-10 minutos):

1. Ve a la pestaña "Releases" en GitHub
2. Deberías ver el nuevo release `v1.0.3`
3. Verifica que tenga:
   - ✅ Release notes con los commits
   - ✅ Archivo DEB: `code-launcher_1.0.3_all.deb`
   - ✅ Archivo AppImage: `CodeLauncher-1.0.3-x86_64.AppImage`

### 6. Probar los Paquetes

Descarga y prueba ambos paquetes:

```bash
# Descargar DEB
wget https://github.com/TU_USUARIO/code-launcher/releases/download/v1.0.3/code-launcher_1.0.3_all.deb

# Instalar y probar
sudo dpkg -i code-launcher_1.0.3_all.deb
code-launcher

# Descargar AppImage
wget https://github.com/TU_USUARIO/code-launcher/releases/download/v1.0.3/CodeLauncher-1.0.3-x86_64.AppImage

# Hacer ejecutable y probar
chmod +x CodeLauncher-1.0.3-x86_64.AppImage
./CodeLauncher-1.0.3-x86_64.AppImage
```

## Qué Hace el Workflow Automáticamente

Cuando pusheas un tag `v1.0.3`, el workflow:

1. **Extrae la versión** del tag (1.0.3)
2. **Verifica** si los archivos de versión coinciden (solo informativo)
3. **Construye en paralelo**:
   - Paquete DEB con versión 1.0.3
   - Paquete AppImage con versión 1.0.3
4. **Genera release notes** automáticamente desde los commits
5. **Crea el release** en GitHub
6. **Sube ambos paquetes** como assets del release

## Ventajas de Este Enfoque

✅ **Simple**: Solo necesitas crear y pushear un tag
✅ **Confiable**: No hay problemas con permisos o estados de git
✅ **Flexible**: Puedes actualizar versiones en archivos o no, funciona igual
✅ **Rápido**: Builds en paralelo reducen el tiempo total
✅ **Automático**: Release notes generados automáticamente

## Solución de Problemas

### El workflow no se ejecuta

**Problema**: Pusheaste un tag pero no pasa nada

**Solución**:
1. Verifica que el tag siga el formato `v*.*.*` (ej: v1.0.3)
2. Verifica que GitHub Actions esté habilitado en tu repositorio
3. Verifica que el archivo `.github/workflows/release.yml` esté en la rama main

### El build falla

**Problema**: El workflow falla en el paso de build

**Solución**:
1. Click en el workflow fallido para ver los logs
2. Identifica qué paso falló
3. Problemas comunes:
   - Dependencias faltantes: Verifica que los scripts de build funcionen localmente
   - Errores de sintaxis: Ejecuta `python3 -m pytest tests/` localmente

### El release se crea pero sin paquetes

**Problema**: El release existe pero no tiene los archivos adjuntos

**Solución**:
1. Verifica que ambos jobs de build completaron exitosamente
2. Revisa los logs del job `create-release`
3. Puede ser un problema temporal de GitHub API - intenta de nuevo

### Quiero borrar un release de prueba

```bash
# Borrar el release en GitHub (vía web o CLI)
gh release delete v1.0.3 --yes

# Borrar el tag localmente
git tag -d v1.0.3

# Borrar el tag remotamente
git push origin :refs/tags/v1.0.3
```

## Comandos Útiles

```bash
# Ver todos los tags
git tag -l

# Ver el último tag
git describe --tags --abbrev=0

# Crear tag anotado con mensaje
git tag -a v1.0.3 -m "Release version 1.0.3"

# Ver información de un tag
git show v1.0.3

# Listar releases con GitHub CLI
gh release list

# Ver detalles de un release
gh release view v1.0.3
```

## Ejemplo Completo

```bash
# 1. Preparar código
git checkout main
git pull origin main

# 2. Actualizar versiones (opcional)
.github/scripts/update_version.sh 1.0.3
git add setup.py packaging/*.sh README.md
git commit -m "chore: bump version to 1.0.3"
git push origin main

# 3. Crear y pushear tag
git tag v1.0.3
git push origin v1.0.3

# 4. Esperar ~5-10 minutos

# 5. Verificar en GitHub:
# - Actions tab: workflow completado ✅
# - Releases tab: nuevo release v1.0.3 ✅

# 6. Descargar y probar
wget https://github.com/TU_USUARIO/code-launcher/releases/download/v1.0.3/code-launcher_1.0.3_all.deb
sudo dpkg -i code-launcher_1.0.3_all.deb
code-launcher
```

## Resumen

**Para crear un release:**
1. Actualiza versiones en archivos (opcional)
2. Crea tag: `git tag v1.0.3`
3. Pushea tag: `git push origin v1.0.3`
4. ¡Listo! El workflow hace el resto automáticamente

**El tag es la fuente de verdad - los builds siempre usan la versión del tag.**
