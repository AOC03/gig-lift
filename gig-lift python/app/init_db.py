from .db import engine, Base
from . import models

if __name__ == "__main__":
    Base.metadata.create_all(bind=engine)
    print(" Database tables created.")
