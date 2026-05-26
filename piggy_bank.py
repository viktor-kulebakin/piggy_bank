import json
import os
from datetime import datetime
from typing import List, Dict, Any

DATA_FILE = "money_box_financial.json"

class FinancialGoal:
    def __init__(self, name: str = "Моя цель", target_amount: float = 0.0, end_date: str = None):
        self.name = name
        self.target_amount = target_amount
        self.current_amount = 0.0
        self.start_date = datetime.now().date()
        self.end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None
        self.is_completed = False  # Флаг завершения цели
        self.filename = DATA_FILE
        self.income_sources: List[Dict[str, Any]] = []
        self.expenses: List[Dict[str, Any]] = []
        self.history: List[str] = []
        self.income_categories = ["Зарплата", "Подарок", "Подработка", "Карманные деньги"]
        self.expense_categories = ["Еда", "Транспорт", "Развлечения", "Техника", "Одежда"]
        self.load_data()

    def _get_current_time(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def load_data(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.target_amount = data.get("target_amount", self.target_amount)
                    self.current_amount = data.get("current_amount", self.current_amount)

                    # Конвертируем строки обратно в даты
                    start_date_str = data.get("start_date")
                    if start_date_str:
                        self.start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            
                    end_date_str = data.get("end_date")
                    if end_date_str:
                        self.end_date = datetime.strptime(end_date_str, "%Y-%m-%d").date()

                self.income_sources = data.get("income_sources", [])
                self.expenses = data.get("expenses", [])
                self.history = data.get("history", [])
                self.income_categories = data.get("income_categories", self.income_categories)
                self.expense_categories = data.get("expense_categories", self.expense_categories)
            except (json.JSONDecodeError, ValueError) as e:
                print(f"⚠️ Ошибка чтения файла: {e}. Создана новая копилка.")
                self._create_empty_file()

    def _create_empty_file(self):
        """Создаёт пустой JSON-файл с базовой структурой"""
        data = {
            "name": self.name,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "start_date": self.start_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d") if self.end_date else None,
            "income_sources": [],
            "expenses": [],
            "history": [],
            "income_categories": self.income_categories,
            "expense_categories": self.expense_categories
        }
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def save_data(self):
        """Сохраняет текущее состояние в JSON-файл."""
        data = {
            "name": self.name,
            "target_amount": self.target_amount,
            "current_amount": self.current_amount,
            "start_date": self.start_date.strftime("%Y-%m-%d"),
            "end_date": self.end_date.strftime("%Y-%m-%d") if self.end_date else None,
            "income_sources": self.income_sources,
            "expenses": self.expenses,
            "history": self.history,
            "income_categories": self.income_categories,
            "expense_categories": self.expense_categories
        }
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def get_progress(self) -> Dict[str, Any]:
        """Получить прогресс по цели"""
        if self.target_amount <= 0:
            progress_percent = 0
        else:
            progress_percent = min(100, (self.current_amount / self.target_amount) * 100)
        remaining = max(0, self.target_amount - self.current_amount)

        return {
            'name': self.name,
            'current': self.current_amount,
            'target': self.target_amount,
            'progress_percent': round(progress_percent, 2),
            'remaining': remaining,
            'start_date': self.start_date,
            'end_date': self.end_date
        }

    def calculate_monthly_plan(self) -> str:
        """Рассчитать ежемесячный план с учётом доходов/расходов"""
        today = datetime.now().date()

        if not self.end_date:
            return "❌ Дата цели не установлена!"
        if self.end_date <= today:
            return "❌ Дата цели уже прошла!"

        # Количество оставшихся месяцев
        months_left = (self.end_date.year - today.year) * 12 + \
                     (self.end_date.month - today.month)

        if months_left <= 0:
            months_left = 1

        remaining_amount = max(0, self.target_amount - self.current_amount)
        monthly_needed = remaining_amount / months_left

        return (f"🎯 Цель: {self.name}\n"
                f"💰 Накоплено: {self.current_amount:,.2f} руб.\n"
                f"🔮 Осталось: {remaining_amount:,.2f} руб.\n"
                f"📅 Достижение через: {months_left} мес.\n"
                f"💸 Нужно откладывать: {monthly_needed:,.2f} руб/мес.")

    def show_detailed_report(self):
        """Подробный отчёт по цели"""
        print(f"\n=== ОТЧЁТ ПО ЦЕЛИ: {self.name} ===")
        print(f"Цель: {self.target_amount:,.2f} руб.")
        print(f"Накоплено: {self.current_amount:,.2f} руб.")

        # Расчёт прогресса
        if self.target_amount > 0:
            progress_percent = min(100, (self.current_amount / self.target_amount) * 100)
        else:
            progress_percent = 0
            bar_length = 20
            filled_length = int(bar_length * progress_percent / 100)
            bar = '█' * filled_length + '░' * (bar_length - filled_length)
            print(f"Прогресс: |{bar}| {progress_percent:.1f}%")

            print("\n💵 Пополнения:")
        if not self.income_sources:
            print("  Пополнений пока не было.")
        else:
            for income in self.income_sources:
                print(f"  • {income['date']}: {income['amount']:,.2f} руб. ({income['source']})")

            print("\n💸 Расходы:")
        if not self.expenses:
            print("  Расходов пока не было.")
        else:
            for expense in self.expenses:
                print(f"  • {expense['date']}: {expense['amount']:,.2f} руб. ({expense['reason']})")

            print("\n📝 История операций:")
        if not self.history:
            print("  История операций пуста.")
        else:
            for record in self.history:
                print(f"  {record}")

    def add_income(self, amount: float, source: str, date: str = None):
        """Добавить пополнение"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        self.income_sources.append({
            'amount': amount,
            'source': source,
            'date': date
        })
        self.current_amount += amount

        timestamp = self._get_current_time()
        self.history.append(f"[{timestamp}] ИСТОЧНИК:{source} | +{amount:,.2f} руб.")
                       
        if source not in self.income_categories:
            self.income_categories.append(source)
            
        self.save_data()
        return True, f"Копилка пополнена на {amount:,.2f} руб. (Категория: {source})"
    
    def add_expense(self, amount: float, reason: str, date: str = None):
        """Добавить расход"""
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        self.expenses.append({
            'amount': amount,
            'reason': reason,
            'date': date
        })
        timestamp = self._get_current_time()
   
        self.history.append(f"[{timestamp}] РАСХОД: {reason} | -{amount:,.2f} руб.")
        
        if reason not in self.expense_categories:
            self.expense_categories.append(reason)
            
        self.save_data()
        return True, f"Снято {amount:,.2f} руб. (Категория: {reason})"
    
    def calculate_plan(self):
        """Рассчитать план накоплений с учётом статуса цели"""
        if self.target_amount <= 0:
            return "❌ Сначала установите цель!"

            # Проверка, достигнута ли цель
        if self.current_amount >= self.target_amount and not self.is_completed:
            self.is_completed = True
            excess = self.current_amount - self.target_amount
            self.save_data()
            return (
            f"🎉 ПОЗДРАВЛЯЕМ! Цель '{self.name}' успешно достигнута!\n"
            f"💰 Накоплено: {self.current_amount:,.2f} руб.\n"
            f"🎯 Цель: {self.target_amount:,.2f} руб.\n"
            f"✅ Превышение: {excess:,.2f} руб.\n"
            f"💡 Хотите установить новую цель? Выберите пункт 3 в меню."
            )

            # Если цель уже была завершена ранее
        if self.is_completed:
            excess = max(0, self.current_amount - self.target_amount)
            if excess > 0:
                return (f"✅ Цель '{self.name}' уже была достигнута!\n"
                        f"💰 Накоплено: {self.current_amount:,.2f} руб.\n"
                        f"🎯 Цель: {self.target_amount:,.2f} руб.\n"
                        f"✅ Превышение: {excess:,.2f} руб.\n"
                        f"💡 Для новых накоплений установите новую цель (пункт 3 в меню).")
            else:
                return (f"✅ Цель '{self.name}' уже была достигнута!\n"
                f"💡 Для новых накоплений установите новую цель (пункт 3 в меню).")
        if self.end_date is None:
            return "❌ Дата цели не установлена! Используйте пункт 3 для установки цели."

        today = datetime.now().date()

        if self.end_date < today:
            return "❌ Дата цели уже прошла! Обновите дату цели."

            # Расчёт точного количества дней
        days_difference = (self.end_date - today).days

        if days_difference <= 0:
            return "❌ Дата цели должна быть в будущем!"

        # Приблизительное количество месяцев (30 дней = 1 месяц)
        months = max(1, days_difference // 30)

        remaining_amount = self.target_amount - self.current_amount
        monthly_payment = remaining_amount / months

        if months == 1:
            return (f"⚠️ До цели осталось примерно {days_difference} дней!\n"
            f"💸 Нужно откладывать: {monthly_payment:,.2f} руб/мес.")
        else:
            return (f"📅 Ваша цель будет достигнута примерно через {months} мес.\n"
            f"💰 Осталось накопить: {remaining_amount:,.2f} руб.\n"
            f"💸 Рекомендуемый платёж: {monthly_payment:,.2f} руб/мес.")
       
    def set_target(self, target_amount: float, end_date: str = None):
        """Установить цель накопления с датой завершения"""
        self.target_amount = target_amount
        self.is_completed = False  # Сбрасываем статус при установке новой цели

        if end_date is None:
            end_date = input("Введите дату достижения цели (ГГГГ-ММ-ДД): ")

        try:
            self.end_date = datetime.strptime(end_date, "%Y-%m-%d").date()
                # Добавляем запись в историю
            timestamp = self._get_current_time()
            self.history.append(f"[{timestamp}] УСТАНОВЛЕНА ЦЕЛЬ: {target_amount:,.2f} руб. к {end_date}")
            print(f"✅ Цель установлена: {target_amount:,.2f} руб. к {end_date}")
        except ValueError:
            print("❌ Неверный формат даты. Используйте ГГГГ-ММ-ДД.")
            return False
        return True
        
    
    def get_progress_bar(self):
        """Получить строку с прогрессом и статусом цели"""
        if self.target_amount <= 0:
            return "🎯 Цель накопления пока не задана."
            # Расчёт реального прогресса (может быть >100 %)
        progress = (self.current_amount / self.target_amount) * 100 if self.target_amount > 0 else 0
        # Для бара ограничиваем 100 %
        display_progress = min(100, progress)
        bars = int(display_progress // 5)  # 20 блоков для 100 %
        progress_bar = "[" + "■" * bars + "□" * (20 - bars) + f"] {display_progress:.1f}%"
        status = f"🎯 Цель: {self.target_amount:,.2f} руб.\n📊 Прогресс: {progress_bar}"

            # Добавляем информацию о статусе
        if self.current_amount >= self.target_amount:
            if self.is_completed:
                excess = self.current_amount - self.target_amount
                if excess > 0:
                    status += f"\n✅ Цель достигнута! Превышение: {excess:,.2f} руб."
                else:
                    status += "\n✅ Цель достигнута!"
            else:
            # Первое достижение цели
                status += "\n🎉 Поздравляем! Цель достигнута!"
        return status
    
    def display_status(self):
            """Отобразить текущий статус цели с учётом её завершения"""
            print("=" * 50)
            print(f"💰 Текущий баланс: {self.current_amount:,.2f} руб.")

            if self.target_amount > 0:
                print(f"🎯 Цель: {self.target_amount:,.2f} руб.")

                 #Расчёт прогресса
                if self.target_amount > 0:
                    progress = (self.current_amount / self.target_amount) * 100
                        # Ограничиваем отображение бара 100 % для визуальной ясности
                    display_progress = min(100, progress)
            else:
                progress = 0
                display_progress = 0

                # Визуализация прогресса (максимум 20 блоков)
                bars = int(display_progress // 5)
                progress_bar = "[" + "■" * bars + "□" * (20 - bars) + f"] {display_progress:.1f}%"
                print(f"📊 Прогресс: {progress_bar}")

                # Показываем поздравление и превышение ТОЛЬКО при первом достижении цели
                if self.current_amount >= self.target_amount and not self.is_completed:
                    self.is_completed = True
                    excess = self.current_amount - self.target_amount
                    print(f"🎉 Поздравляем! Цель достигнута!")
                    print(f"💰 Превышение: {excess:,.2f} руб.")
                    self.save_data()  # Сохраняем статус завершения
                elif self.is_completed:
                    # После первого показа — показываем статус и превышение
                    if self.current_amount > self.target_amount:
                        excess = self.current_amount - self.target_amount
                        print(f"✅ Цель достигнута! Превышение: {excess:,.2f} руб.")
                    else:
                        print("✅ Цель достигнута!")
                else:
                    print("🎯 Цель не установлена")
                print("=" * 50)

   
class Application:
    def __init__(self):
        if not os.path.exists(DATA_FILE):
            # Если файла нет — запрашиваем параметры у пользователя
            name = input("Введите название цели: ")
            target = float(input("Введите сумму цели: "))
            date_str = input("Введите дату цели (ГГГГ-ММ-ДД): ")
            self.box = FinancialGoal(name, target, date_str)
            self.box.save_data()  # Сохраняем начальные данные
        else:
            # Если файл есть, но повреждён — создаём новый
            try:
                with open(DATA_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                # Создаём цель с данными из файла
                name = data.get("name", "Моя цель")
                target = data.get("target_amount", 0.0)
                end_date_str = data.get("end_date")
                self.box = FinancialGoal(name, target, end_date_str)
                # Вручную восстанавливаем поля (load_data уже вызвана в __init__)
                self.box.current_amount = data.get("current_amount", 0.0)
                start_date_str = data.get("start_date")
                if start_date_str:
                    self.box.start_date = datetime.strptime(start_date_str, "%Y-%m-%d").date()
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"⚠️ Ошибка чтения файла: {e}. Создаём новую копилку.")
                name = input("Введите название цели: ")
                target = float(input("Введите сумму цели: "))
                date_str = input("Введите дату цели (ГГГГ-ММ-ДД): ")
                self.box = FinancialGoal(name, target, date_str)
                self.box.save_data()                 

    def choose_category(self, categories):
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
        while True:
            print("Добро пожаловать в Умную Копилку с категориями!")
            self.box.display_status()  # Вызываем новый метод отображения

            # Отображение меню
            print("1. Пополнить (Доход)")
            print("2. Потратить (Расход)")
            print("3. Установить цель накопления")
            print("4. История операций")
            print("5. Показать подробный отчёт")
            print("6. Рассчитать план накоплений")
            print("7. Выход")

            choice = input("\nВыберите действие (1-7): ")

            if choice == "1":
                try:
                    amount = float(input("Введите сумму пополнения: "))
                    category = self.choose_category(self.box.income_categories)
                    success, msg = self.box.add_income(amount, category)
                    print(f"{'✅' if success else '❌'} {msg}")
                except ValueError:
                    print("❌ Ошибка: введите число.")

            elif choice == "2":
                try:
                    amount = float(input("Введите сумму расхода: "))
                    category = self.choose_category(self.box.expense_categories)
                    success, msg = self.box.add_expense(amount, category)
                    print(f"{'✅' if success else '❌'} {msg}")
                except ValueError:
                    print("❌ Ошибка: введите число.")

            elif choice == "3":
                try:
                    target = float(input("Введите сумму цели: "))
                    # Метод set_target теперь сам запросит дату
                    self.box.set_target(target)
                    self.box.save_data()
                except ValueError:
                    print("❌ Ошибка: введите корректную сумму!")

            elif choice == "4":
                print("\n📜 Полная история операций:")
                if not self.box.history:
                    print("История пока пуста.")
                else:
                    for record in self.box.history:
                        print(f"  {record}")
                input("\nНажмите Enter для продолжения...")

            elif choice == "5":
                self.box.show_detailed_report()
                input("\nНажмите Enter для продолжения...")

            elif choice == "6":
                print(self.box.calculate_plan())
                input("\nНажмите Enter для продолжения...")

            elif choice == "7":
                print("\n👋 Данные сохранены. До свидания!")
                break
            else:
                print("❌ Неверный пункт меню.")

    
if __name__ == "__main__":
    app = Application()
    app.run()