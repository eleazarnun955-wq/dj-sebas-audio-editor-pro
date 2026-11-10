# DJ SEBAS PRODUCCIONES

Aplicación Android independiente cuyo producto objetivo es un estudio de creación musical con IA, inspirado en el flujo de trabajo de Suno, más herramientas DJ avanzadas. **No es solamente un editor local ni una aplicación de mezclas.**

## Objetivo del producto

### 1. Creación musical con IA (función principal)
- Generar canciones completas desde descripciones en lenguaje natural.
- Crear canciones a partir de letras propias, con estructura de versos, coros y puentes.
- Elegir género, subgénero, instrumentación, ambiente, tempo, tonalidad e idioma vocal.
- Generar canciones instrumentales o con voz cantada.
- Crear variaciones, transformar el estilo de una pista, editar secciones y extender canciones.
- Guardar generaciones, versiones, letras y metadatos en una biblioteca de proyectos.

### 2. Estudio DJ inteligente (función complementaria)
- Mashup inteligente de varias canciones.
- Análisis de BPM, tonalidad y estructura musical.
- Alineación rítmica y transiciones con crossfade y ajuste de tempo cuando el motor lo permita.
- Herramientas de mezcla, efectos, edición, masterización y exportación.

### 3. Archivos y exportación
- Exportar audio MP3 al dispositivo Android.
- Guardar las exportaciones en `Music/DJ SEBAS PRODUCCIONES`.
- Mantener esta aplicación y su paquete Android independientes de DJ SEBAS AI MUSIC STUDIO PRO 3.0.

## Estado real de esta rama

La compilación inicial contiene una interfaz Android/WebView y herramientas locales de audio: importar/reproducir, recortar y exportar MP3, más una primera implementación de mashup con análisis aproximado de BPM y transiciones por fundido.

**Todavía no está integrado un motor de generación musical con IA.** Las pantallas de creación, letras y estilos no deben anunciarse como generación funcional hasta que el backend produzca audio real y la app pueda recuperar, reproducir y guardar ese resultado. Tampoco debe describirse el mashup actual como beatmatching profesional: aún no implementa time-stretch ni alineación precisa de beats/fase.

## Arquitectura prevista para IA real

- La app Android consume una API de backend mediante HTTPS.
- El backend administra tareas asíncronas de generación, estados, errores y URLs/archivos de audio.
- Las credenciales de proveedores/modelos se guardan únicamente como secretos del backend; nunca en el APK, HTML, repositorio ni logs.
- La interfaz debe distinguir claramente entre generación en cola, en proceso, completada y fallida.
- El adaptador de proveedor debe permitir cambiar de motor sin rehacer la interfaz.
- Antes de habilitar un proveedor se verifican licencia, derechos de uso, coste, límites, idiomas, generación vocal, duración, edición/extensión y disponibilidad de infraestructura GPU.

## Criterios para considerar lista la generación IA

1. Una descripción de texto genera un archivo musical real.
2. Letras introducidas por el usuario producen una canción cantada; la app muestra errores reales si el proveedor no puede cumplirlo.
3. La app consulta el estado de tareas y recupera el audio generado.
4. El usuario puede escuchar, guardar, renombrar y volver a abrir el resultado.
5. Se prueban fallos de red, tareas fallidas, cancelación y exportaciones incompletas.
6. Ninguna función se marca como lista basándose únicamente en una pantalla o botón.

## Compilación

El APK de depuración se construye con GitHub Actions desde esta rama. El paquete Android independiente está configurado como `com.djsebas.producciones`.
