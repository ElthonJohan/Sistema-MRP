"""
advanced_pdf_generator.py
Genera la Guía de Remisión - Remitente con el mismo layout visual
que el formulario impreso de Gráficos Wari E.I.R.L.
Usa ReportLab (ya instalado en el entorno).

Adaptado al modelo de datos del sistema MRP:
- Sin sección de unidad de transporte / conductor
- Sin sección de datos del transportista
- Motivo de traslado fijo: TRASLADO ENTRE ESTABLECIMIENTOS
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
import os

# ── Página A4 portrait ────────────────────────────────────────────────────────
PAGE_W, PAGE_H = A4          # 210 x 297 mm
M = 10 * mm                  # margen general

# Paleta
BLACK  = colors.black
WHITE  = colors.white
GRAY   = colors.HexColor("#CCCCCC")
DARK   = colors.HexColor("#222222")


def _line(c, x1, y1, x2, y2, width=0.5):
    c.setLineWidth(width)
    c.line(x1, y1, x2, y2)


def _rect(c, x, y, w, h, fill=None, stroke=True, line_width=0.5):
    c.setLineWidth(line_width)
    if fill:
        c.setFillColor(fill)
        c.rect(x, y, w, h, fill=1, stroke=1 if stroke else 0)
        c.setFillColor(BLACK)
    else:
        c.rect(x, y, w, h, fill=0, stroke=1 if stroke else 0)


def _text(c, x, y, txt, size=7, bold=False, align="L", width=None, color=BLACK):
    c.setFillColor(color)
    c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    if align == "C" and width:
        c.drawCentredString(x + width / 2, y, str(txt))
    elif align == "R" and width:
        c.drawRightString(x + width, y, str(txt))
    else:
        c.drawString(x, y, str(txt))
    c.setFillColor(BLACK)


class GuiaRemisionPDF:
    """
    Clase principal del formulario.
    Uso:
        g = GuiaRemisionPDF("storage/guides/GR-001.pdf")
        g.build(dispatch_data)
    """

    def __init__(self, filename: str):
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        self.filename = filename
        self.c = canvas.Canvas(filename, pagesize=A4)
        self.W = PAGE_W
        self.H = PAGE_H

    def _y(self, y_from_top_mm):
        """Convierte mm desde el borde superior a coordenada ReportLab."""
        return self.H - y_from_top_mm * mm

    # ─── Bloque superior izquierdo: datos empresa ─────────────────────────────
    def _draw_header_empresa(self):
        c = self.c
        x0 = M
        y0 = self._y(10)

        # Marco empresa
        _rect(c, x0, y0 - 28*mm, 65*mm, 30*mm)

        _text(c, x0 + 2*mm, y0 - 7*mm,  "POLYLINE",  size=14, bold=True)
        _text(c, x0 + 2*mm, y0 - 15*mm, "SAC",       size=25, bold=True)
        _text(c, x0 + 2*mm, y0 - 20*mm, "ARQUITECTURA &", size=10)
        _text(c, x0 + 2*mm, y0 - 25*mm, "CONSTRUCCIÓN", size=10)

        logo_path = "assets/logo.png"
        if os.path.exists(logo_path):
            c.drawImage(
            logo_path,
            x0 + 38*mm,        
            y0 - 27*mm,
            width=25*mm,
            height=27*mm,
            preserveAspectRatio=True,
            mask="auto"
        )


        # Cuadro publicidad (centro-superior)
        px = x0 + 67*mm
        _rect(c, px, y0 - 12*mm, 63*mm, 14*mm, fill=DARK)
        _text(c, px, y0 - 5*mm,  "CONSTRUCCION INMOBILIARIA",
              size=9, bold=True, color=WHITE, align="C", width=63*mm)
     
        _text(c, px + 1*mm, y0 - 18*mm,
              "Av. Gregorio Escobedo 558, Jesús María, Lima", size=7)
        _text(c, px + 1*mm, y0 - 21*mm,
              "polyliesac@yahoo.es", size=7)
        _text(c, px + 1*mm, y0 - 25*mm,
              "Cel.: 943 812 536", size=7)

    # Bloque superior derecho: RUC + título + número 
    
    def _draw_header_ruc(self, guia_number="001-"):
        c = self.c
        rx = self.W - M - 55*mm
        ry = self._y(10)

        # RUC 
        _rect(c, rx, ry - 10*mm, 55*mm, 10*mm, line_width=1.5)
        _text(c, rx, ry - 4*mm, "R.U.C. 20504133061",
              size=11, bold=True, align="C", width=55*mm)

        # GUIA DE REMISION - REMITENTE  
        _rect(c, rx, ry - 19*mm, 55*mm, 9*mm, line_width=1.5)
        _text(c, rx, ry - 13*mm, "GUIA DE REMISION - REMITENTE",
              size=8, bold=True, align="C", width=55*mm)

        # Número de guía  
        
        guia_font_size = 14 if len(str(guia_number)) <= 12 else 14
        _rect(c, rx, ry - 28*mm, 55*mm, 9*mm, line_width=1.5)
        _text(c, rx, ry - 24*mm, guia_number,
              size=guia_font_size, bold=True, align="C", width=55*mm)

    # Fila de fechas 
    def _draw_fechas(self, fecha_emision="", fecha_traslado=""):
        c = self.c
        y_top = self._y(43)   
        x0 = M
        
        col_w = (self.W - 2*M) / 2

        labels = ["FECHA DE EMISIÓN", "FECHA DE INICIO DE TRASLADO"]
        values = [fecha_emision, fecha_traslado]

        for i, (lbl, val) in enumerate(zip(labels, values)):
            cx = x0 + i * col_w
            _rect(c, cx, y_top - 8*mm, col_w, 8*mm)
            _text(c, cx, y_top - 3*mm, lbl, size=6, bold=True,
                  align="C", width=col_w)
            _text(c, cx, y_top - 7*mm, val, size=8,
                  align="C", width=col_w)

    #  Puntos de partida / llegada 
    def _draw_puntos(self, origen="", origen_ubicacion="",
                 destino="", destino_ubicacion=""):
        c = self.c
        y_top = self._y(53)
        x0 = M
        col_w = (self.W - 2*M) / 2

        for i, (titulo, almacen, ubicacion) in enumerate([
            ("PUNTO DE PARTIDA", origen, origen_ubicacion),
            ("PUNTO DE LLEGADA", destino, destino_ubicacion),
            ]):

            cx = x0 + i * col_w
            _rect(c, cx, y_top - 18*mm, col_w, 18*mm)
            _text(c, cx + 1*mm, y_top - 3*mm, titulo, size=7, bold=True)
            _text(c, cx + 1*mm, y_top - 7*mm, "ALMACÉN:", size=6)
            _text(c, cx + 14*mm, y_top - 7*mm, almacen, size=7)
            _line(c, cx + 14*mm, y_top - 7.5*mm,
                  cx + col_w - 2*mm, y_top - 7.5*mm)
            _text(c, cx + 1*mm, y_top - 11*mm, "UBICACIÓN:", size=6)
            _text(c, cx + 16*mm, y_top - 11*mm, ubicacion, size=7)
            _line(c, cx + 16*mm, y_top - 11.5*mm,
                cx + col_w - 2*mm, y_top - 11.5*mm)
        
        
          

    # Destinatario 

    def _draw_destinatario(self, destinatario="", ruc_dest="",
                           tipo_doc=""):
        c = self.c
        y_top = self._y(71)
        x0 = M
        total_w = self.W - 2*M

        _rect(c, x0, y_top - 20*mm, total_w, 20*mm)
        _text(c, x0 + 1*mm, y_top - 3*mm, "DESTINATARIO", size=7, bold=True)
        _text(c, x0 + 1*mm, y_top - 7*mm,
              "NOMBRES / DENOMINACIÓN / RAZÓN SOCIAL:", size=6)
        _text(c, x0 + 1*mm, y_top - 11*mm, destinatario, size=7)
        _line(c, x0 + 1*mm, y_top - 11.5*mm,
              x0 + total_w - 2*mm, y_top - 11.5*mm)
        

    #  Tabla de ítems 
    def _draw_tabla(self, items=None):
        c = self.c
        items = items or []
        y_top = self._y(93)
        x0 = M
        total_w = self.W - 2*M

        col_cant  = 22*mm
        col_unid  = 20*mm
        col_desc  = total_w - col_cant - col_unid
        row_h     = 7*mm
        n_rows    = 10  

        # Encabezado
        _rect(c, x0, y_top - row_h, col_cant, row_h, fill=GRAY)
        _rect(c, x0 + col_cant, y_top - row_h, col_unid, row_h, fill=GRAY)
        _rect(c, x0 + col_cant + col_unid, y_top - row_h,
              col_desc, row_h, fill=GRAY)

        _text(c, x0, y_top - row_h + 2*mm,
              "CANTIDAD", size=7, bold=True, align="C", width=col_cant)
        _text(c, x0 + col_cant, y_top - row_h + 2*mm,
              "UNID.", size=6, bold=True, align="C", width=col_unid)
        _text(c, x0 + col_cant + col_unid, y_top - row_h + 2*mm,
              "M A T E R I A L", size=7, bold=True,
              align="C", width=col_desc)

        # Filas
        for i in range(n_rows):
            ry = y_top - row_h * (i + 2)
            _rect(c, x0, ry, col_cant, row_h)
            _rect(c, x0 + col_cant, ry, col_unid, row_h)
            _rect(c, x0 + col_cant + col_unid, ry, col_desc, row_h)

            if i < len(items):
                item = items[i]
                _text(c, x0 + 1*mm, ry + 2*mm,
                      str(item.get("cantidad", "")), size=8)
                _text(c, x0 + col_cant + 1*mm, ry + 2*mm,
                      str(item.get("unidad", "UND")), size=8)
                _text(c, x0 + col_cant + col_unid + 1*mm, ry + 2*mm,
                      str(item.get("descripcion", "")), size=8)

   
   #OBSERVACIONES
    def _draw_motivo(self):
        c = self.c
        y_top = self._y(170)
        x0 = M
        total_w = self.W - 2*M

        _rect(c, x0, y_top - 20*mm, total_w, 20*mm)
        _text(c, x0 + 1*mm, y_top - 4*mm, "OBSERVACIONES", size=7, bold=True)
        for i in range(2):
            ly = y_top - 11*mm - i * 4*mm
            _line(c, x0 + 2*mm, ly, x0 + total_w - 2*mm, ly)

    #  Tipo y número de comprobante 
    def _draw_comprobante(self, tipo_comprobante=""):
        c = self.c
        y = self._y(196)
        _text(c, M, y, "TIPO Y NÚMERO DE COMPROBANTE DE PAGO:", size=6)
        _text(c, M + 65*mm, y, tipo_comprobante, size=7)
        _line(c, M + 65*mm, y - 1*mm, self.W - M, y - 1*mm)

    #  Firma final 
    def _draw_firma(self):
        c = self.c
        y_top = self._y(207)
        x0 = M
        total_w = self.W - 2*M
        col_w = total_w / 2

        _rect(c, x0, y_top - 18*mm, total_w, 18*mm)
        _line(c, x0 + col_w, y_top, x0 + col_w, y_top - 18*mm)

        _text(c, x0, y_top - 6*mm, "Recibí Conforme",
              size=8, bold=True, align="C", width=col_w)
        _text(c, x0 + col_w, y_top - 6*mm, "POLYLINE SAC",
              size=8, bold=True, align="C", width=col_w)

        _text(c, x0 + 2*mm, y_top - 15*mm, "Sr.(a)(ta):", size=7)
        _line(c, x0 + 20*mm, y_top - 15*mm,
              x0 + col_w - 2*mm, y_top - 15.5*mm)
        
        _text(c, x0 + col_w + 2*mm, y_top - 15*mm, "Sr.:", size=7)
        _line(c, x0 + col_w + 15*mm, y_top - 15*mm,
              x0 + total_w - 2*mm, y_top - 15.5*mm)

    # Método principal 
    def build(self,
          guia_number="001-",
          fecha_emision="",
          fecha_traslado="",
          punto_partida="",
          origen_ubicacion="",        
          punto_llegada="",
          destino_ubicacion="",       
          destinatario="",
          ruc_destinatario="",
          tipo_doc_dest="",
          items=None,
          tipo_comprobante=""):
        
        self._draw_header_empresa()
        self._draw_header_ruc(guia_number)
        self._draw_fechas(fecha_emision, fecha_traslado)
        self._draw_puntos(punto_partida, origen_ubicacion,
                          punto_llegada, destino_ubicacion)   # ← actualizado
        self._draw_destinatario(destinatario, ruc_destinatario, tipo_doc_dest)
        self._draw_tabla(items)
        self._draw_motivo()
        self._draw_comprobante(tipo_comprobante)
        self._draw_firma()

        self.c.save()
        return self.filename

