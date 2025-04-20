from flask import Flask, render_template, request, redirect, url_for, session
import smtplib
from email.mime.text import MIMEText
import requests
from flask_mail import Mail, Message
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask import Flask, render_template
from flask_socketio import SocketIO, send, emit
app = Flask(__name__)

# Your Hugging Face API Key
HUGGINGFACE_API_KEY = "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"
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)
# Store pending meeting requests
pending_requests = []
meeting_requests=[]
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/products')
def products():
    return render_template('products.html')

@app.route('/usecase')
def usecase():
    return render_template('usecase.html')

@app.route('/partners')
def partners():
    return render_template('partners.html')

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/service')
def service():
    return render_template('service.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/chat')
def chat():
    return render_template('chat.html')

@app.route('/meeting_request')
def meeting_request():
    return render_template('meeting_request.html')

@app.route('/submit_request', methods=['POST'])
def submit_request():
    name = request.form.get('name')
    email = request.form.get('email')
    description = request.form.get('description')

    meeting_request = {
        'name': name,
        'email': email,
        'description': description
    }
    meeting_requests.append(meeting_request)

    print("New Meeting Request Added:", meeting_request)
    return "Meeting request submitted successfully!"

@socketio.on('message')
def handleMessage(msg):
    print('Message: ' + msg)
    send(msg, broadcast=True)

@socketio.on('join')
def handleJoin(username):
    print(f'{username} has joined the chat.')
    send(f'{username} has joined the chat.', broadcast=True)
# Flask-Mail config
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'abcd@gmail.com'   # Your Gmail
app.config['MAIL_PASSWORD'] = 'abcd'    # Your Gmail password or app password
mail = Mail(app)

app.secret_key = 'c20d2020bf6c2cb12dc5d2470df69151'  # Needed for session management

# ADMIN PASSWORD
ADMIN_PASSWORD = "admin123"  # Change as you like

# Admin Login Page
@app.route('/admin_login')
def admin_login():
    return render_template('admin_login.html')

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        password = request.form.get('password')
        if password == 'admin123':
            session['admin_logged_in'] = True
            return redirect(url_for('admin_dashboard'))
        else:
            return "Invalid password."

    return '''
        <form method="post">
            <input type="password" name="password" placeholder="Enter Admin Password" required>
            <button type="submit">Login</button>
        </form>
    '''

# Admin Dashboard (after login)
@app.route('/admin_dashboard')
def admin_dashboard():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin'))
    return render_template('admin_dashboard.html', requests=meeting_requests)


@app.route('/handle_request', methods=['POST'])
def handle_request():
    action = request.form.get('action')
    email = request.form.get('email')
    name = request.form.get('name')
    description = request.form.get('description')
    meeting_link = request.form.get('meeting_link')

    if action == 'accept':
        # send email with meeting link
        respon= send_email(email, name, meeting_link)
        #response = send_email("receiver@example.com", "John Doe", "https://your-meeting-link.com")
        print(respon.status_code)
        print(respon.text)
        # remove from meeting_requests after accepted

    elif action == 'reject':
        # simply remove from list
        remove_request(email)

    return redirect(url_for('admin_dashboard'))


def remove_request(email):
    global meeting_requests
    meeting_requests = [req for req in meeting_requests if req['email'] != email]

import smtplib
from email.mime.text import MIMEText

import requests

def send_email(receiver_email, name, meeting_link):
    api_key = "0413674bf8cb264fc5eb444d01b81632-17c877d7-c73f30a7"  # Replace with your Mailgun private API key
    domain = "sandbox0f56f04011fd42b1b1baa80d6b290bdd.mailgun.org"  # Find your Sandbox domain

    return requests.post(
        f"https://api.mailgun.net/v3/{domain}/messages",
        auth=("api", api_key),
        data={
            "from": f"Your App <mailgun@{domain}>",
            "to": [receiver_email],
            "subject": "Meeting Request Accepted!",
            "text": f"Hello {name},\n\nYour meeting request has been accepted!\nMeeting Link: {meeting_link}\n\nThank you."
        }
    )





@app.route('/logout')
def logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('about'))


# Accept Request (with Meeting Link)
@app.route('/admin/accept/<int:req_id>', methods=['POST'])
def admin_accept(req_id):
    meeting_link = request.form.get('meeting_link')
    for req in pending_requests:
        if req['id'] == req_id:
            req['status'] = 'Accepted'
            req['meeting_link'] = meeting_link

            # Send Email
            try:
                msg = Message('Meeting Scheduled ✅',sender=app.config['MAIL_USERNAME'],recipients=[req['email']])
                msg.body = f"""Hi {req['name']},

Good news! Your meeting request has been accepted.
Here is the meeting link: {meeting_link}

See you there!

Best Regards,
Your Team"""
                mail.send(msg)
            except Exception as e:
                print(f"Error sending email: {str(e)}")
            break
    return redirect(url_for('admin_dashboard'))

# Reject Request
@app.route('/admin/reject/<int:req_id>', methods=['POST'])
def admin_reject(req_id):
    for req in pending_requests:
        if req['id'] == req_id:
            req['status'] = 'Rejected'
            break
    return redirect(url_for('admin_dashboard'))

@app.route('/generate_content', methods=['POST'])
def generate_content():
    try:
        data = request.get_json()
        topic = data.get('topic', '')

        headers = {
            "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
        }

        payload = {
            "inputs": f"Write a detailed article about {topic}"
        }

        response = requests.post(
            "https://api-inference.huggingface.co/models/gpt2",
            headers=headers,
            json=payload
        )

        result = response.json()

        generated_text = result[0]['generated_text']

        return jsonify({'generated_text': generated_text})

    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
