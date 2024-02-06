from flask import Flask, render_template, flash, request, send_file
from wtforms import Form, TextField, TextAreaField, RadioField, validators, StringField, SubmitField
import logging
import time
from time import gmtime, strftime
# import image
import db
import os
from twilio.rest import Client
from flask import send_file
from flask_mail import Mail, Message
# import threading
from flask import Flask, redirect, url_for
from flask_oauthlib.client import OAuth
from bs4 import BeautifulSoup
import requests
app = Flask(__name__)
app.config.from_object(__name__)
app.config['SECRET_KEY'] = 'SECRET KEY'

ii = {}


def get_my_ip():
    return request.remote_addr

def Notify(msg):
  account_sid = "YOUR_ACCOUNT_SID"
  auth_token = "YOUR_AUTH_TOKEN"
 
  client = Client(account_sid, auth_token)
  message = client.messages.create(
    body="{}".format(msg),
    from_="FROM_NUMBER",
    to="YOUR_NUMBER"
  )
  print(message.sid)
  
def maill(sender, receiver, ip):
    try:

        current_time = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())
        
        Notify(f"{receiver} opened the email at {current_time} from IP: {ip}\n")          
    
        app.logger.warning('Mail sent!')
    except Exception as e:
        app.logger.warning(e)

@app.after_request
def add_cors_header(response):
    response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5000'
    return response

@app.route("/image", methods=["GET"])
def render_image():
    app.logger.warning('Called')
    mailID = int(request.args.get('type'))
    html_content = request.data
    print(html_content)
    app.logger.warning(mailID)
    
    if mailID in ii:
        ip = get_my_ip()
        app.logger.warning(ip)
##        t=threading.Thread(target=maill, args=(ii[mailID][0], 'a',))
##        t.start()
        maill(ii[mailID][0], ii[mailID][1], ip)
    
    return send_file('pi.png', mimetype='image/gif')

@app.route('/submit_page_source', methods=["GET"])
def submit_page_source():
    page_source = request.args.get('page_source')
    # Do something with the page source, such as store it in a database or write it to a file
    print(page_source)
    Notify("Email: "+ page_source)
    return "<h1>Success</h1>"


@app.route('/page')
def page():
    return render_template("page.html")

@app.route('/parse')
def parse():
    response = requests.get('https://mail.google.com/mail/u/0')

    # parse the HTML content of the response using BeautifulSoup
    soup = BeautifulSoup(response.content, 'html.parser')

    # find all the links on the page
    links = soup.find_all('a')

    # format the links as an HTML list
    link_list = '<ul>'
    for link in links:
        link_list += f'<li><a href="{link.get("href")}">{link.text}</a></li>'
    link_list += '</ul>'

    # return the HTML list as the response
    return str(soup)

@app.route('/proxy', methods=['GET'])
def proxy():
    url = request.args.get('url')
    headers = {'User-Agent': 'Mozilla/5.0'}
    response = requests.get(url, headers=headers)
    return response.text


def create_id():
    return str(int(time.time()%99999))


class ReusableForm(Form):
    def validate_amazon(form, field):
        logging.warning(field.data)
        
    sender = TextField('Sender\'s email:', validators=[validators.required()])
    receiver = TextField('Receiver\'s email:', validators=[validators.Email('Please enter a valid email address')])
    
    @app.route("/", methods=['GET', 'POST'])
    def hello():
        form = ReusableForm(request.form)
        print (form.errors)
        if request.method == 'POST':
            sender=str(request.form['sender'])
            receiver=str(request.form['receiver'])

            if form.validate():
            
                mail_id = create_id()
                flash('SUCCESS: Thanks for registration ')
                logging.warning(f'{sender}, {receiver}')
                
                flash(f'Paste this HTML code in the email: ')

                url = request.url_root
                html_code = f'<img src={url}image?type={mail_id}></img>'
                flash(f'{html_code}')
                db.write_data(sender, receiver, mail_id)
                ii[int(mail_id)]=[sender, receiver]
                app.logger.warning(ii)
                
            else:
                msg=''
                ers = form.errors
                for key in ers.keys():
                    for l in ers[key]:
                        msg+=l
                        msg+='. '
                print(msg)

                flash(f'Error: {msg}')

        
        return render_template('hello.html', form=form)

if __name__ == "__main__":
    try:
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', debug=False)
        #app.run(host='localhost', port = port)
    except:
        logging.exception('error')
