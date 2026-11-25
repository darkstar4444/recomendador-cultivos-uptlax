import joblib
import numpy as np
import pandas as pd
import streamlit as st

# Configuración visual UPTLAX (Guinda y Dorado)
st.set_page_config(
    page_title="Recomendador de Cultivos | UPTLAX",
    page_icon="🌾",
    layout="wide",
)

GUINDA = "#691C32"
GUINDA_OSCURO = "#4A1222"
DORADO = "#BC955C"
DORADO_CLARO = "#FBF7F0"

st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: #FAF8F5;
        }}
        .uptlax-header {{
            background: linear-gradient(90deg, {GUINDA_OSCURO} 0%, {GUINDA} 75%, #8A2441 100%);
            color: #FFFFFF;
            padding: 1.4rem 1.8rem;
            border-radius: 12px;
            border-bottom: 5px solid {DORADO};
            margin-bottom: 1.2rem;
        }}
        .uptlax-header h1 {{
            color: #FFFFFF;
            margin: 0;
            font-size: 1.75rem;
        }}
        .uptlax-header p {{
            color: #F3E5AB;
            margin: 0.35rem 0 0 0;
            font-size: 0.98rem;
        }}
        .result-card {{
            background-color: {DORADO_CLARO};
            border-left: 6px solid {GUINDA};
            border-top: 1px solid {DORADO};
            border-right: 1px solid {DORADO};
            border-bottom: 1px solid {DORADO};
            padding: 1.2rem 1.4rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }}
        .stButton > button {{
            background-color: {GUINDA};
            color: #FFFFFF;
            border: 2px solid {DORADO};
            font-weight: 600;
            border-radius: 8px;
            padding: 0.55rem 1.2rem;
        }}
        .stButton > button:hover {{
            background-color: {GUINDA_OSCURO};
            color: #F3E5AB;
            border-color: {DORADO};
        }}
    </style>
    <div class="uptlax-header">
        <h1>Universidad Politécnica de Tlaxcala (UPTLAX)</h1>
        <p>Sistema de Recomendación de Cultivos mediante Inteligencia Artificial — Top 20 Cultivos</p>
    </div>
    """,
    unsafe_allow_html=True,
)

MODEL_PATH = "modelo_cultivos_top20.joblib"


@st.cache_resource
def cargar_modelo(path: str):
    return joblib.load(path)


try:
    modelo = cargar_modelo(MODEL_PATH)
except FileNotFoundError:
    st.error(
        f"No se encontró `{MODEL_PATH}` en el directorio actual. "
        "Coloca el archivo `.joblib` junto a `app.py` antes de ejecutar."
    )
    st.stop()
except Exception as e:
    st.error(f"Error al cargar el modelo serializado: {e}")
    st.stop()

st.markdown("### Formulario de parámetros de suelo, clima y manejo")

with st.form("form_cultivo"):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("Nutrientes y pH del suelo")
        nitrogeno = st.number_input(
            "Nitrógeno (Nitrogeno)",
            min_value=0.0,
            max_value=250.0,
            value=50.0,
            step=1.0,
            help="Nivel de nitrógeno en el suelo",
        )
        fosforo = st.number_input(
            "Fósforo (Fosforo)",
            min_value=0.0,
            max_value=250.0,
            value=45.0,
            step=1.0,
            help="Nivel de fósforo en el suelo",
        )
        potasio = st.number_input(
            "Potasio (Potasio)",
            min_value=0.0,
            max_value=250.0,
            value=45.0,
            step=1.0,
            help="Nivel de potasio en el suelo",
        )
        ph_suelo = st.number_input(
            "pH del suelo (pH_suelo)",
            min_value=3.0,
            max_value=10.0,
            value=6.5,
            step=0.1,
        )
        tipo_suelo = st.selectbox(
            "Tipo de suelo (Tipo_suelo)",
            options=["franco", "arcilloso", "arenoso"],
        )

    with col2:
        st.subheader("Clima y entorno")
        precipitacion = st.number_input(
            "Precipitación (Precipitacion)",
            min_value=0.0,
            max_value=500.0,
            value=100.0,
            step=1.0,
        )
        temperatura = st.number_input(
            "Temperatura ambiental (Temperatura)",
            min_value=-5.0,
            max_value=50.0,
            value=20.0,
            step=0.5,
        )
        temperatura_crecimiento = st.number_input(
            "Temperatura de crecimiento (Temperatura_crecimiento)",
            min_value=-5.0,
            max_value=55.0,
            value=24.0,
            step=0.5,
        )
        temp_min_tlaxcala = st.number_input(
            "Temperatura mínima Tlaxcala (Temperatura_minima_Tlaxcala)",
            min_value=-10.0,
            max_value=30.0,
            value=6.0,
            step=0.5,
        )
        humedad = st.number_input(
            "Humedad relativa (Humedad)",
            min_value=0.0,
            max_value=100.0,
            value=65.0,
            step=1.0,
        )

    with col3:
        st.subheader("Viento, luz y manejo")
        horas_luz = st.number_input(
            "Horas de luz solar (Horas_luz_solar)",
            min_value=0.0,
            max_value=24.0,
            value=8.0,
            step=0.5,
        )
        velocidad_viento = st.number_input(
            "Velocidad del viento Tlaxcala (Velocidad_viento_Tlaxcala)",
            min_value=0.0,
            max_value=120.0,
            value=12.0,
            step=0.5,
        )
        frecuencia_riego = st.selectbox(
            "Frecuencia de riego (Frecuencia_riego)",
            options=["diario", "dos_veces_por_semana", "semanal"],
        )
        tipo_fertilizante = st.selectbox(
            "Tipo de fertilizante (Tipo_fertilizante)",
            options=["organico", "quimico", "ninguno"],
        )

    enviado = st.form_submit_button("Solicitar recomendación de cultivo")

if enviado:
    # Atributos derivados
    npk_total = float(nitrogeno + fosforo + potasio)
    diferencial_termico = float(temperatura_crecimiento - temp_min_tlaxcala)

    # Validación explícita de coherencia
    errores = []
    if not (0.0 <= humedad <= 100.0):
        errores.append("La humedad debe estar entre 0% y 100%.")
    if not (3.0 <= ph_suelo <= 10.0):
        errores.append("El pH del suelo debe estar entre 3.0 y 10.0.")
    if temperatura_crecimiento < temp_min_tlaxcala:
        errores.append(
            "La temperatura de crecimiento no debería ser menor que la temperatura mínima de Tlaxcala."
        )

    if errores:
        for err in errores:
            st.error(err)
        st.stop()

    # DataFrame exacto que espera el ColumnTransformer del pipeline
    entrada_df = pd.DataFrame(
        [
            {
                "Nitrogeno": float(nitrogeno),
                "Fosforo": float(fosforo),
                "Potasio": float(potasio),
                "pH_suelo": float(ph_suelo),
                "Precipitacion": float(precipitacion),
                "Temperatura": float(temperatura),
                "Horas_luz_solar": float(horas_luz),
                "Temperatura_crecimiento": float(temperatura_crecimiento),
                "Humedad": float(humedad),
                "Temperatura_minima_Tlaxcala": float(temp_min_tlaxcala),
                "Velocidad_viento_Tlaxcala": float(velocidad_viento),
                "Macronutrientes_disponibles": npk_total,
                "Diferencial_termico_Tlaxcala": diferencial_termico,
                "Tipo_suelo": tipo_suelo,
                "Frecuencia_riego": frecuencia_riego,
                "Tipo_fertilizante": tipo_fertilizante,
            }
        ]
    )

    # Asegurar orden exacto de columnas si el pipeline expone feature_names_in_
    if hasattr(modelo, "feature_names_in_"):
        entrada_df = entrada_df[list(modelo.feature_names_in_)]

    prediccion = modelo.predict(entrada_df)[0]

    st.markdown("---")
    st.markdown("### Atributos derivados calculados")
    m1, m2 = st.columns(2)
    m1.metric("NPK_total / Macronutrientes_disponibles", f"{npk_total:.2f}")
    m2.metric("Diferencial_termico_Tlaxcala (°C)", f"{diferencial_termico:.2f} °C")

    st.markdown("### Resultado de la recomendación")
    if hasattr(modelo, "predict_proba"):
        probs = modelo.predict_proba(entrada_df)[0]
        clases = modelo.classes_
        idx_orden = np.argsort(probs)[::-1]
        confianza_top = probs[idx_orden[0]] * 100

        st.markdown(
            f"""
            <div class="result-card">
                <h2 style="color: {GUINDA}; margin: 0;">Cultivo recomendado: {str(prediccion).upper()}</h2>
                <p style="margin: 0.4rem 0 0 0; font-size: 1.05rem;">
                    <strong>Nivel de confianza estimado:</strong> {confianza_top:.2f}%
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("#### Alternativas de recomendación (Top 5 probabilidades)")
        top_df = pd.DataFrame(
            {
                "Cultivo": [clases[i] for i in idx_orden[:5]],
                "Probabilidad (%)": [round(float(probs[i]) * 100, 2) for i in idx_orden[:5]],
            }
        )
        st.dataframe(top_df, use_container_width=True, hide_index=True)
    else:
        st.markdown(
            f"""
            <div class="result-card">
                <h2 style="color: {GUINDA}; margin: 0;">Cultivo recomendado: {str(prediccion).upper()}</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )