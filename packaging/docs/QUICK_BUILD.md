# Quick Build Guide

## 🚀 Available Options

### 1️⃣ Local Installation (Fastest)
```bash
make install
```
✅ Ideal for development
✅ Automatic update with Git
✅ Size: ~100 KB
⏱️ Time: 10 seconds

---

### 2️⃣ Executable Binary
```bash
make binary
```
✅ Single file
✅ Doesn't require Python installed
📦 Size: ~50-100 MB
⏱️ Time: 1-2 minutes

**Install:**
```bash
sudo cp dist/code-launcher /usr/local/bin/
```

---

### 3️⃣ DEB Package
```bash
make deb
```
✅ Automatic dependency management
✅ Easy installation/uninstallation
📦 Size: ~50 KB
⏱️ Time: 5 seconds

**Install:**
```bash
sudo dpkg -i code-project-launcher_1.0.0_all.deb
sudo apt-get install -f
```

---

### 4️⃣ AppImage (Portable)
```bash
make appimage
```
✅ Works on any distribution
✅ Doesn't require installation
✅ Portable
📦 Size: ~100-150 MB
⏱️ Time: 2-3 minutes

**Use:**
```bash
chmod +x CodeLauncher-1.0.0-x86_64.AppImage
./CodeLauncher-1.0.0-x86_64.AppImage
```

---

### 5️⃣ Create Everything
```bash
make all
```
Creates: Binary + DEB + AppImage
⏱️ Time: 3-5 minutes

---

## 🧹 Clean Up

```bash
make clean
```

Removes all build files.

---

## 📊 Quick Comparison

| Method | Size | Installation | Portability | Best For |
|--------|------|--------------|-------------|----------|
| **Local** | 100 KB | Very easy | Low | Development |
| **Binary** | 50-100 MB | Easy | Medium | Simple distribution |
| **DEB** | 50 KB | Very easy | Low | Debian/Ubuntu |
| **AppImage** | 100-150 MB | Not required | High | Universal |

---

## 💡 Recommendations

- **Developing?** → `make install`
- **Debian/Ubuntu?** → `make deb`
- **Any distro?** → `make appimage`
- **Maximum simplicity?** → `make binary`

---

## ⚠️ Requirements

### To run:
```bash
# Debian/Ubuntu
sudo apt install python3 python3-gi gir1.2-gtk-3.0

# Fedora
sudo dnf install python3 python3-gobject gtk3

# Arch
sudo pacman -S python python-gobject gtk3
```

### To build:
```bash
# PyInstaller (binary)
pip3 install pyinstaller

# dpkg-deb (DEB) - already installed on Debian/Ubuntu

# wget (AppImage)
sudo apt install wget
```

---

## 🆘 Help

```bash
make help
```

Shows all available options.
