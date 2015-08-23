import os
from flask import Flask
from server import application

def main():
	application.debug = True
	application.run()
	
if __name__ == '__main__':
	main()