variable "prefijo" {
  description = "Prefijo de los recursos (minúsculas, números y guiones)."
  type        = string
  default     = "notaryverify"

  validation {
    condition     = can(regex("^[a-z0-9-]{3,20}$", var.prefijo))
    error_message = "El prefijo debe tener entre 3 y 20 caracteres: minúsculas, números o guiones."
  }
}

variable "ubicacion" {
  description = "Región de Azure."
  type        = string
  default     = "eastus2"
}

variable "sku_plan" {
  description = "SKU del App Service Plan Linux (F1 gratuito, B1 básico)."
  type        = string
  default     = "B1"

  validation {
    condition     = contains(["F1", "B1", "B2", "S1"], var.sku_plan)
    error_message = "sku_plan admite F1, B1, B2 o S1."
  }
}

variable "imagen_backend" {
  description = "Imagen del backend en GitHub Container Registry (repositorio:etiqueta, sin el host)."
  type        = string
  default     = "upt-faing-epis/proyecto-si784-2026-ii-myprojectgroupcypw-backend:latest"
}

variable "imagen_frontend" {
  description = "Imagen del frontend en GitHub Container Registry (repositorio:etiqueta, sin el host)."
  type        = string
  default     = "upt-faing-epis/proyecto-si784-2026-ii-myprojectgroupcypw-frontend:latest"
}

variable "registro_url" {
  description = "URL del registro de contenedores."
  type        = string
  default     = "https://ghcr.io"
}

variable "usuarios_demo" {
  description = <<-EOT
    Usuarios ficticios opcionales creados al arrancar el backend (mismas
    variables NOTARYVERIFY_BOOTSTRAP_* de .env.example). Vacío = sin usuarios.
    Se pasa desde un secreto (TF_VAR_usuarios_demo); nunca se versiona.
  EOT
  type = object({
    operador_correo   = optional(string, "")
    operador_password = optional(string, "")
    admin_correo      = optional(string, "")
    admin_password    = optional(string, "")
  })
  default   = {}
  sensitive = true
}

variable "etiquetas" {
  description = "Etiquetas comunes de los recursos."
  type        = map(string)
  default = {
    proyecto = "NotaryVerify"
    curso    = "SI784"
    entorno  = "academico"
  }
}
