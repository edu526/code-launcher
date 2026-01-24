# Distribution Guide

This guide will help you choose the best method to distribute Code Project Launcher according to your use case.

## 📦 Distribution Methods

### 1. Local Installation
**Command:** `make install`

**When to use:**
- You're developing the application
- You want automatic updates with Git
- You only need the app on your machine

**Advantages:**
- ✅ Instant installation
- ✅ Automatic update
- ✅ Minimal size
- ✅ Easy to modify

**Disadvantages:**
- ❌ Not portable
- ❌ Requires source code

**Distribution:**
```bash
# Share the repository
git clone <your-repo>
cd code-launcher
make install
```

---

### 2. Executable Binary (PyInstaller)
**Command:** `make binary`

**When to use:**
- You want a single executable file
- Users don't have Python installed
- You need simple distribution

**Advantages:**
- ✅ Single file
- ✅ Doesn't require Python
- ✅ Easy to distribute

**Disadvantages:**
- ❌ Large file (~50-100 MB)
- ❌ Slower startup time
- ❌ Requires GTK on the system

**Distribution:**
```bash
# Create binary
make binary

# Share
scp dist/code-launcher user@server:/tmp/

# User installs
sudo cp /tmp/code-launcher /usr/local/bin/
chmod +x /usr/local/bin/code-launcher
```

---

### 3. DEB Package
**Command:** `make deb`

**When to use:**
- Your users use Debian/Ubuntu
- You want automatic dependency management
- You need clean installation/uninstallation

**Advantages:**
- ✅ Dependency management
- ✅ System integration
- ✅ Small size (~50 KB)
- ✅ Easy update

**Disadvantages:**
- ❌ Only Debian/Ubuntu
- ❌ Requires Python and GTK

**Distribution:**
```bash
# Create package
make deb

# Share
scp code-project-launcher_1.0.0_all.deb user@server:/tmp/

# User installs
sudo dpkg -i /tmp/code-project-launcher_1.0.0_all.deb
sudo apt-get install -f
```

**APT Repository (Advanced):**
```bash
# Create repository
mkdir -p repo/pool/main
cp code-project-launcher_1.0.0_all.deb repo/pool/main/

# Generate index
cd repo
dpkg-scanpackages pool/main /dev/null | gzip -9c > pool/main/Packages.gz

# Users add repo
echo "deb [trusted=yes] http://your-server/repo pool/main" | sudo tee /etc/apt/sources.list.d/code-launcher.list
sudo apt update
sudo apt install code-project-launcher
```

---

### 4. AppImage
**Command:** `make appimage`

**When to use:**
- You want maximum compatibility
- Users use different distributions
- You don't want them to install anything

**Advantages:**
- ✅ Works on any distro
- ✅ Doesn't require installation
- ✅ Portable
- ✅ Doesn't require root permissions

**Disadvantages:**
- ❌ Large file (~100-150 MB)
- ❌ Requires GTK on the system

**Distribution:**
```bash
# Create AppImage
make appimage

# Share
scp CodeLauncher-1.0.0-x86_64.AppImage user@server:/tmp/

# User runs
chmod +x /tmp/CodeLauncher-1.0.0-x86_64.AppImage
/tmp/CodeLauncher-1.0.0-x86_64.AppImage
```

**System integration:**
```bash
# Move to permanent location
mkdir -p ~/.local/bin
mv CodeLauncher-1.0.0-x86_64.AppImage ~/.local/bin/code-launcher

# Create shortcut
cat > ~/.local/share/applications/code-launcher.desktop << EOF
[Desktop Entry]
Name=Code Project Launcher
Exec=$HOME/.local/bin/code-launcher
Icon=code
Type=Application
Categories=Development;
EOF
```

---

## 🎯 Specific Use Cases

### Case 1: Development Team (Same Distro)
**Recommendation:** DEB Package

```bash
# You create
make deb

# Share on internal server
scp code-project-launcher_1.0.0_all.deb server:/var/www/packages/

# Team installs
wget http://server/packages/code-project-launcher_1.0.0_all.deb
sudo dpkg -i code-project-launcher_1.0.0_all.deb
```

---

