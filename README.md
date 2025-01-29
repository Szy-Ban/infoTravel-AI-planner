# Generator planu podróży

---

### Opis

System analizujący preferencje użytkownika (np. preferowane typy aktywności, takie jak chodzenie po górach czy zwiedzanie starodawnych miast) i generujący na ich podstawie plan podróży, uwzględniając zescrapowane wcześniej Points of Interest.

### Funkcje:
- Dopasowywanie POI do preferencji użytkownika i uwzględnianie ich w generowanym planie podróży.
- Optymalizacja trasy podróży z uwzględnieniem czasu zwiedzania i logistyki.
- Sugerowanie dodatkowych atrakcji w okolicy.
- Generowanie miniaturki na podstawie wygenerowanego planu podróży

### Struktura Projektu:

- **config.py**
    Centralna konfiguracja (klucze API, wybór modelu, domyślne parametry).

- **image_generator.py**
    Korzysta z OpenAI Image API do generowania miniaturki podróży.

- **main.py**
    Główny punkt wejścia: zbiera dane od użytkownika, tworzy plan, wyświetla wyniki.

- **poi.py**
    Model danych dla pojedynczego Punktu Zainteresowania (POI).

- **poi_description_generator.py**
    Generuje opisy tekstowe dla POI, codzienne podsumowania i wskazówki dotyczące planu podróży.

- **poi_manager.py**
    Wczytuje POI z pliku JSON, filtruje je na podstawie preferencji użytkownika.

- **text_generator.py**
    Abstrahuje wywołania LLM. Obsługuje OpenAI, Hugging Face lub Groq do generowania tekstu.

- **travel_planner.py**
    Główna logika budowania wielodniowego planu podróży na podstawie dostępnych POI.

- **user_preferences.py**
    Model danych do przechowywania ustawień użytkownika.

### Instalacja
1. Pobierz repo
2. Zainstaluj wymagane pluginy
3. Stwórz plik .env i umieść klucze do API
4. Odpal Maina

---

## Skład

- **Karol Kozikowski**: s27092
- **Michał Kozikowski**: s27093
- **Szymon Baniewicz**: s27087

---

## Źródła wiedzy
- **Huggingface tutorials**
    https://huggingface.co/docs/transformers/llm_tutorial
- **Csvjson**
    https://csvjson.com/csv2json
- **Kaggle**
    https://www.kaggle.com/
- **OpenAI guides**
    https://platform.openai.com/docs/guides/images
    https://platform.openai.com/docs/guides
- **ChatGPT**
    https://chatgpt.com/
