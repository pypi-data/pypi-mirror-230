import string
import sys
import sqlite3
import getpass
import os.path
from cryptography.fernet import Fernet
import random


def encrypt_pass(password_not_encrypted, key):
    fer = Fernet(key)
    encrypted_pass = fer.encrypt(bytes(password_not_encrypted, 'utf-8'))
    return encrypted_pass


def decrypt_pass(password_encrypted, key):
    fer = Fernet(key)
    decrypted_pass = fer.decrypt(password_encrypted)
    return decrypted_pass


def verify_pass(master_password_not_encrypted, key, fetch):
    encrypted_master_password = bytes(fetch[0][0], 'utf-8')
    decrypted_pass = str(decrypt_pass(encrypted_master_password, key), encoding='utf-8')
    return master_password_not_encrypted == decrypted_pass


def generate_random_pass(start):
    remains = start
    num_lowercase = random.randint(1, remains - 3)
    remains -= num_lowercase
    num_uppercase = random.randint(1, remains - 2)
    remains -= num_uppercase
    num_digit = random.randint(1, remains - 1)
    remains -= num_digit
    num_other = remains
    random_pass = ''
    for i in range(0, num_lowercase):
        characters = string.ascii_lowercase
        random_pass += random.choice(characters)
    for i in range(0, num_uppercase):
        characters = string.ascii_uppercase
        random_pass += random.choice(characters)
    for i in range(0, num_digit):
        characters = string.digits
        random_pass += random.choice(characters)
    for i in range(0, num_other):
        characters = string.punctuation
        random_pass += random.choice(characters)
    str_var = list(random_pass)
    random.shuffle(str_var)
    random_pass = ''.join(str_var)
    #print(random_pass)
    return random_pass


def save_or_verify_master(master_password_not_encrypted, key, con, cur):
    if len(master_password_not_encrypted) == 0:
        return False
    res = cur.execute('select * from master_password')
    fetch = res.fetchall()
    if len(fetch) == 0:
        encrypted_master_password_bytes = encrypt_pass(master_password_not_encrypted, key)
        encrypted_master_password_str = str(encrypted_master_password_bytes, encoding='utf-8')
        cur.execute('insert into master_password values(?)', (encrypted_master_password_str,))
        con.commit()
        return True
    else:
        return verify_pass(master_password_not_encrypted, key, fetch)


def generate_encrypted_pass(key):
    generated_pass = generate_random_pass(15)
    encrypted_generated_pass = encrypt_pass(generated_pass, key)
    return encrypted_generated_pass


def add_generated_password(key, con, cur):
    res = cur.execute('select * from passwords')
    fetch = res.fetchall()
    for e in fetch:
        if e[0] == sys.argv[2]:
            return False
    new_password = generate_encrypted_pass(key)
    #print(new_password)
    cur.execute('insert into passwords values(?,?)', (sys.argv[2], new_password))
    con.commit()
    return True


def add_password(password, key, con, cur):
    res = cur.execute('select * from passwords')
    fetch = res.fetchall()
    for e in fetch:
        if e[0] == sys.argv[2]:
            return False
    new_password = encrypt_pass(password, key)
    cur.execute('insert into passwords values(?,?)', (sys.argv[2], new_password))
    con.commit()
    return True


def get_service_list(cur):
    res = cur.execute("select service from passwords")
    fetch = res.fetchall()
    return fetch


def get_decrypted_password(key, cur):
    res = cur.execute("select password from passwords where service=?", (sys.argv[2],))
    fetch = res.fetchall()
    if len(fetch) == 1:
        password_to_decrypt = fetch[0][0]
        decrypted_password = decrypt_pass(password_to_decrypt, key)
        return str(decrypted_password, encoding='utf-8')
    else:
        return ''


def update_password(password_not_encrypted, key, con, cur):
    condition = False
    res = cur.execute('select * from passwords')
    fetch = res.fetchall()
    for e in fetch:
        if e[0] == sys.argv[2]:
            condition = True
    if condition:
        new_password = encrypt_pass(password_not_encrypted, key)
        cur.execute('update passwords set password=? where service=?', (new_password, sys.argv[2]))
        con.commit()
    return condition


