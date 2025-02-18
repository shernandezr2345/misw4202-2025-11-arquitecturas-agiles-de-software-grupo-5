import os

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "postgresql://admin:secret123*@localhost:5432/scrum")
    SQLALCHEMY_TRACK_MODIFICATIONS = False