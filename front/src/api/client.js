// front/src/api/client.js
// Instancia Axios centralizada para el front.
// Ajusta baseURL si el backend corre en otro puerto u host.
import axios from 'axios'

const client = axios.create({
  baseURL: 'https://ubiquitous-space-fortnight-6vrxwq5jq4wc5p99-8000.app.github.dev/api/v1',
  timeout: 8000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Interceptor de errores para mostrar mensajes legibles
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
