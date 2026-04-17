<script setup>
import { ref } from 'vue'


const form = ref({
  nombre: '',
  fechaNacimiento: '',
  ubicacion: '',
  alergias: [],
  email: '',
  password: '',
})


const opcionesAlergias = [
  'Polen de olivo', 
  'Gramíneas', 
  'Cupresáceas', 
  'Plátano de sombra', 
  'Parietaria', 
  'Artemisia', 
  'Arizónicas', 
  'Alternaria'
]

const cargando = ref(false)

const handleRegistro = async () => {
  cargando.value = true
  console.log('Enviando datos a Django:', form.value)
  

  setTimeout(() => {
    cargando.value = false
  }, 1000)
}
</script>


<template>
  <div class="registration-container">
    <div class="form-card">
      <header class="form-header">
        <h1>tualergiahoy.com</h1>
      </header>

      <form @submit.prevent="handleRegistro" class="registration-form">
        <div class="form-group">
          <label>Nombre y Apellidos</label>
          <input v-model="form.nombre" type="text" required />
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>Fecha de Nacimiento</label>
            <input v-model="form.fechaNacimiento" type="date" required />
          </div>
          <div class="form-group">
            <label>Ciudad</label>
            <input v-model="form.ubicacion" type="text" required />
          </div>
        </div>

        <div class="form-group">
          <label>Alergias conocidas</label>
          <div class="alergias-grid">
            <label v-for="alergia in opcionesAlergias" :key="alergia" class="checkbox-label">
              <input type="checkbox" :value="alergia" v-model="form.alergias" />
              <span>{{ alergia }}</span>
            </label>
          </div>
        </div>

        <div class="form-group">
          <label>Correo electrónico</label>
          <input v-model="form.email" type="email" required />
        </div>

        <div class="form-group">
          <label>Contraseña</label>
          <input v-model="form.password" type="password" required />
        </div>

        <button type="submit" :disabled="cargando" class="btn-submit">
          {{ cargando ? 'Procesando...' : 'Registrarse' }}
        </button>
      </form>
    </div>
  </div>
</template>



<style scoped>
  .registration-container {
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: #f3f4f6;
    padding: 20px;
    font-family: sans-serif;
  }

  .form-card {
    background: white;
    padding: 40px;
    border-radius: 16px;
    box-shadow: 0 10px 25px rgba(0,0,0,0.05);
    max-width: 500px;
    width: 100%;
  }

  .form-header {
    margin-bottom: 2rem;
  }

  .form-header h1 {
    color: #31911b;
    margin: 0;
    text-align: center;
    font-size: 2rem;
  }

  .form-group {
    margin-bottom: 20px;
  }

  .form-row {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
  }

  label {
    display: block;
    font-size: 14px;
    font-weight: 600;
    margin-bottom: 8px;
    color: #2f3432;
  }

  input[type="text"],
  input[type="email"],
  input[type="password"],
  input[type="date"] {
    width: 100%;
    padding: 12px;
    border: 1px solid #d1d5db;
    border-radius: 8px;
    box-sizing: border-box;
    transition: all 0.3s ease;
  }

  input:focus {
    outline: none;
    border-color: #31911b;
    box-shadow: 0 0 0 3px rgba(49, 145, 27, 0.1);
  }

  .alergias-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(140px, 1fr));
    gap: 12px;
    
    background: #f9fafb;
    padding: 15px;
    border-radius: 8px;
  }

  .checkbox-label {
    display: flex;
    align-items: center;
    gap: 8px;

    font-size: 13px;

    cursor: pointer;
    transition: color 0.2s ease;
  }

  .checkbox-label:hover {
    color: #31911b;
  }

  .btn-submit {
    width: 100%;
    background-color: #8e958d;
    border-radius: 8px;

    color: white;
    padding: 14px;
    border: none;
    font-weight: bold;

    cursor: pointer;
    transition: all 0.3s ease;
    margin-top: 10px;
  }

  .btn-submit:hover {
    background-color: #31911b;
    transform: translateY(-1px);
  }

  .btn-submit:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
</style>