def delete_service(con, cur):
    condition = False
    res = cur.execute('select * from passwords')
    fetch = res.fetchall()
    for e in fetch:
        if e[0] == sys.argv[2]:
            condition = True
    if condition:
        cur.execute('delete from passwords where service=?', (sys.argv[2],))
        con.commit()
    return condition


def export_db(cur):
    res = cur.execute('select * from passwords')
    fetch = res.fetchall()
    con2 = sqlite3.connect(sys.argv[2])
    cur2 = con2.cursor()
    cur2.execute('drop table if exists passwords')
    cur2.execute('create table if not exists passwords(service varchar(100), password varchar(100))')
    cur2.executemany('insert into passwords values(?,?)', fetch)
    con2.commit()


def import_db(con, cur):
    con2 = sqlite3.connect(sys.argv[2])
    cur2 = con2.cursor()
    res = cur2.execute('select * from passwords')
    fetch = res.fetchall()
    cur.execute('delete from passwords')
    cur.executemany('insert into passwords values(?,?)', fetch)
    con.commit()

def execute():
    key = b'eX04AJCOT2Ym_rvCAiaWBaUs6zbbGd6-HEyHebQah78='
    master_password_not_encrypted = getpass.getpass('Inserire master password ')
    con = sqlite3.connect('default.db')
    cur = con.cursor()
    cur.execute('create table if not exists master_password(password varchar(100))')
    correct_master_pass = save_or_verify_master(master_password_not_encrypted, key, con, cur)
    if not correct_master_pass:
        print('Errore: master password non valida')
    else:
        cur.execute('create table if not exists passwords(service varchar(100), password varchar(100))')
        if len(sys.argv) == 4:
            if sys.argv[1] == 'add' and sys.argv[3] == '-g':
                response = add_generated_password(key, con, cur)
                if response:
                    print('Password generata e salvata con successo!')
                else:
                    print('Servizio già presente nel database.')
        elif len(sys.argv) == 3:
            if sys.argv[1] == 'add':
                message = "Inserire una password per il servizio '" + sys.argv[2] + "' "
                password_not_encrypted = getpass.getpass(message)
                while len(password_not_encrypted) == 0:
                    password_not_encrypted = getpass.getpass(message)
                response = add_password(password_not_encrypted, key, con, cur)
                if response:
                    print('Password salvata con successo!')
                else:
                    print('Servizio già presente nel database.')
            if sys.argv[1] == 'get':
                decrypted_pass = get_decrypted_password(key, cur)
                if decrypted_pass == '':
                    print('Servizio non presente nel database.')
                else:
                    message = "La password per il servizio '" + sys.argv[2] + "' è: " + decrypted_pass
                    print(message)
            if sys.argv[1] == 'update':
                message = "Inserire nuova password per il servizio '" + sys.argv[2] + "' "
                password_not_encrypted = getpass.getpass(message)
                while len(password_not_encrypted) == 0:
                    password_not_encrypted = getpass.getpass(message)
                response = update_password(password_not_encrypted, key, con, cur)
                if response:
                    print('Password salvata con successo!')
                else:
                    print('Servizio non presente nel database.')
            if sys.argv[1] == 'del':
                response = delete_service(con, cur)
                if response:
                    message = "Servizio '" + sys.argv[2] + "' eliminato"
                    print(message)
                else:
                    print('Servizio non presente nel database.')
            if sys.argv[1] == 'export':
                if sys.argv[2] == 'default.db':
                    print('Non è possibile usare questo nome')
                else:
                    export_db(cur)
                    message = "Database password esportato in '" + sys.argv[2] + "'"
                    print(message)
            if sys.argv[1] == 'import':
                if sys.argv[2] == 'default.db':
                    print('Non è possibile usare questo nome')
                else:
                    if os.path.exists(sys.argv[2]):
                        import_db(con, cur)
                        message = "Database password importato da '" + sys.argv[2] + "'"
                        print(message)
                    else:
                        print('File del database non trovato')
        elif len(sys.argv) == 2:
            if sys.argv[1] == 'list':
                print('Servizi disponibili')
                service_list = get_service_list(cur)
                for s in service_list:
                    print("* " + s[0])












