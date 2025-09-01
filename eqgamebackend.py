from flask import Flask, jsonify
from flask import request
from markupsafe import escape
from latex2sympy2_extended import latex2sympy
import re
import json
from sympy import solve
from flask_cors import CORS
from datetime import datetime, timezone

eq_data=json.load(open('all_eqs.json'))
reversed_eq_data=json.load(open('reversed_eqs.json'))
game_list_data=json.load(open('gameList.json'))
app = Flask(__name__)
CORS(app)
symbols = [
    'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
    'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'rho',
    'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega', 'Phi'
]
valid_characters='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
@app.route("/evaluate_expression", methods=["PUT", 'OPTIONS'])
def evaluate_expression_is_valid():
    if request.method == 'OPTIONS':
        # This handles the CORS preflight request
        return '', 204 # Use 204 No Content for a successful preflight
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        print(f"Raw request data: {request.data}")
        return jsonify({"error": "Malformed JSON"}), 400
    latex_expression=data.get('latex')
    meanings=data.get('meanings')
    prev_vars=data.get('prev_vars')
    preveq=data.get("preveq")
    
    try:
       sympyeq= latex2sympy(latex_expression)
    except:
        return jsonify({"result": False, "meaning": []})
    all_vars=search_for_all_vars(latex_expression)
    print(all_vars)
    print(prev_vars)
    if(len(all_vars)==0):
        return jsonify({"result": False, "meaning": []})
    for v in all_vars:
        if(v in prev_vars):
            transition_var=v
            break
    if(prev_vars==[]):
        transition_var=all_vars[0]
    if(transition_var==None):
        return jsonify({"result": False, "meaning": []})
    print(transition_var)
    space=reversed_eq_data[all_vars[0]]
    print(space)
    if(len(space)==0):
        return jsonify({"result": False, "meaning": []})
    for equ in space:
        eq=eq_data[equ]
        brk=False
        for meaning in meanings:
            if meaning in eq['meanings']:
                brk=True
                break
        if(brk):
            continue
        converted=latex2sympy(equ)
        print(eq)
        print(equ)
        print(converted)
        print(all_vars[0])
        print(sympyeq)
        print(list(sympyeq.free_symbols))
        try:
            # print(solve(latex2sympy(equ), list(sympyeq.free_symbols)[0]))
            # print(solve(sympyeq, list(sympyeq.free_symbols)[0]))
            for c in list(converted.free_symbols):
                if(c not in list(sympyeq.free_symbols)):
                    brk=True
                    break
            if(brk):
                continue
            if((solve(converted, list(sympyeq.free_symbols)[0])==solve(sympyeq, list(sympyeq.free_symbols)[0]))or (solve(converted, list(sympyeq.free_symbols)[1])==solve(sympyeq, list(sympyeq.free_symbols)[1]))):
                return jsonify({"result": True, "meaning1": eq['meanings'][eq['variables'].index(transition_var)], "meaning2": preveq['meanings'][preveq['variables'].index(transition_var)] if preveq!={} else "", "vars": all_vars, "eq": eq})
        except:
            pass
    return jsonify({"result": False, "meaning": []})
@app.route("/get_today_equations", methods=["GET", 'OPTIONS'])
def get_todays_equations():
    if request.method == 'OPTIONS':
        return '', 204
    datestr=str(datetime.now(timezone.utc).date())
    return jsonify(game_list_data[datestr])


def search_for_all_vars(latex_expression):
    varsymbols=[]
    LE=latex_expression
    print(LE)
    vars=re.findall(r'\\[a-zA-Z]*', latex_expression)
    # (_[a-zA-Z0-9]|_{.*})*
    for var in vars:
        print(var)
        v=var[1:]
        if('_' in var):
            v='_'.split(var)[0]
        if(v in symbols):
            varsymbols.append(var)
        LE=LE.replace(var, '')
    # vars2=re.findall('[a-zA-Z]*(_[a-zA-Z0-9]|_{.*})', latex_expression)
    # for var in vars2:
    #     v=var[2:]
    #     if('_' in var):
    #         v='_'.split(var)[0]
    #     if(v in symbols):
    #         varsymbols.append(var)
    #     LE=latex_expression.replace(var, '')
    for character in LE:
        if character in valid_characters:
            varsymbols.append(character)
    return varsymbols
    


        



