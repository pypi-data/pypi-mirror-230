
import datetime
import logging
import random
from traceback import format_exception, format_tb
from typing import List,Callable
import requests
import hashlib
import sys
import asyncio
from dataclasses import dataclass
from threading import Lock, Thread,Event
from PIL import Image
import numpy as np
from queue import SimpleQueue
import io
from contextlib import contextmanager
import time
from hashlib import sha256
from secrets import token_hex
from collections import deque
import atexit
import uuid
from supabase import create_client,Client
import websocket
import json




class CollieWatchButton:
    def __init__(self,button_text,callback_func) -> None:
        self.__button_text = button_text
        self.__callback_func = callback_func

class InternalCollieWatchQueuedTask:
    def __init__(self,function,extra_functions: list,args:tuple) -> None:
        self._function = function
        self._extra_functions = extra_functions
        self._args = args
        
    def evaluate(self):
        self._function(*self._args)




class CollieWatch:
    __text_received_callback = lambda x: x
    __callbacks_map = {}
    __supabase: Client = None
    __socket: websocket.WebSocket = None
    __dashboard_lock = Lock()
    __background_thread: Thread()
    __current_dashboard: dict = {}

    @staticmethod
    def has_initialized():
        return CollieWatch.__socket != None
    
    @staticmethod
    def create_block(block_name):
        if "blocks" not in CollieWatch.__current_dashboard:
            CollieWatch.__current_dashboard["blocks"] = {}
        CollieWatch.__current_dashboard["blocks"][block_name] = {}
    
    @staticmethod
    def __background_thread_handler():
        while True:
            CollieWatch.__socket.send(json.dumps(CollieWatch.__current_dashboard))
            time.sleep(1)
        
    @staticmethod
    def initialize(token):
        CollieWatch.__supabase = create_client("https://acyzjlibhoowdqjrdmwu.supabase.co","eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImFjeXpqbGliaG9vd2RxanJkbXd1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTMyNTI2MDgsImV4cCI6MjAwODgyODYwOH0.cSP7MaxuIZUknfp-_9srZyiOmQwokEdDXlyo4mci_S8")
        try:
            data,count = CollieWatch.__supabase.from_("dashboards").select("*").eq("dashboard_token",token).execute()
            user_found = len(data[1]) != 0
            if not user_found:
                print(f'Could not find any dashboards with token "{token}".\nPlease provide a valid dashboard token!')
                return False
            CollieWatch.__socket = websocket.create_connection("wss://seal-app-isidc.ondigitalocean.app/",header=["type: program"],subprotocols=[token])

            CollieWatch._background_thread = Thread(target=CollieWatch.__background_thread_handler,daemon=True)
            CollieWatch._background_thread.start()
            
            return user_found
        except:
            return False

    
    @staticmethod
    def __check_if_block_exists(block_id):
        if "blocks" not in CollieWatch.__current_dashboard:
            return False
        if block_id not in CollieWatch.__current_dashboard["blocks"]:
            return False
        return True

    

    @staticmethod
    def set_text_on_block(block_id: str,message: str):
        if not CollieWatch.has_initialized():
            print("Please make sure to initialize CollieWatch before calling any of the send methods!")
            return False
        if not CollieWatch.__check_if_block_exists(block_id):
            print(f'Block with id "{block_id}" does not exist!')
            return False
        with CollieWatch.__dashboard_lock:
            CollieWatch.__current_dashboard["blocks"][block_id]["type"] = "text"
            CollieWatch.__current_dashboard["blocks"][block_id]["data"] = message
        
    
    
    @staticmethod
    def delete_block(block_id: str):
        if not CollieWatch.has_initialized():
            print("Please make sure to initialize CollieWatch before calling any of the send methods!")
            return False
        if not CollieWatch.__check_if_block_exists(block_id):
            print(f'Block with id "{block_id}" does not exist!')
            return False
        with CollieWatch.__dashboard_lock:
            del CollieWatch.__current_dashboard["blocks"][block_id]
        

    
    




    