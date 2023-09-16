import pandas as pd

class PokemonDataAnalyzer:
    def __init__(self, csv_file):
        self.df = pd.read_csv(csv_file)

    def get_grupos_pokemon(self):
        try:
            grupos = self.df
            return grupos
        except Exception as e:
            print("Error in get_grupos_pokemon:", str(e))
            return []

    def get_altura_media_grupo(self, grupo):
        try:
            grupos = self.get_grupos_pokemon()
            
            unique_group_names = grupos["Group_Name"].unique()
            
            if grupo.lower() in [g.lower() for g in unique_group_names]:
                grupo_df = grupos[grupos["Group_Name"].str.lower() == grupo.lower()]
                
                grupo_df = grupo_df[["Group_Name", "Avg_Height"]]
                
                return grupo_df
            else:
                return None
        except Exception as e:
            print("Error in get_altura_media_grupo:", str(e))
            return None

    def get_peso_medio_grupo(self, grupo):
        try:
            grupos = self.get_grupos_pokemon()
            
            unique_group_names = grupos["Group_Name"].unique()
            
            if grupo.lower() in [g.lower() for g in unique_group_names]:
                grupo_df = grupos[grupos["Group_Name"].str.lower() == grupo.lower()]
                
                grupo_df = grupo_df[["Group_Name", "Avg_Weight"]]
                
                return grupo_df
            else:
                return None
        except Exception as e:
            print("Error in get_peso_medio_grupo:", str(e))
            return None

if __name__ == "__main__":
    csv_file = "C:/Users/angel/OneDrive/Escritorio/Curso Python/Ejercicios/Tema 16/pokemon/pokemon_api_package/pokemon_api/estadisticas_grupo.csv"
    analyzer = PokemonDataAnalyzer(csv_file)
    grupos_pokemon = analyzer.get_grupos_pokemon()
    print("All Pokemon Groups:")
    print(grupos_pokemon)
    
    altura_media_result = analyzer.get_altura_media_grupo("Dragon")
    print("Altura Media para el Grupo Dragon:")
    print(altura_media_result)
    
    peso_medio_result = analyzer.get_peso_medio_grupo("Dragon")
    print("Peso Medio para el Grupo Dragon:")
    print(peso_medio_result)
