import json
eq_data=json.load(open('all_eqs.json'))
var_data={}
for eqkey in eq_data.keys():
    for variable in eq_data[eqkey]['variables']:
        if not variable in var_data.keys():
            var_data[variable]=[eq_data[eqkey]['eq']]
        else:
            var_data[variable].append(eq_data[eqkey]['eq'])
json.dump(var_data,open('reversed_eqs.json','w'))
print(var_data)