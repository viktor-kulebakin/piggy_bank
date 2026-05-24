import json
import os
from datetime import datetime

# Файл для сохранения данных
DATA_FILE = "money_box_categories.json"


class MoneyBox:
    """Класс для управления копилкой с поддержкой категорий и времени."""

    def __init__(self, filename=DATA_FILE):
        self.filename = filename
        self.balance = 0.0
        self.target = 0.0
        self.history = []
        
        # Списки категорий по умолчанию
        self.income_categories = ["Зарплата", "Подарок", "Подработка", "Карманные деньги"]
        self.expense_categories = ["Еда", "Транспорт", "Развлечения", "Техника", "Одежда"]
        
        self.load_data()

    def load_data(self):
        """Загружает данные из JSON-файла."""
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.balance = data.get("balance", 0.0)
                    self.target = data.get("target", 0.0)
                    self.history = data.get("history", [])
                    # Загружаем сохраненные категории, если они есть
                    self.income_categories = data.get("income_categories", self.income_categories)
                    self.expense_categories = data.get("expense_categories", self.expense_categories)
            except (json.JSONDecodeError, KeyError):
                print("⚠️ Ошибка чтения файла. Создана новая копилка.")

    def save_data(self):
        """Сохраняет текущее состояние в JSON-файл."""
        data = {
            "balance": self.balance,
            "target": self.target,
            "history": self.history,
            "income_categories": self.income_categories,
            "expense_categories": self.expense_categories
        }
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def _get_current_time(self):
        """Возвращает текущую дату и время."""
        return datetime.now().strftime("%d.%m.%Y %H:%M:%S")

    def deposit(self, amount, category):
        """Пополнение баланса с указанием категории."""
        if amount <= 0:
            return False, "Сумма должна быть больше нуля!"
        
        self.balance += amount
        timestamp = self._get_current_time()
        self.history.append(f"[{timestamp}] ИСТОЧНИК: {category} | +{amount:,.2f} руб.")
        
        if category not in self.income_categories:
            self.income_categories.append(category)
            
        self.save_data()
        return True, f"Копилка пополнена на {amount:,.2f} руб. (Категория: {category})"

    def withdraw(self, amount, category):
        """Снятие денег с указанием категории расходов."""
        if amount <= 0:
            return False, "Сумма должна быть больше нуля!"
        if amount > self.balance:
            return False, "Недостаточно средств в копилке!"

        self.balance -= amount
        timestamp = self._get_current_time()
        self.history.append(f"[{timestamp}] РАСХОД: {category} | -{amount:,.2f} руб.")
        
        if category not in self.expense_categories:
            self.expense_categories.append(category)
            
        self.save_data()
        return True, f"Снято {amount:,.2f} руб. (Категория: {category})"

    def set_target(self, target_amount):
        """Установка финансовой цели."""
        if target_amount <= 0:
            return False, "Цель должна быть больше нуля!"
        self.target = target_amount
        self.save_data()
        return True, "Финансовая цель успешно обновлена!"

    def get_progress_bar(self):
        """Генерация строки прогресса."""
        if self.target <= 0:
            return "🎯 Цель накопления пока не задана."
        percent = (self.balance / self.target) * 100
        bar = "■" * int(min(percent, 100) // 5) + "□" * (20 - int(min(percent, 100) // 5))
        status = f"🎯 Цель: {self.target:,.2f} руб.\n📊 Прогресс: [{bar}] {percent:.1f}%"
        if self.balance >= self.target:
            status += "\n🎉 Поздравляем! Цель достигнута!"
        return status


class Application:
    """Класс пользовательского интерфейса."""

    def __init__(self):
        self.box = MoneyBox()

    def display_status(self):
        print("\n" + "=" * 50)
        print(f"💰 Текущий баланс: {self.box.balance:,.2f} руб.")
        print(self.box.get_progress_bar())
        print("=" * 50)

    def choose_category(self, categories):
        """Интерактивный выбор или создание новой категории."""
        print("\nВыберите категорию из списка:")
        for idx, cat in enumerate(categories, 1):
            print(f"  {idx}. {cat}")
        print(f"  {len(categories) + 1}. [Своя категория]")
        
        try:
            choice = int(input("Ваш выбор: "))
            if 1 <= choice <= len(categories):
                return categories[choice - 1]
            elif choice == len(categories) + 1:
                new_cat = input("Введите название новой категории: ").strip()
                return new_cat if new_cat else "Другое"
        except ValueError:
            pass
        print("⚠️ Неверный выбор. Выбрана категория 'Другое'.")
        return "Другое"

    def run(self):
        print("👋 Добро пожаловать в Умную Копилку с категориями!")

        while True:
            self.display_status()
            print("1. Пополнить (Доход)")
            print("2. Потратить (Расход)")
            print("3. Установить цель накопления")
            print("4. История операций")
            print("5. Выход")

            choice = input("\nВыберите действие (1-5): ").strip()

            if choice == "1":
                try:
                    amount = float(input("Введите сумму пополнения: "))
                    category = self.choose_category(self.box.income_categories)
                    success, msg = self.box.deposit(amount, category)
                    print(f"{'✅' if success else '❌'} {msg}")
                except ValueError:
                    print("❌ Ошибка: введите число.")

            elif choice == "2":
                try:
                    amount = float(input("Введите сумму расхода: "))
                    category = self.choose_category(self.box.expense_categories)
                    success, msg = self.box.withdraw(amount, category)
                    print(f"{'✅' if success else '❌'} {msg}")
                except ValueError:
                    print("❌ Ошибка: введите число.")

            elif choice == "3":
                try:
                    target = float(input("Введите сумму цели: "))
                    success, msg = self.box.set_target(target)
                    print(f"{'✅' if success else '❌'} {msg}")
                except ValueError:
                    print("❌ Ошибка: введите число.")

            elif choice == "4":
                print("\n📜 Полная история операций:")
                if not self.box.history:
                    print("История пока пуста.")
                else:
                    for record in self.box.history:
                        print(f"  {record}")
                input("\nНажмите Enter для продолжения...")

            elif choice == "5":
                print("\n👋 Данные сохранены. До свидания!")
                break
            else:
                print("❌ Неверный пункт меню.")


if __name__ == "__main__":
    app = Application()
    app.run()
