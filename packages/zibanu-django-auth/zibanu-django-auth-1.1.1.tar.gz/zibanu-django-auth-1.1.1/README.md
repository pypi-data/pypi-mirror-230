# Paquete de autenticación y autorización de Zibanu para Django - zibanu.django.auth package


Este paquete contiene los servicios y librerias necesarias para la autenticación y autorización de usuarios a través de la API de Django. Estos componentes proporcionan la funcionalidad necesaria para gestionar la autenticación de usuarios y permitir el acceso a recursos protegidos.

El repositorio ofrece once (11) servicios API REST para el login, cambio de contraseña, listado de grupo, inicio de sesión, permisos de listado, actualización de perfil, actualización de autenticación, solicitud de contraseña, agregar usuario, eliminar usuario, listar usuarios o actualizar usuarios.   


## APIs
- [Login (Iniciar sesión)](#login-iniciar-sesión)
- [Refresh (Actualizar)](#refresh-actualizar)
- [Change Password (Cambio de contraseña)](#zibanudjangoauthapiservicesuserchange_password-cambio-de-contraseña)
- [Request Password (Solicitud de contraseña)](#zibanudjangoauthapiservicesuserrequest_password-solicitud-de-contraseña)
- [User Add (Agregar usuario)](#zibanudjangoauthapiservicesuseradd-agregar-usuario)
- [User Delete (Eliminar usuario)](#zibanudjangoauthapiservicesuserdelete-eliminar-usuario)
- [User List (Lista de usuarios)](#zibanudjangoauthapiservicesuserlist-lista-de-usuarios)
- [User Update (Actualización de usuarios)](#zibanudjangoauthapiservicesuserupdate-module-actualización-de-usuarios)
- [Permission List (Permisos de lista)](#zibanudjangoauthapiservicespermissionlist-permisos-de-lista)
- [Profile Update (Actualización de perfil)](#zibanudjangoauthapiservicesprofileupdate-actualización-de-perfil)
- [Group List (Lista de grupo)](#zibanudjangoauthapiservicesgrouplist-lista-de-grupo)



### Login (Iniciar sesión)

Toma un conjunto de credenciales de usuario y devuelve un token web JSON deslizante para probar la autenticación de esas credenciales.

Retorna:

```
{
  "email": "string"
  "password": "string"
}
```

### Refresh (Actualizar)

Toma un token web JSON deslizante y devuelve una versión nueva y actualizada del período de actualización del token que no ha expirado.

Retorna:

```
{
  "token": "string"
}
```



 # zibanu.django.auth.api.services package

Contiene módulos o clases relacionados con la funcionalidad de los servicios de autenticación de Zibanu para Django.

## zibanu.django.auth.api.services.user module

Este modulo contiene la definición de la clase UserService. Esta clase es una subclase de la clase ModelViewSet y proporciona un conjunto de servicios REST para el modelo de admiinistración de usuarios de django.

Define los siguientes métodos:


### zibanu.django.auth.api.services.user.change_password (Cambio de contraseña) 

Servicio REST para cambiar la contraseña del usuario.

Parámetros: 
- *Request*: Solicitar objeto de HTTP.
- **args*: Tupla de parámetros.
- ***kwargs*: Diccionario de parámetros.

Retorna:

- Objeto Response con estado HTTP 200 si no existen errores y un objeto JSON.

```
{
  "full_name": "Guest",
  "email": "user@example.com",
  "last_login": "2023-08-02T05:27:42.500Z",
  "username": "lRhuazZ9swzssfflX6.kwald@icQeVTu-+X3f0b5922c_xe4j4dG@RkKkA3r0TX@RlfdHPFxTrsoZnK9dWS2Y6Ehb@EE_b0TzF",
  "is_staff": true,
  "is_superuser": true
}
```
____________
### zibanu.django.auth.api.services.user.request_password (Solicitud de contraseña)
Servicio REST para solicitar contraseña y enviar por correo electrónico.

Parámetros: 
- *Request*: Solicitar objeto de HTTP.
- **args*: Tupla de parámetros.
- ***kwargs*: Diccionario de parámetros.

Retorna:

- Objeto Response con estado HTTP 200 si no existen errores y un objeto JSON.

```
{
  "full_name": "Guest",
  "email": "user@example.com",
  "last_login": "2023-08-02T05:36:44.403Z",
  "username": "mWwuZ",
  "is_staff": true,
  "is_superuser": true
}
```
____________
### zibanu.django.auth.api.services.user.add (Agregar usuario)
Servicio REST para crear usuario con su perfil.

Parámetros:
- *Request*: Solicitar objeto de HTTP.
- **args*: Tupla de parámetros.
- ***kwargs*: Diccionario de parámetros.

Retorna:

- Objeto Response con estado HTTP 200 si no existen errores y un objeto JSON.

```
{
  "full_name": "Guest",
  "email": "user@example.com",
  "last_login": "2023-08-02T05:37:05.899Z",
  "username": "ydGJD6gGCVlSaN@balstNsnJLj",
  "is_staff": true,
  "is_superuser": true
}
```
____________
### zibanu.django.auth.api.services.user.delete  (Eliminar usuario)
Servicio REST para eliminar un objeto de usuario.

Parámetros: 
- *Request*: Solicitar objeto de HTTP.
- **args*: Tupla de parámetros.
- ***kwargs*: Diccionario de parámetros.

Retorna:

- Objeto Response con estado HTTP 200 si no existen errores y un objeto JSON.

```
{
  "full_name": "Guest",
  "email": "user@example.com",
  "last_login": "2023-08-02T05:37:32.699Z",
  "username": "w2OUlyqJrgc_1vWUXxflSt86eOuV2sitCh5zLiy8Cm_ldalAlZUDSkyRtmxiu+unwhsJp_-Nnu-kPULH8AHI3hVDc_reAd7i.iT1o",
  "is_staff": true,
  "is_superuser": true
}
```
____________

### zibanu.django.auth.api.services.user.list  (Lista de usuarios)
Servicio REST para actualizar el usuario, incluyendo perfil, grupos y permisos.

Parámetros: 
- *Request*: Solicitar objeto de HTTP.
- **args*: Tupla de parámetros.
- ***kwargs*: Diccionario de parámetros.

Retorna:

- Objeto Response con estado HTTP 200 si no existen errores y un objeto JSON.

```
[
  {
    "full_name": "Guest",
    "email": "user@example.com",
    "last_login": "2023-08-02T05:38:00.491Z",
    "username": "U07l706kG6cV5Ljy-re2Y",
    "is_staff": true,
    "is_superuser": true
  }
]
```
____________

### zibanu.django.auth.api.services.user.update (Actualización de usuarios)
Servicio REST para actualizar el usuario, incluyendo perfil, grupos y permisos.

Parámetros: 
- *Request*: Solicitar objeto de HTTP.
- **args*: Tupla de parámetros.
- ***kwargs*: Diccionario de parámetros.

Retorna:

- Response: Objeto de respuesta con estado HTTP (200 si se realiza correctamente).

```
{
  "full_name": "Guest",
  "email": "user@example.com",
  "last_login": "2023-08-02T05:38:56.663Z",
  "username": "lQhl73VM6B03n3Xaz9F58o3LaJknj4VXPj8rqyXCCxu.-mPX2cJLdagL+84dRUVtBs4BO",
  "is_staff": true,
  "is_superuser": true
}
```



## zibanu.django.auth.api.services.permission module 

Contiene un conjunto de métodos para gestionar los permisos de los servicios relacionados con la autenticación y la autorización de Zibanu para Django.

### zibanu.django.auth.api.services.permission.list (Permisos de lista)
Servicio REST para permisos de lista

Parámetros:
- *Request*: Solicitar objeto de HTTP.
- **args*: Tupla de parámetros.
- ***kwargs*: Diccionario de parámetros.

Retorna:

- Objeto Response con estado HTTP y conjunto de datos.

```
[
  {
    "id": 0,
    "name": "string"
  }
]
```

## zibanu.django.auth.api.services.profile module

Contiene un conjunto de métodos para la gestión de perfiles de usuario de Zibanu para Django.


### zibanu.django.auth.api.services.profile.update (Actualización de perfil)
Servicio REST para actualizar el modelo UserProfile.

Parámetros:
- *Request*: Solicitar objeto de HTTP.
- **args*: Tupla de parámetros.
- ***kwargs*: Diccionario de parámetros.

Retorna:

- Objeto Response con estado HTTP 200 si no existen errores y un objeto JSON.

```
{
  "timezone": "Africa/Abidjan",
  "theme": "string",
  "lang": "str",
  "avatar": "string",
  "messages_timeout": 0,
  "keep_logged_in": true,
  "app_profile": {
    "additionalProp1": "string",
    "additionalProp2": "string",
    "additionalProp3": "string"
  },
  "multiple_login": true,
  "secure_password": true
}
```

## zibanu.django.auth.api.services.group module

Contiene un conjunto de métodos para la gestión de grupos de usuarios de Zibanu para Django.

### zibanu.django.auth.api.services.group.list (Lista de grupo)

Servicio REST para listar grupos.

Parámetros:
- *Request*: Solicitar objeto de HTTP.
- **args*: Tupla de parámetros.
- ***kwargs*: Diccionario de parámetros.

Retorna:

- Objeto Response con estado HTTP y lista de dataset.

```
[
  {
    "id": 0,
    "name": "string"
  }
]
```



## zibanu.django.auth.lib package

Paquete que contiene módulos, clases y utilidades relacionadas con la autenticación y autorización de Zibanu para Django.

## zibanu.django.auth.lib.signals module

Este módulo tiene como objetivo manejar señales personalizadas de Django para capturar eventos relacionados con la autenticación y la gestión de contraseñas.

Se definen dos señales:

- Se utiliza para gestionar eventos relacionados con el cambio de contraseña.

```
on_change_password = dispatch.Signal()
```
- Se utiliza para gestionar eventos relacionados con el restablecimiento de contraseña.

```
on_request_password = dispatch.Signal()
```
________
Los decoradores `@receiver` se utilizan para asociar funciones receptoras (event handlers) a las señales definidas. Cada una de ellas se activará cuando se emita la señal correspondiente.

```
@receiver(on_change_password, dispatch_uid="on_change_password")
```
- Asigna la función receptora a la señal `on_change_password`. Se agrega un identificador único (`dispatch_uid`) para garantizar que la conexión de la señal sea única y no se duplique.

________
```
@receiver(on_request_password, dispatch_uid="on_request_password")
```

- Asigna la función receptora a la señal `on_request_password`. Se agrega un identificador único (`dispatch_uid`) para garantizar que la conexión de la señal sea única y no se duplique.

________


```
@receiver(user_logged_in, dispatch_uid="on_user_logged_in")
```

- Asigna la función receptora a la señal `user_logged_in`. Se agrega un identificador único (`dispatch_uid`) para garantizar que la conexión de la señal sea única y no se duplique.

________


```
@receiver(user_login_failed, dispatch_uid="on_user_login_failed")
```
- Asigna la función receptora a la señal `user_login_failed`. Se agrega un identificador único (`dispatch_uid`) para garantizar que la conexión de la señal sea única y no se duplique.

________

```
auth_event(sender: Any, user: Any = None, **kwargs)→ None:
```

Esta función actúa como un manejador para eventos capturados por las señales de cambio de contraseña o solicitud de contraseña.


Parámetros:

- *sender*: Clase de emisor de la señal.
- *user*: Objeto de usuario para obtener datos.
- ***kwargs*: Diccionario con campos y parámetros.

Retorno:

- Ninguno.


## zibanu.django.auth.lib.utils module

Este modulo contiene la siguiente función:

- `get_user`: Obtiene el objeto de usuario de SimpleJWT TokenUser.

Parámetros:

- *user*: Objeto de usuario de tipo de usuario de token SimpleJWT o tipo de objeto de usuario

Retorna:

- user: Tipo de objeto de usuario de Django.


# zibanu.django.auth.api.serializers package

Este directorio contiene serializadores para la API de autenticación de Zibanu para Django.

## zibanu.django.auth.api.serializers.group module

GroupListSerializer es un serializador para una lista de grupos. Incluye los siguientes campos:

* id: El ID del grupo.
* name: El nombre del grupo.

## zibanu.django.auth.api.serializers.permission module

PermissionSerializer es un serializador para un permiso. Incluye los siguientes campos:

* id: El ID del permiso.
* name: El nombre del permiso.

## zibanu.django.auth.api.serializers.profile module

ProfileSerializer es un serializador para un perfil de usuario. Incluye los siguientes campos:

* timezone: La zona horaria del usuario.
* theme: El tema del usuario.
* lang: El idioma del usuario.
* avatar: El avatar del usuario.
* message_timeout: Tiempo de espera de los mensajes del usuario.
* keep_logged_in: Si el usuario desea permanecer conectado.
* app_profile: El perfil de la aplicación del usuario.
* multiple_login: Si el usuario permite múltiples inicios de sesión.
* secure_password: Si la contraseña del usuario es segura.

## zibanu.django.auth.api.serializers.token module

TokenObtainSerializer es un serializador para obtener un token mediante la autenticación de correo electrónico. Incluye los siguientes campos:

* username_field: El campo que se usará para la autenticación del nombre de usuario.
* email: La dirección de correo electrónico del usuario.
* password: La contraseña del usuario.

TokenObtainSlidingSerializer es una subclase de TokenObtainSerializer que usa un token deslizante. Incluye los siguientes campos:

* token.

## zibanu.django.auth.api.serializers.user module

La clase UserSerializer se utiliza para serializar y deserializar un solo objeto de usuario. Incluye los siguientes campos:UserSerializer es un serializador para un usuario. Incluye los siguientes campos:

* email.
* full_name.
* last_login.
* is_staff.
* is_superuser.
* is_active.
* profile.
* roles.
* first_name.
* last_name.
* permissions.
* username.
* password.

El método `create` se utiliza para crear un nuevo objeto de usuario. Toma un diccionario de datos validados como entrada y crea un nuevo objeto de usuario con los datos proporcionados. Si el objeto de usuario se crea correctamente, devuelve el objeto de usuario. Si el objeto de usuario ya existe, genera una excepción `ValidationError`.

### UserListSerializer

UserListSerializer es un serializador para una lista de usuarios. Incluye los siguientes campos:

* full_name.
* email.
* last_login.
* username.
* is_staff.
* is_superuser.

El método `get_full_name` se utiliza para obtener el nombre completo de un objeto de usuario. Toma un objeto de usuario como entrada y devuelve el nombre completo del usuario.



