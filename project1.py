from datetime import datetime
import os

class Transaction:
    def __init__(self, name, surname, amount, ttype, date: datetime, last_balance):
        self.name = name
        self.surname = surname
        self.amount = float(amount)
        self.ttype = ttype
        self.date = date
        self.last_balance = last_balance

    def transform(self):
        return (f"{self.name} {self.surname} | Növ: {self.ttype} | "
                f"Məbləğ: {self.amount} ₼ | "
                f"Tarix: {self.date.strftime('%d-%m-%Y')} | "
                f"Balans: {self.last_balance} ₼")


class BudgetManager:
    def __init__(self, name, surname, balance=0.0):
        self.name = name
        self.surname = surname
        self.__balance = balance
        self.transactions = []

    @property
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):
        self.__balance = value

    def add_transaction(self, amount, ttype, date):
        if amount <= 0:
            raise ValueError("Məbləğ müsbət olmalıdır!")

        if ttype == "Gəlir":
            self.balance += amount
        elif ttype == "Xərc":
            if self.balance >= amount:
                self.balance -= amount
            else:
                raise ValueError("Balansınızda kifayət qədər vəsait yoxdur!")
        else:
            raise ValueError("Əməliyyat növü yalnız 'Gəlir' və ya 'Xərc' ola bilər!")

        transaction = Transaction(self.name, self.surname, amount, ttype, date, self.balance)
        self.transactions.append(transaction)
        return transaction

    def filter_by_date(self, start_date, end_date):
        new_transactions = []
        for transaction in self.transactions:
            if start_date <= transaction.date <= end_date:
                new_transactions.append(transaction)
        return new_transactions


#Hər müştərinin öz BudgetManager obyekti olmalıdır, ona görə yeni class məcburiyyəti yarandı.
class BankSystem:
    def __init__(self):
        self.customers = {}   # key: "Ad Soyad", value: BudgetManager obyekti

    def add_customer(self, name, surname, start_balance=0.0):
        key = f"{name} {surname}"
        if key not in self.customers:
            self.customers[key] = BudgetManager(name, surname, start_balance)
        return self.customers[key]

    def get_customer(self, name, surname):
        return self.customers.get(f"{name} {surname}")

    #Artıq hər müştəri birlikdə bu classda toplandığına görə fayla yazma prosesi 'w' ilə həyata keçirilir.
    def save_all(self, filename):
        with open(filename, "w", encoding="utf-8") as f:
            for customer in self.customers.values():
                for transaction in customer.transactions:
                    f.write(transaction.transform() + "\n")

#Bu funksiya yalnız hesabat üçün nəzərdə tutulub! Geri yükləmə uğursuz ola bilər.
    def save_report(self, filename, start_date, end_date):
        with open(filename, "w", encoding="utf-8") as f:
            for customer in self.customers.values():
                filtered = customer.filter_by_date(start_date, end_date)
                if not filtered:
                    print(f"{customer.name} {customer.surname} adlı adamın bu aralıqda əməliyyatı yoxdur.")
                    continue
                for transaction in filtered:
                    f.write(transaction.transform() + "\n")


    def load(self, filename):
        with open(filename, "r", encoding="utf-8") as f:
            for line in f.readlines():
                if not line.strip(): continue
                parts = [p.strip() for p in line.strip().split("|")]

                #load() funksiyası Transaction classındakı transform() funksiyasındakı dəyişikliklərə qarşı həssasdır.

                full_name = parts[0]
                name, surname = full_name.split(" ", 1)

                ttype = parts[1].replace("Növ:", "").strip()
                amount = float(parts[2].replace("Məbləğ:", "").replace("₼", "").strip())
                date_str = parts[3].replace("Tarix:", "").strip()
                date = datetime.strptime(date_str, "%d-%m-%Y")
                last_balance = float(parts[4].replace("Balans:", "").replace("₼", "").strip())

                customer = self.add_customer(name, surname)
                transaction = Transaction(name, surname, amount, ttype, date, last_balance)
                customer.transactions.append(transaction)
                customer.balance = last_balance


def get_date(message):
    day, month, year = map(int, input(f"{message} (Gün Ay İl): ").split())
    return datetime(year, month, day)

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


