import os
from database import SessionLocal
from models.material import Material
from models.requirement import Requirement
from models.warehouse import Warehouse
from .advanced_pdf_generator import GuiaRemisionPDF  


def generate_dispatch_pdf(dispatch):
    """
    Genera el PDF de la guía de remisión para el objeto dispatch dado.
    Retorna la ruta del archivo generado.
    """
    db = SessionLocal()

    try:
        # Datos del requerimiento 
        requirement = db.query(Requirement).filter(
            Requirement.id == dispatch.requirement_id
        ).first()

        destination_name     = "Desconocido"
        destination_location = "Desconocido"

        if requirement:
            destination_warehouse = db.query(Warehouse).filter(
                Warehouse.id == requirement.warehouse_id_obra
            ).first()
            if destination_warehouse:
                destination_name     = destination_warehouse.name
                destination_location = destination_warehouse.location or ""

        origin_name = "Almacén Principal"
        origin_location = ""

        # Buscar el almacén principal en la base de datos
        origin_warehouse = db.query(Warehouse).filter(
            Warehouse.type == "Almacén Principal"
            ).first()
        origin_name     = origin_warehouse.name     if origin_warehouse else "Almacén Principal"
        origin_location = origin_warehouse.location if origin_warehouse else ""

        #  Fecha formateada 
        if hasattr(dispatch.dispatch_date, "strftime"):
            fecha_str = dispatch.dispatch_date.strftime("%d / %m / %Y")
        else:
            fecha_str = str(dispatch.dispatch_date)

        #  Ítems de la guía 
        items_data = []
        for item in dispatch.items:
            material = db.query(Material).filter(
                Material.id == item.material_id
            ).first()
            material_name = material.name if material else "Material desconocido"
            items_data.append({
            "cantidad":    item.dispatched_qty,
            "unidad":      material.unit if material and material.unit else "UND",
            "descripcion": material_name,
        })

        # Generar PDF 
        os.makedirs("storage/guides", exist_ok=True)
        filename = f"storage/guides/{dispatch.guia_number}.pdf"

        pdf = GuiaRemisionPDF(filename)
        pdf.build(
            guia_number        = dispatch.guia_number,
            fecha_emision      = fecha_str,
            fecha_traslado     = fecha_str,
            punto_partida      = origin_name,
            origen_ubicacion   = origin_location,                
            punto_llegada      = destination_name,      
            destino_ubicacion  = destination_location,  
            destinatario       = destination_name,
            ruc_destinatario   = "",
            tipo_doc_dest      = "",
            items              = items_data,
            tipo_comprobante   = f"Requerimiento ID: {dispatch.requirement_id}",
        )

        return filename

    finally:
        db.close()