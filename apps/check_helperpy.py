#coding=utf-8
import os

def get_log():
    with open('example.txt', 'r') as file:
        content = file.read()
        print(content)
    return content