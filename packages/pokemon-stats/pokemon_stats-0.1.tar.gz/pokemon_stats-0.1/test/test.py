import unittest
import pandas as pd
from pokemon_stats_package.pokemon_stats.pokemon_stats import PokemonDataAnalyzer
class TestPokemonDataAnalyzer(unittest.TestCase):
    def setUp(self):
        self.csv_file = "C:/Users/angel/OneDrive/Escritorio/Curso Python/Ejercicios/Tema 16/pokemon/pokemon_api_package/pokemon_api/estadisticas_grupo.csv"
        self.analyzer = PokemonDataAnalyzer(self.csv_file)

    def test_get_grupos_pokemon(self):
        grupos_pokemon = self.analyzer.get_grupos_pokemon()
        self.assertIsInstance(grupos_pokemon, pd.DataFrame)
        self.assertFalse(grupos_pokemon.empty)

    def test_get_altura_media_grupo_existing(self):
        grupo = "Dragon"
        altura_media_result = self.analyzer.get_altura_media_grupo(grupo)
        self.assertIsInstance(altura_media_result, pd.DataFrame)
        self.assertFalse(altura_media_result.empty)
        self.assertEqual(altura_media_result.iloc[0]['Group_Name'].lower(), grupo.lower())

    def test_get_altura_media_grupo_non_existing(self):
        grupo = "NonExistentGroup"
        altura_media_result = self.analyzer.get_altura_media_grupo(grupo)
        self.assertIsNone(altura_media_result)

    def test_get_peso_medio_grupo_existing(self):
        grupo = "Dragon"
        peso_medio_result = self.analyzer.get_peso_medio_grupo(grupo)
        self.assertIsInstance(peso_medio_result, pd.DataFrame)
        self.assertFalse(peso_medio_result.empty)
        self.assertEqual(peso_medio_result.iloc[0]['Group_Name'].lower(), grupo.lower())

    def test_get_peso_medio_grupo_non_existing(self):
        grupo = "NonExistentGroup"
        peso_medio_result = self.analyzer.get_peso_medio_grupo(grupo)
        self.assertIsNone(peso_medio_result)

if __name__ == "__main__":
    unittest.main()
