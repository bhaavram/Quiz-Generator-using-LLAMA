import io
import zipfile

def create_zip(qti_content):
    """
    Create a ZIP file containing the QTI file.
    """
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
        zipf.writestr("quiz.qti", qti_content)
    zip_buffer.seek(0)
    return zip_buffer