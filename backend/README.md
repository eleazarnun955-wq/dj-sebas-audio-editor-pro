# DJ SEBAS PRODUCCIONES — backend IA (base de integración)

Este servicio es un adaptador FastAPI para conectar la app Android con un servidor **ACE-Step 1.5** administrado de forma privada. ACE-Step expone una API asíncrona: crear tarea con `POST /release_task`, consultar con `POST /query_result` y recuperar audio desde `/v1/audio`.

## Funciones del adaptador

- `GET /health`: estado del adaptador.
- `GET /api/music/models`: modelos disponibles.
- `POST /api/music/generate`: genera una tarea desde descripción y/o letra; permite idioma, instrumental, duración, BPM y tonalidad.
- `GET /api/music/tasks/{task_id}`: estado y metadatos; devuelve una ruta de audio cuando la tarea termina.
- `GET /api/music/audio?path=...`: transmite el MP3 desde el origen ACE-Step fijo, sin aceptar hosts arbitrarios.

Todas las rutas `/api/music/*` requieren `Authorization: Bearer <DJ_SEBAS_BACKEND_TOKEN>`. El servicio falla cerrado si el token no está configurado.

## Ejecución local

1. Instalar Python 3.11 o superior.
2. Crear entorno virtual e instalar `pip install -r requirements.txt`.
3. Configurar `ACE_STEP_BASE_URL`, `ACE_STEP_API_KEY` (si el proveedor la exige) y `DJ_SEBAS_BACKEND_TOKEN` mediante variables de entorno.
4. Ejecutar `uvicorn app.main:app --host 0.0.0.0 --port 8000`.

## Despliegue y seguridad: pendiente antes de producción

- ACE-Step requiere un host con GPU, memoria y almacenamiento para pesos del modelo. Este adaptador HTTP por sí solo **no contiene el modelo ni genera música**.
- No se debe desplegar el adaptador públicamente con un token fijo compartido dentro del APK: los secretos incluidos en una app Android pueden extraerse. Antes de conectar el cliente móvil hay que implementar autenticación por usuario/sesiones de corta duración, cuotas, límites de tamaño, rate limiting, almacenamiento persistente de tareas y limpieza de archivos.
- Mantener `ACE_STEP_API_KEY` y credenciales del proveedor únicamente en secretos del servidor.
- Verificar licencia y términos del modelo, derechos de los audios cargados y coste real de GPU antes de habilitar el servicio.

## Alcance funcional del modelo

ACE-Step documenta generación desde texto/letras, selección de idioma vocal, modo instrumental, BPM, tonalidad, duración y tareas de edición como cover/repaint/complete; las capacidades exactas dependen del modelo base/turbo cargado. La aplicación debe mostrar únicamente las operaciones que el servidor confirme que soporta.

La integración Android todavía no está conectada a este backend. No presentar la generación IA como disponible hasta completar autenticación móvil, desplegar el motor y probar de extremo a extremo generación, consulta, descarga y guardado MP3.
