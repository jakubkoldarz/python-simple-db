# Projekt został wykonany przez Jakuba Kołdarza
# w ramach zajęć z przedmiotu Wstęp do programowania

import sqlite3
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from random import choice, randint

# Funkcja pomocnincza służąca wyświetlaniu danych do konsoli
def log(obj, msg):
    print(f'<{str(obj)}>: {msg}')


# Klasa bazy danych odpowiedzialna za połączenie z nią
# oraz wykonywanie poszczególnych poleceń
class Database:

    # Ścieżka do bazy danych
    PATH = 'students_v1.db'

    # Konstruktor
    def __init__(self):
        self.conn = sqlite3.connect(self.PATH) # Połączenie z bazą danych
        self.create_table() # Stworzenie właściwej tabeli w bazie danych

    def __str__(self):
        return 'DB' 

    # Funkcja odpowiedzialna za utworzenie tabeli 
    def create_table(self):
        try:
            self.conn.execute('''CREATE TABLE students (    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                                                            first_name      TEXT, 
                                                            last_name       TEXT,
                                                            gender          TEXT,
                                                            address         TEXT,
                                                            birth_year      INTEGER,
                                                            field_of_study  TEXT,
                                                            year_of_study   INTEGER)''')
        except sqlite3.OperationalError as err:
            log(self, f'Wystąpił błąd podczas tworzenia tabeli {err.args}')


    # Sprawdzenie argumentów (czy jest listą, czy zawaiera przynajmniej jeden element)
    def check_args(self, args):
        return len(args) > 0 and isinstance(args, list) 


    # Funkcja odpowiedzialna za wstawianie danych do bazy
    # przyjmuje jako argmunets 'args' listę z danymi jednego studenta
    def insert(self, args):
        # Przygotowanie polecenia do bazy danych
        statement = 'INSERT INTO students VALUES (null, '
        # Sprawdzenie argumentów przysłanych przez aplikację (lub użytkownika)
        if not self.check_args(args):
            return
        # Wypełnienie polecenia danymi przysłanymi z aplikacji (lub od użytkownika)
        for i in range(len(args)):
            statement += str(args[i]) if isinstance(args[i], int) else f"'{args[i]}'" # odpowiednie przypisanie danych tj. w cudzysłowiach dla stringów, bez dla liczb
            statement += ', '
        statement = statement.rstrip(', ')
        statement += ')'
        log(self, statement) # wypisanie na konsole polecenia 
        self.conn.execute(statement) # wykowanie polecenia 

    

    # Funkcja odpowiedzialna za wybranie danych z bazy
    def select(self, args = {}):
        # Przygotowanie polecenia do bazy danych
        statement = 'SELECT * FROM students'
        # Sprawdzenie poprawności podanych argumentów
        if not isinstance(args, dict):
            return
        
        # generowanie polecenia SQL
        if not len(args) == 0:
            statement += ' WHERE'
            for key in args:
                # zabezpieczenie przed komentarzami
                if '--' in args[key] or '/*' in args[key]:
                    return [] # zwrócenie pustej tablicy w przypadku błędnych argumentów
                arg = str(args[key]) if isinstance(args[key], int) else f"'{args[key]}'" # odpowiednie przypisanie danych
                # zmiana składni w przypadku użycia znaku '%' przez użytkownika
                statement += f" {key} LIKE {arg} AND" if '%' in args[key] else f" {key} = {arg} AND"  


        statement = statement.rstrip('AND') # usuwanie ostatniego słowa 'AND' 
        log(self, statement)                # wypisywanie polecenia

        # zapytanie do bazy danych
        try:
            return self.conn.execute(statement)
        except sqlite3.OperationalError as err:
            # informacja zwrotna do konsoli w przypadku niepowodzenia
            log(self, f'Wystąpił błąd podczas pobierania danych. {err.args}')


    # Funkcja odpowiedzialna za wyczyszczenie tabeli z danych
    def del_all(self):
        try:
            # wywołanie okienka z zapytaniem (Tak/Nie)
            choice = messagebox.askyesno(title='Powiadomienie', message='Czy aby na pewno chcesz skasować wszystkie dane?')
            if choice: # w przypadku potwierdzenia operacji
                self.conn.execute('DELETE FROM students') # kasowanie danych
        except sqlite3.Error as err:
            # w przypadku jakiegokolwiek błędy informacja zwrotna dla użytkownika
            messagebox.showerror(title='Ostrzeżenie', message='Nie udało się pomyślnie usunąć danych!')
    

    # Funkcja odpowiedzialna za usuwanie pojedyńczego rekordu w bazie danych
    # jako argument przyjmuje id pojedyńczego rekordu
    def del_single(self, id):
        statement = f'DELETE FROM students WHERE id IN {id}'
        if len(id) == 1:
            statement = statement.strip(',)') + ')'
        log(self, statement)
        try:
            self.conn.execute(statement)
        except Exception as err:
            log(self, f'Nie udało się wykonać polecenia {err.args}')
            messagebox.showerror(title='Ostrzeżenie', message='Nie udało się pomyślnie usunąć danych!')


    # Funkcja odpowiedzialna za zapisanie danych do bazy
    # argument 'msg' odpowiada za wysłanie informacji zwrotnej dla użytkownika
    def commit(self, msg = False):
        try:
            self.conn.commit() # właściwe zapisanie do bazy
        except:
            if msg: # w przypadku błędu wysłanie informacji zwrotnej do użytkownika
                messagebox.showerror(title='Ostrzeżenie', message='Nie udało się pomyślnie zapisać danych!')
        log(self, 'Zapisywanie danych') # wypisanie informacji na konsoli
        if msg: # przypadku powodzenia oraz argumentu 'msg=True' zwrócenie informacji do użytkownika 
            messagebox.showinfo(title='Powiadomienie', message='Dane zostały pomyślnie zapisane')


