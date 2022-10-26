#!/usr/bin/env python3
from datetime import date, datetime
from typing import NamedTuple, List
import os
import locale
import argparse
import csv
import re
from PyPDF2 import PdfReader

class Transaction(NamedTuple):
    received: date
    details: str
    amount: float
    transaction_type: str


class TransactionWithRewards(NamedTuple):
    received: date
    details: str
    amount: float
    transaction_type: str
    rewards: float


_DATE_FORMAT = "%d/%m/%Y"
_DATE_FORMAT_ALT = "%d/%m/%Y %H:%M:%S"

# Convert Amount to Number


def try_sanitize_amount(amnts):
    xxx = amnts.split()
    try:
        return locale.atof(xxx[0])
    except ValueError:
        return None

# Parse Date

def try_parse_date(ds: str):
    try:
        return datetime.strptime(ds, _DATE_FORMAT)
    except:
        try:
            return datetime.strptime(ds, _DATE_FORMAT_ALT)
        except:
            return None
    return None

# parses credit card statement
def yield_credit_infos(fname: str, show_rewards: bool, password: str):

    reader = PdfReader(fname, password=password)

    def try_transaction(line):
        line = line.replace(",","").strip()
        line_regex = "^([\d]{2}\/[\d]{2}\/[\d]{4})[ 0-9:]*(.*)[ ]{1}([\d]*[.][\d]{2})([ Cr]*)"
        values = re.split(line_regex, line)
        if(len(values) == 1):
            return
        
        transaction_date = values[1].strip()
        amount = values[3].strip()
        details = values[2].strip()

        transaction_date = try_parse_date(transaction_date)
        if transaction_date is None:
            # If start of line is not Date skip,
            # as it will not be Transaction
            return

        if 'Cr' in values[4]:
            transaction_type = 'credit'
        else:
            transaction_type = 'debit'

        amount = try_sanitize_amount(amount)

        if amount is None:
            return

        if show_rewards:
            diners_rewards = 0
            if transaction_type == 'credit' and (details.find('IMPS PMT ') != -1 or amount < 100):
                diners_rewards = 0
            else:
                details_regex = ".*( )([\d]*)$"
                rewards_values = re.split(details_regex, details)

                if(len(rewards_values) > 1):
                    diners_rewards = rewards_values[2]
            
            if transaction_type == 'credit':
                diners_rewards = diners_rewards * -1

            yield TransactionWithRewards(
                received=transaction_date.date(),
                details=details,
                amount=amount,
                transaction_type=transaction_type,
                rewards=diners_rewards
            )
        else:
            yield Transaction(
                received=transaction_date.date(),
                details=details,
                amount=amount,
                transaction_type=transaction_type,
            )

    number_of_pages = len(reader.pages)
    page_counter = 0
    while (page_counter < number_of_pages):
        print("%s PAGE %s OF %s %s" %
              ("=" * 50, page_counter + 1, number_of_pages, "=" * 50))

        lines = reader.pages[page_counter].extract_text().splitlines()

        # Logic to start with Transactions block
        page_start_mark = "Transactions"
        page_start_mark_found = False
        
        for line in lines:
            if(page_start_mark_found == False and line.find(page_start_mark) != -1):
                page_start_mark_found = True
            if page_start_mark_found:
                for t in try_transaction(line):
                    print(t)
                    yield t
        page_counter = page_counter + 1

def get_credit_infos(fname: str, show_rewards: bool, password: str) -> List[Transaction]:
    return list(yield_credit_infos(fname, show_rewards, password))


def main(pdf_path, show_rewards, password):
    infos = []

    if os.path.isfile(pdf_path):
        infos = get_credit_infos(pdf_path, show_rewards, password)
    else:
        files = [f for f in os.listdir(pdf_path)]
        files = filter(lambda f: f.endswith(('.pdf', '.PDF')), files)
        for f in files:
            infos.extend(get_credit_infos(
                os.path.join(pdf_path, f), show_rewards, password))

    with open('output.csv', 'w') as f:
        writer = csv.writer(f, lineterminator='\n')
        if show_rewards:
            writer.writerow(
                ('Date', 'Transaction', 'Amount', 'Type', 'Rewards'))
        else:
            writer.writerow(('Date', 'Transaction', 'Amount', 'Type'))
        for tup in infos:
            writer.writerow(tup)


def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')


def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--statement-path', required=True, type=str,
                        help='path to statements pdf file or directory')
    parser.add_argument('--show-rewards', type=str2bool,
                        help='show rewards', default=True)
    parser.add_argument('--password', type=str,
                        help='password for pdf if locked', default=None)

    return parser.parse_args()


if __name__ == '__main__':
    arguments = parse_arguments()
    main(arguments.statement_path, arguments.show_rewards, arguments.password)