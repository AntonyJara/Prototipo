from flask import Flask, request, jsonify, send_file, render_template_string
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
import openai
import os
from io import BytesIO
import json

app = Flask(__name__)

# Configurar OpenAI API
openai.api_key = os.environ.get('OPENAI_API_KEY')

# HTML INTEGRADO EN EL MISMO ARCHIVO
HTML_TEMPLATE = '''<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Asistente Pedagógico - Generador de Competencias</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            background: white;
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            max-width: 600px;
            width: 100%;
        }

        h1 {
            color: #667eea;
            text-align: center;
            margin-bottom: 10px;
            font-size: 28px;
        }

        .subtitle {
            text-align: center;
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 600;
            font-size: 14px;
        }

        select, input[type="text"] {
            width: 100%;
            padding: 12px 15px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 15px;
            transition: all 0.3s;
            font-family: inherit;
        }

        select:focus, input[type="text"]:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        button {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s, box-shadow 0.2s;
        }

        button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
        }

        button:active {
            transform: translateY(0);
        }

        button:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }

        .loading {
            display: none;
            text-align: center;
            margin-top: 20px;
            color: #667eea;
            font-weight: 600;
        }

        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
            margin: 20px auto;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .error {
            background: #fee;
            color: #c33;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            display: none;
        }

        .success {
            background: #efe;
            color: #3c3;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            display: none;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎓 Asistente Pedagógico</h1>
        <p class="subtitle">Generador de Competencias y Criterios de Evaluación</p>

        <form id="competenciaForm">
            <div class="form-group">
                <label for="ciclo">Ciclo Educativo:</label>
                <select id="ciclo" name="ciclo" required>
                    <option value="">Selecciona un ciclo</option>
                    <option value="III">III Ciclo (1° y 2° grado)</option>
                    <option value="IV">IV Ciclo (3° y 4° grado)</option>
                    <option value="V">V Ciclo (5° y 6° grado)</option>
                </select>
            </div>

            <div class="form-group">
                <label for="area">Área Curricular:</label>
                <select id="area" name="area" required>
                    <option value="">Selecciona un área</option>
                    <option value="Comunicación">Comunicación</option>
                    <option value="Matemática">Matemática</option>
                    <option value="Personal Social">Personal Social</option>
                    <option value="Ciencia y Tecnología">Ciencia y Tecnología</option>
                    <option value="Educación Religiosa">Educación Religiosa</option>
                    <option value="Arte y Cultura">Arte y Cultura</option>
                    <option value="Educación Física">Educación Física</option>
                </select>
            </div>

            <div class="form-group">
                <label for="tema">Tema de la Unidad:</label>
                <input type="text" id="tema" name="tema" placeholder="Ej: Conservando la naturaleza prevenimos los desastres" required>
            </div>

            <button type="submit" id="submitBtn">Generar Documento</button>
        </form>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Generando documento con IA, por favor espera...</p>
        </div>

        <div class="error" id="error"></div>
        <div class="success" id="success"></div>
    </div>

    <script>
        document.getElementById('competenciaForm').addEventListener('submit', async (e) => {
            e.preventDefault();

            const submitBtn = document.getElementById('submitBtn');
            const loading = document.getElementById('loading');
            const error = document.getElementById('error');
            const success = document.getElementById('success');

            error.style.display = 'none';
            success.style.display = 'none';

            submitBtn.disabled = true;
            loading.style.display = 'block';

            const formData = {
                ciclo: document.getElementById('ciclo').value,
                area: document.getElementById('area').value,
                tema: document.getElementById('tema').value
            };

            try {
                const response = await fetch('/generar', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(formData)
                });

                if (response.ok) {
                    const blob = await response.blob();
                    const url = window.URL.createObjectURL(blob);
                    const a = document.createElement('a');
                    a.href = url;
                    a.download = `Competencias_${formData.area}_Ciclo_${formData.ciclo}.docx`;
                    document.body.appendChild(a);
                    a.click();
                    window.URL.revokeObjectURL(url);
                    document.body.removeChild(a);

                    success.textContent = '✅ Documento generado exitosamente. Descarga iniciada.';
                    success.style.display = 'block';
                } else {
                    const errorData = await response.json();
                    throw new Error(errorData.error || 'Error al generar el documento');
                }
            } catch (err) {
                error.textContent = '❌ ' + err.message;
                error.style.display = 'block';
            } finally {
                loading.style.display = 'none';
                submitBtn.disabled = false;
            }
        });
    </script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/generar', methods=['POST'])
def generar_documento():
    try:
        data = request.json
        ciclo = data.get('ciclo')
        area = data.get('area')
        tema = data.get('tema')

        if not all([ciclo, area, tema]):
            return jsonify({'error': 'Faltan datos requeridos'}), 400

        # Generar contenido con IA
        contenido = generar_contenido_ia(ciclo, area, tema)

        # Crear documento Word
        doc = crear_documento_word(ciclo, area, tema, contenido)

        # Guardar en memoria
        file_stream = BytesIO()
        doc.save(file_stream)
        file_stream.seek(0)

        return send_file(
            file_stream,
            mimetype='application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            as_attachment=True,
            download_name=f'Competencias_{area}_Ciclo_{ciclo}.docx'
        )

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def generar_contenido_ia(ciclo, area, tema):
    prompt = f'''Eres un asistente pedagógico experto en el Currículo Nacional de Educación Básica del Perú.

