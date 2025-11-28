# Usuarios y Credenciales por Defecto

Este documento detalla los usuarios iniciales del sistema, sus credenciales por defecto (solo para entornos de desarrollo) y las consideraciones de seguridad necesarias.

---

# 1. Usuarios por Defecto

El backend incluye un usuario inicial para permitir el acceso a la API y a las funciones administrativas en un entorno de desarrollo.

**Usuario Administrador por defecto:**
- **Username:** string  
- **Password:** string
- **Rol:** admin
- **Estado:** activo

> Este usuario se crea únicamente para facilitar pruebas y configuración del entorno local.

**Usuario Jugador por defecto:**
- **Username:** user1 
- **Password:** pass123
- **Rol:** player
- **Estado:** activo 

**Usuario Inactivo por defecto:**
- **Username:** user_inactive 
- **Password:** pass456
- **Rol:** player
- **Estado:** inactivo 

---

# 2. Consideraciones de Seguridad

- Las credenciales por defecto **no deben usarse en producción**.
- Se recomienda cambiar la contraseña en cuanto el sistema esté instalado.
- Es recomendable desactivar o eliminar el usuario `string` cuando el sistema se despliegue.
- Nunca almacenar contraseñas en texto plano dentro del repositorio o documentación pública.
- En producción, las contraseñas deben almacenarse usando hashing seguro (ej. bcrypt).

---

# 3. Recomendaciones

- Crear un usuario administrador real inmediatamente después de la instalación.
- Usar contraseñas fuertes y rotación periódica de claves.
- Proteger el archivo `.env` y excluirlo de Git mediante `.gitignore`.
- Configurar autenticación fuerte y bloqueo por intentos fallidos si el proyecto lo implementa más adelante.

---

