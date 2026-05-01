import io
import PyPDF2
import logging

logger = logging.getLogger(__name__)


def encrypt_pdf(file_bytes: bytes, password: str) -> io.BytesIO:
    """
    Agrega una contraseña de apertura al PDF.
    """
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        writer = PyPDF2.PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(password)

        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream
    except Exception as e:
        logger.error(f"Error encrypting PDF: {e}")
        raise ValueError(
            "No se pudo encriptar el PDF. Asegúrate de que el archivo es válido y no está ya protegido."
        )


def unlock_pdf(file_bytes: bytes, password: str) -> io.BytesIO:
    """
    Remueve la protección de un PDF si se proporciona la contraseña correcta.
    """
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))

        if reader.is_encrypted:
            # Intenta desencriptar
            success = reader.decrypt(password)
            if not success:
                raise ValueError("Contraseña incorrecta.")
        else:
            raise ValueError("El archivo no está encriptado.")

        writer = PyPDF2.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream
    except ValueError as ve:
        raise ve
    except Exception as e:
        logger.error(f"Error unlocking PDF: {e}")
        raise ValueError(
            "Error procesando el PDF protegido. Verifica que el archivo no esté corrupto."
        )


def set_permissions_pdf(
    file_bytes: bytes,
    owner_password: str,
    user_password: str = "",
    block_print: bool = False,
    block_modify: bool = False,
    block_copy: bool = False,
    block_annotate: bool = False,
    block_fill_forms: bool = False,
    block_assemble: bool = False,
    block_print_high_res: bool = False,
) -> io.BytesIO:
    """
    Aplica restricciones de permisos al PDF usando contraseñas.
    """
    try:
        # Por defecto permitimos todo (-4)
        permisos = -4

        # Limpiamos los bits para bloquear operaciones específicas
        if block_print:
            permisos &= ~4  # Bit 3: Print
        if block_modify:
            permisos &= ~8  # Bit 4: Modify
        if block_copy:
            permisos &= ~16  # Bit 5: Copy/Extract
        if block_annotate:
            permisos &= ~32  # Bit 6: Annotate
        if block_fill_forms:
            permisos &= ~256  # Bit 9: Fill interactive forms
        if block_assemble:
            permisos &= ~1024  # Bit 11: Assemble document
        if block_print_high_res:
            permisos &= ~2048  # Bit 12: Print high quality

        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))

        # Si el archivo origen ya está encriptado, hay que desencriptarlo primero
        # Asumiremos que el frontend enviaría el password de apertura si fuera necesario,
        # pero por ahora, la vista no lo pide para origen protegido. Si falla, dará error.
        if reader.is_encrypted:
            raise ValueError(
                "El archivo original está protegido. Desbloquéalo primero antes de cambiar permisos."
            )

        writer = PyPDF2.PdfWriter()
        for page in reader.pages:
            writer.add_page(page)

        writer.encrypt(
            user_password=user_password,
            owner_password=owner_password,
            permissions_flag=permisos,  # type: ignore
        )

        output_stream = io.BytesIO()
        writer.write(output_stream)
        output_stream.seek(0)
        return output_stream
    except ValueError as ve:
        raise ve
    except Exception as e:
        logger.error(f"Error setting permissions: {e}")
        raise ValueError("Error al configurar permisos en el archivo PDF.")
