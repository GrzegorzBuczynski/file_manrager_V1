# Makefile dla systemów Unix/Linux - Instalacja zależności Python
push:
	git add .
	git commit -m "make push!"
	@echo manualy write git push

# Makefile dla Windows - Instalacja zależności Python

# Zmienne dla Windows
PYTHON := python
PIP := pip
VENV_DIR := venv
REQUIREMENTS := requirements.txt
VENV_ACTIVATE := $(VENV_DIR)\Scripts\activate.bat

# Domyślny target
.PHONY: all
all: install

# Sprawdzenie czy Python jest zainstalowany (Windows)
.PHONY: check-python
check-python:
	@$(PYTHON) --version >nul 2>&1 || (echo Python nie jest zainstalowany! && exit 1)
	@echo Python znaleziony: 
	@$(PYTHON) --version

# Sprawdzenie czy pip jest zainstalowany (Windows)
.PHONY: check-pip
check-pip: check-python
	@$(PIP) --version >nul 2>&1 || (echo pip nie jest zainstalowany! && exit 1)
	@echo pip znaleziony:
	@$(PIP) --version

# Utworzenie pliku requirements.txt
$(REQUIREMENTS):
	@echo Tworzenie pliku requirements.txt...
	@echo opencv-python > $(REQUIREMENTS)
	@echo Pillow >> $(REQUIREMENTS)
	@echo # tkinter jest wbudowany w Python >> $(REQUIREMENTS)
	@echo # os, csv, datetime, subprocess, platform, sys, collections - moduly standardowe >> $(REQUIREMENTS)

# Instalacja zależności dla użytkownika
.PHONY: install
install: check-pip $(REQUIREMENTS)
	@echo Instalowanie zaleznosci...
	$(PIP) install --user opencv-python Pillow
	@echo Instalacja zakonczona!

# Instalacja zależności globalnie
.PHONY: install-global
install-global: check-pip $(REQUIREMENTS)
	@echo Instalowanie zaleznosci globalnie...
	$(PIP) install opencv-python Pillow
	@echo Instalacja globalna zakonczona!

# Utworzenie środowiska wirtualnego
.PHONY: venv
venv: check-python
	@echo Tworzenie srodowiska wirtualnego...
	$(PYTHON) -m venv $(VENV_DIR)
	@echo Srodowisko wirtualne utworzone w $(VENV_DIR)\
	@echo Aby je aktywowac, uzyj:
	@echo   $(VENV_ACTIVATE)

# Instalacja w środowisku wirtualnym
.PHONY: install-venv
install-venv: venv $(REQUIREMENTS)
	@echo Instalowanie zaleznosci w srodowisku wirtualnym...
	$(VENV_ACTIVATE) && pip install opencv-python Pillow
	@echo Instalacja w venv zakonczona!

# Uruchomienie skryptu (sprawdza czy plik istnieje)
.PHONY: run
run: check-python
	@if exist file_manager.py (echo Uruchamianie file_manager.py... && $(PYTHON) file_manager.py) else (echo Plik file_manager.py nie istnieje!)

# Uruchomienie dowolnego pliku Python
.PHONY: run-file
run-file: check-python
	@set /p file="Podaj nazwe pliku Python (z .py): " && $(PYTHON) %file%

# Test importów
.PHONY: test
test: check-python
	@echo Testowanie importow...
	@$(PYTHON) -c "import os; print('✓ os')" 2>nul || echo "✗ os"
	@$(PYTHON) -c "import csv; print('✓ csv')" 2>nul || echo "✗ csv"
	@$(PYTHON) -c "import cv2; print('✓ cv2')" 2>nul || echo "✗ cv2"
	@$(PYTHON) -c "import datetime; print('✓ datetime')" 2>nul || echo "✗ datetime"
	@$(PYTHON) -c "import tkinter; print('✓ tkinter')" 2>nul || echo "✗ tkinter"
	@$(PYTHON) -c "import subprocess; print('✓ subprocess')" 2>nul || echo "✗ subprocess"
	@$(PYTHON) -c "import platform; print('✓ platform')" 2>nul || echo "✗ platform"
	@$(PYTHON) -c "import sys; print('✓ sys')" 2>nul || echo "✗ sys"
	@$(PYTHON) -c "from PIL import Image, ImageTk; print('✓ PIL')" 2>nul || echo "✗ PIL"
	@$(PYTHON) -c "from collections import defaultdict; print('✓ collections')" 2>nul || echo "✗ collections"
	@echo Test zakonczony!

# Szybki test tylko cv2 i PIL
.PHONY: test-deps
test-deps: check-python
	@echo Testowanie glownych zaleznosci...
	@$(PYTHON) -c "import cv2; print('OpenCV:', cv2.__version__)" 2>nul || echo "✗ OpenCV nie zainstalowany"
	@$(PYTHON) -c "from PIL import Image; print('✓ PIL/Pillow dziala')" 2>nul || echo "✗ PIL/Pillow nie zainstalowany"

# Info o systemie
.PHONY: info
info:
	@echo === Informacje o systemie ===
	@$(PYTHON) -c "import platform; print('System:', platform.system(), platform.release())"
	@$(PYTHON) -c "import sys; print('Python:', sys.version)"
	@$(PIP) --version 2>nul || echo pip nie znaleziony

# Czyszczenie
.PHONY: clean
clean:
	@echo Usuwanie srodowiska wirtualnego...
	@if exist $(VENV_DIR) rmdir /s /q $(VENV_DIR)
	@if exist $(REQUIREMENTS) del $(REQUIREMENTS)
	@echo Wyczyszczono!

# Pomoc
.PHONY: help
help:
	@echo === Dostepne polecenia ===
	@echo   make install        - Instalacja zaleznosci (--user)
	@echo   make install-global - Instalacja globalna
	@echo   make venv           - Utworzenie srodowiska wirtualnego
	@echo   make install-venv   - Instalacja w srodowisku wirtualnym
	@echo   make test           - Test wszystkich importow
	@echo   make test-deps      - Test tylko OpenCV i PIL
	@echo   make run            - Uruchomienie file_manager.py (jesli istnieje)
	@echo   make run-file       - Uruchomienie dowolnego pliku .py
	@echo   make info           - Informacje o systemie
	@echo   make clean          - Usuniecie plikow tymczasowych
	@echo   make help           - Ta pomoc