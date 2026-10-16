# SPEC-02: Monitoreo de Teams y Motor OCR

## 1. Alcance
Especifica la detección de mensajes nuevos en Microsoft Teams (Web Fluent UI), la captura de imágenes adjuntas en alta definición, el procesamiento mediante WinOCR nativo, la extracción tolerante de direcciones IP y el despacho de alertas y respuestas con cita.

## 2. Selectores Estables del DOM de Teams
- **Mensaje individual:** `div[data-tid="chat-pane-message"]`
- **Texto del mensaje:** `div[data-message-content] p`
- **Imágenes adjuntas:** `img[data-tid^="lazy-image"]`
- **Barra lateral de chats:** `[data-tid='chat-list'], [role='grid'], [role='list'], nav, .chat-list, .left-rail`
- **Ítem de chat individual:** `div[role='treeitem']`, `.fui-TreeItem`, `[data-tid*='chat-list-item']`
- **Cuadro de entrada:** `div[contenteditable='true'], div[data-tid='ckeditor'], [role='textbox']`
- **Botón Enviar:** `button[aria-label*='Enviar'], button[aria-label*='Send'], button[data-tid*='send']`

## 3. Detección Inteligente de Mensajes No Leídos
Para evitar clics innecesarios y consumo de memoria:
1. Comprobar si el ítem de chat ya está seleccionado (`aria-selected="true"`).
2. Si no está seleccionado, evaluar mediante script en el navegador:
   - Presencia de estilos con `fontWeight >= 700` o `'bold'`.
   - Atributos `aria-label` que contengan `"unread"`, `"sin leer"`, `"no leído"`, `"mensajes nuevos"`.
   - Atributos o clases con `'badge'`, `'counter'` o `'unread'`.
3. Solo si es no leído (o en lectura forzada inicial), se realiza clic silencioso en segundo plano.

## 4. Pipeline de Ingesta OCR (WinOCR Nativo)
1. **Detección de Imagen:**
   - Descartar avatares y emojis (filtrado por `class`, `src` y `data-tid`).
2. **Estrategia 1 (Alta Definición):**
   - Clic forzado sobre la miniatura para desplegar el modal de galería de Teams.
   - Esperar 4.0 segundos a la descarga completa de la imagen.
   - Extraer el `src` (`blob:https://...`) y convertir a base64 evaluando `FileReader` directamente en el navegador.
   - Guardar como `teams_latest.png`. Cerrar el modal con `Escape`.
3. **Estrategias de Respaldo:**
   - Screenshot directo del nodo contenedor del mensaje.
   - Screenshot de la miniatura `<img>`.
4. **Preprocesamiento de Imagen (PIL):**
   - Escalar al 300% con filtro `LANCZOS`.
   - Convertir a escala de grises (`L`).
5. **Reconocimiento Óptico (WinOCR):**
   - Debe ejecutarse en un hilo secundario (`ThreadPoolExecutor`) con su propio `asyncio.new_event_loop()` para evitar colisiones con el bucle de eventos de Playwright.
   - Probar secuencialmente los diccionarios `'es-ES'` y `'en-US'`.

## 5. Extracción y Normalización de IPs (`extract_ips`)
1. **Normalización Previa:**
   - Reemplazar saltos de línea por espacios.
   - Corregir aberraciones tipográficas comunes de OCR:
     - `'92` y `’92` $\to$ `192`
     - `Ã` y `ã` $\to$ `.1` (reparando `192Ã68` a `192.168`)
     - `?` $\to$ `7` (reparando `7?` a `77`)
     - Eliminar el bloque corrupto `192168` (ruido OCR que contamina el siguiente octeto).
2. **Patrón Exacto:** `\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b`
3. **Patrón Ultra-Tolerante OCR:** `\b(192)[ .]*(168)[ .]+(\d{1,3})[ .]+(\d{1,3})\b`
4. **Validación Numérica:**
   - Descartar `0.0.0.0`.
   - Validar que cada uno de los 4 octetos se encuentre en el rango cerrado $[0, 255]$.
   - Eliminar duplicados preservando el orden.

## 6. Criterios de Soporte
- Coincidencia textual directa contra `CRITERIOS`.
- Coincidencia por expresiones regulares contra `CRITERIOS_REGEX` (ej. solicitudes de apoyo, reportes de bots trabados, sin conexión, o pedidos de reinicio).
