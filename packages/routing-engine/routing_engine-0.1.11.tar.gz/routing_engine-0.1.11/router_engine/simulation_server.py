from flask import Flask, request, jsonify
from waitress import serve
import connexion
import json
import threading
import asyncio
import time
from router_engine.helpers.classes import DotWrapper 
import gunicorn.app.base

router_inst = None

def not_found_error_handler(error ):
    return {"status" : 3 , "status_message" : "Invalid Request"} , 400


class StandaloneApplication(gunicorn.app.base.BaseApplication):

    def __init__(self, app, options=None):
        self.options = options or {}
        self.application = app
        super().__init__()

    def load_config(self):
        config = {key: value for key, value in self.options.items() if key in self.cfg.settings and value is not None}
        for key, value in config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application

class simServerClass:
    port = 5030
    app = connexion.App(__name__)
    app.add_error_handler(404 , not_found_error_handler)
    router_instance = None



    def __init__(self,port,router_instance):
        self.port = port
        self.router_instance = router_instance
        global router_inst
        router_inst = router_instance

    def run_simulation_server(self):
        t = threading.Thread(target=self.run_server)
        t.start()


    @app.route('/simulate', methods=['POST'])
    def simulate():
        global router_inst
        request_data = request.json
        context = request_data['context']
        # print(f"context: {context}")
        context_dn = DotWrapper(context)
        # print(f"person_name: {context_dn.person.name}")
        # print(f"context_dn: {context_dn}")

        simulate_result = router_inst.simulate_rules_outcome(context_dn)
        # print(f"simulate_result: {simulate_result}")
        response = {"request":request_data,"results":simulate_result}
        return json.dumps(response)



    def run_server(self):
        print("Starting Simulation Server......")
        serve(self.app, host='0.0.0.0', port=self.port)
        # options = {
        # 'bind': '%s:%s' % ('0.0.0.0', self.port),
        # # 'workers': 1,
        #  }
        # StandaloneApplication(self.app, options).run()
        # self.app.run(host='0.0.0.0', port=self.port)