# SkillViz Analytics for Engineers

## 📊 Opis Aplikacji

SkillViz Analytics to zaawansowana aplikacja webowa stworzona w Streamlit do analizy rynku pracy dla inżynierów. Aplikacja umożliwia analizę danych o ofertach pracy w formacie JSON, dostarczając kompleksowe analizy dotyczące zapotrzebowania na umiejętności, poziomów doświadczenia i trendów rekrutacyjnych w różnych lokalizacjach.

### 🔑 Kluczowe Funkcjonalności

- **System Logowania**: Kompletny system uwierzytelniania z kontrolą dostępu opartą na rolach
- **Tryb Gościa**: Dostęp do danych demonstracyjnych bez logowania (ograniczone do 50 wyników)
- **Separacja Danych**: Oddzielne dane demo dla gości i prawdziwe dane dla zalogowanych użytkowników
- **Zarządzanie Kategoriami**: Organizacja danych według kategorii zdefiniowanych przez użytkownika
- **Wykrywanie Duplikatów**: Automatyczne unikanie duplikatów przy dodawaniu danych
- **Analiza Trendów**: Analizy czasowe bazujące na datach publikacji ofert pracy
- **Interaktywne Wizualizacje**: Wykresy i dashboard z filtrowaniem danych
- **Interface Polski**: Pełne wsparcie języka polskiego

### 👥 Role Użytkowników

- **Gość**: Dostęp do danych demo (50 ofert z justjoin.it) - tylko przeglądanie
- **Administrator**: Pełny dostęp - upload danych, zarządzanie użytkownikami, wszystkie analizy
- **Użytkownik**: Dostęp do przeglądania prawdziwych danych - analizy, wizualizacje, filtry

## 🏗️ Architektura Techniczna

### Stack Technologiczny

| Technologia | Wersja | Zastosowanie |
|-------------|---------|--------------|
| **Python** | 3.11+ | Backend, logika biznesowa |
| **Streamlit** | Latest | Frontend, interfejs użytkownika |
| **Pandas** | Latest | Przetwarzanie i analiza danych |
| **Plotly** | Latest | Interaktywne wizualizacje |
| **NumPy** | Latest | Obliczenia numeryczne |

### Architektura Modułowa

```
SkillViz Analytics/
├── app.py                    # Główny moduł aplikacji
├── auth.py                   # System uwierzytelniania
├── data_processor.py         # Przetwarzanie danych
├── visualizations.py         # Generowanie wykresów
├── .streamlit/
│   └── config.toml          # Konfiguracja serwera
├── attached_assets/         # Zasoby i dane demo
└── README.md               # Dokumentacja
```

### Separacja Danych

#### Dane Demonstracyjne (Goście)
- **Źródło**: Rzeczywiste oferty pracy z justjoin.it
- **Rozmiar**: 50 ofert pracy (ograniczenie)
- **Dostęp**: Automatyczny, bez logowania
- **Kategoria**: `demo` 
- **Storage**: `demo_df`, `demo_categories_data`

#### Dane Prawdziwe (Administratorzy)
- **Źródło**: JSON przesyłany przez administratorów
- **Rozmiar**: Bez ograniczeń
- **Dostęp**: Po uwierzytelnieniu
- **Kategorie**: Definiowane przez użytkownika
- **Storage**: `df`, `categories_data`

## 📁 Struktura Plików i Kluczowe Klasy

### 1. `auth.py` - System Uwierzytelniania

#### Klasa `AuthManager`
```python
class AuthManager:
    def __init__(self):
        # Inicjalizuje bazę użytkowników z domyślnymi kontami
        
    def authenticate(username: str, password: str) -> bool:
        # Uwierzytelnia użytkownika z hashowaniem SHA256
        
    def is_authenticated(self) -> bool:
        # Sprawdza status logowania w sesji
        
    def is_admin(self) -> bool:
        # Weryfikuje uprawnienia administratora
        
    def register_user(username: str, password: str) -> bool:
        # Rejestruje nowego użytkownika (tylko admin)
```

**Funkcje pomocnicze:**
- `show_login_form()`: Formularz logowania Streamlit
- `show_user_management()`: Panel zarządzania użytkownikami
- `show_auth_header()`: Header z informacjami o użytkowniku

### 2. `data_processor.py` - Przetwarzanie Danych

#### Klasa `JobDataProcessor`
```python
class JobDataProcessor:
    def __init__(self):
        self.df = None                      # Dane prawdziwe (admin)
        self.demo_df = None                 # Dane demo (goście)
        self.categories_data = {}           # Kategorie danych prawdziwych
        self.demo_categories_data = {}      # Kategorie danych demo
```

