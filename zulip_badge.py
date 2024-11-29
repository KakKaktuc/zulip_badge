import zulip
from datetime import *
from tabulate import tabulate
from collections import defaultdict
from sys import argv


class Bot():
    "бот для получения сообщений из топика по прогулам"

    def get_date():
        "определяем с какого и по какое число будет производится сбор о пропусках"
        #дата в формате ГГГГ-ММ-ДД
        script, date_from, date_to = argv

        try:
            correct_date_from = datetime.strptime(date_from,"%Y-%m-%d")
            correct_date_to = datetime.strptime(date_to + ", " + "23:59:59", "%Y-%m-%d, %H:%M:%S")

            correct_date_from = int(correct_date_from.timestamp())
            correct_date_to = int(correct_date_to.timestamp())
            
            # Возвращаем отформатированные строки
            return correct_date_from, correct_date_to
        except ValueError:
            print("Дата введена неверно!")


    def get_messages(date_from, date_to):
        "собираем сообщения за период указанный в методе get_date"
        #определяем файл подключения к zulip api(работает только на включенном впн)
        client = zulip.Client(config_file="~/zulip_badge/zuliprc")

        channel_name = "your_channel"
        topic_name = "Пропуски, опоздания, замены"

        #запрос для получения сообщений
        response= client.get_messages({
            "anchor":date_from,
            "num_before":1000,
            "num_after":1,
            "narrow":[
                {"operator":"stream", "operand":channel_name},
                {"operator":"topic", "operand": topic_name},
            ],
        })

        if response["result"] == "success":
            #отображает название канала и темы
            sender_count = defaultdict(int)
            for message in response["messages"]:
                #отображает ldap 
                if date_from <= message['timestamp'] <= date_to:
                    if 'data-user-group-id="27"' in message['content']:
                        sender_ldap = message['sender_email'].split('@')[0]
                        sender_count[sender_ldap] += 1 
            return sender_count 
        else:
            print("Ошибка получения сообщений: ", response["msg"])
            return {}
        

    def create_table():
        date_from, date_to = Bot.get_date()
        if date_from is None or date_to is None:
            return

        sender_count = Bot.get_messages(date_from, date_to)
        if not sender_count:
            print("Нет данных для отображения.")
            return

        # Подготовка данных для таблицы
        table_data = [[sender, count] for sender, count in sender_count.items()]
        table_data.sort(key=lambda x: x[1], reverse=True)
        headers = ["Ldap", "Количество сообщений"]
        # Вывод таблицы
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

if __name__ == "__main__":
    Bot.create_table()