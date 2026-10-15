# Guía de instalación y ejecución

Esta guía explica cómo configurar Supabase, crear las tablas y ejecutar el sistema recomendador.

## 1. Requisitos

- Una cuenta y un proyecto creado en [Supabase](https://supabase.com/).
- Python 3.10 o superior.
- Git, si se clona el repositorio.
- La URL y la clave `service_role` del proyecto de Supabase.

La clave `service_role` se encuentra en **Project Settings → API**. Es una credencial privada: no debe publicarse ni subirse al repositorio.

## 2. Descargar el proyecto

Desde una terminal:

```powershell
git clone URL_DEL_REPOSITORIO
cd Sistema-Recomendador
```

Si el proyecto ya está descargado, solo hay que abrir una terminal en su carpeta raíz, donde están `main.py`, `seed.py` y `schema_supabase.sql`.

## 3. Configurar las credenciales

Crear un archivo llamado `.env` en la raíz del proyecto, tomando como referencia `example.env.txt`:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-service-role-key
```

No cambiar los nombres `SUPABASE_URL` y `SUPABASE_KEY`. El archivo `.env` está excluido por `.gitignore`.

## 4. Crear la base de datos

1. Abrir el proyecto en Supabase.
2. Entrar en **SQL Editor**.
3. Crear una consulta nueva.
4. Copiar todo el contenido de `schema_supabase.sql`.
5. Presionar **Run**.

El script crea las tablas `Usuario`, `Autor`, `Editorial`, `Genero`, `Libro`, `Preferencia`, `GeneroLibro` y `UsuarioGenero`. También crea relaciones, restricciones, triggers, índices y políticas RLS.

Este paso se realiza una sola vez por proyecto de Supabase. No se ejecuta desde Python.

## 5. Cargar los datos iniciales

Con las credenciales configuradas, ejecutar:

```powershell
py seed.py
```

El script carga:

- 12 géneros.
- 9 editoriales.
- 18 autores.
- 100 libros.
- 20 usuarios.
- Las preferencias de género de los usuarios.

Si el catálogo ya tiene 100 libros, la carga se omite para evitar duplicados.

## 6. Cargar compras para usuarios existentes

Si no se quieren crear usuarios demo nuevos, usar el script independiente:

```powershell
py seed_preferencias.py
```

Este script toma los usuarios que ya existen en la tabla `Usuario`, conserva sus géneros favoritos y agrega 7 u 8 compras nuevas por ejecución. En aproximadamente el 5% de los casos genera 10 compras. No crea usuarios nuevos ni repite libros que ya tengan registrados en `Preferencia`.

Para reiniciar las preferencias de género y las compras de todos los usuarios existentes:

```powershell
py .\seed_preferencias.py --reset-preferencias
```

En ambos modos, `emilianolanaro@gmail.com` queda siempre sin compras para probar el caso Cold Start. El modo `--reset-preferencias` además reemplaza sus géneros favoritos y las compras de todos los usuarios. Debe usarse solo con datos de prueba.

## 7. Ejecutar la demostración

```powershell
py main.py
```

El programa:

1. Verifica o carga el catálogo.
2. Busca recomendaciones para `pabloleal@gmail.com` usando sus géneros favoritos.
3. Registra una preferencia explícita con rating 5.
4. Registra una interacción implícita sin rating.

## 8. Reiniciar los datos

Para borrar los datos de las tablas y cargar nuevamente todo el catálogo:

```powershell
py seed.py --reset
```

Este comando debe usarse únicamente en un entorno de desarrollo o prueba, porque elimina los datos existentes.

## 9. Solución de problemas

### Faltan las variables de entorno

Verificar que exista `.env` en la raíz del proyecto y que contenga una URL y una clave válidas:

```env
SUPABASE_URL=https://tu-proyecto.supabase.co
SUPABASE_KEY=tu-service-role-key
```

### Error de conexión o autorización

Comprobar que la URL corresponda al proyecto correcto y que se esté usando la clave `service_role`, no una clave pública `anon`.

### Error porque no existe una tabla

Volver al SQL Editor de Supabase y ejecutar todo `schema_supabase.sql` antes de ejecutar `seed.py`.

### El comando `py` no existe

Instalar Python desde [python.org](https://www.python.org/downloads/) y activar la opción **Add Python to PATH** durante la instalación. Luego cerrar y volver a abrir la terminal.

También se puede ejecutar con:

```powershell
python seed.py
python main.py
```
