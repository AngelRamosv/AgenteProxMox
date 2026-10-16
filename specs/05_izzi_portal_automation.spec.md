# SPEC-05: Automatización del Portal Izzi (FrontRPAIzzi)

## 1. Alcance
Regula la interacción con la plataforma web `https://frontrpaizzi.azurewebsites.net/robots` desarrollada con PrimeNG y Angular. Establece la estrategia de búsqueda por IP, manejo de dropdowns, diálogos modales y rutinas Keep-Alive anti-sueño.

## 2. Detección y Paginación
1. **Localización de Pestaña:**
   - Buscar entre todas las páginas del contexto de Chrome la URL que contenga `frontrpaizzi`.
2. **Reset a Página 1 (Invariante):**
   - Antes de cualquier búsqueda, hacer clic explícito en el botón de página 1 (`ul.pagination li, button, a` con texto `"1"`).
   - Pausa de 2.0 segundos para renderizado de la tabla.
3. **Búsqueda de Fila:**
   - Utilizar coincidencia con límite de palabra (`\b{IP}\b`) sobre los elementos `<tr>` para evitar falsos positivos (por ejemplo, evitar que `.4` coincida con `.40` o `.14`).
   - Si no se encuentra en Página 1, hacer clic en el botón de Página 2 y reintentar.

## 3. Disparo del Proceso Robot (PrimeNG)
1. **Despliegue de Opciones:**
   - Ubicar el componente `<p-dropdown>` dentro de la fila localizada.
   - Forzar clic en `.p-dropdown-trigger` o `.p-dropdown-label`.
   - Esperar 1.5 segundos a que se monte la lista superpuesta en el DOM.
2. **Selección del Comando:**
   - Localizar `p-dropdownitem li` con texto `"Iniciar Proceso"`.
   - Forzar clic en el elemento.
   - Esperar 2.0 segundos para la animación del cuadro de diálogo.
3. **Confirmación en Modal Activo:**
   - **Regla Crítica:** Acotar la búsqueda del botón únicamente dentro del cuadro de diálogo activo: `div[role='alertdialog']`.
   - Localizar el botón con etiqueta `"Si, Enviar"` (`span.p-button-label` o clase `button.p-confirm-dialog-accept`).
   - Forzar clic sobre el botón de confirmación.

## 4. Rutina Keep-Alive Anti-Sueño (`izzi_keep_alive`)
1. Detectar cuál es la pestaña que tiene el foco activo del usuario (`document.hasFocus()`).
2. Traer temporalmente la pestaña de izzi al frente y simular un clic de interacción en `body`.
3. Devolver inmediatamente el foco a la pestaña previa del usuario para mantener la sesión activa sin interrumpir el trabajo de pantalla.
