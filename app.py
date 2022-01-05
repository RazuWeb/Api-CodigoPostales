from os import execl, name, path
from MySQLdb.cursors import Cursor
from flask import  Flask, json, jsonify, render_template, request, Response
import flask
from flask_mysqldb import MySQL
from config import config
from flask_httpauth import HTTPBasicAuth

import pandas as pd
import xlrd
import re


app = Flask(__name__)  
auth = HTTPBasicAuth()

""" app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'pruebaBackEnd'
app.config['MYSQL_PORT'] = '3306' """

mysql = MySQL(app)

path = 'cPdescarga.xls'


@auth.verify_password
def authenticate(username, password):
    if username and password:
        if username == 'sam' and password == 'sam':
            return True
        else:
            return False

    return False

@app.route('/', methods=['GET'])
def Index():
    return render_template('index.html')

@app.route('/estados', methods=['GET'])
@auth.login_required
def Estados():
    cur = mysql.connection.cursor()
    sql = "SELECT estados.idEstado, estados.nombreEstado FROM estados"
    cur.execute(sql)
    mysql.connection.commit()
    datos = cur.fetchall()
    payload = []
    content = {}
    for r in datos:
        rSinGuiones = re.sub("\_"," ", r[1])
        content = {'idEstado':r[0], 'NombreEstado': rSinGuiones}
        payload.append(content) 
    return jsonify(payload)



   

@app.route('/municipios/<idEstado>', methods=['GET'])
@auth.login_required
def getMunicipios(idEstado):
    cur = mysql.connection.cursor()
    sql = "SELECT municipios.idMunicipio, municipios.nombreMunicipio FROM municipios WHERE municipios.idEstadoFK = {0}".format(idEstado)
    cur.execute(sql)
    mysql.connection.commit()
    datos = cur.fetchall()
    payload = []
    content = {}
    for r in datos:
        content = {'idMunicipio':r[0], 'nombreMunicipio': r[1]}
        payload.append(content) 
    return jsonify(payload) 



@app.route('/datosPostales/<tipo>/<dato>', methods=['GET'])
@auth.login_required
def getCP(tipo, dato):
    print(tipo + '|' + dato)
    if tipo == '1':
        sql = "SELECT colonias.CP,colonias.nombreColonia, municipios.nombreMunicipio, estados.nombreEstado FROM   municipios,colonias,estados WHERE estados.idEstado = municipios.idEstadoFK AND   municipios.idMunicipio = colonias.idMunicipioFK AND colonias.CP= '{0}'".format(dato)
    elif tipo == '2':
        sql = "SELECT colonias.CP,colonias.nombreColonia, municipios.nombreMunicipio, estados.nombreEstado FROM   municipios,colonias,estados WHERE estados.idEstado = municipios.idEstadoFK AND   municipios.idMunicipio = colonias.idMunicipioFK AND colonias.nombreColonia LIKE '%{0}%'".format(dato)
    elif tipo == '3':
        sql = "SELECT colonias.CP,colonias.nombreColonia, municipios.nombreMunicipio, estados.nombreEstado FROM municipios,colonias,estados WHERE estados.idEstado = municipios.idEstadoFK AND municipios.idMunicipio = colonias.idMunicipioFK AND municipios.idMunicipio = {0}".format(dato)
    elif tipo == '4':
        sql = "SELECT colonias.CP,colonias.nombreColonia, municipios.nombreMunicipio, estados.nombreEstado FROM municipios,colonias,estados WHERE estados.idEstado = municipios.idEstadoFK AND municipios.idMunicipio = colonias.idMunicipioFK AND estados.idEstado = {0}".format(dato)
    
    try:
        cur = mysql.connection.cursor()
        cur.execute(sql)
        mysql.connection.commit()
        datos = cur.fetchall()
        payload = []
        content = {}
        if datos != None:
            for r in datos:
               
                content = {'CP':r[0], 'Colonia': r[1], 'Municipio':r[2], 'Estado':re.sub("\_"," ", r[3])}
                payload.append(content)
                
            
        return jsonify(payload)
    except Exception as ex:
        return jsonify({'message': 'Error'})






@app.route('/speedscript', methods=['POST'])
@auth.login_required
def SpeedScript():
    if request.method == 'POST':
        exelData = pd.ExcelFile(path)
        exelDataEstados = exelData.sheet_names
        
        """ print(exelData.parse(sheet_name='Aguascalientes')["d_asenta"]) """

        for i in exelDataEstados:  
            print(i)    
            """ df = pd.read_excel(path, sheet_name=i) """   
            lastid  = 0
            if i != 'Nota':
                cur = mysql.connection.cursor()
                sql = "INSERT INTO estados (nombreEstado) VALUES ('{0}')".format(i)
                cur.execute(sql)
                mysql.connection.commit()
                lastid = cur.lastrowid
                
                
            
            if i != 'Nota' and lastid != 0:
                municipios = exelData.parse(sheet_name=i)["D_mnpio"]
                colonias = exelData.parse(sheet_name=i)["d_asenta"]
                cps = exelData.parse(sheet_name=i)["d_codigo"]
                conjunto = set(municipios)
                municipiosLista = list(conjunto)
                for  municipioLista in  municipiosLista:
                    cur = mysql.connection.cursor()
                    sql = "INSERT INTO municipios (idEstadoFK,nombreMunicipio) VALUES ({0},'{1}')".format(lastid,municipioLista)
                    cur.execute(sql)
                    mysql.connection.commit()
                    lastidM = cur.lastrowid

                    for indice, colonia in enumerate(colonias):           
                        if municipios[indice] == municipioLista:
                            cur = mysql.connection.cursor()
                            sql = "INSERT INTO colonias (idMunicipioFK,nombreColonia,CP) VALUES ({0},'{1}','{2}')".format(lastidM,colonia,cps[indice])
                            cur.execute(sql)
                            mysql.connection.commit()
                
          
                    
    return render_template('index.html')        

@app.route('/vaciarbd', methods=['DELETE'])
def vaciarDB():
    cur = mysql.connection.cursor()
    sql = "TRUNCATE TABLE colonias;"
    cur.execute(sql)
    mysql.connection.commit()


    sql2 = "TRUNCATE TABLE municipios;"
    cur.execute(sql2)
    mysql.connection.commit()

    sql3 = "TRUNCATE TABLE estados;"
    cur.execute(sql3)
    mysql.connection.commit()

    return render_template('index.html')  

if __name__ == '__main__':
    app.config.from_object(config['development'])
    app.run(port=4000)