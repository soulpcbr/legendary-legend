import cv2
import numpy as np

def process_image_for_ocr(image_np, invert=False):
    """
    Processa uma imagem (numpy array) para melhorar a precisão do OCR.

    :param image_np: Imagem em formato numpy array (BGR ou RGB).
    :param invert: Se True, inverte as cores (útil para texto branco em fundo preto).
    :return: Imagem processada (binarizada).
    """
    # Converter para escala de cinza
    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)

    # Inverter cores se solicitado
    # Tesseract prefere texto preto em fundo branco.
    # Se a legenda for branca em fundo preto (padrão Windows), inverter torna preto em branco.
    if invert:
        gray = cv2.bitwise_not(gray)

    # Aplicar thresholding (binarização)
    # Otsu's thresholding determina automaticamente o valor ideal de corte
    # É robusto para diferentes condições de iluminação
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

    # Opcional: Dilation/Erosion se o texto estiver muito fino ou grosso
    # Por enquanto, apenas binarização deve bastar para fontes de tela (que são nítidas)

    return binary
