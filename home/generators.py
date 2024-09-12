import datetime
import random
import string

from sequences import get_next_value


def random_string_generator(size=10, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def random_uppercase_string_generator(size=3, chars=string.ascii_uppercase):
    return ''.join(random.choice(chars) for _ in range(size))


def random_password_generator(size=10, chars=string.ascii_letters + string.digits + "!#$%&@"):
    return ''.join(random.choice(chars) for _ in range(size))


def random_number_generator(size=10, chars=string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def random_lowercase_generator(size=10, chars=string.ascii_lowercase):
    return ''.join(random.choice(chars) for _ in range(size))


def random_prescription_number_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def random_account_no_generator(unitNo, chars=string.ascii_uppercase + string.digits):
    return unitNo + "-" + ''.join(random.choice(chars) for _ in range(10))


def random_contract_no_generator(chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(2)) + "/" + ''.join(
        random.choice(string.digits) for _ in range(6))


def random_employee_no_generator(chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(2)) + "/" + ''.join(random.choice(chars) for _ in range(4))


def journal_entry_no_generator(chars=string.ascii_uppercase + string.digits):
    return datetime.datetime.now().strftime("%Y%m%d") + "/" + ''.join(random.choice(chars) for _ in range(6))


def transaction_no_generator(chars=string.ascii_uppercase + string.digits):
    return datetime.datetime.now().strftime("%Y%m%d") + "/" + ''.join(random.choice(chars) for _ in range(8))


def visit_no_generator(chars=string.ascii_uppercase):
    return datetime.datetime.now().strftime("%Y%m%d %H%M") + "" + ''.join(random.choice(chars) for _ in range(1))


def ledger_entry_no_generator(chars=string.ascii_uppercase + string.digits):
    return datetime.datetime.now().strftime("%Y%m%d") + "/" + ''.join(random.choice(chars) for _ in range(6))


def invoice_no_generator(chars=string.ascii_uppercase + string.digits):
    return datetime.datetime.now().strftime("%Y%m%d") + "/" + ''.join(random.choice(chars) for _ in range(4))


def claim_no_generator(chars=string.ascii_uppercase + string.digits):
    return "CMS/" + datetime.datetime.now().strftime("%Y%m%d") + "/" + ''.join(random.choice(chars) for _ in range(4))


def member_number_generator(chars=string.ascii_uppercase + string.digits):
    return str(
        get_next_value(sequence_name="member_no", initial_value=1001)) + "".join(
        random.choice(chars) for _ in range(4))


def sp_number_generator(chars=string.ascii_uppercase + string.digits):
    return datetime.datetime.now().strftime("%Y%m") + "/" + ''.join(random.choice(chars) for _ in range(4))


def profile_number_generator(chars=string.ascii_uppercase + string.digits):
    return datetime.datetime.now().strftime("%Y%m") + ''.join(random.choice(chars) for _ in range(6))
    # return str(get_next_value(sequence_name="profile_no", initial_value=1000001))


def cp_number_generator(chars=string.ascii_uppercase + string.digits):
    return "CP-" + datetime.datetime.now().strftime("%Y%m%d") + "-" + ''.join(random.choice(chars) for _ in range(6))
    # return str(get_next_value(sequence_name="profile_no", initial_value=1000001))


def ads_number_generator():
    return str(get_next_value(sequence_name="adj_no", initial_value=30001))


def bg_number_generator():
    return str(get_next_value(sequence_name="bg_no", initial_value=1001))


def mn_number_generator(group_code):
    return datetime.datetime.now().strftime("%y") + str(group_code) + str(
        get_next_value(sequence_name="mn_no", initial_value=1001))