Genera información educativa para:
- Ciclo: {ciclo}
- Área: {area}
- Tema: {tema}

Proporciona la siguiente información en formato JSON:
{{
  "competencia": "Nombre completo de la competencia del área según el Currículo Nacional",
  "capacidades": ["Capacidad 1", "Capacidad 2", "Capacidad 3"],
  "estandar": "Estándar de aprendizaje para el ciclo {ciclo} relacionado con esta competencia",
  "criterios": ["Criterio de evaluación 1", "Criterio de evaluación 2"],
  "instrumento": "Lista de cotejo",
  "competencia_transversal": "Nombre de la competencia transversal relacionada",
  "enfoque_transversal": "Nombre del enfoque transversal",
  "descripcion_enfoque": "Breve descripción del enfoque transversal"
}}

Asegúrate de que sea información precisa según el Currículo Nacional del Perú.'''

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Eres un experto en educación y currículo nacional peruano."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1500
        )

        contenido_texto = response.choices[0].message.content
        inicio = contenido_texto.find('{')
        fin = contenido_texto.rfind('}') + 1
        contenido_json = contenido_texto[inicio:fin]

        return json.loads(contenido_json)

    except Exception as e:
        print(f"Error en IA: {e}")
        return {
            "competencia": f"Competencia principal del área de {area}",
            "capacidades": ["Capacidad relacionada 1", "Capacidad relacionada 2"],
            "estandar": f"Estándar de aprendizaje para ciclo {ciclo}",
            "criterios": ["Criterio de evaluación 1", "Criterio de evaluación 2"],
            "instrumento": "Lista de cotejo",
            "competencia_transversal": "Gestiona su aprendizaje de manera autónoma",
            "enfoque_transversal": "Enfoque de orientación al bien común",
            "descripcion_enfoque": "Promueve valores y actitudes para el bienestar colectivo"
        }

def crear_documento_word(ciclo, area, tema, contenido):
    doc = Document()

    section = doc.sections[0]
    section.left_margin = Inches(0.8)
    section.right_margin = Inches(0.8)
    section.top_margin = Inches(0.8)
    section.bottom_margin = Inches(0.8)

    titulo = doc.add_heading('COMPETENCIAS Y CRITERIOS DE EVALUACIÓN', 0)
    titulo.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()
    info = doc.add_paragraph()
    info.add_run(f'Ciclo: ').bold = True
    info.add_run(f'{ciclo}\n')
    info.add_run(f'Área: ').bold = True
    info.add_run(f'{area}\n')
    info.add_run(f'Tema: ').bold = True
    info.add_run(f'{tema}')

    doc.add_paragraph()

    tabla = doc.add_table(rows=1, cols=5)
    tabla.style = 'Table Grid'

    headers = ['Competencias y Capacidades', 'Estándar de Aprendizaje', 
               'Criterios de Evaluación', 'Instrumento de Evaluación', 
               'Competencia Transversal']

    for i, header in enumerate(headers):
        cell = tabla.rows[0].cells[i]
        cell.text = header
        for paragraph in cell.paragraphs:
            for run in paragraph.runs:
                run.font.bold = True
                run.font.size = Pt(11)

    row = tabla.add_row()

    comp_text = f"{contenido['competencia']}\n\nCapacidades:\n" + "\n".join([f"• {cap}" for cap in contenido['capacidades']])
    row.cells[0].text = comp_text

    row.cells[1].text = contenido['estandar']

    crit_text = "\n".join([f"• {crit}" for crit in contenido['criterios']])
    row.cells[2].text = crit_text

    row.cells[3].text = contenido['instrumento']

    trans_text = f"{contenido['competencia_transversal']}\n\nEnfoque: {contenido['enfoque_transversal']}\n\n{contenido['descripcion_enfoque']}"
    row.cells[4].text = trans_text

    for row in tabla.rows:
        for cell in row.cells:
            cell.width = Inches(2.0)

    doc.add_paragraph()
    doc.add_paragraph()
    footer = doc.add_paragraph('Documento generado por Asistente Pedagógico IA')
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    footer.runs[0].font.size = Pt(9)
    footer.runs[0].font.color.rgb = RGBColor(128, 128, 128)

    return doc

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
