"""!
@file test_api.py
@brief Tests de integracion para la API HTTP de C.O.C.O.

@details
Cubre:
    - 200 en /predict/cushing con payload valido
    - serializacion JSON completa del resultado real
    - defaults de booleanos opcionales
    - validacion 422 con payload incompleto
    - validacion 422 con tipo invalido
"""

from pathlib import Path
import sys

import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import api as api_module


client = TestClient(api_module.app)


def payload_completo(**overrides):
    payload = {
        "edad": 11,
        "raza": "bichon_frise",
        "peso": 125,
        "polidipsia": True,
        "abdomen_inflamado": True,
        "alopecia": True,
        "polifagia": True,
        "poliuria": True,
        "debilidad": True,
        "piel_fina": False,
        "jadeo": True,
        "alp": 780,
        "alt": 220,
        "usg": 1.012,
        "colesterol": 410,
    }
    payload.update(overrides)
    return payload


def payload_minimo(**overrides):
    payload = {
        "edad": 11,
        "raza": "bichon_frise",
        "peso": 125,
        "alp": 780,
        "alt": 220,
        "usg": 1.012,
        "colesterol": 410,
    }
    payload.update(overrides)
    return payload


class TestApiCushing:

    def test_predict_cushing_ok_retorna_json_esperado(self):
        response = client.post("/predict/cushing", json=payload_completo())

        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")

        data = response.json()

        assert {"crisp", "label", "etiqueta", "confidence", "fuerza", "consenso", "rules", "aggregated"}.issubset(
            data.keys()
        )
        assert isinstance(data["crisp"], (int, float))
        assert 0.0 <= data["crisp"] <= 1.0
        assert isinstance(data["label"], str)
        assert isinstance(data["etiqueta"], str)
        assert isinstance(data["confidence"], (int, float))
        assert 0.0 <= data["confidence"] <= 1.0
        assert isinstance(data["fuerza"], (int, float))
        assert 0.0 <= data["fuerza"] <= 1.0
        assert isinstance(data["consenso"], (int, float))
        assert 0.0 <= data["consenso"] <= 1.0
        assert isinstance(data["rules"], list)
        assert isinstance(data["aggregated"], list)

        for item in data["rules"]:
            assert isinstance(item, dict)
            assert {"activation", "consequent", "weight"}.issubset(item.keys())

    def test_predict_cushing_acepta_booleanos_omitidos(self):
        response = client.post("/predict/cushing", json=payload_minimo())

        assert response.status_code == 200

        data = response.json()
        assert "crisp" in data
        assert "rules" in data
        assert isinstance(data["rules"], list)

    def test_predict_cushing_rechaza_payload_incompleto(self):
        payload = payload_completo()
        payload.pop("alp")

        response = client.post("/predict/cushing", json=payload)

        assert response.status_code == 422

    def test_predict_cushing_rechaza_tipo_invalido(self):
        payload = payload_completo(alp="no_es_numero")

        response = client.post("/predict/cushing", json=payload)

        assert response.status_code == 422


class TestApiSerializacion:

    def test_predict_cushing_devuelve_json_serializable(self):
        response = client.post("/predict/cushing", json=payload_completo())

        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, dict)
        assert isinstance(data["rules"], list)
        assert isinstance(data["aggregated"], list)