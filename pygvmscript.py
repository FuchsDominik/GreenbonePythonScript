from gvm.connections import UnixSocketConnection
from gvm.protocols.gmp import Gmp

# path = '/tmp/gvm/gvmd/gvmd.sock' - Location of the maacos sock location
path = '/run/gvmd/gvmd.sock' # Location of the linux sock location

connection = UnixSocketConnection(path=path)

# using the with statement to automatically connect and disconnect to gvmd
with Gmp(connection=connection) as gmp:
    # get the response message returned as a utf-8 encoded string
    response = gmp.get_targets()

    # print the response message
    print('Targets: ')
    print(response)

    response = gmp.get_tasks()

    print('Tasks: ')
    print(response)