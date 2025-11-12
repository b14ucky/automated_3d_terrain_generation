# PYFOREST

`pyforest` – szybka symulacja lasu w C++ z interfejsem dla Pythona.

---

## 1. Wymagania

-   Windows 10/11
-   Python 3.12 (64-bit)
-   Visual Studio Build Tools z C++ (MSVC)
-   Python powinien mieć katalog `Include` i `libs` w standardowej instalacji (nie embeddable zip)

---

## 2. Struktura plików

```bash
pyforest/
│
├─ __init__.py
├─ pyforest.cpp          # źródło modułu C++
└─ PYFOREST_README.md    # ta dokumentacja
```

---

## 3. Lokalizacja nagłówków i bibliotek Pythona

1. Nagłówki:

    ```bash
    <PythonPath>\Include
    ```

    np.  
    `C:\Users\<User>\AppData\Local\Programs\Python\Python312\Include`

    Aby to szybko sprawdzić, można uruchomić **Windows PowerShell** i wpisać polecenie:

    ```bash
    python -m sysconfig | findstr data
    ```

2. Biblioteka linkera:

    ```bash
    <PythonPath>\libs\python312.lib
    ```

⚠️ Upewnij się, że ścieżki **nie zawierają spacji** lub użyj skróconych nazw (8.3).

---

## 4. Kompilacja modułu (.pyd)

1. Otwórz **x64 Native Tools Command Prompt for VS** (64-bitowy Python i biblioteka).
2. Przejdź do katalogu z `pyforest.cpp`.
3. Wpisz (dostosowując ścieżki do swojego Pythona):

```bash
cl /EHsc /O2 /LD pyforest.cpp ^
/I "C:\Users\<User>\AppData\Local\Programs\Python\Python312\Include" ^
"C:\Users\<User>\AppData\Local\Programs\Python\Python312\libs\python312.lib" ^
/Fe:pyforest.cp312-win_amd64.pyd
```

-   `/EHsc` → obsługa wyjątków C++
-   `/O2` → maksymalna optymalizacja
-   `/LD` → tworzy DLL (`.pyd` dla Pythona)
-   `/Fe:` → nazwa wyjściowego modułu `.pyd`

Po poprawnej kompilacji powstanie plik:

```bash
pyforest.cp312-win_amd64.pyd
```

---

## 5. Użycie w Pythonie

```python
from pyforest import pyforest

# Inicjalizacja lasu

pyforest.init_forest(width=100, height=100, initial_trees=5)

# Pętla symulacji

while pyforest.get_coverage() < 0.15:
    pyforest.seed_trees()
    pyforest.grow_trees()
    pyforest.decay_seeds()

# Pobranie danych

trees = pyforest.get_trees() # lista drzew: [(x,y), ...]
seeds = pyforest.get_seeds() # lista nasion: [(x,y,strength), ...]
forest_map = pyforest.get_map() # lista list z mapą: 0=EMPTY,1=SEED,2=TREE

print("Trees:", len(trees))
print("Seeds:", len(seeds))
print("Coverage:", pyforest.get_coverage())
```

## 6. Uwagi

-   Jeśli masz spacje w ścieżkach do Pythona → użyj **8.3 skrótów** lub zainstaluj Pythona w katalogu bez spacji.
-   Kompilacja musi być zgodna z architekturą Pythona:
    -   64-bitowy Python → x64 Native Tools Command Prompt
    -   32-bitowy Python → x86 Native Tools Command Prompt
-   `g_forest` w kodzie to globalna instancja symulacji, wszystkie funkcje operują na niej.

---

## 7. Dalsze możliwości

-   Można rozbudować moduł o dodatkowe funkcje wizualizacji w Pythonie.
-   Wydajność jest już znacznie wyższa niż w Pythonie, więc można symulować większe lasy.
