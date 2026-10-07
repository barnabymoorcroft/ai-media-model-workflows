import json,pathlib,unittest
class T(unittest.TestCase):
 def test_sources(self):
  d=json.loads(pathlib.Path("catalog/models.json").read_text())
  self.assertTrue(all(x["source"].startswith("http") for x in d["models"]))
if __name__=="__main__":unittest.main()
