# Zakładka "Kanały Sprzedaży" w Python Dash

## Wprowadzenie
Celem tego projektu było rozszerzenie istniejącej aplikacji Dash o nową zakładkę pod nazwą "Kanały Sprzedaży". Zakładka ta została stworzona w celu analizy sprzedaży w różnych kanałach oraz dostarczenia szczegółowych informacji na temat klientów.

>Zakładka umożliwia użytkownikowi:

    Zrozumienie, w jakie dni tygodnia generowana jest największa sprzedaż dla każdego kanału.
    Szczegółowe przeglądanie danych dotyczących klientów dla wybranego kanału sprzedaży.

## Funkcjonalności
Zakładka "Kanały Sprzedaży" oferuje następujące możliwości:

>Wykresy:
    A.Wykres słupkowy (stacked bar chart): Prezentuje rozkład sprzedaży w dniach tygodnia dla poszczególnych kanałów sprzedaży, takich jak:

    Flagship store
    e-Shop
    TeleShop
    MBR
    B.Wykres porównawczy: Pokazuje liczbę transakcji oraz sumę sprzedaży (w tysiącach) dla każdego kanału sprzedaży, wykorzystując dwie osie Y, aby zapewnić czytelność obu miar.

>Szczegóły klientów:
    Dropdown: Pozwala użytkownikowi wybrać jeden z dostępnych kanałów sprzedaży.
    Po wyborze kanału wyświetlane są szczegółowe dane dotyczące klientów, w tym:
    Liczba unikalnych klientów.
    Łączna sprzedaż wygenerowana w danym kanale.
    Łączna liczba transakcji zarejestrowanych dla klientów w danym kanale.

## Technologie
Projekt został stworzony z użyciem następujących technologii:
    Dash: Framework do tworzenia interaktywnych aplikacji webowych w Pythonie.
    Plotly: Do tworzenia interaktywnych wykresów.
    Pandas: Do analizy i przetwarzania danych. 

>Pliki projektu
    app.py - główny plik aplikacji, który integruje zakładki.
    database.py- zawiera klasy i funkcje do wczytywania danych z różnych źródeł,takich  jak pliki CSV (np. transactions, country_codes, customers, prod_cat_info).
        Obsługuje wczytywanie danych z wielu plików, np. katalog transactions.
    tab3.py - kod odpowiedzialny za zakładkę "Kanały Sprzedaży".
    tab1.py i tab2.py - inne zakładki aplikacji (Sprzedaż globalna i Produkty).
    
    

## Uruchomienie
    1.Upewnij się, że masz zainstalowanego Pythona w wersji 3.x. Sprawdź to poleceniem:
            python --version
    
    2.Zainstaluj wymagane bibliotek:
        pip install -r requirements.txt

    3.Uruchom aplikację:
        python app.py 

    4.Otwórz przeglądarkę internetową i przejdź pod adres:
    http://127.0.0.1:8050/

