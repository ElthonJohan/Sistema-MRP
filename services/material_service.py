from sqlalchemy.orm import Session
from models.material import Material

# Crear
def create_material(db: Session, code, name, unit, description):
    # Validar código único
    existing_code = db.query(Material).filter(Material.code == code).first()
    if existing_code:
        return False, 'code'

    # Validar nombre único
    existing_name = db.query(Material).filter(Material.name == name).first()
    if existing_name:
        return False, 'name'

    material = Material(
        code=code,
        name=name,
        unit=unit,
        description=description
    )
    db.add(material)
    db.commit()
    db.refresh(material)
    return True, material

# Listar
def get_materials(db: Session):
    return db.query(Material).all()

def get_materials_filtered(db: Session, skip: int=0, limit:int =10,
                           code_filter: str = None, name_filter: str = None, unit_filter: str = None):
    query = db.query(Material)

    if code_filter:
        query = query.filter(Material.code.ilike(f"%{code_filter}%"))
    if name_filter:
        query = query.filter(Material.name.ilike(f"%{name_filter}%"))
    if unit_filter:
        query = query.filter(Material.unit.ilike(f"%{unit_filter}%"))

    #Obtener total de materiales antes de paginar
    total_count = query.count()

    #Aplicar paginación
    materials = query.offset(skip).limit(limit).all()


    return materials, total_count

# Eliminar
def delete_material(db: Session, material_id):
    material = db.query(Material).filter(Material.id == material_id).first()
    if material:
        db.delete(material)
        db.commit()
        
def delete_material_code(db: Session, code):
    material = db.query(Material).filter(Material.code == code).first()
    if material:
        db.delete(material)
        db.commit()

# Actualizar
def update_material(db: Session, material_id, code, name, unit, description):
    material = db.query(Material).filter(Material.id == material_id).first()

    if material:
        # Validar código único (excepto el mismo)
        existing_code = db.query(Material).filter(
            Material.code == code,
            Material.id != material_id
        ).first()

        if existing_code:
            return False, 'code'

        # Validar nombre único (excepto el mismo)
        existing_name = db.query(Material).filter(
            Material.name == name,
            Material.id != material_id
        ).first()

        if existing_name:
            return False, 'name'

        material.code = code
        material.name = name
        material.unit = unit
        material.description = description

        db.commit()
        return True, material
