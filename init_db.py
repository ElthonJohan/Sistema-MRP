from database import Base, engine

# importar todos los modelos
from models import warehouse, material, inventory
from models import requirement, dispatch, receipt, movement

def init_db():
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    print("Base de datos creada correctamente")