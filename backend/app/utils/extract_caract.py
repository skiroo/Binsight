import os
import json
import numpy as np
import cv2
from PIL import Image as PILImage

def extraire_caracteristiques(image_path):
    with PILImage.open(image_path) as img:
        img = img.convert('RGB')
        np_img = np.array(img)
        hauteur, largeur = img.shape[:2]
        taille_ko = round(os.path.getsize(image_path) / 1024, 2)

        # Moyenne RGB
        moyenne_rouge = int(np.mean(np_img[:, :, 0]))
        moyenne_vert = int(np.mean(np_img[:, :, 1]))
        moyenne_bleu = int(np.mean(np_img[:, :, 2]))

        # Contraste (max - min pixel value)
        contraste = float(np.max(np_img) - np.min(np_img))

        # Histogramme RGB (256 niveaux)
        hist_r = cv2.calcHist([np_img], [0], None, [256], [0, 256]).flatten().tolist()
        hist_g = cv2.calcHist([np_img], [1], None, [256], [0, 256]).flatten().tolist()
        hist_b = cv2.calcHist([np_img], [2], None, [256], [0, 256]).flatten().tolist()
        histogramme = json.dumps({'r': hist_r, 'g': hist_g, 'b': hist_b})

        # Contours détectés (Canny)
        gray = cv2.cvtColor(np_img, cv2.COLOR_RGB2GRAY)
        edges = cv2.Canny(gray, 100, 200)
        contours_detectes = bool(np.sum(edges) > 0)

        # Luminance moyenne (perçue)
        luminance = np.mean(0.2126 * np_img[:, :, 0] + 0.7152 * np_img[:, :, 1] + 0.0722 * np_img[:, :, 2])

        # Ratio de pixels sombres (valeurs < 50)
        dark_ratio = np.sum(gray < 50) / gray.size

        # Texture globale (Laplacien)
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        texture_score = np.var(laplacian)

        return {
            'taille_ko': taille_ko,
            'hauteur': hauteur,
            'largeur': largeur,
            'moyenne_rouge': moyenne_rouge,
            'moyenne_vert': moyenne_vert,
            'moyenne_bleu': moyenne_bleu,
            'contraste': contraste,
            'histogramme': histogramme,
            'contours_detectes': contours_detectes,
            'luminance_moyenne': round(float(luminance), 2),
            'dark_pixel_ratio': round(float(dark_ratio), 4),
            'texture_score': round(float(texture_score), 2)
        }
