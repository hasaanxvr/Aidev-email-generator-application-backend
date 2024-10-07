import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email_notification(username):
    # Set up the MIME
    message = MIMEMultipart()
    message['From'] = "hasaan1108@gmail.com"
    #message['To'] = "maximeleveille@droit-inc.com"
    message['To'] = "mhasaan@xavor.com"

    message['Subject'] = "New User Alert"

    # Add body to the email
    body = f'A new user {username} created an account on the AI email generation platform for sales outreach. This email serves as a notification for a new account user.'
    message.attach(MIMEText(body, 'plain'))

    # Set up the SMTP server (Gmail)
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # Enable security
        server.login('hasaan1108@gmail.com', 'anpg ekkl dagj agnv')  # Login to the email account

        # Convert the message to a string and send the email
        text = message.as_string()
        server.sendmail('hasaan1108@gmail.com', 'mhasaan@xavor.com', text)

        print("Email sent successfully!")
    
    except Exception as e:
        print(f"Failed to send email. Error: {str(e)}")
    
    finally:
        server.quit()  # Close the connection to the server

