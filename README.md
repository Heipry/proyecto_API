# GOG vs SteamDB Version Checker

![Status](https://img.shields.io/badge/Status-Online-success?style=flat-square)
![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square)
![FastAPI](https://img.shields.io/badge/FastAPI-High%20Performance-009688?style=flat-square)

### 🔗 Acceder a la herramienta: [https://gog-steam-checker.onrender.com/](https://gog-steam-checker.onrender.com/)

---

## 📖 Descripción

Herramienta web diseñada para comparar la fecha del paquete de GOG de un videojuego con la de Steam.

El sistema permite contrastar la versión actual disponible en plataformas sin DRM frente a las últimas actualizaciones desplegadas en plataformas de distribución masiva, ayudando a identificar rápidamente si un instalador offline ha quedado obsoleto.

## ✨ Funcionalidades

* **Búsqueda Unificada:** Localiza títulos simultáneamente en múltiples bases de datos.
* **Análisis de Versiones:** Algoritmo de comparación que cruza números de build y fechas de lanzamiento.
* **Diagnóstico Visual:**
    * 🟢 **Sincronizado:** Las versiones coinciden o entran en el margen de tolerancia.
    * 🔴 **Desactualizado:** Se detecta un retraso significativo en la actualización offline.
    * 🟡 **Adelantado:** La versión offline es más reciente (hotfixes o pre-releases).
* **Arquitectura API-First:** Frontend SPA (Single Page Application) que consume datos vía API REST, servido de forma integrada por FastAPI.

## 🛠️ Stack Tecnológico

Este proyecto demuestra la implementación de una arquitectura web moderna y ligera:

* **Backend:** Python, **FastAPI**, Uvicorn.
* **Frontend:** JavaScript (Vanilla), Bootstrap 5.
* **Infraestructura:** Despliegue continuo (CI/CD) en **Render**.

## 🎓 Contexto Educativo

Este proyecto ha sido desarrollado como un **recurso didáctico práctico**. Sirve como ejemplo real de cómo desplegar un **servicio web moderno basado en Python** (FastAPI) alejándose de las arquitecturas monolíticas tradicionales.

El código ilustra conceptos clave para formaciones:
* **Modernización Web:** Transición de scripts locales a servicios en la nube (SaaS).
* **Arquitectura Limpia:** Separación de responsabilidades entre la obtención de datos y la presentación.
* **Despliegue Continuo (CI/CD):** Cómo llevar código de un entorno local a producción en **Render** de forma automatizada.

## 🚀 Despliegue

El servicio se encuentra desplegado y operativo en la nube.
[https://gog-steam-checker.onrender.com/](https://gog-steam-checker.onrender.com/)

> **Nota:** La ejecución en local requiere configuración de variables de entorno privadas para el acceso a los proveedores de datos por lo que esa información queda restringida.

---

**Javier Díaz** - Desarrollador y Consultor Web.
