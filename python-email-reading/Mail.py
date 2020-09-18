import mailparser
import imaplib
import email
import json
import bs4
import re

def setup(email_user, email_pass, host, folder_name):
    mail = imaplib.IMAP4_SSL(host, 993)
    mail.login(email_user, email_pass)
    mail.select(folder_name)
    return mail

def fetch_emails(mail):
    type, data = mail.search(None, 'ALL')
    print(type)
    mail_ids = data[0]
    id_list = mail_ids.split()

    with open("Data/transactions.json", "w") as result_file:
        result_file.write("{")
        for num in id_list:
            type, data = mail.fetch(num, '(RFC822)' )
            raw_email = data[0][1]

            result_file.write('"{}":'.format(num))

            email_content = mailparser.parse_from_bytes(raw_email)
            email_content = bs4.BeautifulSoup(email_content.body, "lxml")
            
            email_td_tags = email_content.find_all('td')
            important_email_content = email_td_tags[3:30]

            transaction_details = cleaning_reformatting(important_email_content)
            
            # cleaning the data of empty fileds and re formatting it into CSV
            transaction_details = [ele for ele in transaction_details if (ele not in ("", " "))] 


            current_transaction = json_formatting(transaction_details)

            if(current_transaction["Date"] != "N/A"):
                res = json.dumps(current_transaction)
                result_file.write(res)
                result_file.write(", \n")
            else:
                result_file.write("{},\n")

        result_file.write("}")

def cleaning_reformatting(important_email_content):
    transaction_details = []
    for html_tag in important_email_content:
        line = str(html_tag)

        first_closing = line.index('>') + 1
        inilist = [m.start() for m in re.finditer(r"<", line)] 
        second_opening = inilist[1]

        current_processed_information = line[first_closing:second_opening]
        # print(current_processed_information)

        # filtering and renaming fields
        if("DATE" in current_processed_information):
            transaction_details.append("Date")
            continue
        if("REF" in current_processed_information):
            transaction_details.append("Transaction_Ref")
            continue
        if("THE SUM" in current_processed_information):
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
            # transaction_details.append(current_processed_information)
            continue
        if("Sender Name" in current_processed_information):
            transaction_details.append("Sender")
            continue
        if("Transaction Details" in current_processed_information):
            transaction_details.append("Description")
            continue
        if("Beneficiary Name" in current_processed_information):
            transaction_details.append("Beneficiary")
            continue
            
        transaction_details.append(current_processed_information)

    return transaction_details

def json_formatting(transaction_details):
    current_transaction = {}

    if("Transaction_Ref" in transaction_details):
        # Extract Transaction Reference
        transaction_ref_index = transaction_details.index('Transaction_Ref')
        transaction_ref_object = transaction_details[transaction_ref_index + 1]
        current_transaction["Transaction_Ref"] = transaction_ref_object
    else:
        current_transaction["Transaction_Ref"] = "N/A"

    if("Type" in transaction_details):
        # Extract the transaction Type and account
        type_index = transaction_details.index('Type')
        type_object = transaction_details[type_index + 1].split()[0]
        account_object = transaction_details[type_index + 2].split()[0]
        current_transaction["Account"] = account_object
        current_transaction["Type"] = type_object
    else:
        current_transaction["Account"] = "N/A"
        current_transaction["Type"] = "N/A"

    if("Card" in transaction_details):
        # Extract Card number
        card_index = transaction_details.index('Card')
        card_object = transaction_details[card_index + 1].strip()
        current_transaction["Card"] = card_object
    else:
        current_transaction["Card"] = "N/A"

    if("Date" in transaction_details):
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

    if("Amount" in transaction_details):
        # Extract Amount and currency
        amount_index = transaction_details.index('Amount')
        amount_object = transaction_details[amount_index + 1]
        if(' \xa0 ' in amount_object):
            amount_value = amount_object.split(' \xa0 ')[0]
            currency_value = amount_object.split(' \xa0 ')[1].strip()
            currency_value = currency_value[2:-2]
        else:
            amount_value = amount_object.split(' ')[0]
            currency_value = amount_object.split(' ')[2].strip()
            # print(currency_value)
        current_transaction["Amount"] = amount_value
        current_transaction["Currency"] = currency_value
    else:
        current_transaction["Amount"] = "N/A"
        current_transaction["Currency"] = "N/A"

    if("Sender" in transaction_details):
        # Extract Sender
        sender_index = transaction_details.index('Sender')
        sender_object = transaction_details[sender_index + 2]
        current_transaction["Sender"] = sender_object
    else:
        current_transaction["Sender"] = "N/A"

    if("Beneficiary" in transaction_details):
        # Extract Beneficiary
        beneficiary_index = transaction_details.index('Beneficiary')
        beneficiary_object = transaction_details[beneficiary_index + 2]
        current_transaction["Beneficiary"] = beneficiary_object
    else:
        current_transaction["Beneficiary"] = "N/A"

    if("Merchant name" in transaction_details):
        merchant_index = transaction_details.index('Merchant name')
        merchant_object = transaction_details[merchant_index + 1]
        current_transaction["Merchant"] = merchant_object
    else:
        current_transaction["Merchant"] = "N/A"
        
    if("Country" in transaction_details):
        #  Extract Country information
        country_index = transaction_details.index('Country')
        country_object = transaction_details[country_index + 1].split('-')[0].strip()
        current_transaction["Country"] = country_object
    else:
        current_transaction["Country"] = "N/A"

    if("Description" in transaction_details):
        # Extract description
        description_index = transaction_details.index('Description')
        description_object = transaction_details[description_index + 1].split(' - ')[0].strip()
        current_transaction["Description"] = description_object
    else:
        current_transaction["Description"] = "N/A"

    if(current_transaction["Sender"] != "N/A"):
        current_transaction["Type"] = "CREDIT"

    return current_transaction


if __name__ == "__main__":
    mail = setup("", "", "outlook.office365.com", "BAB")
    fetch_emails(mail)
    exit()