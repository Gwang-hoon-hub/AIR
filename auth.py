import jwt
from flask_bcrypt import Bcrypt

SECRET_KEY = '123'
app.config['SECRET_KEY'] = SECRET_KEY  # 임시 번호
app.config['BCRYPT_LEVEL'] = 10
bcrypt = Bcrypt(app);