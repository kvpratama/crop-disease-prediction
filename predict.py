from gradio_client import Client
client = Client("https://kvpratama-plant-disease.hf.space/--replicas/6d874/")
result = client.predict('./test/test/AppleCedarRust2.JPG', api_name="/predict")
print(result)