**Kluczowe metody:**
- `get_data(is_guest=False)`: Pobiera odpowiednie dane według typu użytkownika
- `get_categories(is_guest=False)`: Lista kategorii dla typu użytkownika
- `get_data_by_category(category, is_guest=False)`: Filtruje dane według kategorii i typu użytkownika
- `process_json_data()`: Przetwarza nowe dane JSON (tylko admin)
- `_initialize_demo_data()`: Ładuje dane demonstracyjne przy starcie
- `has_demo_data()`, `has_real_data()`: Sprawdza dostępność danych

**Funkcje analityczne:**
- `get_skills_statistics(df)`: Statystyki umiejętności
- `get_skill_combinations(df)`: Analizy kombinacji umiejętności
- `get_skills_by_location(df)`: Umiejętności według lokalizacji
- `get_market_summary(df)`: Podsumowanie rynku pracy

### 3. `visualizations.py` - Wizualizacje

#### Klasa `JobMarketVisualizer`
```python
class JobMarketVisualizer:
    def __init__(self, df: pd.DataFrame):
        # Inicjalizuje z DataFrame do wizualizacji
```

**Generatory wykresów:**
- `create_skills_demand_chart(df, top_n=15)`: Wykres słupkowy zapotrzebowania na umiejętności
- `create_experience_distribution_chart(df)`: Wykres kołowy poziomów doświadczenia  
- `create_city_distribution_chart(df, top_n=10)`: Rozkład ofert według miast
- `create_top_companies_chart(df, top_n=10)`: Top firmy rekrutujące
- `create_publishing_trends_chart(df)`: Trendy publikacji w czasie
- `create_skills_trends_chart(df, top_skills=5)`: Trendy umiejętności w czasie
- `create_experience_skills_heatmap(df, top_skills=10)`: Mapa cieplna umiejętności vs doświadczenie
- `create_workplace_type_chart(df)`: Analiza typu miejsca pracy

### 4. `app.py` - Główna Aplikacja

#### Architektura UI
```
Header: Uwierzytelnianie / Tryb Gościa
├── Sidebar: Upload danych (Admin) | Filtry
│   ├── Specjalizacja (kategorie)
│   ├── Miasto  
│   ├── Poziom doświadczenia
│   └── Firma
└── Main Area: 
    ├── Metryki (oferty, umiejętności, miasta, firmy)
    └── Zakładki analityczne (5)
        ├── 📊 Skills Analysis
        ├── 🎯 Experience Levels  
        ├── 🌍 Location Analysis
        ├── 🏢 Company Insights
        └── 📈 Trends
```

**Kluczowe funkcje:**
- `main()`: Główna funkcja z kontrolą uwierzytelniania i inicjalizacją sesji
- `display_analytics()`: Dashboard analityczny z separacją danych
- `display_welcome_screen()`: Ekran powitalny z instrukcjami
- `process_data()`: Przetwarzanie uploadowanych danych (admin tylko)

## 🔧 Zarządzanie Danymi

### Lifecycle Danych

1. **Inicjalizacja**: Automatyczne ładowanie danych demo przy starcie
2. **Upload Admin**: Przetwarzanie JSON → walidacja → normalizacja → kategoryzacja
3. **Dostęp Gościa**: Automatyczny dostęp do danych demo (50 ofert)
4. **Dostęp Użytkownika**: Dostęp do pełnych danych po uwierzytelnieniu
5. **Filtrowanie**: Dynamiczne filtrowanie według kategorii, miasta, poziomu, firmy

### Format Danych JSON

```json
[
  {
    "title": "Senior Data Engineer",
    "companyName": "Example Company", 
    "city": "Warszawa",
    "experienceLevel": "senior",
    "workingTime": "full_time",
    "workplaceType": "remote",
    "remoteInterview": true,
    "openToHireUkrainians": false,
    "publishedAt": "2025-08-18T16:00:16.827Z",
    "requiredSkills": ["Python", "SQL", "Docker", "AWS"],
    "link": "https://example.com/job-offer"
  }
]
```

**Wymagane pola:**
- `title`, `companyName`, `city`, `experienceLevel`, `requiredSkills`

**Opcjonalne pola:**
- `publishedAt` (dla analiz trendów), `workplaceType`, `remoteInterview`

## 🚀 How to Run Locally

### Prerequisites

- **Python 3.11+** installed on your system
- **pip** package manager

### Quick Start

1. **Clone the repository** (or download the source code)
   ```bash
   git clone <repository-url>
   cd skillviz-analytics
   ```

2. **Install dependencies**
   ```bash
   pip install streamlit>=1.49.0 pandas>=2.3.2 plotly>=6.3.0 numpy>=2.3.2 requests>=2.31.0
   ```
   
   *Alternative: If you have `uv` package manager:*
   ```bash
   uv pip install -r pyproject.toml
   ```

3. **Run the application**
   ```bash
   streamlit run app.py --server.port 5000
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5000
   ```

### Environment Variables (Optional)

For email verification functionality, set these environment variables:
```bash
export EMAILLABS_APP_KEY=your_app_key
export EMAILLABS_SECRET_KEY=your_secret_key  
export EMAILLABS_FROM_EMAIL=your_sender_email@domain.com
```

