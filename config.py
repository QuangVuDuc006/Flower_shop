import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bi-mat-khong-the-bat-mi'
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Lấy link DB từ biến môi trường (trên Render), nếu ko có thì dùng SQLite (ở nhà)

    uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = uri or 'sqlite:///' + os.path.join(basedir, 'flower_shop.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')