import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app, db, User, Category, Product
from werkzeug.security import generate_password_hash

def seed():
    with app.app_context():
        db.create_all()
        
        # Check if admin exists
        if not User.query.filter_by(email='admin@example.com').first():
            admin = User(
                username='AdminBoss',
                email='admin@example.com',
                password=generate_password_hash('admin123', method='pbkdf2:sha256'),
                is_admin=True
            )
            db.session.add(admin)
            print("✅ Admin created: admin@example.com / admin123")

        # Categories
        cats = ['Hoa Tình Yêu', 'Hoa Sinh Nhật', 'Hoa Khai Trương', 'Hoa Cưới', 'Lan Hồ Điệp']
        cat_objs = []
        for c_name in cats:
            c = Category.query.filter_by(name=c_name).first()
            if not c:
                c = Category(name=c_name)
                db.session.add(c)
                cat_objs.append(c)
            else:
                cat_objs.append(c)
        db.session.commit()
        
        # Products (Dummy Data - using Placehold.co for images)
        # Note: In production, these should be local files in static/uploads
        if Product.query.count() == 0:
            products = [
                {"name": "Bó Hồng Đỏ Thắm", "price": 500000, "cat": cat_objs[0], "img": "https://placehold.co/400x400/ffadad/white?text=Hong+Do"},
                {"name": "Giỏ Hướng Dương", "price": 350000, "cat": cat_objs[1], "img": "https://placehold.co/400x400/ffd6a5/white?text=Huong+Duong"},
                {"name": "Lãng Hoa Chúc Mừng", "price": 1200000, "cat": cat_objs[2], "img": "https://placehold.co/400x400/fdffb6/black?text=Chuc+Mung"},
                {"name": "Bó Baby Trắng", "price": 450000, "cat": cat_objs[0], "img": "https://placehold.co/400x400/caffbf/black?text=Baby+White"},
                {"name": "Lan Hồ Điệp Vàng", "price": 2500000, "cat": cat_objs[4], "img": "https://placehold.co/400x400/9bf6ff/black?text=Lan+Vang"},
                {"name": "Hoa Cầm Tay Cô Dâu", "price": 800000, "cat": cat_objs[3], "img": "https://placehold.co/400x400/a0c4ff/white?text=Co+Dau"},
            ]
            
            for p in products:
                # Hack: Storing full URL for seed data, but app handles filename usually
                prod = Product(
                    name=p['name'], 
                    price=p['price'], 
                    description="Mẫu hoa thiết kế hiện đại, phù hợp tặng dịp đặc biệt.",
                    stock=20,
                    category=p['cat'],
                    image=p['img'] 
                )
                db.session.add(prod)
            db.session.commit()
            print("✅ Dummy products seeded!")
        else:
            print("ℹ️ Products already exist.")

if __name__ == '__main__':
    seed()