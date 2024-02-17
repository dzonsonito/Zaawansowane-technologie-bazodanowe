import tkinter as tk
from tkinter import messagebox, ttk
import pyodbc
import random

def connect_to_database():
    try:
        server = 'MATEUSZ'
        database = 'BAZY'

        conn = pyodbc.connect('DRIVER={SQL Server};SERVER='+server+';DATABASE='+database+';Trusted_Connection=yes;')
        messagebox.showinfo("Sukces", "Połączono z bazą danych.")
        return conn
    except Exception as e:
        messagebox.showerror("Błąd", "Wystąpił błąd podczas łączenia z bazą danych: " + str(e))

def get_pickers_from_database():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT Imię, Nazwisko FROM Pracownicy WHERE Stanowisko='Picker'")
    pickers = [f"{row[0]} {row[1]}" for row in cursor.fetchall()]
    conn.close()
    return pickers

def get_products_from_database():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT Nazwa FROM Produkty")
    products = [row[0] for row in cursor.fetchall()]
    conn.close()
    return products

def get_clients_from_database():
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("SELECT ID FROM Klienci")
    clients = [row[0] for row in cursor.fetchall()]
    conn.close()
    return clients


def display_orders():
    orders_window = tk.Toplevel()
    orders_window.title("Lista zamówień")

    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            z.ID, 
            k.Imię, 
            k.Nazwisko, 
            z.Data_Zamówienia, 
            z.Status, 
            STRING_AGG(
                CASE 
                    WHEN p.Stanowisko = 'Picker' THEN 'Picker: ' + p.Imię + ' ' + p.Nazwisko 
                    WHEN p.Stanowisko = 'PAK' THEN 'PAK: ' + p.Imię + ' ' + p.Nazwisko 
                    ELSE 'Inne: ' + p.Imię + ' ' + p.Nazwisko 
                END
                , ', '
            ) AS Pracownicy 
        FROM 
            Zamówienia z 
        JOIN 
            Klienci k ON z.ID_Klienta = k.ID 
        LEFT JOIN 
            Pracownicy p ON z.ID = p.ID_Zamówienia
        GROUP BY 
            z.ID, k.Imię, k.Nazwisko, z.Data_Zamówienia, z.Status
    """)

    orders = cursor.fetchall()

    for order in orders:
        order_label = tk.Label(
            orders_window,
            text=f"ID zamówienia: {order[0]}, Klient: {order[1]} {order[2]}, Data zamówienia: {order[3]}, Status: {order[4]}, Pracownicy: {order[5]}"
        )
        order_label.pack()

    conn.close()

    orders = cursor.fetchall()

    for order in orders:
        order_label = tk.Label(
            orders_window,
            text=f"ID zamówienia: {order[0]}, Klient: {order[1]} {order[2]}, Data zamówienia: {order[3]}, Status: {order[4]}, {order[5]}"
        )
        order_label.pack()

    conn.close()


def generate_order(picker):
    # Sprawdzenie, czy wybrano Pickera
    if not picker:
        messagebox.showwarning("Błąd", "Wybierz Pickera.")
        return

    # Pobranie produktów z bazy danych
    products = get_products_from_database()
    product = random.choice(products)
    quantity = random.randint(1, 10)
    price = random.uniform(1, 100)
    location = 'Sekcja artykułów biurowych'

    # Losowanie klienta
    clients = get_clients_from_database()
    client_id = random.choice(clients)

    # Pobranie imienia i nazwiska Pickera
    picker_name = picker.split()[0]
    picker_surname = picker.split()[1] if len(picker.split()) > 1 else ""

    # Wstawienie nowego zamówienia do bazy danych
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO Zamówienia (ID_Klienta, Data_Zamówienia, Status) VALUES (?, GETDATE(), ?)", (client_id, 'Nowe'))
    conn.commit()

    cursor.execute("SELECT IDENT_CURRENT('Zamówienia')")  # Pobranie ostatniego ID zamówienia
    order_id = cursor.fetchone()[0]

    cursor.execute("INSERT INTO Szczegóły_Zamówienia (ID_Zamówienia, ID_Produktu, Ilość) VALUES (?, ?, ?)", (order_id, 1, quantity))
    conn.commit()

    # Przypisanie zamówienia do Pickera
    cursor.execute("UPDATE Pracownicy SET ID_Zamówienia = ? WHERE Imię = ? AND Nazwisko = ?", (order_id, picker_name, picker_surname))
    conn.commit()

    conn.close()

    messagebox.showinfo("Sukces", "Wygenerowano nowe zamówienie: {} x {} - {} - {}".format(quantity, product, price, picker))

def complete_order(order_id):
    # Oznaczenie zamówienia jako skompletowane w bazie danych
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("UPDATE Zamówienia SET Status = 'Skompletowane' WHERE ID = ?", (order_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sukces", f"Zamówienie o ID {order_id} zostało oznaczone jako skompletowane.")

def delete_order(order_id):
    # Usunięcie zamówienia o podanym ID z tabeli Zamówienia
    conn = connect_to_database()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Zamówienia WHERE ID = ?", (order_id,))
    conn.commit()
    conn.close()
    messagebox.showinfo("Sukces", f"Zamówienie o ID {order_id} zostało usunięte.")

def display_orders():
    orders_window = tk.Toplevel()
    orders_window.title("Lista zamówień")

    conn = connect_to_database()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            z.ID, 
            k.Imię, 
            k.Nazwisko, 
            z.Data_Zamówienia, 
            z.Status, 
            STRING_AGG(
                CASE 
                    WHEN p.Stanowisko = 'Picker' THEN 'Picker: ' + p.Imię + ' ' + p.Nazwisko 
                    WHEN p.Stanowisko = 'PAK' THEN 'PAK: ' + p.Imię + ' ' + p.Nazwisko 
                    ELSE 'Inne: ' + p.Imię + ' ' + p.Nazwisko 
                END
                , ', '
            ) AS Pracownicy 
        FROM 
            Zamówienia z 
        JOIN 
            Klienci k ON z.ID_Klienta = k.ID 
        LEFT JOIN 
            Pracownicy p ON z.ID = p.ID_Zamówienia
        GROUP BY 
            z.ID, k.Imię, k.Nazwisko, z.Data_Zamówienia, z.Status
    """)

    orders = cursor.fetchall()

    for order in orders:
        order_label = tk.Label(
            orders_window,
            text=f"ID zamówienia: {order[0]}, Klient: {order[1]} {order[2]}, Data zamówienia: {order[3]}, Status: {order[4]}, Pracownicy: {order[5]}"
        )
        order_label.pack()

    conn.close()

    orders = cursor.fetchall()

    for order in orders:
        order_label = tk.Label(
            orders_window,
            text=f"ID zamówienia: {order[0]}, Klient: {order[1]} {order[2]}, Data zamówienia: {order[3]}, Status: {order[4]}, {order[5]}"
        )
        order_label.pack()

    conn.close()

