
import credentials
import email
import imaplib

# Email Login
imap = imaplib.IMAP4_SSL(credentials.imap_server)
imap.login(credentials.username, credentials.password)

# Scrape Email for Position Details

def Scraper():

    imap.select('Trades')
    _, msgnums = imap.search(None, 'UNSEEN')

    position_details_list = []
    for msgnum in msgnums[0].split():
        _, data = imap.fetch(msgnum, '(RFC822)')
        messege = email.message_from_bytes(data[0][1])
        
        myorder = messege.get('Subject')
        position_details = {}
        if myorder.startswith("Alert: "):
            # Remove the "Alert: " prefix and convert the str to dict
            position_details = eval(myorder.replace("Alert: ", "", 1))
            # Append the dictionary to the list
            position_details_list.append(position_details)

    imap.close()
    return position_details_list