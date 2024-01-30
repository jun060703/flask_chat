from flask import Flask, render_template, request, redirect, url_for, flash, session,Response
import firebase_admin
from firebase_admin import credentials, auth, db
from flask_socketio import SocketIO, send,emit
import requests
import re
import socket
app = Flask(__name__)
app.secret_key = '12341234'
socketio = SocketIO(app)
connected_users = 0 

cred = credentials.Certificate({
    "type": "service_account",
    "project_id": "chatpotpolio",
    "private_key_id": "627656378f0ae6336c8cad2710c615c861c08045",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQCr3a1X6HfxXbkv\nKP2eUI8EA49smTfx084kszMNm6j9rzAx4Q6fpdKgHfnMAuj3Rh0wmPwMCNkxdGOR\nZfIHU1Z+Gx/EjJ6vuJXr4WqXU6sW9vcnSH1hDSb1YlcKKjwNx5VMcnibijFsutmp\nbH4N0SEAufalGEJYRDQCNKM/12AqHdMBmwugEHeqJt2NbX9hUttmHci/Wb8nIJzU\n300bp9Lye4x+6VH/rCVGd3NCEE+dlrQNtqBBzEZBToKJdeS+vfGAodNS4/9GB1Yu\n8id2Pc77NQ6/235YSn4S9O8rOBcc8YPnT54z2mSEZSGxn6Qat3zD0UTDYDHDRiHY\n0QC43NJ7AgMBAAECggEADAfG6AXmS3d3jIUOh8P01t+W7Q+mml9sqSYAF15DjIp0\nUbGC0AsP/NRMVYsImrKGPY4f6om+Bley1o0vzXJ4dfhZF22OeBdwKyRKzU/2hHOC\nJnZNDHuatAePty7wqDhFy6WhqqWYQxerP9BP3JC8giwCR1k036/agiMEIGZnnVr+\nuI/cjl3iQa125diduQuwOIkDQKVisUcpoa81PhjK9cB6tMatuxQ9UDvTqvixp4kg\nxSYd8jw7b1X2CgbArD1mMPGagEpz7RYocnRoSFxRVOCnImBBuw6ne2/0mduvaXLn\nqBq5KOFtbLrNoAjAfcye6T9DMuNA3tDdhh2kt8GyYQKBgQDWB1jM47M8e3GWfN3s\n1UIBnlDyEw5e0SGe9l6KuVyw+nWa8na3i2Q2OTGywFeiXqe4Gq/JriQYUFXSkKNt\nf/0k2vB6U3rvlPeB3gw4yJZlE49vwSasL/soUl10axrkEiOFHkxV2F/+A9k6fKEW\np85L/bpl2boTG7kFD4TZOrL/IQKBgQDNka2FdFMm1qpO1P1OiolCrd3CS7feMTq8\nFcH4W216DXuxIwNGO1zdwRCFSEBNBvl1TqKNrWaESz1qsTWlXg4XbuCBRBuCgXwA\n0DHeOqojKaLGQFZzYpNUaGzX3phJm3x85rwsgWRXQkjc65derrLMR0sbLCROQFQz\nlU6QKJCqGwKBgFRHmlk8ROVJOuZmj0FmjNJ0VC2vAVanBZVCMOJxsaVjSxJT7hnC\nwxhzFzXrddbTbTobECPb9gy4/cKoACLrZnSv3khdPSjAwWIbXTazDj4JIM+CAMeH\nMWCkZnakgndTCTevQaIATXSKcW0NjKWOOLdF17OptBM4NHhgrxCXg8rhAoGAQ264\nFwDzjdf5AecIOM1k/UR/bA7ef7pyY+RXPprvLIxjuNWda1ppuixsuOvce+f/yKVE\n2Wi6KkdsHCWJTXeu86zhZEXtKEBFZxbkZNull+c+h/3u3ebGIXgnzCAuoGaqzWX6\n8DZ5rc4GjMGTY/G2oR/52S3/stOTS2B85vkHi2UCgYBI3oGO7Gj5LNa3Mef7DhSM\nSGHBG+1r5wxrdVvGk/HBrCq9fKNf75DgfeN7ZdRuZcLSCnn7NltLzwPSi4NNAhuT\nJH0kDJjrVOtuME+QNGWtKZm2IP81xdtMcN4rTKq/j3RlmNDP1Cz1BwpNw0YHUlRp\nzZwwJcYhrhE9ALxXpd2XDg==\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-wxebv@chatpotpolio.iam.gserviceaccount.com",
    "client_id": "110127439326031644033",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-wxebv%40chatpotpolio.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
})
firebase_admin.initialize_app(cred, {'databaseURL': 'https://chatpotpolio-default-rtdb.asia-southeast1.firebasedatabase.app/'})
ref = db.reference('users')


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form.get('pw')
        name = request.form['name']


        user_data = {'email': email, 'name': name, 'password': password}
        ref_users = db.reference('users')
        ref_users.push(user_data)
        
        flash("회원가입이 완료되었습니다!", 'success')
        return redirect(url_for('login_user'))
    return render_template('signin.html')

@app.route('/login', methods=['GET', 'POST'])
def login_user():
    ref_users = db.reference('users')

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('pw')

        if email is None or password is None:
            flash("이메일 또는 비밀번호가 입력되지 않았습니다.", 'danger')
            return redirect(url_for('login_user'))

        query = ref_users.order_by_child('email').equal_to(email).get()
        
        for user_key, user_data in query.items():
            if user_data.get('password') == password:
                session['user_id'] = user_key
                session['username'] = user_data.get('name')
                flash("로그인 성공!", 'success')
                return redirect(url_for('chat'))

        flash("이메일 또는 비밀번호가 올바르지 않습니다.", 'danger')
        return redirect(url_for('login_user'))

    return render_template('login.html')

@app.route('/chat')
def chat():
    return render_template('chatting.html')


@socketio.on('connect')
def handle_connect():
    global connected_users
    connected_users += 1
    emit('update_user_count', {'count': connected_users}, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    global connected_users
    connected_users -= 1
    emit('update_user_count', {'count': connected_users}, broadcast=True)



@socketio.on('message')
def handle_message(msg):
    username = session.get('username')
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(("pwnbit.kr", 443))
    req = requests.get("http://ipconfig.kr")
    print("외부 IP: ", re.search(r'IP Address : (\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})', req.text)[1], end=" ")
    print("내부 IP: ", sock.getsockname()[0], end=" ")
    message=f"{username}: {msg}" 
    send(message, broadcast=True)
    


@app.route('/logout')
def logout():
    session.clear()
    flash("로그아웃 되었습니다.", 'success')
    return redirect(url_for('login'))

if __name__ == "__main__":
    socketio.run(app,host='0.0.0.0', port=9080, debug=True)
