import collections
import requests
import json
from datetime import datetime
import os


class CheckBNB:

    def __init__(self, datefrom, minbalans, price):
        self.BINANCE_API = "ТУТ ДОЛЖЕН БЫТЬ API KEY :-) "
        self.CONTRACT = ""
        self.DATEFROM = datefrom
        self.REPORT = ""
        self.MINIMUN_BALANCE = float(minbalans)
        self.PRICE = float(price)
        self.adress_former = []
        with open('adress_former.txt', 'r') as filehandle:
            for line in filehandle:
                currentPlace = line.replace("\n", "")
                currentPlace = currentPlace.lower().strip()
                self.adress_former.append(currentPlace)

        self.adress_check = []
        with open('adress_check.txt', 'r') as filehandle:
            for line in filehandle:
                currentPlace = line.replace("\n", "")
                currentPlace = currentPlace.lower().strip()
                self.adress_check.append(currentPlace)

        self.adress_to_in_ignore = [
            "0xBD612a3f30dcA67bF60a39Fd0D35e39B7aB80774",  # Binance Hot Wallet
            "0x161bA15A5f335c9f06BB5BbB0A9cE14076FBb645",  # Binance Hot Wallet
            "0x10ED43C718714eb63d5aA57B78B54704E256024E",
            "0x2298aae9a1b581c755a24bf902c755e92623b804",  # PancakeSwap V2 pool to exchange between PGIRL and WBNB.
            "0x5a193dd5eaa28edba9ee7999cfc88325a8cf0e8c",  # PancakeSwap V2 pool to exchange between PGIRL and BUSD.
            "0x4c4da68d45f23e38ec8407272ee4f38f280263c0",  # Panda Girl: PGIRL Token Contract
            "0x2298aae9a1b581c755a24bf902c755e92623b804",  # PancakeSwap V2 pool to exchange between PGIRL and WBNB.
            "0xddad61e2125209d3534f3ff5fae4fb7479adfa98",  # Deployer address for Panda Girl.
            "0x5a193dd5eaa28edba9ee7999cfc88325a8cf0e8c",  # PancakeSwap V2 pool to exchange between PGIRL and BUSD.
            "0xbb7739301dec47ff36b6fcac67dc200d6ee464b4",  # PancakeSwap V2 pool to exchange between PGIRL and BTCB.
            "0x3a60236B97081D9F30deaBbE77DD3EEDd0066469",  # PancakeSwap V2 pool to exchange between Cake and PGIRL
            "0x2aBdE1F8b5C863D6f62402C8af12c945fE711e37",  # Адресс рассылки массовой пандагерл.
        ]

        self.numberblock_of_timestamp = self.get_numberblock_of_timestamp()

    # Получаем номер блока в блокчене BNB соответсвующего дате начала конкурса. Начиная с этого блока будем проверять
    # транзакции.
    def get_numberblock_of_timestamp(self):
        dt = datetime.strptime(self.DATEFROM, "%d/%m/%Y %H:%M:%S")
        ts = int(dt.timestamp())
        URL = "https://api.bscscan.com/api" + \
              "?module=block" + \
              "&action=getblocknobytime" + \
              "&timestamp=" + ts.__str__() + \
              "&closest=before" + \
              "&apikey=" + self.BINANCE_API
        s = requests.session()
        r = s.get(URL)

        j = json.loads(r.text)
        return j['result']

    # Получаем список транзакций BNB заданного кошелька
    def get_transaction(self, adress):

        sb = self.numberblock_of_timestamp
        URL = "https://api.bscscan.com/api" + \
              "?module=account" + \
              "&action=txlist" + \
              "&address=" + adress + \
              "&startblock=" + sb + \
              "&endblock=999999999" + \
              "&sort=desc" + \
              "&page=1" + \
              "&offset=100" + \
              "&apikey=" + self.BINANCE_API
        s = requests.session()
        r = s.get(URL)

        j = json.loads(r.text)
        return j['result']

    # Получаем список транзакций BEP20 токена по контракту на кошельке
    def get_transaction_for_contract(self, adress):
        sb = self.numberblock_of_timestamp
        URL = "https://api.bscscan.com/api" + \
              "?module=account" + \
              "&action=tokentx" + \
              "&address=" + adress + \
              "&contractaddress=" + self.CONTRACT + \
              "&startblock=" + sb + \
              "&endblock=999999999" + \
              "&sort=desc" + \
              "&page=1" + \
              "&offset=200" + \
              "&apikey=" + self.BINANCE_API
        s = requests.session()
        r = s.get(URL)

        j = json.loads(r.text)
        return j['result']

    # Рекурсивная проверка BNB транзакций на кошельке
    def check_transactions_recursive(self, waletcheck_transactions, waletcheck, i=0, startcheck=""):
        i = i + 1

        if waletcheck_transactions is None:
            return
        for wt in waletcheck_transactions:

            if wt['from'] in self.adress_to_in_ignore:
                continue
            if wt['to'] in self.adress_to_in_ignore:
                continue
            if wt['contractAddress'] != "":
                continue
            if wt['from'] in self.adress_former:
                if not startcheck == "":
                    with open(self.REPORT, "a") as file:
                        file.writelines(startcheck + "\n")
                return

            elif i < 3:
                if wt['from'] == waletcheck:
                    continue
                if wt['contractAddress'] == "":
                    self.check_transactions_recursive(self.get_transaction(wt['from']), wt['from'], i)

    # Рекурсивная проверка  транзакций BEP20 токенов на кошельке
    def check_transactions_recursive_for_contract(self, waletcheck_transactions, waletcheck, i=0, startcheck=""):
        i = i + 1

        if waletcheck_transactions is None:
            return
        for wt in waletcheck_transactions:

            if wt['from'] in self.adress_to_in_ignore:
                continue
            if wt['to'] in self.adress_to_in_ignore:
                continue

            if wt['from'] in self.adress_former:
                if not startcheck == "":
                    with open(self.REPORT, "a") as file:
                        file.writelines(startcheck + "\n")

                return

            elif i < 3:
                if wt['from'] == waletcheck:
                    continue

                self.check_transactions_recursive_for_contract(self.get_transaction_for_contract(wt['from']),
                                                               wt['from'], i)

    # Получаем баланс токенов PGIRL на кошельке
    def get_balance_walet(self, waletcheck):
        URL = "https://api.bscscan.com/api" + \
              "?module=account" + \
              "&action=tokenbalance" + \
              "&contractaddress=0x4c4da68D45F23E38ec8407272ee4f38F280263c0" + \
              "&address=" + waletcheck + \
              "&tag=latest" + \
              "&apikey=" + self.BINANCE_API
        s = requests.session()
        r = s.get(URL)
        j = json.loads(r.text)
        tokens = float(j.get('result'))
        return tokens

    # Проверка любого токена любого контракта
    def run_check_any_contract(self, contract, name):
        self.CONTRACT = contract
        self.REPORT = "ThisIsScamer" + name + ".txt"
        if os.path.isfile(self.REPORT):
            os.remove(self.REPORT)
        for waletcheck in self.adress_check:
            waletcheck_transactions = self.get_transaction_for_contract(waletcheck)
            if waletcheck_transactions is not None:
                self.check_transactions_recursive_for_contract(waletcheck_transactions, waletcheck,
                                                               startcheck=waletcheck)

    # Проверка BNB Транзакций
    def run_check_BNB(self):
        self.REPORT = "ThisIsScamerBNB.txt"
        if os.path.isfile(self.REPORT):
            os.remove(self.REPORT)
        for waletcheck in self.adress_check:
            waletcheck_transactions = self.get_transaction(waletcheck)
            if waletcheck_transactions is not None:
                self.check_transactions_recursive(waletcheck_transactions, waletcheck, startcheck=waletcheck)

    # Проверка PGIRL Транзакций
    def run_check_PGIRL(self):
        self.CONTRACT = "0x4c4da68D45F23E38ec8407272ee4f38F280263c0"
        self.REPORT = "ThisIsScamerPGIRL.txt"
        if os.path.isfile(self.REPORT):
            os.remove(self.REPORT)
        for waletcheck in self.adress_check:
            waletcheck_transactions = self.get_transaction_for_contract(waletcheck)
            if waletcheck_transactions is not None:
                self.check_transactions_recursive_for_contract(waletcheck_transactions, waletcheck,
                                                               startcheck=waletcheck)

    # Проверка BUSD Транзакций
    def run_check_BUSD(self):
        self.run_check_any_contract("0xe9e7CEA3DedcA5984780Bafc599bD69ADd087D56", "BUSD")

    # Проверка минимального баланса
    def run_check_minimum_balance(self):
        self.REPORT = "ThisIsBalanceLess_" + int(self.MINIMUN_BALANCE).__str__() + ".txt"
        if os.path.isfile(self.REPORT):
            os.remove(self.REPORT)
        for waletcheck in self.adress_check:
            balance = self.get_balance_walet(waletcheck)
            total = balance * self.PRICE
            if total < self.MINIMUN_BALANCE:
                self.adress_check.remove(waletcheck)
                with open(self.REPORT, "a") as file:
                    file.writelines(waletcheck + "\n")
