# TFM- Specialized Terminology and Polysemic Variation

## Español

Este repositorio acompaña al Trabajo de Fin de Máster (TFM) titulado  
_**Specialized Terminology and Polysemic Variation: Guiding Large Language Models in the Translation of Domain-Specific Polysemous Terms**_.  
El objetivo principal del proyecto es **evaluar el comportamiento de traducción a nivel de término de los modelos de lenguaje ante la polisemia terminológica** en textos especializados y proponer métodos de mejora mediante recursos terminológicos contextualizados y técnicas de *prompting*.

El repositorio está organizado en **tres bloques funcionales**:

---

## 1. `term_obtention` – Detección de términos polisémicos

Este bloque se centra en la **identificación automática de términos polisémicos** compartidos por múltiples áreas de especialidad en tres lenguas: español, euskera e inglés.

- Se aplican **tres procesos de filtrado** para seleccionar las **10 parejas de dominios** que más términos polisémicos comparten y sus respectivos términos.
- El resultado se presenta en forma de **archivos csv** divididos por carpetas. La siguiente tabla muestra un ejemplo de estructura, eligiendo únicamente un término de cada uno:
| Par de idioma | Término origen | Término meta    | Domain                                                            |
|---------------|----------------|-----------------|-------------------------------------------------------------------|
| BA-EN         | osagai         | ingredient      | Medical Sciences > Parmaceutical Technology                       |
|               |                | component       | Technological Sciences > Environmental Technology and Engineering |
| BA-ES         | urradura       | rozadura        | Medical Sciences > Parmaceutical Technology                       |
|               |                | abrasión        | Technological Sciences > Environmental Technology and Engineering |
| EN-BA         | destruction    | hondamen        | Medical Sciences > Parmaceutical Technology                       |
|               |                | suntsipen       | Technological Sciences > Environmental Technology and Engineering |
| EN-ES         | flow           | caudal          | Physics > Electromagnetism                                        |
|               |                | circular        | Technological Sciences > Electrical Technology and Engineering    |
| ES-BA         | afinidad       | elkarkidetsasun | Juridical Sciences & Law > Constitutional Law                     |
|               |                | afinitate       | Technological Sciences > Electrical Technology and Engineering    |
| ES-EN         | aislador       | isolator        | Physics > Electromagnetism                                        |
|               |                | insulator       | Technological Sciences > Electrical Technology and Engineering    |
---

## 2. `context_obtention` – Extracción de contextos y construcción del recurso

En esta fase se extraen **contextos reales de uso** de los términos polisémicos, procedentes de **Wikipedia** y del corpus terminológico **Garaterm**.

- Se trabaja con una de las parejas de dominios seleccionadas.
- Se construye el archivo `recurso_final`, que contiene el recurso terminológico contextualizado empleado en la fase experimental.
- Este bloque incluye:
  - **Hasta 10 ejemplos de uso por término** y por dominio de la pareja seleccionada.
  - **Datasets temáticos** extraídos de Wikipedia para cada área especializada.
  - Las **etiquetas y filtros aplicados** para la obtención de los corpus.

---

## 3. `experimentation` – Pruebas con modelos de lenguaje y evaluación

En este bloque se realiza la **experimentación con modelos de lenguaje (LLMs)** mediante distintas estrategias de *prompting*:

- Se emplean las variantes: `0-shot`, `0-shot-plus`, `1-shot` y `few-shot`.
- Los *scripts* permiten automatizar la creación de prompts a partir del recurso.
- Se incluyen las respuestas generadas por distintos **modelos**:
  - **GPT** (OpenAI)
  - **Gemini** (Google)
  - **LLaMA** (Meta)
  - **Latxa** (UPV/EHU)
- Se adjunta el cuaderno `cuadernilloo_final`, que contiene:
  - El **sistema de evaluación** por término y contexto.
  - **Gráficos** con los resultados comparativos entre modelos y estrategias.

---

## Información adicional

- Las **claves de API** necesarias para ejecutar los modelos han sido **retiradas** por motivos de privacidad. Para reproducir los experimentos es necesario introducir las tuyas propias.

## English

This project is part of a Master's Thesis (TFM) and is focused on experimenting with and generating prompts for the contextual translation of technical terms, especially in physics and engineering.

- Scripts to create various prompt types (0-shot, 1-shot, few-shot, etc.).
- Tools to process data and examples from CSV files.
- Utilities to read and display generated prompts.
- 
| Language Pair | Source Term | Target Term     | Domain                                                            |
|---------------|-------------|-----------------|-------------------------------------------------------------------|
| BA-EN         | osagai      | ingredient      | Medical Sciences > Parmaceutical Technology                       |
|               |             | component       | Technological Sciences > Environmental Technology and Engineering |
| BA-ES         | urradura    | rozadura        | Medical Sciences > Parmaceutical Technology                       |
|               |             | abrasión        | Technological Sciences > Environmental Technology and Engineering |
| EN-BA         | destruction | hondamen        | Medical Sciences > Parmaceutical Technology                       |
|               |             | suntsipen       | Technological Sciences > Environmental Technology and Engineering |
| EN-ES         | flow        | caudal          | Physics > Electromagnetism                                        |
|               |             | circular        | Technological Sciences > Electrical Technology and Engineering    |
| ES-BA         | afinidad    | elkarkidetsasun | Juridical Sciences & Law > Constitutional Law                     |
|               |             | afinitate       | Technological Sciences > Electrical Technology and Engineering    |
| ES-EN         | aislador    | isolator        | Physics > Electromagnetism                                        |
|               |             | insulator       | Technological Sciences > Electrical Technology and Engineering    |

Note: The API keys for the different models have been redacted. To use this repository, please use your own.
