from Credentials import Account

if __name__ == '__main__':
    account = Account()
    creds = account.getAuthToken()
    print(creds)