# ⚡ Clase IA

# Plataforma de solicitud de prácticas

**Del requerimiento en prosa a la especificación, y de la especificación al código.**

## El requerimiento

Esto es todo lo que tenemos. Un párrafo, como llega en la realidad: incompleto y ambiguo.

> "Necesitamos una plataforma de solicitud de prácticas con tres perfiles: un empleador que envía una oferta ofreciendo la práctica, un administrador que revisa y aprueba la práctica para que se publique, y un estudiante que postula a la práctica."

A partir de este párrafo definimos las reglas de negocio, el modelo de datos y las vistas. **La IA escribe el código; nosotros decidimos qué debe hacer.**

## Stack

| Capa | Tecnología | Por qué |
| --- | --- | --- |
| Frontend | **React** | Las tres vistas de la aplicación |
| Backend | **FastAPI** (Python) | API y validación de las reglas de negocio |
| Base de datos | **PostgreSQL** | Persistencia |
| Infraestructura | **Docker** | Correr todo en local y desplegar en el servidor de la universidad |

---

# Acceso: login y registro

Lo primero que ve cualquier persona que entra es la pantalla de **login**, con acceso a **registro**.

## Registro

- Lo primero que se pide es **qué tipo de usuario se va a crear**. Según esa elección se muestra un formulario u otro.
- **Estudiante:** nombre, apellido, correo, contraseña, carrera *(selector con las carreras cargadas por el administrador)*.
- **Empleador:** nombre, apellido, correo, contraseña, empresa a la que pertenece.
- **El administrador no aparece en el selector de registro.** Se crea por *seed* directamente en la base de datos.

> Decisión de diseño: si cualquiera pudiera registrarse como administrador, cualquiera podría aprobar sus propias ofertas. El rol con más poder nunca se auto-asigna desde un formulario público.

## Login

Al iniciar sesión, cada usuario es redirigido a su panel según su rol:

- Administrador → panel de administración
- Empleador → panel de empleador
- Estudiante → panel de estudiante

---

# Vista del administrador

**Pestaña Perfil**

Información de su cuenta: nombre, apellido y correo.

**Pestaña Dashboard**

Solicitudes de ofertas separadas por estado: **pendientes de aprobación**, **aprobadas** y **rechazadas**.

Por cada oferta se muestra toda su información y, además, **los estudiantes inscritos en esa oferta**.

**Pestaña Carreras**

Agregar carreras. Estas carreras alimentan el selector del registro de estudiantes y el selector de carrera al crear una oferta.

---

# Vista del empleador

**Pestaña Perfil**

Información de su cuenta: nombre, apellido, correo y empresa a la que pertenece.

**Pestaña Crear oferta**

Formulario con:

- Título
- Descripción
- Requisitos
- Carrera a la que va enfocada la oferta *(selector con las carreras que el administrador haya agregado)*
- Modalidad: **remoto**, **presencial** o **híbrida**
- Si es presencial o híbrida, se pide dirección: **calle, número, comuna y región** *(campos ocultos si la modalidad es remoto)*

**Pestaña Mis ofertas aprobadas**

Ofertas aprobadas por el administrador. Por cada una, la **cantidad de estudiantes que han postulado** y la información de cada estudiante, incluida su carta de presentación.

---

# Vista del estudiante

**Pestaña Ofertas disponibles**

Todas las ofertas **aprobadas** correspondientes **a su carrera**, con opción de postular.

Al postular se le exige obligatoriamente un cuadro de texto de **máximo 500 caracteres** donde se presenta y explica por qué sería un buen candidato para esa oferta. Ese texto se muestra al empleador en su panel de ofertas aprobadas.

**Pestaña Mis postulaciones**

Ofertas a las que ya postuló. Estas ofertas **no vuelven a aparecer** en la pestaña de ofertas disponibles.

---

# Reglas de negocio

Esto es lo que el enunciado **no dice** y que tenemos que decidir nosotros. Es el trabajo del ingeniero, no de la IA.

## Ciclo de vida de una oferta

```javascript
OFERTA:  PENDIENTE ──aprueba──> APROBADA (visible para estudiantes)
              └────rechaza────> RECHAZADA (con motivo)
```

- Una oferta nace en **PENDIENTE** al ser creada por el empleador.
- Solo el administrador cambia el estado.
- El rechazo exige **motivo obligatorio**, visible para el empleador.
- **Solo las ofertas APROBADAS son visibles para los estudiantes.** Esta única regla justifica la existencia del rol administrador.

> El estado no es una columna más de la base de datos: es la regla de negocio hecha dato. Cada transición del diagrama es un endpoint de la API.

## Reglas de visibilidad y validación

- Un estudiante solo ve ofertas **APROBADAS** **y** de **su carrera**.
- Un estudiante **no puede postular dos veces** a la misma oferta *(restricción única estudiante + oferta en la base de datos, no solo en la interfaz)*.
- Un empleador solo ve **sus propias** ofertas y las postulaciones a **sus propias** ofertas.
- La carta de presentación es **obligatoria** y de **máximo 500 caracteres**, validado en el servidor.
- Dirección obligatoria solo si la modalidad es presencial o híbrida.
- Una oferta apunta a **una** carrera.
- Correo único por usuario. Contraseña almacenada con *hash*, nunca en texto plano.

## Matriz de permisos

| Acción | Administrador | Empleador | Estudiante |
| --- | --- | --- | --- |
| Crear carrera | Sí | No | No |
| Crear oferta | No | Sí | No |
| Ver ofertas pendientes | Todas | Solo las propias | No |
| Aprobar o rechazar oferta | Sí | No | No |
| Ver ofertas aprobadas | Todas | Solo las propias | Solo las de su carrera |
| Postular | No | No | Sí |
| Ver postulantes de una oferta | Todas | Solo las propias | No |

> Ocultar un botón en el navegador no es seguridad. **La autorización se verifica siempre en el servidor.**

## Modelo de datos

| Entidad | Campos principales |
| --- | --- |
| Usuario | Nombre, apellido, correo, contraseña (hash), **rol**: admin / empleador / estudiante |
| Carrera | Nombre. Creada por el administrador |
| Estudiante | Usuario + carrera |
| Empleador | Usuario + empresa |
| Oferta | Empleador, título, descripción, requisitos, carrera, modalidad, dirección (opcional), **estado**, motivo de rechazo |
| Postulación | Estudiante, oferta, carta de presentación (máx. 500) |

## Fuera de alcance

Decidir **qué no construir** también es trabajo de ingeniería. Queda deliberadamente fuera:

- Cupos por oferta y fecha de cierre
- Edición de una oferta ya enviada / reenvío tras rechazo
- Que el empleador acepte o rechace postulantes *(en esta versión solo los visualiza)*
- Retiro de una postulación por parte del estudiante
- Recuperación de contraseña, notificaciones por correo, carga de currículum
- Búsqueda, filtros y paginación

## Datos de arranque (seed)

Para que la aplicación sea usable desde el primer minuto, la base se inicializa con:

- Un usuario **administrador**
- Un conjunto inicial de **carreras** *(sin carreras, ningún estudiante puede registrarse: el registro del estudiante depende de un catálogo que solo el admin puede crear)*

---

Todo corre con **Docker**: contenedor de frontend, contenedor de backend, contenedor de PostgreSQL, orquestados con Docker Compose.

El mismo `docker compose up` que funciona en el computador debe funcionar en el **servidor de la universidad**. Esa es la razón de contenerizar: eliminar el "en mi máquina funciona".
