# Makefile dla Windows/Unix - Instalacja zależności Python

# Zmienne uniwersalne
PYTHON := python
PIP := pip
VENV_DIR := venv
REQUIREMENTS := requirements.txt

# Wykrycie systemu operacyjnego
ifeq ($(OS),Windows_NT)
    VENV_ACTIVATE := $(VENV_DIR)\Scripts\activate.bat
    SHELL_TYPE := windows
else
    VENV_ACTIVATE := $(VENV_DIR)/bin/activate
    SHELL_TYPE := unix
endif

# Domyślny target
.PHONY: all
all: install

# Sprawdzenie czy Python jest zainstalowany
.PHONY: check-python
check-python:
	@$(PYTHON) --version >/dev/null 2>&1 || (echo "Python nie jest zainstalowany!" && exit 1)
	@echo "Python znaleziony:" 
	@$(PYTHON) --version

# Sprawdzenie czy pip jest zainstalowany
.PHONY: check-pip
check-pip: check-python
	@$(PIP) --version >/dev/null 2>&1 || (echo "pip nie jest zainstalowany!" && exit 1)
	@echo "pip znaleziony:"
	@$(PIP) --version

# Utworzenie pliku requirements.txt
$(REQUIREMENTS):
	@echo "Tworzenie pliku requirements.txt..."
	@echo "opencv-python" > $(REQUIREMENTS)
	@echo "Pillow" >> $(REQUIREMENTS)
	@echo "# tkinter jest wbudowany w Python" >> $(REQUIREMENTS)
	@echo "# os, csv, datetime, subprocess, platform, sys, collections - moduly standardowe" >> $(REQUIREMENTS)

# Instalacja zależności dla użytkownika
.PHONY: install
install: check-pip $(REQUIREMENTS)
	@echo "Instalowanie zaleznosci..."
	$(PIP) install --user opencv-python Pillow
	@echo "Instalacja zakonczona!"

# Instalacja zależności globalnie
.PHONY: install-global
install-global: check-pip $(REQUIREMENTS)
	@echo "Instalowanie zaleznosci globalnie..."
	$(PIP) install opencv-python Pillow
	@echo "Instalacja globalna zakonczona!"

# Utworzenie środowiska wirtualnego
.PHONY: venv
venv: check-python
	@echo "Tworzenie srodowiska wirtualnego..."
	$(PYTHON) -m venv $(VENV_DIR)
	@echo "Srodowisko wirtualne utworzone w $(VENV_DIR)"
	@echo "Aby je aktywowac, uzyj:"
ifeq ($(OS),Windows_NT)
	@echo "  $(VENV_ACTIVATE)"
else
	@echo "  source $(VENV_ACTIVATE)"
endif

# Instalacja w środowisku wirtualnym
.PHONY: install-venv
install-venv: venv $(REQUIREMENTS)
	@echo "Instalowanie zaleznosci w srodowisku wirtualnym..."
ifeq ($(OS),Windows_NT)
	$(VENV_ACTIVATE) && pip install opencv-python Pillow
else
	. $(VENV_ACTIVATE) && pip install opencv-python Pillow
endif
	@echo "Instalacja w venv zakonczona!"

# Uruchomienie skryptu (sprawdza czy plik istnieje)
.PHONY: run
run: check-python
	@if [ -f "file_manager.py" ]; then \
		echo "Uruchamianie file_manager.py..."; \
		$(PYTHON) file_manager.py; \
	else \
		echo "Plik file_manager.py nie istnieje!"; \
	fi

# Uruchomienie dowolnego pliku Python
.PHONY: run-file
run-file: check-python
	@read -p "Podaj nazwe pliku Python (z .py): " file; $(PYTHON) $$file

# Test importów
.PHONY: test
test: check-python
	@echo "Testowanie importow..."
	@$(PYTHON) -c "import os; print('✓ os')" 2>/dev/null || echo "✗ os"
	@$(PYTHON) -c "import csv; print('✓ csv')" 2>/dev/null || echo "✗ csv"
	@$(PYTHON) -c "import cv2; print('✓ cv2')" 2>/dev/null || echo "✗ cv2"
	@$(PYTHON) -c "import datetime; print('✓ datetime')" 2>/dev/null || echo "✗ datetime"
	@$(PYTHON) -c "import tkinter; print('✓ tkinter')" 2>/dev/null || echo "✗ tkinter"
	@$(PYTHON) -c "import subprocess; print('✓ subprocess')" 2>/dev/null || echo "✗ subprocess"
	@$(PYTHON) -c "import platform; print('✓ platform')" 2>/dev/null || echo "✗ platform"
	@$(PYTHON) -c "import sys; print('✓ sys')" 2>/dev/null || echo "✗ sys"
	@$(PYTHON) -c "from PIL import Image, ImageTk; print('✓ PIL')" 2>/dev/null || echo "✗ PIL"
	@$(PYTHON) -c "from collections import defaultdict; print('✓ collections')" 2>/dev/null || echo "✗ collections"
	@echo "Test zakonczony!"

# Szybki test tylko cv2 i PIL
.PHONY: test-deps
test-deps: check-python
	@echo "Testowanie glownych zaleznosci..."
	@$(PYTHON) -c "import cv2; print('OpenCV:', cv2.__version__)" 2>/dev/null || echo "✗ OpenCV nie zainstalowany"
	@$(PYTHON) -c "from PIL import Image; print('✓ PIL/Pillow dziala')" 2>/dev/null || echo "✗ PIL/Pillow nie zainstalowany"

# Info o systemie
.PHONY: info
info:
	@echo "=== Informacje o systemie ==="
	@$(PYTHON) -c "import platform; print('System:', platform.system(), platform.release())"
	@$(PYTHON) -c "import sys; print('Python:', sys.version)"
	@$(PIP) --version 2>/dev/null || echo "pip nie znaleziony"

# Czyszczenie
.PHONY: clean
clean:
	@echo "Usuwanie srodowiska wirtualnego..."
	@rm -rf $(VENV_DIR) 2>/dev/null || true
	@rm -f $(REQUIREMENTS) 2>/dev/null || true
	@echo "Wyczyszczono!"

# Dodaj target git push
.PHONY: push
push:
	git add .
	git commit -m "make push!"
	@echo "Teraz recznie wykonaj: git push"

# Pomoc
.PHONY: help
help:
	@echo "=== Dostepne polecenia ==="
	@echo "  make install        - Instalacja zaleznosci (--user)"
	@echo "  make install-global - Instalacja globalna"
	@echo "  make venv           - Utworzenie srodowiska wirtualnego"
	@echo "  make install-venv   - Instalacja w srodowisku wirtualnym"
	@echo "  make test           - Test wszystkich importow"
	@echo "  make test-deps      - Test tylko OpenCV i PIL"
	@echo "  make run            - Uruchomienie file_manager.py (jesli istnieje)"
	@echo "  make run-file       - Uruchomienie dowolnego pliku .py"
	@echo "  make info           - Informacje o systemie"
	@echo "  make clean          - Usuniecie plikow tymczasowych"
	@echo "  make push           - Git add, commit i przypomnienie o push"
	@echo "  make help           - Ta pomoc"