def send_to_packing(order_id):
    conn = connect_to_database()
    cursor = conn.cursor()

    # Sprawdzenie, czy zamówienie ma status "Skompletowane"
    cursor.execute("SELECT Status FROM Zamówienia WHERE ID = ?", (order_id,))
    status = cursor.fetchone()[0]
    if status != "Skompletowane":
        messagebox.showwarning("Błąd", "Zamówienie jeszcze nie jest gotowe.")
        conn.close()
        return

    # Wybór losowego pracownika z stanowiskiem "PAK"
    cursor.execute("SELECT Imię, Nazwisko FROM Pracownicy WHERE Stanowisko='PAK' ORDER BY NEWID()")
    pak_worker = cursor.fetchone()
    if pak_worker:
        pak_name = pak_worker[0]
        pak_surname = pak_worker[1]
        cursor.execute("UPDATE Zamówienia SET Numer_PAK = ? WHERE ID = ?", (f"{pak_name} {pak_surname}", order_id))
        conn.commit()
        messagebox.showinfo("Sukces", f"Zamówienie o ID {order_id} zostało przekazane do pakowania. Pakujący: {pak_name} {pak_surname}")
    else:
        messagebox.showerror("Błąd", "Brak pracownika do pakowania.")
    conn.close()

# Tworzenie głównego okna
root = tk.Tk()
root.title("Aplikacja do zarządzania zamówieniami")

# Tworzenie przycisku "Połącz z bazą danych"
connect_button = tk.Button(root, text="Połącz z bazą danych", command=connect_to_database)
connect_button.pack(pady=20)

# Tworzenie przycisku "Wyświetl zamówienia"
display_orders_button = tk.Button(root, text="Wyświetl zamówienia", command=display_orders)
display_orders_button.pack(pady=10)

# Pole wyboru Pickera
picker_label = tk.Label(root, text="Wybierz Pickera:")
picker_label.pack()
picker_combobox = ttk.Combobox(root, values=get_pickers_from_database())
picker_combobox.pack()

# Tworzenie przycisku "Wygeneruj zamówienie"
generate_order_button = tk.Button(root, text="Wygeneruj zamówienie", command=lambda: generate_order(picker_combobox.get()))
generate_order_button.pack(pady=10)

# Etykieta i pole tekstowe do wprowadzenia ID zamówienia
complete_order_label = tk.Label(root, text="Wprowadź ID zamówienia do oznaczenia jako skompletowane:")
complete_order_label.pack()
order_id_entry = tk.Entry(root)
order_id_entry.pack()

# Tworzenie przycisku "Oznacz jako skompletowane"
complete_order_button = tk.Button(root, text="Oznacz jako skompletowane", command=lambda: complete_order(order_id_entry.get()))
complete_order_button.pack(pady=10)

# Etykieta i pole tekstowe do wprowadzenia ID zamówienia do przekazania do pakowania
send_to_packing_label = tk.Label(root, text="Wprowadź ID zamówienia do przekazania do pakowania:")
send_to_packing_label.pack()
send_to_packing_entry = tk.Entry(root)
send_to_packing_entry.pack()

# Tworzenie przycisku "Przekaż do pakowania"
send_to_packing_button = tk.Button(root, text="Przekaż do pakowania", command=lambda: send_to_packing(send_to_packing_entry.get()))
send_to_packing_button.pack(pady=10)

# Etykieta i pole tekstowe do wprowadzenia ID zamówienia do usunięcia
delete_order_label = tk.Label(root, text="Wprowadź ID zamówienia do usunięcia:")
delete_order_label.pack()
delete_order_entry = tk.Entry(root)
delete_order_entry.pack()

# Tworzenie przycisku "Usuń zamówienie"
delete_order_button = tk.Button(root, text="Usuń zamówienie", command=lambda: delete_order(delete_order_entry.get()))
delete_order_button.pack(pady=10)

# Uruchomienie pętli głównej
root.mainloop()
