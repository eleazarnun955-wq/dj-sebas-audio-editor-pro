# DJ SEBAS PRODUCCIONES

Aplicación Android independiente para editar, mezclar y organizar audio local desde el teléfono. Esta entrega prioriza herramientas que funcionan sin suscripciones, servidores externos ni servicios de generación musical.

## Alcance de esta versión

### Herramientas de audio local
- Importar y reproducir archivos de audio compatibles.
- Visualizar la forma de onda.
- Recortar y exportar selecciones en MP3.
- Exportar canciones completas a MP3.
- Grabar voz cuando el dispositivo concede permiso de micrófono.
- Ecualizador de graves, medios y agudos durante la reproducción.
- Mezclar dos pistas con controles de volumen independientes.
- Fusionar y dividir audio con las herramientas disponibles en la app.
- Efectos de reproducción, procesamiento básico y masterización local.
- Biblioteca local, favoritos y proyectos guardados en el dispositivo.
- Consultar exportaciones guardadas.

### Mix de varias canciones
- Selección de hasta 20 canciones y ajuste del orden.
- Exportación MP3 por bloques directamente a `Music/DJ SEBAS PRODUCCIONES`.
- Estimación aproximada de BPM para decidir si conviene ajustar la duración del fundido.
- Cuando no hay una lectura fiable o los tempos no son compatibles, usa un fundido convencional.

**Límite importante:** no es beatmatching profesional. Esta versión no implementa time-stretch, análisis de tonalidad ni alineación precisa de beats/fase. Por eso la función se presenta como mix con transiciones automáticas, no como mashup inteligente profesional.

## Generación musical con IA

Se deja fuera de esta entrega. Las opciones gratuitas encontradas son demos web con cuotas compartidas o servicios externos que no garantizan una API gratuita estable para integrar en la APK. No se conectará un servidor de pago ni se simulará generación de canciones. Se podrá reconsiderar en otra versión si existe una opción realmente gratuita y estable.

## Exportación y compatibilidad
- Las exportaciones se guardan en `Music/DJ SEBAS PRODUCCIONES`.
- El paquete Android es `com.djsebas.producciones`, independiente de DJ SEBAS AI MUSIC STUDIO PRO 3.0.
- La compilación de depuración se genera con GitHub Actions.

## Verificación pendiente antes de entregar como versión final
1. Compilar APK desde el commit final.
2. Revisar que todas las herramientas mostradas respondan sin errores.
3. Probar importación, reproducción, recorte y exportación MP3 en Android físico.
4. Probar mezcla de dos pistas, transiciones de varias canciones y exportación larga.
5. Verificar permisos, guardado en la carpeta dedicada y reinstalación independiente.

Una compilación correcta de GitHub Actions no sustituye las pruebas en un teléfono real.
