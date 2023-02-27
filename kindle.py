# coding: utf8
import feedparser
from fpdf import FPDF
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from email import encoders
from configparser import ConfigParser
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
#use ini file to store confiuguration

config = ConfigParser()
config.read('nosync.ini')
#get current date
import datetime
now = datetime.datetime.now()
#view current date no time
currentdate = now.strftime("%Y-%m-%d")



# Define the RSS feed URLs
#feed_urls = ['https://www.forbes.com/real-time/']
feed_urls = [config.get('RSS', 'feed')]
# Parse the RSS feeds
entries = []
for feed_url in feed_urls:
    feed = feedparser.parse(feed_url)   
    #change encoding to utf-8
    entries += feed.entries
   


#Generate a PDF File with the RSS entries



# Generate the PDF file
# pdf = FPDF()
# # use leter size paper
# pdf.add_page(orientation = 'P')
# pdf.set_font("Times", size=10)
# for entry in entries:
#     pdf.cell(0, 10, txt=entry.title + '\n' )
#     pdf.cell(0, 10, txt=entry.summary, ln=1, align='C')
# pdf.output(currentdate + "_news.pdf")
pdf_file = currentdate + '_news.pdf'
c = canvas.Canvas(pdf_file, pagesize=letter)
c.setFont('Helvetica', 12)

y = 750  # initial y-position for text

for entry in feed.entries:
    title = entry.title
    summary = entry.summary
    #if image is present in the feed add it to the pdf
    if entry.has_key('media_content'):
        image = entry.media_content[0]['url']
        #center the image above text
        c.drawImage(image, 50, y-100, width=100, height=100)
        y -= 100
    
    #draw a divider line
    c.line(50, y, 550, y)
    y -= 20


    #if title is longer than 100 characters split it into 100 character chunks
    if len(title) > 90:
        title = [title[i:i+90] for i in range(0, len(title), +90)]
        for i in title:
            c.drawString(50, y, i)
            y -= 30
    else:
            c.drawString(50, y, title)
            y -= 30
    # check if summary contains any html tags and links using a regex
    import re
    if re.search('<.*?>', summary):
        #remove html tags and links
        summary = re.sub('<.*?>', '', summary)
        summary = re.sub('http.*? ', '', summary)
        #check if summary contains the word readmore and remove it
    if re.search('Read More', summary):
           summary = re.sub('Read More.*? ', '', summary)      
    if len(summary) > 90:
        #split summary into 100 character chunks
        summary = [summary[i:i+90] for i in range(0, len(summary), 90)]
        for i in summary:
            c.drawString(50, y, i)
            y -= 20
  #check if the page is full and if so create a new page
    if y < 50:
        c.showPage()
        y = 750

c.save()
# Define email parameters
#hotmail stmp server


smtp_server = config.get('Email', 'smtp_server')
print(smtp_server)
smtp_port = config.get('Email', 'smtp_port')
print(smtp_port)
smtp_username = config.get('Email', 'smtp_username')
smtp_password = config.get('Email', 'smtp_password')
from_email = config.get('Email', 'from_email')
to_email = config.get('Email', 'to_email')

# Compose the email
msg = MIMEMultipart()
msg['From'] = from_email
msg['To'] = to_email
msg['Subject'] = 'Daily News'
msg.attach(MIMEText('Please find attached today\'s news digest.'))

# Attach the PDF file
with open(currentdate +'_news.pdf', 'rb') as f:
    attachment = MIMEBase('application', 'pdf')
    attachment.set_payload(f.read())
    encoders.encode_base64(attachment)
    attachment.add_header('Content-Disposition', 'attachment', filename=  currentdate +'_news.pdf')
    print(attachment)
    msg.attach(attachment)
# Send the email


def send_news():
    smtp = smtplib.SMTP(smtp_server, smtp_port)
    smtp.starttls()
    smtp.login(smtp_username, smtp_password)
    smtp.sendmail(from_email, to_email, msg.as_string())
    smtp.quit()

send_news()
