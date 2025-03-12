from flask import Flask, request, jsonify, send_file
import os
import subprocess

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.route("/run-energyplus", methods=["POST"])
def run_energyplus():
    if "idf" not in request.files or "epw" not in request.files:
        return jsonify({"error": "Arquivos .idf e .epw são obrigatórios!"}), 400

    idf_file = request.files["idf"]
    epw_file = request.files["epw"]

    idf_path = os.path.join(UPLOAD_FOLDER, "input.idf")
    epw_path = os.path.join(UPLOAD_FOLDER, "weather.epw")

    idf_file.save(idf_path)
    epw_file.save(epw_path)

    try:
        # Rodar EnergyPlus
        command = ["EnergyPlus", "-r", "-d", OUTPUT_FOLDER, "-w", epw_path, idf_path]
        result = subprocess.run(command, capture_output=True, text=True)

        if result.returncode != 0:
            return jsonify({"error": f"Erro ao rodar EnergyPlus: {result.stderr}"}), 500

        # Enviar o arquivo de saída
        output_csv = os.path.join(OUTPUT_FOLDER, "eplusout.csv")
        return send_file(output_csv, as_attachment=True, download_name="resultados.csv")

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
