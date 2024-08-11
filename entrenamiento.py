import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Cargamos los datos
df = pd.read_csv('Phishing_Email.csv')
X = df['Email Text']
y = df['Label']

# Dividir los datos en conjunto de entrenamiento y prueba
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Vectorización del texto
vectorizer = TfidfVectorizer()
X_train_vectorized = vectorizer.fit_transform(X_train)
X_test_vectorized = vectorizer.transform(X_test)

# Entrenamiento del modelo
model = RandomForestClassifier()
model.fit(X_train_vectorized, y_train)

# Guardar el modelo y el vectorizador
joblib.dump(model, 'modelo_preentrenado.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')
