
import streamlit as st
import pandas as pd
from google.cloud import firestore
from google.oauth2 import service_account
import firebase_admin
from firebase_admin import credentials, firestore
import json

# credenciales para pruebas
if not firebase_admin._apps:
    path = "/content/survey_streamlit_production/"
    cred = credentials.Certificate(path + "names-firebase.json")
    firebase_admin.initialize_app(cred)
db = firestore.Client()

# key_dict = json.loads(st.secrets["textkey"])
# creds = service_account.Credentials.from_service_account_info(key_dict)
# db = firestore.Client(credentials=creds, project="names-project-demo")

dbNames = db.collection("names")
st.header("Nuevo registro")

index = st.text_input("index")
name = st.text_input("Name")
sex = st.selectbox(
    "Select Sex",
    ("F", "M", "Other")
)

submit = st.button("Crear nuevo registro")

# Una vez que el nombre es enviado, subir a la base de datos

if index and name and sex and submit:
  doc_ref = db.collection("names").document(name)
  doc_ref.set({
      "index": index,
      "name": name,
      "sex": sex
  })

sidebar = st.sidebar

sidebar.write("Registro insertado correctamente")

def loadByName(name):
  names_ref = dbNames.where(u"name", u"==", name)
  currentName = None
  for myname in names_ref.stream():
    currentName = myname
  return currentName

sidebar.subheader("Buscar nombre")
nameSearch = sidebar.text_input("nombre")
btnFiltrar = sidebar.button("Buscar")

if btnFiltrar:
  doc = loadByName(nameSearch)
  if doc is None:
    sidebar.write("El nombre no existe")
  else:
    sidebar.write(doc.to_dict())

sidebar.markdown("""---""")

btnEliminar = sidebar.button("Eliminar")

if btnEliminar:
  deletename = loadByName(nameSearch)
  if deletename is None:
    sidebar.write(f"{nameSearch} no existe")
  else:
    dbNames.document(deletename.id).delete()
    sidebar.write(f("{nameSearch} eliminado"))

sidebar.markdown("""---""")
newname = sidebar.text_input("Actualizar nombre")
btnActualizar = sidebar.button("Actualizar")

if btnActualizar: 
  updatename = loadByName(nameSearch)
  if updatename is None:
    st.write(f"{nameSearch} no existe")
  else:
    myupdatename = dbNames.document(updatename.id)
    myupdatename(
        {
            "name":newname
        }
    )
names_ref = list(db.collection(u'names').stream())
names_dict = list(map(lambda x: x.to_dict(), names_ref))
names_dataframe = pd.DataFrame(names_dict)
st.dataframe(names_dataframe)
