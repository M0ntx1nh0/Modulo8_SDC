from fpdf import FPDF
import os

def generar_pdf_resultados(jugador, radar_image_path, pdf_file_name):
    pdf = FPDF()
    pdf.add_page()

    # Agregar título
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, txt=f"Resumen de {jugador}", ln=True, align="C")
    pdf.ln(10)  # Añadir espacio antes de la imagen

    # Añadir la imagen generada
    pdf.image(radar_image_path, x=10, y=pdf.get_y(), w=180)  # Ajuste la imagen al PDF

    # Guardamos el PDF en el archivo correspondiente
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)
    
    # Usamos el nombre que recibimos como argumento para el PDF
    output_path = os.path.join(output_dir, pdf_file_name)
    pdf.output(output_path)

    return output_path