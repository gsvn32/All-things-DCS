#Email Notifiation Service 
import smtplib

def send_email(subscriber, content):
    # Email settings
    sender_email = 'kalyann33@gmail.com' # Enter sender email address
    sender_password = 'chsdupvwabnkhgfr' # Enter sender email password
    receiver_email = subscriber # Enter receiver email address
    message = 'Subject: Notification\n\n' + content
    
    # Sending email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
            smtp.starttls()
            smtp.ehlo()
            smtp.login("kalyann33@gmail.com", "chsdupvwabnkhgfr")
            smtp.sendmail(sender_email, receiver_email, message)
    except Exception as e:
        print('Error sending email to', e)

def notification_service(publisher, content, subscribers_list):
    # Send email notifications to all subscribers
    for subscriber in subscribers_list:
        send_email(subscriber, content)
    
    # Send notification to publisher
    publisher_content = f'The content "{content}" has been successfully published and sent to {len(subscribers_list)} subscribers.'
    send_email(publisher, publisher_content)

# Example usage
publisher = 'kalyann33@gmail.com'
content = 'Hello subscribers!'
subscribers_list = ['kalyann33@gmail.com',]
notification_service(publisher, content, subscribers_list)
