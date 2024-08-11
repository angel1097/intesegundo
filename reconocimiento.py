import cv2
import mediapipe as mp
import numpy as np
import os

# Función para cargar imágenes y convertirlas en vectores de características
def cargar_imagenes(carpeta):
    imagenes = []
    rutas = [os.path.join(carpeta, f) for f in os.listdir(carpeta) if f.endswith('.png')]
    for ruta in rutas:
        imagen = cv2.imread(ruta)
        if imagen is not None:
            imagenes.append(imagen)
    return imagenes

# Función para extraer características faciales usando Face Mesh
def extraer_caracteristicas(imagen):
    if imagen is None:
        print("Error: La imagen es None.")
        return None

    if not isinstance(imagen, np.ndarray):
        print("Error: La imagen no es una matriz NumPy.")
        return None

    # Validar dimensiones
    if len(imagen.shape) != 3 or imagen.shape[2] != 3:
        print("Error: La imagen no tiene 3 canales de color.")
        return None

    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=True, max_num_faces=1, min_detection_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils
    imagen_rgb = cv2.cvtColor(imagen, cv2.COLOR_BGR2RGB)
    resultados = face_mesh.process(imagen_rgb)

    if resultados.multi_face_landmarks:
        landmarks = resultados.multi_face_landmarks[0]
        ih, iw, _ = imagen.shape
        características = np.array([
            (landmark.x * iw, landmark.y * ih)
            for landmark in landmarks.landmark
        ])
        return características
    return None


# Función para comparar dos imágenes de rostros
def comparar_rostros(imagen1, imagen2):
    características1 = extraer_caracteristicas(imagen1)
    características2 = extraer_caracteristicas(imagen2)

    if características1 is not None and características2 is not None:
        # Comparar características usando distancia  simple
        distancia = np.linalg.norm(características1 - características2)
        return distancia
    return float('inf')

def reconocer_rostro(imagen):
    carpeta = 'capturas'
    imagenes = cargar_imagenes(carpeta)

    for imagen_registrada in imagenes:
        distancia = comparar_rostros(imagen, imagen_registrada)
        if distancia < 1000:  #  considera otro  rostro similar en la carpeta capturas
            return True

    return False

def iniciar_reconocimiento_biometrico():
    carpeta = 'capturas'
    imagenes = cargar_imagenes(carpeta)

    cap = cv2.VideoCapture(0)
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar el frame.")
            break

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        resultados = face_mesh.process(frame_rgb)

        if resultados.multi_face_landmarks:
            for face_landmarks in resultados.multi_face_landmarks:
                ih, iw, _ = frame.shape
                x_min = int(min([landmark.x for landmark in face_landmarks.landmark]) * iw)
                x_max = int(max([landmark.x for landmark in face_landmarks.landmark]) * iw)
                y_min = int(min([landmark.y for landmark in face_landmarks.landmark]) * ih)
                y_max = int(max([landmark.y for landmark in face_landmarks.landmark]) * ih)

                x_min = max(x_min, 0)
                x_max = min(x_max, iw)
                y_min = max(y_min, 0)
                y_max = min(y_max, ih)

                rostro = frame[y_min:y_max, x_min:x_max]
                if rostro is not None and isinstance(rostro, np.ndarray):
                    cv2.imshow('Reconocimiento Biométrico', rostro)

                    if reconocer_rostro(rostro):
                        cap.release()
                        cv2.destroyAllWindows()
                        return True

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    return False

