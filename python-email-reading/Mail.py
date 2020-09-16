import bs4
import imaplib
import base64
import os
import re
import email
import mailparser
import json

email_user = "mazen-almazni@hotmail.com"
email_pass = "almazni012013"
host = "outlook.office365.com"

mail = imaplib.IMAP4_SSL(host, 993)
mail.login(email_user, email_pass)

mail.select('BAB')

type, data = mail.search(None, 'ALL')
print(type)
mail_ids = data[0]
id_list = mail_ids.split()

with open("transactions2.json", "w") as ff:
    for num in data[0].split():
        current_transaction = {}
        transaction_details = []

        typ, data = mail.fetch(num, '(RFC822)')
        raw_email = data[0][1]

        email_content = mailparser.parse_from_bytes(raw_email)
        email_content = bs4.BeautifulSoup(email_content.body, "lxml")

        email_td_tags = email_content.find_all('td')
        important_email_content = email_td_tags[3:30]
        for thing in important_email_content:
            line = str(thing)

            first_closing = line.index('>') + 1
            inilist = [m.start() for m in re.finditer(r"<", line)]
            second_opening = inilist[1]

            current_processed_information = line[first_closing:second_opening]

            # filtering and renaming fields
            if("DATE" in current_processed_information):
                transaction_details.append("Date")
                continue
            if("REF" in current_processed_information):
                transaction_details.append("Transaction_Ref")
                continue
            if("Amount" in current_processed_information):
                transaction_details.append("Amount")
                continue
            if("A/C" in current_processed_information):
                transaction_details.append("Type")
                transaction_details.append(current_processed_information)
                continue
            if("**" in current_processed_information):
                transaction_details.append("Card")
                transaction_details.append(current_processed_information)
                continue
            if("Account Number" in current_processed_information):
                transaction_details.append("Type")
                transaction_details.append("DEBIT THE A/C")
                transaction_details.append(current_processed_information)
                continue

            transaction_details.append(current_processed_information)

        # cleaning the data of empty fileds and re formatting it into CSV
        transaction_details = [
            ele for ele in transaction_details if (ele not in ("", " "))]

        if(len(transaction_details) > 0):
            if "Date" in transaction_details:
                # Extract Date and Time details
                date_index = transaction_details.index('Date')
                date_object = transaction_details[date_index + 1]
                date_value = date_object.split(' ')[0]
                time_value = date_object.split(' ')[1]
                current_transaction["Date"] = date_value
                current_transaction["Time"] = time_value
            else:
                current_transaction["Date"] = "N/A"
                current_transaction["Time"] = "N/A"

            if "Transaction_Ref" in transaction_details:
                # Extract Transaction Reference
                transaction_ref_index = transaction_details.index(
                    'Transaction_Ref')
                transaction_ref_object = transaction_details[transaction_ref_index + 1]
                current_transaction["Transaction_Ref"] = transaction_ref_object
            else:
                current_transaction["Transaction_Ref"] = "N/A"

            if "Amount" in transaction_details:
                # Extract Amount and currency
                amount_index = transaction_details.index('Amount')
                amount_object = transaction_details[amount_index + 1]
                amount_value = amount_object.split(' \xa0 (')[0]
                currency_value = amount_object.split(' \xa0 (')[1][:-1].strip()
                current_transaction["Amount"] = amount_value
                current_transaction["Currency"] = currency_value
            else:
                current_transaction["Amount"] = "N/A"
                current_transaction["Currency"] = "N/A"

            if "Type" in transaction_details:
                # Extract the transaction Type and account
                type_index = transaction_details.index('Type')
                type_object = transaction_details[type_index + 1].split()[0]
                account_object = transaction_details[type_index + 2].split()[0]
                current_transaction["Type"] = type_object
                current_transaction["Account"] = account_object
            else:
                current_transaction["Type"] = "N/A"
                current_transaction["Account"] = "N/A"

            # Extract Card number
            if "Card" in transaction_details:
                card_index = transaction_details.index('Card')
                card_object = transaction_details[card_index + 1].strip()
                current_transaction["Card"] = card_object
            else:
                current_transaction["Card"] = "N/A"

            if "Country" in transaction_details:
                #  Extract Country information
                country_index = transaction_details.index('Country')
                country_object = transaction_details[country_index + 1].split('-')[
                    0].strip()
                current_transaction["Country"] = country_object
            else:
                current_transaction["Country"] = "N/A"

            if "Transaction Details" in transaction_details:
                # Extract description
                description_index = transaction_details.index(
                    'Transaction Details')
                description_object = transaction_details[description_index + 1].split(' - ')[
                    0].strip()
                if(len(transaction_details) != 25):
                    current_transaction["Description"] = description_object
                else:
                    current_transaction["Description"] = "needs_user_input"
            else:
                current_transaction["Description"] = "N/A"

            res = json.dumps(current_transaction)
            ff.write(res)
            ff.write(", \n")

        # print(current_transaction)

exit()
