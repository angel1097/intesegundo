import cv2
import mediapipe as mp
import os
import time

def iniciar_registro_biometrico():
    os.makedirs('capturas', exist_ok=True)
    cap = cv2.VideoCapture(0)
    mp_face_mesh = mp.solutions.face_mesh
    face_mesh = mp_face_mesh.FaceMesh(static_image_mode=False, max_num_faces=1, min_detection_confidence=0.5)
    mp_drawing = mp.solutions.drawing_utils
    drawing_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1)

    blink_count = 0
    blink_threshold = 3
    blink_detected = False

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        original_frame = frame.copy()
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = face_mesh.process(frame_rgb)

        if results.multi_face_landmarks:
            for face_landmarks in results.multi_face_landmarks:
                ih, iw, _ = frame.shape

                # Obtener los límites del rostro
                x_min = int(min([landmark.x for landmark in face_landmarks.landmark]) * iw)
                x_max = int(max([landmark.x for landmark in face_landmarks.landmark]) * iw)
                y_min = int(min([landmark.y for landmark in face_landmarks.landmark]) * ih)
                y_max = int(max([landmark.y for landmark in face_landmarks.landmark]) * ih)

                # Asegúrate de que las coordenadas estén dentro de los límites de la imagen
                x_min = max(x_min, 0)
                x_max = min(x_max, iw)
                y_min = max(y_min, 0)
                y_max = min(y_max, ih)

                # Recortar solo la región del rostro
                rostro = original_frame[y_min:y_max, x_min:x_max]

                # Contar parpadeos
                left_eye_top = face_landmarks.landmark[159]
                left_eye_bottom = face_landmarks.landmark[145]
                right_eye_top = face_landmarks.landmark[386]
                right_eye_bottom = face_landmarks.landmark[374]

                left_eye_height = abs(left_eye_top.y - left_eye_bottom.y)
                right_eye_height = abs(right_eye_top.y - right_eye_bottom.y)

                if left_eye_height < 0.02 and right_eye_height < 0.02:
                    if not blink_detected:
                        blink_count += 1
                        blink_detected = True
                else:
                    blink_detected = False

                if blink_count >= blink_threshold:
                    timestamp = int(time.time())
                    img_path = os.path.join('capturas', f'registro_{timestamp}.png')
                    cv2.imwrite(img_path, rostro)
                    blink_count = 0

                    # Cierra la cámara después de guardar el reconocimineto de la cara
                    cap.release()
                    cv2.destroyAllWindows()
                    return img_path

                # Mostrar la malla facial en la imagen
                frame_with_mesh = frame.copy()
                mp_drawing.draw_landmarks(
                    image=frame_with_mesh,
                    landmark_list=face_landmarks,
                    connections=mp_face_mesh.FACEMESH_TESSELATION,
                    landmark_drawing_spec=drawing_spec,
                    connection_drawing_spec=drawing_spec)

                cv2.imshow('Registro Biométrico', frame_with_mesh)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    img_path = iniciar_registro_biometrico()
    if img_path:
        print(f"Imagen de registro capturada: {img_path}")