### Default Login Credentials

| Role | Email | Password | Access Level |
|------|--------|----------|--------------|
| **Admin** | `admin@skillviz.com` | `Skillviz^2` | Full access + data management |
| **Test User** | `test@skillviz.com` | `test123` | View all data |
| **Guest** | *(no login needed)* | - | Limited demo data (50 jobs) |

### Configuration

The app includes a default Streamlit configuration in `.streamlit/config.toml`:
```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

### Troubleshooting

- **Port already in use**: Use a different port with `--server.port 8501`
- **Module not found**: Ensure all dependencies are installed with `pip list`
- **Data not loading**: Check if demo data files exist in `attached_assets/` directory

---

## 🔧 Developer Setup

### Advanced Configuration

### Kluczowe Wzorce Kodowania

#### Separacja Danych
```python
# Pobieranie odpowiednich danych
is_guest = not auth_manager.is_authenticated()
data = processor.get_data(is_guest=is_guest)
categories = processor.get_categories(is_guest=is_guest)
```

#### Zarządzanie Sesją Streamlit
```python
# Inicjalizacja z separacją danych
if 'data_loaded' not in st.session_state:
    st.session_state.processor = JobDataProcessor()
    current_data = st.session_state.processor.get_data(is_guest=is_guest)
```

#### Filtrowanie UI
```python
# Wyłączanie filtrów dla gości
if auth_manager.is_authenticated():
    selected_city = st.selectbox("Miasto:", cities)
else:
    selected_city = st.selectbox("Miasto:", ['All'], disabled=True, 
                                help="Zaloguj się aby filtrować")
```

### Rozszerzanie Aplikacji

#### Dodawanie Nowych Wizualizacji
1. Dodaj metodę do `JobMarketVisualizer`
2. Wykorzystaj Plotly dla spójności
3. Uwzględnij separację danych (demo vs real)
4. Dodaj do odpowiedniej zakładki w `display_analytics()`

#### Dodawanie Nowych Filtrów
1. Rozszerz logikę w `display_analytics()`
2. Dodaj kontrolki UI w sidebar
3. Zastosuj filtr do `display_df`
4. Uwzględnij ograniczenia dla gości

## 🔐 Dane Logowania

### Domyślne Konta

| Rola | Login | Hasło | Opis |
|------|--------|-------|------|
| **Administrator** | `skillviz` | `Skillviz^2` | Pełny dostęp + zarządzanie |
| **Użytkownik Testowy** | `testuser` | `test123` | Tylko prawdziwe dane |
| **Gość** | - | - | Automatyczny dostęp do danych demo |

### Zarządzanie Użytkownikami
- Admin może tworzyć nowe konta przez panel "👥 Users"
- Hasła są hashowane SHA256 + sól
- Sesje są zarządzane przez Streamlit session_state

## 🔍 Monitoring i Debugging

### Logi Aplikacji
- Błędy wyświetlane w interfejsie Streamlit
- Logi systemowe w terminalu
- Walidacja JSON z komunikatami błędów

### Metryki Wydajności
- Czas ładowania danych
- Rozmiar przetwarzanych DataFrame
- Status separacji danych (demo vs real)

### Typowe Problemy
1. **Port zajęty**: Zmień port w config.toml lub użyj `--server.port`
2. **Błędy JSON**: Sprawdź strukturę i wymagane pola  
3. **Brak danych**: Upewnij się, że demo data się załadowała
4. **Problemy z logowaniem**: Sprawdź wielkość liter, sesja Streamlit

## 🔬 Testowanie

### Testowanie Funkcjonalności
1. **Tryb Gościa**: Sprawdź automatyczne ładowanie danych demo
2. **Logowanie**: Przetestuj różne role użytkowników
3. **Upload**: Sprawdź walidację i przetwarzanie JSON
4. **Filtry**: Przetestuj wszystkie kombinacje filtrów
5. **Wizualizacje**: Sprawdź poprawność wykresów

### Test Cases
- Upload danych z różnymi kategoriami
- Logowanie z nieprawidłowymi danymi  
- Przejście gość → użytkownik → admin
- Filtry z pustymi wynikami
- JSON z brakującymi polami

## 🤝 Wsparcie i Rozwój

### Kontakt
- Sprawdź logi w terminalu dla błędów technicznych
- Upewnij się, że wszystkie pakiety są zainstalowane
- Zweryfikuj format danych JSON
- Przetestuj różne role użytkowników

### Roadmap
- [ ] Dodatkowe filtry zaawansowane
- [ ] Eksport wykresów jako obrazy
- [ ] API endpoint dla integracji
- [ ] Wsparcie dla innych formatów danych
- [ ] Zaawansowane analizy ML

---

**Wersja**: 2.0.0  
**Ostatnia aktualizacja**: Sierpień 2025  
**Licencja**: MIT  
**Środowisko**: Python 3.11+ | Streamlit | Replit