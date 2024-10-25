from flask import Flask, render_template, request, session, redirect, url_for
import funciones,mysql.connector,os
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()


app = Flask(__name__)
app.secret_key=os.getenv('KEY_FOR_APP')
DB_HOST =os.getenv('DB_HOST')
DB_USERNAME =os.getenv('DB_USERNAME')
DB_PASSWORD =os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')


# Connect to the database
connection = mysql.connector.connect(
    host=DB_HOST,
    user=DB_USERNAME,
    password=DB_PASSWORD,
    database=DB_NAME,
    autocommit=True,
           )
global cur
cur = connection.cursor() 

@app.route("/")
def login():    
    resultado=funciones.listado_paradas(cur)
    paradas=[]
    for paradax in resultado:
       paradas+=paradax                  
    return render_template('login.html',n_paradas=paradas)

@app.route("/new_data", methods=["POST"])
def new_data(): 
    global parada,cedula,password 
    parada = request.form['parada']
    cedula = request.form['cedula']
    password = request.form['clave']
    
    cur.execute(f"SELECT cedula FROM {parada} WHERE cedula = '{cedula}' ")
    result = cur.fetchone()
    if result != []:   
      cur.execute(f"SELECT password FROM tabla_index  WHERE nombre ='{parada}'" )
      ident=cur.fetchall() 
      for idx in ident:   
        if password == idx[0]:                                             
            fecha = datetime.strftime(datetime.now(),"%Y %m %d - %H:%M:%S")
            informacion=funciones.info_parada(cur,parada)
            cabecera=funciones.info_cabecera(cur,parada)
            miembros=funciones.lista_miembros(cur,parada)
            diario=funciones.diario_general(cur,parada)
            return render_template('info.html',informacion=informacion,cabecera=cabecera,fecha=fecha,miembros=miembros,diario=diario) 

@app.route('/aportes') 
def aportes():
    return render_template('login_a.html',parada=parada)

@app.route('/finanzas', methods=["GET", "POST"]) 
def finanzas(): 
    fecha = datetime.strftime(datetime.now(),"%Y %m %d - %H:%M:%S")
    diario=funciones.diario_general(parada)
    return render_template('finanzas.html',diario=diario,fecha=fecha,parada=parada)

@app.route('/direccion') 
def direccion(): 
    return render_template('direccion.html')

@app.route('/administrar') 
def administrar():
    return render_template('login_dir.html')

@app.route('/login_a', methods =['GET', 'POST'])
def login_a():
    msg = ''
    account=[]
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account=funciones.logge_a(parada,password)                                       
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            fecha = datetime.strftime(datetime.now(),"%Y %m %d - %H:%M:%S")  
            informacion=funciones.info_parada(parada) 
            miembros=funciones.lista_miembros(parada)
            datos=funciones.aportacion(parada) 
            cabecera=funciones.info_cabecera(parada)
            return render_template('usuario.html',informacion=informacion,miembros=miembros,datos=datos,cabecera=cabecera,fecha=fecha)
        else:
            msg = 'Incorrecto nombre de usuario / password !'
    return render_template('login_a.html', msg = msg)


@app.route('/login_dir', methods =['GET', 'POST'])
def login_dir():
    msg = ''
    account=[]
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        cur.execute(f"SELECT * FROM usuarios WHERE nombre ='{username}' AND password = '{password}'")
        accounts =cur.fetchall()
        for accountx in accounts:
          account +=accountx                                          
        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['username'] = account[1]
            fecha = datetime.strftime(datetime.now(),"%Y %m %d - %H:%M:%S")  
            return render_template('index.html',fecha=fecha)
        else:
            msg = 'Incorrecto nombre de usuario / password !'
    return render_template('login_dir.html', msg = msg)

@app.route('/logout')
def logout():
	session.pop('loggedin', None)
	session.pop('id', None)
	session.pop('username', None)
	return redirect(url_for('info'))



@app.route('/nueva_p') 
def nueva_p(): 
    return render_template('direccion.html')
                           
                           
@app.route('/editar_p') 
def editar_p(): 
    return render_template('direccion.html')                           
                           
@app.route('/n_miembro') 
def n_miembro(): 
    return render_template('direccion.html')
                           
                           
@app.route('/editar_miembro') 
def editar_miembro(): 
    return render_template('direccion.html') 
 



if __name__ == "__main__":
    app.run(debug=True,port=9500)