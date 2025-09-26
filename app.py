from flask import Flask, request, send_file, jsonify
from weasyprint import HTML
from bs4 import BeautifulSoup
import io
import os

app = Flask(__name__)

def html_to_pdf(html_content, auto_style=True):
    """
    Convert HTML string to PDF in memory.
    Returns a BytesIO object with PDF data.
    """
    if auto_style:
        soup = BeautifulSoup(html_content, 'html.parser')

        # Add default styling if none is present
        if not soup.find('style') and not soup.find('link', rel='stylesheet'):
            style_tag = soup.new_tag('style')
            style_tag.string = """
                body {
    font-family: Arial, Helvetica, sans-serif;
    margin: 40px;
    line-height: 1.6;
    color: #333;
}

                h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
                h2 { color: #34495e; margin-top: 30px; }
                h3 { color: #7f8c8d; }
                p { margin-bottom: 12px; text-align: justify; }
                table { border-collapse: collapse; width: 100%; margin: 20px 0; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #3498db; color: white; }
                tr:nth-child(even) { background-color: #f8f9fa; }
                img { max-width: 100%; height: auto; }
            """
            if soup.head:
                soup.head.append(style_tag)
            else:
                head_tag = soup.new_tag('head')
                head_tag.append(style_tag)
                soup.insert(0, head_tag)

            html_content = str(soup)

    # Generate PDF into memory
    pdf_io = io.BytesIO()
    HTML(string=html_content).write_pdf(pdf_io)
    pdf_io.seek(0)
    return pdf_io

# -------------------------------
# Routes
# -------------------------------

@app.route("/", methods=["GET"])
def home():
    """Root endpoint for browser/health testing"""
    return jsonify({
        "message": "PDF API is running! Use POST /convert to generate PDFs.",
        "endpoints": {
            "POST /convert": "Convert HTML to PDF (JSON: {html, filename})",
            "GET /health": "Health check"
        }
    })

@app.route("/convert", methods=["POST"])
def convert_html():
    """
    Convert HTML -> PDF.
    JSON body: { "html": "<html>...</html>", "filename": "mydoc.pdf" }
    """
    try:
        data = request.get_json(force=True)
        html_content = data.get("html", "")
        filename = data.get("filename", "document.pdf")

        if not html_content.strip():
            return jsonify({"error": "Missing 'html' content"}), 400

        pdf_io = html_to_pdf(html_content)

        return send_file(
            pdf_io,
            mimetype="application/pdf",
            as_attachment=True,
            download_name=filename
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/health", methods=["GET"])
def health():
    """Simple health check endpoint"""
    return jsonify({"status": "ok"}), 200

# -------------------------------
# Main entry
# -------------------------------

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
