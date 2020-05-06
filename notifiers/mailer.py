# Copied from RealSnek 
# --------
# --------
import smtplib, ssl

def notify_in_email(text):
    """Send a mail.
       Subject is AutoNotification

    Arguments:
        text {string} -- plain text body of the email
    """

    decorated_message= "Subject: SUBJECT_HERE" + '\n' + '\n' + text

    smtp_server = "smtp.gmail.com"
    port = 587  # For starttls
    sender_email    = "SENDER_EMAIL"
    receiver_email  = "RECEIVER_EMAIL"
    password = "PASSWORD"

    # Create a secure SSL context
    context = ssl.create_default_context()

    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(sender_email, password)

        #Send email here
        server.sendmail(sender_email, receiver_email, decorated_message)

    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit()

# --------
# --------
