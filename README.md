# SkillViz Analytics for Engineers

## 📊 Opis Aplikacji

SkillViz Analytics to zaawansowana aplikacja webowa stworzona w Streamlit do analizy rynku pracy dla inżynierów. Aplikacja umożliwia analizę danych o ofertach pracy w formacie JSON, dostarczając kompleksowe analizy dotyczące zapotrzebowania na umiejętności, poziomów doświadczenia i trendów rekrutacyjnych w różnych lokalizacjach.

### 🔑 Kluczowe Funkcjonalności

- **System Logowania**: Kompletny system uwierzytelniania z kontrolą dostępu opartą na rolach
- **Zarządzanie Kategoriami**: Organizacja danych według kategorii zdefiniowanych przez użytkownika
- **Wykrywanie Duplikatów**: Automatyczne unikanie duplikatów przy dodawaniu danych
- **Analiza Trendów**: Analizy czasowe bazujące na datach publikacji ofert pracy
- **Interaktywne Wizualizacje**: Wykresy i dashboard z filtrowaniem danych
- **Export Danych**: Możliwość eksportu analiz w formacie CSV

### 👥 Role Użytkowników

- **Administrator**: Pełny dostęp - upload danych, zarządzanie użytkownikami, wszystkie analizy
- **Użytkownik**: Dostęp do przeglądania - analizy, wizualizacje, export danych

## 📁 Struktura Plików

### Główne Pliki

| Plik | Opis |
|------|------|
| `app.py` | Główna aplikacja Streamlit - interfejs użytkownika i logika prezentacji |
| `auth.py` | System uwierzytelniania i zarządzania użytkownikami |
| `data_processor.py` | Klasa przetwarzania i analizy danych |
| `visualizations.py` | Klasa tworzenia wykresów i wizualizacji |
| `pyproject.toml` | Konfiguracja projektu i zależności |
| `.streamlit/config.toml` | Konfiguracja serwera Streamlit |

### Konfiguracja

```
.streamlit/
└── config.toml          # Konfiguracja serwera (port 5000, adres 0.0.0.0)
```

## 🏗️ Architektura Klas i Funkcji

### 1. `auth.py` - System Uwierzytelniania

#### Klasa `AuthManager`
- **`__init__()`**: Inicjalizuje bazę użytkowników z domyślnymi kontami
- **`authenticate(username, password)`**: Uwierzytelnia użytkownika
- **`register_user(username, password)`**: Rejestruje nowego użytkownika (tylko admin)
- **`is_admin()`**: Sprawdza uprawnienia administratora
- **`get_all_users()`**: Pobiera listę wszystkich użytkowników
- **`delete_user(username)`**: Usuwa użytkownika (tylko admin)

#### Funkcje pomocnicze
- **`show_login_form()`**: Wyświetla formularz logowania
- **`show_user_management()`**: Panel zarządzania użytkownikami
- **`show_auth_header()`**: Header z informacjami o użytkowniku

### 2. `data_processor.py` - Przetwarzanie Danych

#### Klasa `JobDataProcessor`
- **`process_json_data(json_data, category, append_to_existing)`**: Główna funkcja przetwarzania danych JSON
- **`get_data_by_category(category)`**: Filtruje dane według kategorii
- **`get_skills_statistics(df)`**: Generuje statystyki umiejętności
- **`get_skill_combinations(df)`**: Analizuje kombinacje umiejętności
- **`get_skills_by_location(df)`**: Umiejętności według lokalizacji
- **`clear_category_data(category)`**: Usuwa dane kategorii
- **`_remove_duplicates(new_df, existing_df)`**: Wykrywa i usuwa duplikaty
- **`_clean_data(df)`**: Czyści i normalizuje dane

### 3. `visualizations.py` - Wizualizacje

#### Klasa `JobMarketVisualizer`
- **`create_skills_demand_chart(df, top_n)`**: Wykres zapotrzebowania na umiejętności
- **`create_experience_distribution_chart(df)`**: Rozkład poziomów doświadczenia
- **`create_city_distribution_chart(df, top_n)`**: Rozkład ofert według miast
- **`create_top_companies_chart(df, top_n)`**: Top firmy rekrutujące
- **`create_publishing_trends_chart(df)`**: Trendy publikacji w czasie
- **`create_skills_trends_chart(df, top_skills)`**: Trendy umiejętności w czasie
- **`create_experience_skills_heatmap(df, top_skills)`**: Mapa cieplna umiejętności vs doświadczenie

### 4. `app.py` - Główna Aplikacja

#### Kluczowe Funkcje
- **`main()`**: Główna funkcja aplikacji z kontrolą uwierzytelniania
- **`process_data(json_data, category, append_to_existing)`**: Przetwarzanie przesłanych danych
- **`display_analytics()`**: Wyświetla dashboard analityczny
- **`display_welcome_screen()`**: Ekran powitalny z instrukcjami

