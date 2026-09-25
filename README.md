# 📚 Sistema Recomendador Híbrido de Libros

Repositorio del Trabajo Práctico Integrador de la materia **Ciencia de Datos** de la **UTN Facultad Regional de Concepción del Uruguay**.

Este proyecto implementa la arquitectura de datos y el motor de recomendación para una tienda virtual de libros con un **catálogo cerrado de exactamente 100 títulos**, diseñado con **Domain-Driven Design (DDD)** y persistido en la nube mediante **Supabase (PostgreSQL)**.

---

## 🏗️ Arquitectura del Repositorio

El proyecto está organizado bajo los principios de **Domain-Driven Design (DDD)** y **Clean Architecture**:

```text
Sistema-Recomendador/
├── .env                              # Credenciales de conexión a Supabase (ignorado por Git)
├── .gitignore                        # Archivos y cachés ignorados por Git
├── example.env.txt                   # Plantilla de variables de entorno requeridas
├── schema_supabase.sql               # Script DDL oficial para el SQL Editor de Supabase
├── seed.py                           # Script de inyección inicial y mantenimiento de datos
├── main.py                           # Orquestador y demostración de Casos de Uso
├── docs/                             # Documentación técnica modular
│   ├── 01_DATABASE_SCHEMA.md         # Modelo relacional, tablas, triggers y RLS
│   ├── 02_DDD_ARCHITECTURE.md        # Capas de Dominio, Aplicación e Infraestructura
│   └── 03_SEED_DATA_AND_COLD_START.md # Dataset de 100 libros y solución al Cold Start
└── src/
    ├── domain/                       # Core de Negocio (Entidades, Value Objects, Repositorios)
    │   ├── entities/                 # Libro (1..100), Usuario (0..3 géneros), Preferencia, etc.
    │   ├── value_objects/            # Rating (1..5 o None), Email
    │   ├── exceptions.py             # Excepciones de invariantes de dominio
    │   └── repositories/             # Interfaces abstractas (IoC)
    ├── application/                  # Casos de Uso (Seed, ColdStart, Preferencias) y DTOs
    └── infrastructure/               # Adaptadores técnicos (SupabaseClient, Repositorios, Datos)
        ├── config.py                 # Cargador tipado de configuración
        ├── data/seed_data.py         # 100 libros, autores, editoriales y usuarios reales
        └── repositories/             # Implementaciones concretas de repositorios con Supabase
```

---

## ⚡ Guía Rápida de Puesta en Marcha

### 1. Configurar Variables de Entorno
Copia la plantilla `example.env.txt` como `.env` e ingresa tu URL y API Key de Supabase:
```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-service-role-key-aqui
```

### 2. Crear las Tablas en Supabase
Copia el contenido de [`schema_supabase.sql`](schema_supabase.sql) y ejecútalo en el **SQL Editor** de tu consola de Supabase. Este script crea:
* Las tablas del modelo (`Usuario`, `Autor`, `Editorial`, `Genero`, `Libro`, `Preferencia`, `GeneroLibro`, `UsuarioGenero`).
* Los **triggers** que enforzan el catálogo de 100 libros y el límite de 3 géneros por usuario.
* Los índices de rendimiento para consultas del recomendador.
* Las políticas de seguridad de fila (**RLS**).

### 3. Inyectar los Datos Semilla (100 Libros Reales)
Ejecuta el script dedicado de inyección de datos:
```powershell
py seed.py
```
> **Nota:** Si en algún momento necesitas reiniciar la base de datos limpia desde cero, ejecuta:
> ```powershell
> py seed.py --reset
> ```

### 4. Probar los Casos de Uso del Recomendador
Ejecuta el orquestador principal:
```powershell
py main.py
```
Este comando ejecutará los casos de uso:
1. Verificación del catálogo.
2. Cálculo de recomendaciones para **Cold Start** (usuarios nuevos según onboarding).
3. Registro de feedback explícito (calificación 1 a 5) e implícito (clicks/navegación).

---

## 📖 Documentación Detallada

Para profundizar en cada componente técnico, consulta la documentación modular en la carpeta [`docs/`](docs/):

1. [**Esquema de Base de Datos y Triggers (`docs/01_DATABASE_SCHEMA.md`)**](docs/01_DATABASE_SCHEMA.md):
   * Modelo relacional derivado del diagrama UML `pkg`.
   * Enforzamiento de invariantes a nivel de base de datos (PostgreSQL PL/pgSQL).
   * Índices de rendimiento para filtrado colaborativo.
2. [**Arquitectura Orientada al Dominio (`docs/02_DDD_ARCHITECTURE.md`)**](docs/02_DDD_ARCHITECTURE.md):
   * Detalle de las 4 capas: Dominio, Aplicación, Infraestructura y Presentación.
   * Entidades, Aggregates, Value Objects y Contratos de Repositorios (Inversión de Control).
3. [**Dataset Semilla y Mitigación de Cold Start (`docs/03_SEED_DATA_AND_COLD_START.md`)**](docs/03_SEED_DATA_AND_COLD_START.md):
   * Catálogo canónico de 100 libros con autores, páginas y precios reales.
   * Estrategia algorítmica para el arranque en frío mediante onboarding temático.