### Case 2: End Users (Different Distros)
**Recommendation:** AppImage

```bash
# You create
make appimage

# Publish on GitHub Releases
gh release create v1.0.0 CodeLauncher-1.0.0-x86_64.AppImage

# Users download
wget https://github.com/your-user/code-launcher/releases/download/v1.0.0/CodeLauncher-1.0.0-x86_64.AppImage
chmod +x CodeLauncher-1.0.0-x86_64.AppImage
./CodeLauncher-1.0.0-x86_64.AppImage
```

---

### Case 3: Quick Demo
**Recommendation:** Binary

```bash
# You create
make binary

# Share via USB/Email
cp dist/code-launcher /media/usb/

# User runs
chmod +x /media/usb/code-launcher
/media/usb/code-launcher
```

---

### Case 4: Active Development
**Recommendation:** Local Installation

```bash
# Clone and install
git clone <repo>
cd code-launcher
make install

# Update
git pull
# Automatically updates with hooks
```

---

## 📊 Decision Matrix

| Need | Recommended Method |
|------|-------------------|
| Maximum compatibility | AppImage |
| Minimum size | DEB |
| Extreme simplicity | Binary |
| Active development | Local |
| Debian/Ubuntu only | DEB |
| No installation | AppImage |
| No Python on target | Binary or AppImage |
| Frequent updates | Local or DEB (with repo) |

---

## 🚀 Publishing on GitHub

### Create Release with All Formats

```bash
# Create all formats
make all

# Create tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# Create release on GitHub
gh release create v1.0.0 \
  dist/code-launcher \
  code-project-launcher_1.0.0_all.deb \
  CodeLauncher-1.0.0-x86_64.AppImage \
  --title "Code Project Launcher v1.0.0" \
  --notes "First stable version"
```

### Release README

```markdown
# Code Project Launcher v1.0.0

## Downloads

### Debian/Ubuntu
- [code-project-launcher_1.0.0_all.deb](link) (50 KB)
- `sudo dpkg -i code-project-launcher_1.0.0_all.deb`

### Any Distribution (AppImage)
- [CodeLauncher-1.0.0-x86_64.AppImage](link) (100 MB)
- `chmod +x CodeLauncher-1.0.0-x86_64.AppImage && ./CodeLauncher-1.0.0-x86_64.AppImage`

### Executable Binary
- [code-launcher](link) (50 MB)
- `chmod +x code-launcher && ./code-launcher`

## Installation from Source Code
```bash
git clone https://github.com/your-user/code-launcher
cd code-launcher
make install
```
```

---

## 🔄 Version Updates

### Change Version

Edit these files:
```bash
# setup.py
version="1.0.1"

# build_deb.sh
VERSION="1.0.1"

# build_appimage.sh
VERSION="1.0.1"
```

### Create New Release

```bash
# Update version
sed -i 's/1.0.0/1.0.1/g' setup.py build_deb.sh build_appimage.sh

# Commit
git add .
git commit -m "Bump version to 1.0.1"
git tag -a v1.0.1 -m "Release v1.0.1"
git push origin main --tags

# Build
make clean
make all

# Publish
gh release create v1.0.1 \
  dist/code-launcher \
  code-project-launcher_1.0.1_all.deb \
  CodeLauncher-1.0.1-x86_64.AppImage
```

---

## 📝 Distribution Checklist

Before distributing, verify:

- [ ] Version updated in all files
- [ ] README.md updated
- [ ] CHANGELOG.md with changes
- [ ] Tests passing
- [ ] Successful build of all formats
- [ ] Tested on at least 2 different distributions
- [ ] Documentation updated
- [ ] Screenshots updated
- [ ] Git tag created
- [ ] GitHub release published

---

## 🆘 Support

For distribution issues:
1. Verify that all scripts have execution permissions
2. Review build logs
3. Test on a clean VM
4. Consult BUILD_INSTRUCTIONS.md for details

---

## 📚 Additional Resources

- [BUILD_INSTRUCTIONS.md](BUILD_INSTRUCTIONS.md) - Detailed instructions
- [QUICK_BUILD.md](QUICK_BUILD.md) - Quick guide
- [README.md](README.md) - General documentation
