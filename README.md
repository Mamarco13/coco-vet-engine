# C.O.C.O - Motor difuso para prediccion de Cushing canino

Este repositorio contiene un **motor de inferencia difusa** para estimar el **riesgo/sospecha** de Sindrome de Cushing en perros, junto con su base de conocimiento en JSON. El proyecto esta dividido en:

- **backend/**: motor difuso, base de conocimiento, y ejemplo de ejecucion.
- **frontend/**: estructura base sin implementacion (pendiente).

> Nota de alcance: este motor **no diagnostica**; produce una **estimacion de riesgo** (0-1) basada en reglas y funciones de pertenencia definidas en la base de conocimiento.

---

## 1) Como levantar el proyecto (backend)

### 1.1 Requisitos

- Python 3.x con `pip` disponible.
- No hay servidor web en este backend; el ejemplo es un script ejecutable.

### 1.2 Instalacion de dependencias

Desde la raiz del repositorio:

```bash
python -m venv .venv

# Windows (PowerShell)
.\.venv\Scripts\Activate.ps1
pip install -r backend/requirements.txt

# Linux/WSL
source .venv/bin/activate
pip install -r backend/requirements.txt
```

### 1.3 Ejecucion del ejemplo

El ejemplo completo esta en `backend/main.py` y construye:

- modulo demografico (`ModuloDemografico`),
- modulo clinico (`ModuloClinico`),
- modulo de laboratorio (`ModuloLaboratorio`),
- predictor difuso (`PrediccionCushing`).

Ejecuta desde la raiz:

```bash
python backend/main.py
```

Actualmente `backend/main.py` usa `argparse`, por lo que espera argumentos obligatorios por CLI. Ejemplo completo:

```bash
python backend/main.py \
  --edad 11 \
  --raza bichon_frise \
  --peso 125 \
  --alp 780 \
  --alt 220 \
  --usg 1.012 \
  --colesterol 410 \
  --polidipsia \
  --abdomen-inflamado \
  --alopecia \
  --polifagia \
  --poliuria \
  --debilidad \
  --jadeo
```

Notas:

- Los flags clinicos son booleanos (si se incluyen, se consideran `True`).
- Si no se incluye un flag clinico, se considera `False`.

Salida esperada (resumen):

- `Riesgo estimado` (valor crisp en [0, 1])
- `Nivel de riesgo` (etiqueta linguistica)
- `Confianza fuzzy` (metrica compuesta del motor)
- listado de reglas activadas + pesos
- informe de explicabilidad

### 1.4 Ejecutar tests

Los tests importan modulos como `sistema`, `logicaDifusa` y `modulos`, por lo que se recomienda ejecutarlos desde `backend/`:

```bash
cd backend
python -m pytest
```

Si prefieres ejecutarlos desde la raiz, deberas exponer `backend/` en el `PYTHONPATH`.

---

## 2) Estructura actual del repositorio

```
.
README.md
backend/
  main.py
  requirements.txt
  conocimiento/
    cushing/
      metadata.json
      reglas/
        riesgo_muy_alto.json
        riesgo_alto.json
        riesgo_medio.json
        riesgo_bajo.json
        riesgo_muy_bajo.json
      variables/
        demograficas.json
        clinicas.json
        laboratorio.json
        consecuente.json
  logicaDifusa/
    __init__.py
    defuzzification.py
    funcionesPertenencia.py
    reglas.py
    sistema.py
    variables.py
  modulos/
    __init__.py
    moduloClinico.py
    moduloDemografico.py
    moduloLaboratorio.py
  sistema/
    __init__.py
    prediccion.py
    prediccionCushing.py
  tests/
    test_prediccion_cushing.py
    test_reglas.py
    test_sistema.py
    test_variables.py
frontend/
  public/
  src/
```

---

## 3) Frontend (pendiente)

Este repositorio incluye la carpeta `frontend/`, pero **no hay implementacion aun**. Este apartado queda por completar cuando exista una interfaz funcional.

---

## 4) Arquitectura del backend (componentes y responsabilidades)

```mermaid
graph TD
  D[ModuloDemografico] --> P[PrediccionCushing]
  C[ModuloClinico] --> P
  L[ModuloLaboratorio] --> P

  KB[Base de conocimiento JSON] --> P

  P --> FS[FuzzySystem]
  FS --> OUT[Resultado: crisp + etiqueta + confianza + reglas activas]
```

### Capas principales

1. **Entrada (modulos)**
   - Encapsulan datos de paciente por dominios.
   - Clases simples con getters/setters.

2. **Fachada de prediccion (`PrediccionCushing`)**
   - Carga la base JSON desde `backend/conocimiento/cushing/`.
   - Construye variables fuzzy (antecedentes y consecuentes).
  - Construye reglas fuzzy (antecedentes -> consecuente).
   - Mapea modulos → diccionario `inputs` para el motor.
   - Ejecuta inferencia y devuelve resultados.

3. **Motor difuso (`logicaDifusa/FuzzySystem`)**
   - Evalua reglas (activacion + peso).
   - Agrega salidas (Mamdani: MIN implicacion, MAX agregacion).
   - Defuzzifica (centroide) y calcula una confianza compuesta.

4. **Base de conocimiento JSON**
   - Define variables, universos, terminos y reglas.
   - Mantiene la logica clinica fuera del codigo.

---

## 5) Contratos de entrada (inputs)

El predictor construye un diccionario `inputs` con **nombres de variables exactamente iguales** a los declarados en `backend/conocimiento/cushing/variables/*.json`.

### 5.1 Modulo demografico — `backend/modulos/moduloDemografico.py`

Campos:

- `edad` (anios, numerica)
- `peso_rel` (porcentaje respecto a la media raza-sexo, numerica)
- `raza` (categorica, string)

En `PrediccionCushing.predecir()` se transforman a:

- `edad` -> numero
- `peso_relativo` -> numero (nota: el atributo en el modulo se llama `peso_rel`)
- `raza` -> string (normalizada internamente por la MF categorica)

### 5.2 Modulo clinico — `backend/modulos/moduloClinico.py`

Campos (booleanos):

- `polidipsia`, `poliuria`, `polifagia`
- `abdomen_inflamado` (mapeado a variable fuzzy `abdomen`)
- `alopecia`
- `debilidad_muscular`
- `piel_fina`
- `jadeo`

Transformacion a fuzzy:

- `True` -> `1.0`
- `False` o `None` -> `0.0`

### 5.3 Modulo de laboratorio — `backend/modulos/moduloLaboratorio.py`

Campos:

- `alp` (U/L)
- `alt` (U/L)
- `usg` (densidad urinaria)
- `colesterol` (mg/dL)

Se pasan como valores numericos directamente.

### 5.4 Clipping de entradas fuera de rango

Antes de inferir, el predictor recorta valores numericos fuera del universo declarado y emite un `warnings.warn`:

- si `valor < u_min` -> se recorta a `u_min`
- si `valor > u_max` -> se recorta a `u_max`

Las variables categoricas (string) se omiten en esta validacion.

---

## 6) Salida del sistema (outputs)

`PrediccionCushing.predecir()` devuelve el resultado de `FuzzySystem.infer(...)` con esta estructura:

- `crisp` (`float`): valor defuzzificado del output `riesgo`.
- `label` (`str`): etiqueta interna del termino ganador (ej. `muy_alto`).
- `etiqueta` (`str`): etiqueta humanizada (ej. `Muy alto`).
- `confidence` (`float`): confianza compuesta (ver seccion 8).
- `fuerza` (`float`): fuerza agregada de activaciones.
- `consenso` (`float`): grado de acuerdo entre reglas activas.
- `rules` (`list[RuleResult]`): reglas activas con `activation`, `consequent`, `rule.weight`.
- `aggregated` (`np.ndarray`): membership agregada del output.

Interpretacion recomendada:

- `crisp` aproxima un **grado continuo de sospecha** en [0, 1].
- `confidence` **no es una probabilidad clinica**; es una metrica interna del motor.

---

## 7) Base de conocimiento JSON (formato y convenciones)

La base se carga desde:

- `backend/conocimiento/cushing/metadata.json`
- `backend/conocimiento/cushing/variables/*.json`
- `backend/conocimiento/cushing/reglas/*.json`

### 7.1 Metadata

Archivo: `backend/conocimiento/cushing/metadata.json`

Estructura actual:

```json
{
  "metadata": {
    "version": "1.0",
    "fecha": "16/05/2026",
    "autor": "Manuel Martínez Cobos",
    "descripcion": "Base de conocimiento difusa para predicción de Cushing canino"
  }
}
```

El cargador tambien acepta el caso en que los campos esten al nivel raiz (sin el nodo `metadata`). Los campos obligatorios que valida el motor son: `autor`, `version`, `descripcion`.

### 7.2 Variables

Los JSON de variables se fusionan en dos grupos:

- **Antecedentes**: cualquier archivo en `variables/` cuyo nombre **no** contenga la palabra `consecuente`.
- **Consecuentes**: archivos cuyo nombre **si** contiene `consecuente`.

Cada variable se define como:

```json
{
  "nombre_variable": {
    "tipo": "numerica|binaria|categorica",
    "universo": [inicio, fin, paso],
    "unidad": "...",
    "fuente": "...",
    "terminos": {
      "etiqueta": {"funcion": "trimf|zmf|smf", "params": [...]}
    }
  }
}
```

Notas importantes del motor (`PrediccionCushing._crear_variable_fuzzy`):

- Si `tipo` **falta**, se asume `numerica`.
- Solo existe tratamiento especial para `tipo == "categorica"`.
  - En categoricas no se usa `universo`; internamente se crea un universo dummy `[0.0, 1.0]`.
  - Cada termino se define como lista de strings aceptadas.
- `binaria` se trata como variable numerica (mismo flujo que `numerica`).

#### Variables categoricas (detalle)

En Cushing hay una variable categorica: `raza`.

- Cada termino contiene una lista de razas aceptadas.
- La pertenencia es crisp:
  - si la raza esta en la lista → membership = 1.0
  - si no esta → membership = 0.0

Normalizacion aplicada por el motor antes de comparar:

- `strip()`
- `lower()`
- espacios y guiones → `_`

Ejemplos:

- `"Bichon Frise"` → `"bichon_frise"`
- `"miniature-schnauzer"` → `"miniature_schnauzer"`

### 7.3 Reglas

Cada archivo en `backend/conocimiento/cushing/reglas/*.json` contiene una lista de reglas. Estructura:

```json
[
  {
    "label": "...",
    "antecedentes": [
      {"variable": "edad", "termino": "mayor"},
      {"variable": "alp", "termino": "elevada"}
    ],
    "conectiva": "AND",
    "consecuente": {"variable": "riesgo", "termino": "alto"},
    "peso": 1.0,
    "fuente": "..."
  }
]
```

Compatibilidad:

- El motor usa `conectiva` como operador logico.
- Si `conectiva` no esta, intenta `tipo` y por defecto asume `AND`.

---

## 8) Algoritmo de inferencia (como se calcula el riesgo)

### 8.1 Evaluacion de reglas

Cada regla tiene:

- antecedentes: lista de pares `(variable, MF_del_termino)`
- operador: `AND` / `OR`
- peso: `weight`

Para cada antecedente $i$ se calcula el grado de pertenencia:

$$\mu_i = MF_i(x_i)$$

Combinacion:

- AND -> $\min(\mu_1, \mu_2, ..., \mu_n)$
- OR -> $\max(\mu_1, \mu_2, ..., \mu_n)$

Activacion final (con peso):

$$\alpha = combine(\mu) \cdot weight$$

Una regla se considera **activa** si $\alpha > 0$.

### 8.2 Agregacion Mamdani

Para el consecuente (output) se usa:

- implicacion: **MIN** (recorte)
- agregacion: **MAX** (union)

Para cada regla activa:

$$\mu_{recortada}(u) = \min(\alpha, \mu_{consecuente}(u))$$

Agregacion total:

$$\mu_{agg}(u) = \max_{reglas}(\mu_{recortada}(u))$$

### 8.3 Defuzzificacion

El motor usa **centroide** (`CentroidDefuzzifier`):

$$crisp = \frac{\int u\,\mu_{agg}(u)\,du}{\int \mu_{agg}(u)\,du}$$

### 8.4 Confianza compuesta

El motor calcula tres magnitudes:

- **Fuerza**: media autoponderada de activaciones.
  $$fuerza = \frac{\sum (\alpha^2 \cdot w)}{\sum (\alpha \cdot w)}$$

- **Consenso**: fraccion de activacion ponderada que apunta al termino dominante.
  $$consenso = \frac{\max(\sum \alpha \cdot w \; por\ termino)}{\sum (\alpha \cdot w)}$$

- **Confianza final**:
  $$confidence = fuerza \cdot consenso$$

---

## 9) Variables definidas para Cushing (detalle actual)

### 9.1 Demograficas (`backend/conocimiento/cushing/variables/demograficas.json`)

- `edad` (0-20 anios, paso 0.1)
  - `joven`: `zmf(0, 4)`
  - `adulto`: `trimf(3, 6.5, 10)`
  - `mayor`: `smf(8, 12)`

- `peso_relativo` (50-150 %, paso 1)
  - `bajo`: `zmf(50, 85)`
  - `normal`: `trimf(80, 100, 120)`
  - `alto`: `smf(115, 140)`

- `raza` (categorica)
  - `protectora`: `golden_retriever`, `labrador_retriever`, `border_collie`, `cocker_spaniel`
  - `neutra`: `mestizo`, `beagle`, `rottweiler`, `boxer`, `west_highland_white_terrier`, `cavalier_king_charles_spaniel`, `cockapoo`, `shih_tzu`, `pomeranian`, `english_springer_spaniel`, `pug`, `chihuahua`, `german_shepherd_dog`, `other_purebred`
  - `predispuesta_moderada`: `staffordshire_bull_terrier`, `jack_russell_terrier`, `lhasa_apso`, `yorkshire_terrier`, `poodle`, `dachshund`
  - `predispuesta_alta`: `bichon_frise`, `border_terrier`, `miniature_schnauzer`

> En el JSON existe `pesos_numericos` para estos terminos, pero **el motor actual no los usa**.

### 9.2 Clinicas (`backend/conocimiento/cushing/variables/clinicas.json`)

Todas las clinicas comparten:

- universo: 0-1 (paso 0.01)
- terminos:
  - `no`: `trimf(0, 0, 0.4)`
  - `si`: `trimf(0.6, 1, 1)`

Variables:

- `polidipsia`
- `poliuria`
- `abdomen`
- `alopecia`
- `debilidad_muscular`
- `piel_fina`
- `polifagia`
- `jadeo`

### 9.3 Laboratorio (`backend/conocimiento/cushing/variables/laboratorio.json`)

- `alp` (0-3000 U/L, paso 10)
  - `normal`: `zmf(0, 150)`
  - `elevada`: `trimf(100, 400, 800)`
  - `muy_elevada`: `smf(700, 1500)`

- `usg` (1.000-1.060, paso 0.001)
  - `diluida`: `zmf(1.000, 1.015)`
  - `intermedia`: `trimf(1.010, 1.020, 1.030)`
  - `concentrada`: `smf(1.025, 1.045)`

- `alt` (0-1500 U/L, paso 5)
  - `normal`: `zmf(0, 80)`
  - `elevada`: `trimf(60, 150, 350)`
  - `muy_elevada`: `smf(300, 700)`

- `colesterol` (50-600 mg/dL, paso 5)
  - `normal`: `zmf(50, 220)`
  - `elevado`: `trimf(180, 300, 450)`
  - `muy_elevado`: `smf(400, 550)`

### 9.4 Variable de salida (`backend/conocimiento/cushing/variables/consecuente.json`)

- `riesgo` (0-1, paso 0.01)
  - `muy_bajo`: `zmf(0, 0.06)`
  - `bajo`: `trimf(0.02, 0.12, 0.24)`
  - `medio`: `trimf(0.28, 0.50, 0.72)`
  - `alto`: `trimf(0.76, 0.87, 0.94)`
  - `muy_alto`: `smf(0.96, 1.0)`

---

## 10) Reglas de Cushing (que hay implementado)

Las reglas estan separadas por nivel de riesgo:

- `riesgo_muy_bajo.json` (3 reglas)
- `riesgo_bajo.json` (4 reglas)
- `riesgo_medio.json` (6 reglas)
- `riesgo_alto.json` (10 reglas)
- `riesgo_muy_alto.json` (4 reglas)

Total actual: **27 reglas**.

Cada regla incluye:

- `label`: descripcion breve
- `antecedentes`: lista de (variable, termino)
- `conectiva`: `AND` / `OR`
- `consecuente`: `(riesgo, <nivel>)`
- `peso`: ponderacion (1.0 tipico; 2.0 en reglas muy fuertes)
- `fuente`: trazabilidad bibliografica/justificacion

---

## 11) Explicabilidad

Hay dos niveles de explicabilidad:

1. **Retorno estructurado** (`results["rules"]`)
   - Lista de `RuleResult` con activacion, consecuente y peso.

2. **Informe por consola** (`PrediccionCushing.explicar_decision()`)
   - Imprime las reglas activadas con su activacion y peso.

---

## 12) Como extender o adaptar el motor

### 12.1 Anadir una nueva variable fuzzy

1. Declara la variable en un JSON dentro de `backend/conocimiento/cushing/variables/`.
2. Asegurate de que el nombre coincide con la clave que usaran las reglas.
3. Actualiza `PrediccionCushing.predecir()` para incluir el valor en `inputs`.

Si una regla usa una variable que no esta en `inputs`, la evaluacion fallara con:

- `ValueError: Falta input para '<variable>'`

### 12.2 Anadir reglas

1. Crea o edita un JSON en `backend/conocimiento/cushing/reglas/`.
2. Usa terminos que existan en la variable.
3. Ajusta `peso` si quieres priorizar o despriorizar esa regla.

### 12.3 Crear un predictor para otra patologia

Patron recomendado:

- Crear `backend/conocimiento/<patologia>/` con `metadata.json`, `variables/`, `reglas/`.
- Crear `backend/sistema/prediccion<Patologia>.py` copiando la estructura de `PrediccionCushing`.
- Implementar el mapeo de entradas (`inputs`) desde modulos o desde un DTO.

---

## 13) Notas operativas (errores comunes)

- Si `raza` no coincide con las cadenas esperadas (normalizadas), su pertenencia sera 0.0 y las reglas que dependan de raza pueden no activarse.
- Si **ninguna regla activa**, `FuzzySystem.infer()` lanza `ValueError("No hay reglas activas")`.
- Si un valor numerico cae fuera del universo definido, se aplica clipping y se emite un warning.

---

## 14) Referencias internas (codigo clave)

- `backend/sistema/prediccionCushing.py`
  - carga y fusion de base JSON
  - creacion de variables fuzzy (incluye categoricas)
  - construccion de reglas
  - ejecucion de inferencia + explicabilidad

- `backend/logicaDifusa/sistema.py`
  - Mamdani + defuzzificacion centroide
  - calculo de `fuerza`, `consenso` y `confidence`

- `backend/logicaDifusa/reglas.py`
  - evaluacion de reglas (AND/OR, peso)

- `backend/conocimiento/cushing/*`
  - verdad del modelo (variables + reglas)
