#coding=utf-8

from apps import app
from flask import render_template, request, redirect,jsonify
from io import BytesIO
import json
import time
import sys
import os
import requests
import re

sys.path.append(os.path.dirname(__file__))
import subprocess
import gm_helper
import scripts.excel_helper
import scripts.svn_helper
import scripts.ftp_helper

app.config["JSON_AS_ASCII"] = False

#主界面
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

#gm page
@app.route('/gm')
def gm():
	return render_template('gm.html')

#excel check page
@app.route('/check')
def check():
    return render_template('check.html')

@app.route('/bashtool')
def bashtool():
    return render_template('bashtool.html')

@app.route('/svnlog')
def svnlog():
    return render_template('svnlog.html')

@app.route('/upload')
def upload():

    return render_template('upload.html')


#gm request
@app.route('/get-gm', methods=['GET'])
def get_gm():
    data = gm_helper.format_gm_list()
    return to_json(data)

#gm svn up
@app.route('/update_svn', methods=['GET'])
def update_svn():
    '''
    try:
        # '/root/myproject/game-flask-server/apps/svn_gm_folder/debug'
        result = subprocess.run(['svn', 'update', './apps/svn_gm_folder/debug'], capture_output=True, text=True)
        if result.returncode == 0:
            return jsonify({'message': 'SVN updated successfully', 'output': result.stdout}), 200
        else:
            return jsonify({'message': 'Error updating SVN', 'output': result.stderr}), 500
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500
    '''
    cmd = 'svn up ./apps/svn_gm_folder/debug'
    execute_bash(cmd)

#excel checklog request
@app.route('/get-checklog', methods=['GET'])
def get_checklog():
    cmd = 'svn up /root/platform/doc/excel'
    execute_bash(cmd)
    try:
        res = scripts.excel_helper.main('check')
        return to_json(res)
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500


@app.route('/get-searchlog', methods=['POST'])
def get_searchlog():
    data = request.json
    cmd = 'svn up /root/platform/doc/excel'
    execute_bash(cmd)
    try:
        res = scripts.excel_helper.main('search', data["data"])
        return to_json(res)
    except Exception as e:
        return jsonify({'message': 'An error occurred', 'error': str(e)}), 500

@app.route('/get-checkrule', methods=['GET'])
def show_excel_check_rule():
    res = scripts.excel_helper.read_json_config()
    return to_json(res)
    

@app.route('/get-svnlog', methods=['GET'])
def get_svnlog():
    res = scripts.svn_helper.get_svn_info()
    return to_json(res)

'''
@app.route('/file-upload', methods=['POST'])
def file_upload():
    if 'file' not in request.files:
        return jsonify({"error": "没有文件上传"}), 400

    file = request.files['file']
    print(file)
    if file.filename == '':
        return jsonify({"error": "文件名不能为空"}), 400
    if file:
        UPLOAD_FOLDER = "./apps/package"
        file.save(os.path.join(UPLOAD_FOLDER, file.filename))
        return jsonify({"message": "文件上传成功", "filename": file.filename}), 200
    else:
        return jsonify({"error": "不允许的文件类型"}), 400
'''

@app.route('/file-to-ftp', methods=['POST'])
def file_to_ftp():
    file_name = request.json['data']
    #scripts.ftp_helper.get_res_version()
    '''
    scripts.ftp_helper.download_pkg_by_name(file_name)
    #time.sleep(5)
    upload_result, msg = scripts.ftp_helper.upload_file_to_ftp(file_name, file_name)
    #scripts.ftp_helper.delete_download_file_by_name(file_name)
    
    if upload_result:
        res =to_json(f"{file_name}")
        return res
    else:
        res =to_json(msg)
        return res
    '''
    msg = scripts.ftp_helper.create_package_name(file_name)
    res =to_json(msg)
    return res

@app.route('/download-namelist', methods=['GET'])
def get_pkg_list():
    file_name_list = scripts.ftp_helper.get_pkg_name_list()
    return to_json(file_name_list)

def execute_bash(bash_cmd):
    result = subprocess.run(bash_cmd, capture_output=True, text=True,shell=True,)
    
    if result.returncode != 0:
        print("Error executing script:")
        print(result.stderr)
        return result.stderr
    print(result.stdout)
    return result.stdout

#data 2 json
def to_json(data):
    dict = {}
    dict['data'] = data
    data_json = json.dumps(dict)
    return data_json