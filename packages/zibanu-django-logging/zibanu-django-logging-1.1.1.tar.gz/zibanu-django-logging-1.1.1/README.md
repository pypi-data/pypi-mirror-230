# Paquete de Acceso de Zibanu para Django - zibanu.django.logging package

Utilidad para poder realizar el proceso de iniciar sesión (login) a través de la API.

Además, contiene señales en la API para registrar eventos importantes relacionados con el login y otros eventos de interés.

Por ejemplo, cuando un usuario realiza un inicio de sesión éxitoso, se genera una señal que activa una función para registrar la información ingresada, como el usuario que inició sesión, la hora del inicio de sesión y otros detalles relevantes, en una tabla de registro o log.
La información registrada puede incluir detalles como el tipo de acción (inicio de sesión), el usuario involucrado, la dirección IP desde la que se realizó el inicio de sesión, la fecha y hora del evento, entre otros.

Antes de registrar la información en el log, se valida si **zibanu.django.logging** está instalado en la API,
de no estarlo, se omite el registro de eventos en el log, dado que esta funcionalidad depende de su disponibilidad.

Por último, se ha creado una tabla en la base de datos para almacenar la información de registro de eventos.
Esta tabla puede tener campos como "usuario", "hora", "acción", "dirección IP", etc., para almacenar los detalles relevantes de cada evento registrado.

## zibanu.django.logging.lib package

Este paquete proporciona señales y funcionalidades relacionadas con la gestión de registros y eventos en una aplicación. Adicionalmente expone la clase zibanu.django.logging.lib.DbHandler para ser utilizada dentro del sistema de logging de *python3* de manera que el sistema pueda almacenarlo en la tabla de logging.

```python
LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "verbose": {
            "format": "[{levelname}] - {asctime} - {module}/{process:d}/{thread:d}: {message}",
            "style": "{"
        },
        "simple": {
            "format": "[{levelname}] - {asctime} - {module}: {message}",
            "style": "{"
        }
    },
    "handlers": {
        "zibanu": {
            "level": "DEBUG",
            "class": "zibanu.django.logging.lib.handlers.DbHandler",
            "formatter": "simple"
        }
    },
    "root": {
        "handlers": ["zibanu"],
        "level": "DEBUG"
    }
}
```

Dentro de este paquete, se encuentran implementadas varias señales que permiten a los desarrolladores registrar y manejar eventos específicos en la aplicación. Estas señales son utilizadas para notificar sobre eventos significativos que ocurren durante la ejecución del programa.

## zibanu.django.logging.lib.signals module

Este módulo tiene como objetivo gestionar eventos relacionados con el envío de correos electrónicos. Utiliza el marco de señales de Django para lograr esto.

Se utiliza para gestionar eventos relacionados con el envío de correos electrónicos.


```
send_mail = dispatch.Signal()
```
______

El decorador `@receiver` se utiliza para definir una función receptora que escucha la señal `send_mail`. Esta función se va a activar cada vez que se envíe la señal `send_mail`.


```
@receiver(send_mail)
```
________
Esta función actúa como el controlador de eventos que registra información relevante sobre eventos de correo electrónicos para la señal `send_mail`. 

```
on_send_mail(sender, mail_from: str, mail_to: list, subject: str, smtp_error: str, smtp_code: int, **kwargs):
```


Esta función acepta los siguientes parámetros:

Parámetros:

- sender: Clase de emisor de la señal.
- mail_from: Dirección de correo electrónico del remitente.
- mail_to: Lista de direcciones de correo destinatarios.
- subject: Asunto del correo electrónico.
- smtp_error: Cadena de error SMTP.
- smtp_code: Código de error SMTP.
- **kwargs: Diccionario de parámetros.

Retorno:

Ninguno.


## zibanu.django.logging.apps module
```
class zibanu.django.logging.apps.ZbDjangoLogging(app_name, app_module)
```
Clase heredada de django.apps.AppConfig para definir la configuración de la aplicación zibanu.django.logging.

```
default_auto_field= 'django.db.models.AutoField'
```

```
label= 'zb_logging'
```

```
name= 'zibanu.django.logging'
```

**Método**
```
ready()
```
Método de anulación utilizado para el cargador de aplicaciones django después de que la aplicación se haya cargado correctamente.

## zibanu.django.logging.models module

Contiene los modelos para la aplicación de registro. El modelo Log almacena información sobre todas las acciones que se realizan en el sistema. El modelo MailLog almacena información sobre todos los correos electrónicos que se envían a través del sistema.


### Log model
El modelo Log tiene los siguientes campos:

* action: Una cadena que describe la acción que se realizó.
* sender: Una cadena que identifica el objeto que envió la acción.
* detail: Una cadena que proporciona más información sobre la acción.
* ip_address: La dirección IP del usuario que realizó la acción.
* user: Una clave externa al modelo de usuario.

### MailLog model
El modelo MailLog tiene los siguientes campos:

* log: Una clave externa al modelo Log.
* mail_from: La dirección de correo electrónico desde la que se envió el mensaje.
* mail_to: La dirección de correo electrónico a la que se envió el mensaje.
* subject: El asunto del mensaje.
* smtp_code: El código SMTP que se devolvió cuando se envió el mensaje.
* smtp_error: El mensaje de error SMTP que se devolvió cuando se envió el mensaje.







