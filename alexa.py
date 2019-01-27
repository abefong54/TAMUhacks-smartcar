import smartcar
from flask import Flask, redirect, request, jsonify
from flask_cors import CORS

def testing(carName, mileage):
    print("this works you son of a bitch!!")

    print(carName, mileage)