#### Struktura Interfejsu
- **Sidebar**: Upload danych (admin) / informacje (użytkownik) + filtry
- **Main Area**: 5 zakładek analitycznych + sekcja eksportu

## 🚀 Instrukcja Uruchomienia

### Wymagania
- Python 3.11+
- Dostęp do internetu (instalacja pakietów)

### Instalacja i Uruchomienie

1. **Klonowanie/Pobranie Projektu**
   ```bash
   # Jeśli używasz git
   git clone <repository-url>
   cd skillviz-analytics
   ```

2. **Instalacja Zależności**
   ```bash
   # Automatycznie zainstaluje wszystkie wymagane pakiety
   pip install streamlit pandas plotly numpy
   ```

3. **Uruchomienie Aplikacji**
   ```bash
   streamlit run app.py --server.port 5000
   ```

4. **Dostęp do Aplikacji**
   - Otwórz przeglądarkę i przejdź do: `http://localhost:5000`
   - Aplikacja automatycznie przekieruje do strony logowania

### Alternatywne Uruchomienie (dla Replit)
```bash
# Aplikacja automatycznie konfiguruje się na porcie 5000
streamlit run app.py --server.port 5000 --server.address 0.0.0.0
```

## 🔐 Dane Logowania

### Domyślne Konta

| Rola | Login | Hasło | Uprawnienia |
|------|--------|-------|-------------|
| Administrator | `skillviz` | `Skillviz^2` | Pełny dostęp + zarządzanie |
| Użytkownik Testowy | `testuser` | `test123` | Tylko przeglądanie |

### Tworzenie Nowych Kont
1. Zaloguj się jako administrator
2. Kliknij przycisk "👥 Users" w headerze
3. Użyj sekcji "➕ Register New User"
4. Wprowadź dane nowego użytkownika

## 📖 Instrukcja Użytkowania

### Dla Administratorów

1. **Logowanie**: Użyj danych administratora
2. **Upload Danych**: 
   - W sidebarze wybierz metodę (plik JSON lub wklej tekst)
   - Wpisz kategorię (np. "Python", "Java")
   - Zaznacz "Append to existing data" aby uniknąć duplikatów
3. **Zarządzanie Danymi**:
   - Przeglądaj dostępne kategorie
   - Usuwaj niepotrzebne dane
   - Zarządzaj kontami użytkowników

### Dla Użytkowników

1. **Logowanie**: Użyj przydzielonych danych
2. **Analiza Danych**:
   - Wybierz kategorię w sidebarze
   - Zastosuj filtry (miasto, poziom doświadczenia, firma)
   - Przeglądaj 5 zakładek analitycznych
3. **Export**: Pobierz dane lub analizy w formacie CSV

### Zakładki Analityczne

| Zakładka | Zawartość |
|----------|-----------|
| 📊 Skills Analysis | Top umiejętności, statystyki, kombinacje |
| 🎯 Experience Levels | Rozkład poziomów doświadczenia, mapa cieplna |
| 🌍 Location Analysis | Analiza geograficzna, umiejętności według miast |
| 🏢 Company Insights | Top firmy, analiza typu pracy (remote/office) |
| 📈 Trends | Trendy publikacji i zapotrzebowania na umiejętności |

## 📊 Format Danych

### Wymagany Format JSON
```json
[
  {
    "title": "Senior Data Engineer",
    "companyName": "Example Company",
    "city": "Warsaw",
    "experienceLevel": "senior",
    "workingTime": "full_time",
    "workplaceType": "remote",
    "remoteInterview": true,
    "publishedAt": "2025-08-18T13:00:28.333Z",
    "requiredSkills": ["Python", "SQL", "Docker", "AWS"],
    "link": "https://example.com/job-offer"
  }
]
```

### Wymagane Pola
- `title`: Tytuł stanowiska
- `companyName`: Nazwa firmy
- `city`: Miasto
- `experienceLevel`: Poziom doświadczenia (junior, mid, senior)
- `requiredSkills`: Lista wymaganych umiejętności
- `publishedAt`: Data publikacji (dla analiz trendów)

## 🔧 Rozwiązywanie Problemów

### Najczęstsze Problemy

1. **Błąd portu**: Upewnij się, że port 5000 jest wolny
2. **Błąd JSON**: Sprawdź format przesyłanych danych
3. **Brak danych**: Administrator musi najpierw przesłać dane
4. **Problemy z logowaniem**: Sprawdź wielkość liter w haśle

### Logi i Debugowanie
- Logi aplikacji wyświetlają się w terminalu
- Błędy JSON są wyświetlane w interfejsie
- Sprawdź konsolę przeglądarki dla błędów JavaScript

## 🤝 Wsparcie

W przypadku problemów:
1. Sprawdź logi w terminalu
2. Upewnij się, że wszystkie pakiety są zainstalowane
3. Zweryfikuj format danych JSON
4. Sprawdź uprawnienia użytkownika

---

**Wersja**: 1.0.0  
**Ostatnia aktualizacja**: Sierpień 2025