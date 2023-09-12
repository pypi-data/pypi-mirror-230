import os
import sys

# current_directory = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.join(current_directory, '../..'))
# print()

import sensenova

id = "nova-ptc-xs-v1"
print(sensenova.Model.list())
# print(sensenova.Model.retrieve(id=id))
print(sensenova.Model.delete(sid=id))
# print(sensenova.Model.list())
