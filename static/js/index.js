let dbVaciar = document.getElementById('dbVaciar')
let speedscript = document.getElementById('speedscript')
let id = document.getElementById('buscar');
let reniciar = document.getElementById('reiniciar')
const selectEstados = document.getElementById('selectEstados')
const selectMunicipios= document.getElementById('selectMunicipios')
const tableCP = document.getElementById('tableCP')
const templateCodigosPostales =  document.getElementById('templateCodigosPostales').content
const fragment = document.createDocumentFragment();
const datosBusqueda = document.getElementById('datosBusqueda');

//////Eventos Listener click
id.addEventListener('click', async e =>{
   e.preventDefault()
   const estado = document.getElementById('selectEstados').value
   const municipio = document.getElementById('selectMunicipios').value
   const colonia = document.getElementById('colonias').value
   const cp = document.getElementById('cp').value

   let tipo = '';
   let dato ;

   if(cp){
      tipo = '1';
      dato = cp
   }
   else if(colonia){
      tipo = '2';
      dato = colonia
   }
   else if(municipio != 0){
      tipo = '3';
      dato = municipio
   }

   else if(estado != 0){
      tipo = '4';
      dato = estado
   }
   console.log(tipo + ' | ' + dato);
   
   if(dato && tipo){
      let res = await axios.get(`http://localhost:4000/datosPostales/${tipo}/${dato}`)
      let json = res.data
      console.log(json);
      tableCP.querySelector('tbody').innerHTML= ''

      json.forEach(el =>{
         
         templateCodigosPostales.querySelector(".cpT").textContent = el.CP
         templateCodigosPostales.querySelector('.coloniaT').textContent = el.Colonia
         templateCodigosPostales.querySelector('.municipioT').textContent = el.Municipio
         templateCodigosPostales.querySelector('.estadoT').textContent = el.Estado
         let clone = document.importNode(templateCodigosPostales,true)
         fragment.appendChild(clone)
      })

      tableCP.querySelector('tbody').appendChild(fragment)
   }
   else{
      console.log('llene algun campo');
   }

})

reniciar.addEventListener('click', e =>{
   e.preventDefault();
   datosBusqueda.reset();
   console.log('me diste clcik');
})


selectEstados.addEventListener('change', async e=>{
   let idEstado = e.target.value 
   try {
      let res = await axios.get('http://localhost:4000/municipios/'+ idEstado)
      console.log(res);
      let municipios = res.data;
      for ( let i = 0, opt = 1 ; i<municipios.length; i ++, opt++)
      {
       
         if(i == 0){
            selectMunicipios.options[i] = new Option('Seleccione un municipio', '0', true)
         }
         selectMunicipios.options[opt] = new Option(municipios[i].nombreMunicipio,municipios[i].idMunicipio)
      }
      selectMunicipios.options[0].disabled=true

   } catch (error) {
      console.log(error);
   }
   

})


speedscript.addEventListener('click',async e=>{
   e.preventDefault()
   let s = confirm('Esta seguro de realizar esta accion, esto podria demorar mas de una hora')
   if(s = true){
      try {
         await axios.post('http://localhost:4000/speedscript')
      } catch (error) {
         console.log(error);
      }
   }
})


dbVaciar.addEventListener('click', async e=>{
   e.preventDefault()
   let s = confirm('Esta seguro de realizar esta accion, esto borrara toda la informacion, para volver a obtener los datos sera necesarion usar el boton SpeedScript')
   if(s = true){
      try {
         await axios.delete('http://localhost:4000/vaciarbd')
      } catch (error) {
         console.log(error);
      }
   }
})


const getEstados = async() =>{
   try {
      let res = await axios.get('http://localhost:4000/estados')
      console.log(res.status);
      let estados = res.data
      
      for ( let i = 0, opt = 1 ; i<estados.length; i ++, opt++)
      {
         if(i == 0){
            selectEstados.options[i] = new Option('Seleccione un Estado', '0', true)
         }
         
         selectEstados.options[opt] = new Option(estados[i].NombreEstado,estados[i].idEstado)
      }
      selectEstados.options[0].disabled=true

   } catch (error) {
      
   }
}



document.addEventListener("DOMContentLoaded", getEstados);