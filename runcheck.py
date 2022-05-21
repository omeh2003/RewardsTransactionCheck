import CheckBNB

if __name__ == "__main__":
    # Задаем дату старта конкурса. Минимальную стоимость монет на балансе. И текущий курс токена.
    checkBNB = CheckBNB.CheckBNB("16/05/2022 09:15:32", 20, 0.000000000020835)
    # Проверка на минимальный баланс
    checkBNB.run_check_minimum_balance()
    # Проверка транзакций BUSD
    checkBNB.run_check_BUSD()
    # Проверка транзакций BNB
    checkBNB.run_check_BNB()
    # Проверка транзакций PGIRL
    checkBNB.run_check_PGIRL()
    print("Check  Complete!")