print("\n------XOŞ GƏLMİSİNİZ------")
system = BankSystem()
base_filename = input("Əsas faylın adı (boş buraxsanız transactions.txt): ").strip()
if not base_filename: base_filename = "transactions.txt"

choice1 = input("Köhnə faylı yükləyək? (Bəli(b)/Xeyir(x)): ").strip().lower()
if choice1 == "b":
    try:
        print("Fayl oxunur...")
        system.load(base_filename)
    except FileNotFoundError:
        print("Fayl tapılmadı, yeni fayl yaradılacaq.")
    except Exception as e:
        print(f"Gözlənilməz xəta baş verdi: {e}")
    else:
        print("Məlumatlar uğurla yükləndi!")
    finally:
        print("Yükləmə mərhələsi bitdi.\n")

#print("----MENYU----")
while True:
    clear_screen()
    print("\n----MENYU----")
    print("\n1. Yeni Əməliyyat")
    print("2. Müştərinin əməliyyatlarına tarix aralığına görə bax")
    print("3. Tarix aralığına görə hesabat faylı yarat")
    print("4. Saxla və çıx")

    secim = input("\nSeçiminiz: ")



    match secim:
        case "1":
            while True:
                try:
                    line = input("Məlumatları daxil edin (Ad Soyad Məbləğ Növ(Gəlir/Xərc) Tarix(Gün Ay İl)) - (menyuya qayıtmaq üçün 'm'): ")
                    if line.strip().lower() == "m":
                        break
                    parts = line.split()

                    name = parts[0]
                    surname = parts[1]
                    amount = float(parts[2])
                    ttype = parts[3]
                    date = datetime(int(parts[6]), int(parts[5]), int(parts[4]))

                    customer = system.get_customer(name, surname)
                    if customer is None:
                        start_str = input(f"{name} {surname} üçün başlanğıc balans (susmaya görə dəyəri: 0): ").strip()
                        start_balance = float(start_str) if start_str else 0.0
                        customer = system.add_customer(name, surname, start_balance)

                    customer.add_transaction(amount, ttype, date)
                    print(f"Əməliyyat uğurlu oldu! {name} {surname} üçün cari balans: {customer.balance}\n")

                except ValueError as e:
                    print("Xəta:", e, "- Yenidən cəhd edin.\n")
                    continue
                except IndexError:
                    print("Bütün məlumatları düzgün formatda daxil edin.\n")
                    continue

                davam = input("Yeni əməliyyat əlavə etmək istəyirsiniz? (Bəli(b)/Xeyir(x)): ").strip().lower()
                if davam == "x":
                    break
            input("\nDavam etmək üçün Enter basın...")

        case "2":
            try:
                name, surname = map(str, input("Ad və Soyad daxil edin: ").split())
                customer = system.get_customer(name, surname)
                if customer is None:
                    print("Müştəri tapılmadı!")
                    input("\nDavam etmək üçün Enter basın...")
                    continue

                start_date = get_date("Başlanğıc tarixi")
                end_date = get_date("Son tarix")
                filtered = customer.filter_by_date(start_date, end_date)
                if not filtered:
                    print("Bu aralıqda əməliyyat yoxdur.")
                    input("\nDavam etmək üçün Enter basın...")
                    continue

                for transaction in filtered:
                    print(transaction.transform())

            except ValueError as e:
                print(f"Gözlənilməz xəta: {e} - Yenidən yoxlayın.")

            input("\nDavam etmək üçün Enter basın...")

        case "3":
            try:
                start_date = get_date("Başlanğıc tarixi")
                end_date = get_date("Son tarix")
                filename_new = input("Saxlanılacaq faylın adı (boş buraxsanız hesabat.txt): ").strip()
                if not filename_new: filename_new = "hesabat.txt"
                system.save_report(filename_new, start_date, end_date)

                print("Hesabat yaradıldı")

            except ValueError as e:
                print(f"Yenidən cəhd edin: {e}")

            input("\nDavam etmək üçün Enter basın...")


        case "4":
            system.save_all(base_filename)

            print("\n--- Yekun balanslar ---")
            for customer in system.customers.values():
                print(f"{customer.name} {customer.surname}: {customer.balance} ₼")

            print("\nMəlumatlar fayla yazıldı.")
            break

        case _:
            print("Xəta! Yalnız 1-4 arası seçim mümkündür.")
            input("\nDavam etmək üçün Enter basın...")