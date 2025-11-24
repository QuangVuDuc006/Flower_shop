import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'bi-mat-khong-the-bat-mi'
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Lấy link DB từ biến môi trường (trên Render), nếu ko có thì dùng SQLite (ở nhà)
    uri = "postgresql://neondb_owner:npg_B63WdJaTIYnf@ep-frosty-mountain-ah14v267-pooler.c-3.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require"

    # uri = os.environ.get('DATABASE_URL')
    if uri and uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)
    SQLALCHEMY_DATABASE_URI = uri or 'sqlite:///' + os.path.join(basedir, 'flower_shop.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(basedir, 'static/uploads')

    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,  # Kiểm tra kết nối trước khi dùng (Quan trọng nhất)
        "pool_recycle": 300,    # Tự động làm mới kết nối sau mỗi 300 giây (5 phút)
    }