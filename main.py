from flask import Flask, request, send_file
import tempfile
from pathlib import Path
import os

from core import apply_watermark
from settings import Settings

app = Flask(__name__)

settings = Settings(
    scale=10,
    position="bottomright",
    padding=1,
)

@app.route('/watermark', methods=['POST'])
def watermark_pdf():
    if 'file' not in request.files:
        return {'error': 'No file provided'}, 400
        
    file = request.files['file']
    if not file.filename.endswith('.pdf'):
        return {'error': 'File must be a PDF'}, 400

    # Create temporary files for input and output
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as input_temp:
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as output_temp:
            # Save uploaded file
            file.save(input_temp.name)
            
            try:
                # Apply watermark
                apply_watermark(Path(input_temp.name), output_temp.name, settings)
                
                # Send the watermarked file
                response = send_file(
                    output_temp.name,
                    mimetype='application/pdf',
                    as_attachment=True,
                    download_name=f'{file.filename}'
                )
                
                # Clean up temp files after sending response
                @response.call_on_close
                def cleanup():
                    os.unlink(input_temp.name)
                    os.unlink(output_temp.name)
                
                return response
                
            except Exception as e:
                # Clean up temp files on error
                os.unlink(input_temp.name)
                os.unlink(output_temp.name)
                return {'error': str(e)}, 500
            
if __name__ == '__main__':
    app.run()