# Klasa odpowiedzialna za obsługę interfejsu i logiki aplikacji
class App:

    # Stałe wartości dla aplikacji
    TITLE = 'Projekt Bazodanowy - Jakub Kołdarz'
    SIZE = '1000x500'
    COLUMNS = ['first_name', 'last_name', 'gender', 'address', 'birth_year', 'field_of_study', 'year_of_study']
    COLUMN_NAMES = ['Imię', 'Nazwisko', 'Płeć', 'Pełny Adres', 'Rok urodzenia', 'Kierunek studiów', 'Rok studiów']

    # Konstruktor
    def __init__(self):
        self.db = Database()

    def __str__(self):
        return 'APP'

    # Funkcja odpowiedziala za uruchomienie interfejsu aplikacji
    def start(self):
        # Stworzenie root aplikacji
        self.root = tk.Tk()

        # Nadanie aplikacji właściwości
        self.root.title(self.TITLE)
        self.root.geometry(self.SIZE)
        self.root.resizable(0, 0)
        # Wywołanie fukncji, kiedy użytkownik spróbuje zamknąć okno aplikacji
        self.root.protocol('WM_DELETE_WINDOW', func=self.on_close)

        # Menu 
        self.menu_data = tk.Menu(self.root, tearoff=0)
        self.menu_data.add_command(label='Wygeneruj dane', command=lambda: self.generate_data(25))

        self.menu_del = tk.Menu(self.root, tearoff=0)
        self.menu_del.add_command(label='Usuń rekord(y)', command=lambda: self.del_data(self.table.selection()))
        self.menu_del.add_command(label='Usuń wszystkie', command=lambda: self.del_data())

        self.main_menu = tk.Menu(self.root, tearoff=0)
        self.main_menu.add_cascade(label='Dane', menu=self.menu_data)
        self.main_menu.add_command(label='Zapisz', command=lambda: self.db.commit(msg=True))
        self.main_menu.add_cascade(label='Usuń', menu=self.menu_del)
        self.root.configure(menu=self.main_menu)

        # Edycja siatki dla elementów
        self.root.columnconfigure(0, weight=5)
        self.root.columnconfigure(1, weight=0)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=1)

        # Stworzenie tabeli odpowiedzialnej za wyświetlanie studentów
        self.table = ttk.Treeview(self.root, columns=['id', *self.COLUMNS], show='headings')

        # Edycja listy
        for i in range(len(self.COLUMNS)):
            self.table.heading(self.COLUMNS[i], text=self.COLUMN_NAMES[i])

        self.table['displaycolumns'] = self.COLUMNS

        # Nadanie odpowiednich rozmiarów kolumną w tabeli
        self.table.column('first_name', width=75)
        self.table.column('last_name', width=75)
        self.table.column('gender', width=40, anchor='center')
        self.table.column('address', width=225)
        self.table.column('birth_year', width=90, anchor='center')
        self.table.column('field_of_study', width=135)
        self.table.column('year_of_study', width=82, anchor='center')


        self.table.grid(column=1, row=0, rowspan=2, sticky='news', pady=(25, 25), padx=(0, 25))

        self.scrollbar = ttk.Scrollbar(self.root, orient='vertical', command=self.table.yview)
        self.scrollbar.place(relx=0.98, y=20, relheight=0.9)
        self.table.configure(yscrollcommand=self.scrollbar.set)


        # Lewa sekcja aplikacji (Wyszukiwanie/Dodawanie)
        self.frame_left = ttk.Frame(self.root)
        self.frame_left.grid(row=0, rowspan=2, column=0, padx=25, pady=25)

        self.frame_add = ttk.Frame(self.frame_left)
        self.frame_add.pack(expand=1, fill='both', side='top')

        self.frame_add.columnconfigure(0, weight=1)
        self.frame_add.columnconfigure(1, weight=3)
        self.frame_add.rowconfigure(0, weight=1)
        self.frame_add.rowconfigure(9, weight=1)

        self.label_add = ttk.Label(self.frame_add, text='Dodawanie rekordów', font='Arial 13')
        self.label_add.grid(column=0, columnspan=2, row=0)

        self.button_add = ttk.Button(self.frame_add, text='Dodaj rekord', command=lambda: self.add(), width=100)
        self.button_add.grid(column=0, row=9, columnspan=2, pady=7)

        self.add_values = []
        for i in range(1, len(self.COLUMN_NAMES) + 1):
            # Konfiguracja siatki
            self.frame_add.rowconfigure(i, weight=1)
            ttk.Label(self.frame_add, text=self.COLUMN_NAMES[i - 1], justify='left', width=16).grid(column=0, row=i)
            self.add_values.append(tk.StringVar())
            if i == 3: # dodawanie pola wyboru płci
                ttk.Combobox(self.frame_add, textvariable=self.add_values[i - 1], width=12, values=('Mężczyzna', 'Kobieta')).grid(column=1, row=i)
            else:
                ttk.Entry(self.frame_add, textvariable=self.add_values[i - 1], width=15).grid(column=1, row=i)
            

        # Pola odpowiedzialne za wyszukiwanie 
        self.frame_search_args = ttk.Frame(self.frame_left)

        self.frame_search_args.columnconfigure(0, weight=3)
        self.frame_search_args.columnconfigure(1, weight=1)

        self.frame_search_args.pack(expand=1, fill='both', side='bottom', pady=(25, 0))

        self.label_search = ttk.Label(self.frame_search_args, text='Wyszukiwanie rekordów', font='Arial 13')
        self.label_search.grid(column=0, columnspan=2, row=0)

        # Sekcja odpowiedzialna za logike wyszukiwania 
        self.entry_group = []
        self.check_group = []
        self.check_values = []

        self.button_search = ttk.Button(self.frame_search_args, text='Wyszukaj', command=lambda: self.load(), width=100)
        self.button_search.grid(column=0, row=8, columnspan=2, pady=7)

        self.frame_search_args.rowconfigure(0, weight=1)
        self.frame_search_args.rowconfigure(8, weight=1)

        for i in range(1, len(self.COLUMN_NAMES) + 1):

            # Konfiguracja siatki 
            self.frame_search_args.rowconfigure(i, weight=1)
            self.check_values.append(tk.StringVar(value='disabled'))

            # Pola tekstowe
            entry_tmp = ttk.Entry(self.frame_search_args, state='disabled')
            entry_tmp.grid(column=0, row=i)
            self.entry_group.append(entry_tmp)

            # Checkboxy
            check_tmp = ttk.Checkbutton(self.frame_search_args, 
                                text=self.COLUMN_NAMES[i - 1], 
                                onvalue='active',
                                offvalue='disabled',
                                variable=self.check_values[i - 1], 
                                width=18, 
                                command=lambda: self.toggle_btn(self))
            check_tmp.grid(column=1, row=i)
            self.check_group.append(check_tmp)

        self.load()             # Załadowanie bazy danych
        self.root.mainloop()    # Uruchomienie aplikacji


    # Funkcja usuwająca dane z bazy danych
    def del_data(self, id = None):
        # Jeżeli id jest puste (użytkownik wybrał opcję czyszczenia bazy danych)
        if not isinstance(id, tuple):
            self.db.del_all()
        # Jeżeli id jest krotką z długością różną od zera (użytkownik zaznaczył rekordy do usunięcia)
        elif len(id) > 0:
            ids_to_remove = []
            for r in id:
                ids_to_remove.append(self.table.item(r)['values'][0])
            self.db.del_single(tuple(ids_to_remove))
        # Jeżeli id jest pustą krotką (użytkownik nie zaznaczył żadnej pozycji)
        else:
            messagebox.showinfo(title='Powiadomienie', message='Proszę zaznaczyć rekord do usunięcia')
            return
        self.load(all=True) # Odświeżenie tabeli 


    # Funkcja ładująca listę z bazy danych
    def load(self, all = False):
        # Pobieranie argumentów z pól tekstowych
        # lub przy przesłaniu opcji 'all=True' wybieranie wszystkich osób z bazy  
        args = self.get_search_args() if not all else {}
        
        # Czyszczenie danych z tabeli w celu zapełnienie jej nowymi
        for child in self.table.get_children():
            self.table.delete(child)
        
        # Wpisywanie danych z bazy do tabeli
        try:
            for row in self.db.select(args):
                log(self.db, row)
                self.table.insert('', tk.END, values=(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7]))
        except Exception as err:
            log(self, f'Wystąpił błąd podczas pobierania danych {err.args}')

    # Funkcja do przełączania stanu pól tekstowych
    def toggle_btn(self, _):
        # Przełączenie stanów pól tekstowych
        for i, v in enumerate(self.check_values):
            self.entry_group[i]['state'] = v.get()


    # Funkcja do pozyskiwania danych z pól tekstowych
    def get_search_args(self):
        # Utworzenie słownika
        args = dict()
        # Dodawanie elementów do słownika
        for index, value in enumerate(self.check_values):
            if value.get() == 'active':
                args[self.COLUMNS[index]] = self.entry_group[index].get()

        return args


    # Funkcja odpowiedzialna za zachowanie aplikacji podczas wyłączania
    def on_close(self):
        choice = messagebox.askyesnocancel(title='Powiadomienie', message='Czy chcesz zapisać zmiany w bazie danych zanim wyjdziesz?')
        # Po wybraniu opcji 'Anuluj':
        if choice == None:
            return
        # Po wybraniu opcji 'Tak' lub 'Nie'
        elif choice:
            self.db.commit(msg=True)
        self.root.destroy()


    # Funkcja odpowiedzialna za generowanie danych, jako argument pobiera liczbę danych do wygenerowania
    def generate_data(self, num):
        # Dane do generowania
        fnames_m = ['Jakub', 'Tomasz', 'Wiktor', 'Jarosław', 'Kamil', 'Adrian', 'Adam', 'Nataniel', 'Marcel']
        fnames_f = ['Oliwia', 'Natalia', 'Wiktoria', 'Anna', 'Maja', 'Aleksandra', 'Barbara', 'Karolina']
        lastnames = ['Adamik', 'Baliga', 'Balik', 'Stoś', 'Michnal', 'Cisłak', 'Wilk', 'Dereń', 'Derewicz', 'Mikołajczyk', 'Galik', 'Kołdarz', 'Hak']
        genders = ['M', 'K']
        fields_of_study = ['Informatyka', 'Zarządzanie', 'Matematyka', 'Robotyka', 'Automatyka', 'Psychologia', 'Budownictwo', 'Lotnictwo', 'Architektura']
        cities = ['Rzeszów', 'Krosno', 'Kraków', 'Katowice', 'Wrocław', 'Przemyśl', 'Szczecin', 'Warszawa', 'Gdańsk']
        streets = ['Słoneczna', 'Hetmańska', 'W.Pola', '3-go Maja', 'Armii Krajowej', 'Baczyńskiego', 'Cicha', 'Graniczna', 'Hanasiewicza', 'Handlowa', 'Łączna']

        # Generowanie danych 
        for _ in range(num):
            gender_c = randint(0, 1)                                        # płeć
            fname_c = choice(fnames_f) if gender_c else choice(fnames_m)    # imię
            lastname_c = choice(lastnames)                                  # nazwisko
            field_of_study_c = choice(fields_of_study)                      # kierunek studiów
            birth_year = randint(1998, 2004)                                # rok urodzenia (na sztywno <1998;2004>)
            year_of_study = randint(1, 3)                                   # rok studiów (na szytwno <1;3>)
            postal_code = f'{randint(15, 38)}-{randint(100, 700)}'          # kod pocztowy
            address_c = f'{choice(cities)} {postal_code}, ul.{choice(streets)} {randint(1, 50)}/{randint(1, 25)}' # generowanie pełnego adresu
            # wstawienie wygynerowanej osoby do bazy danych
            self.db.insert([fname_c, lastname_c, genders[gender_c], address_c, birth_year, field_of_study_c, year_of_study])
        self.load(all=True) # Odświeżenie danych po generacji danych


    # Funkcja odpowiedzialna za dodawanie wartości wpisanych przez użytkownika do bazy
    def add(self):
        student = []
        try:
            gender = self.add_values[2].get()[0]
            if not (gender == 'K' or gender == 'M'):
                raise TypeError

            student.append(self.add_values[0].get()) # Imię 
            student.append(self.add_values[1].get()) # Nazwisko
            student.append(gender) # Płeć
            student.append(self.add_values[3].get()) # Pełny adres
            student.append(int(self.add_values[4].get())) # Rok urodzenia
            student.append(self.add_values[5].get()) # Kierunek studiów
            student.append(int(self.add_values[6].get())) # Rok studiów
            if '' in student:
                raise TypeError
            self.db.insert(student)
            self.load()
        except:
            messagebox.showerror(title='Ostrzeżenie', message='Nie udało się dodać danych do bazy! Proszę uzupełnić wszsytkie pola poprawnie.')


app = App()
app.start()
