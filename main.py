from flask import Flask, render_template, request, redirect, url_for, flash, session
import firebase_admin
from firebase_admin import credentials, auth, db
import os
import base64
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask_socketio import SocketIO


app = Flask(__name__)
app.secret_key = '12341234'

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
messages = []

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form.get('pw')
        hashed_password = hash_password(password)
        name = request.form['name']

        # Firebase Authentication을 통한 회원가입
        try:
            user = auth.create_user(
                email=email,
                password=password
            )
            user_data = {'email': email, 'name': name,'password':password}
            ref_users = db.reference('users')
            ref_users.push(user_data)
            flash("회원가입이 완료되었습니다!", 'success')
            return redirect(url_for('login_user'))
        except auth.AuthError as e:
            flash(f"회원가입 중 오류가 발생했습니다: {e}", 'danger')
            return redirect(url_for('signin'))

    return render_template('signin.html')


def hash_password(password):
    # 솔트 생성
    salt = os.urandom(16)

    # PBKDF2 알고리즘을 사용하여 비밀번호 해싱
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))

    # 해시된 비밀번호와 솔트를 조합하여 저장
    hashed_password = f'{base64.urlsafe_b64encode(salt).decode()}${key.decode()}'
    return hashed_password

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
        print(query.items())
        for user_key, user_data in query.items():
            if user_data.get('password') == password:
                session['user_id'] = user_key
                session['username'] = user_data.get('username')
                flash("로그인 성공!", 'success')
                return redirect(url_for('chat'))

        flash("이메일 또는 비밀번호가 올바르지 않습니다.", 'danger')
        return redirect(url_for('login_user'))

    return render_template('login.html')


@app.route('/chat', methods=['GET', 'POST'])
def chat():
    if request.method == 'POST':
        new_message = {'sender': 'sender', 'text': request.form.get('message')}
        messages.append(new_message)

    return render_template('chatting.html', messages=messages)

@app.route('/logout')
def logout():
    session.clear()
    flash("로그아웃 되었습니다.", 'success')
    return redirect(url_for('login'))

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8020, debug=True)
