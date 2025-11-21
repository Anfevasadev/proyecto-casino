// front/src/api/client.js
// Instancia Axios centralizada para el front.
// Ajusta baseURL si el backend corre en otro puerto u host.
import axios from 'axios'

const client = axios.create({
  baseURL: 'https://sturdy-space-halibut-qp4jpvqx55j2x97x-8000.app.github.dev/api/v1',
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Ejemplo de interceptor de respuesta para extraer mensajes de error legibles
client.interceptors.response.use(
  (response) => response,
  (error) => {
    const detail = error?.response?.data?.detail
    if (detail) {
      error.message = Array.isArray(detail) ? detail.join(', ') : detail
    }
    return Promise.reject(error)
  }
)

export default client
