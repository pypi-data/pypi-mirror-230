# Librería sobre pokemon_stats

## Funcionalidades básicas

### 1. Método get_grupos_pokemon()
Devuelve el contenido de un archivo .csv cuya estructura es: Group_Name,Avg_Height,Avg_Weight. Dicho archivo se genera a partir del paquete pokemon_api_package del proyecto final.

### 2. Método get_altura_media_grupo(grupo)
Devuelve los valores de Group_Name y Avg_Height a partir de un valor string con el nombre de los grupos de pokemon.

### 3. Método get_peso_medio_grupo(grupo)
Devuelve los valores de Group_Name y Avg_Weight a partir de un valor string con el nombre de los grupos de pokemon.

### La forma de instalarlo es con:
pip install pokemon_stats

### Ejemplos de importación en proyecto cliente:
from pokemon_stats.pokemon_stats import get_grupos_pokemon, get_altura_media_grupo, get_peso_medio_grupo

### Ejemplo de uso en proyecto cliente:
print(get_grupos_pokemon()) 

print(get_altura_media_grupo(["dragon"]))

print(get_peso_medio_grupo(["dragon"]))


