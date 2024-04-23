import sys

from gvm.connections import UnixSocketConnection
from gvm.errors import GvmError
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeCheckCommandTransform

path = '/run/gvmd/gvmd.sock'
connection = UnixSocketConnection(path=path)
transform = EtreeCheckCommandTransform()

username = 'admin'
password = 'admin'

try:
    tasks = []

    with Gmp(connection=connection, transform=transform) as gmp:
        gmp.authenticate(username, password)

        # Find targets and the right target
        # TODO: Automatically create this target if system is newly set up
        print('Targets:')
        targets = gmp.get_targets()

        for target in targets.xpath('target'):
            if target.find('hosts').text == '10.33.168.54':
                target_id = target.get('id')
            print(target.get('id'))
            print(target.find('name').text)

        # print('Tasks:')
        # tasks = gmp.get_tasks(f'task_id={target_id}')

        # for task in tasks.xpath('task'):
        #     print(task.get('id'))
        #     print(task.find('name').text)
        # Get all tasks
        tasks = gmp.get_tasks()

        # Filter tasks based on target_id
        filtered_tasks = [task for task in tasks.xpath('task') if task.find('target').get('id') == target_id]

        # Count the number of tasks for the target
        task_count = len(filtered_tasks)

        # Now, when creating a new task, you can use this count to append an ascending number to the task name
        task_name = f'Automated Scan {task_count + 1}'

        # Get config for Task
        # TODO: Automatically create this config if system is newly set up
        config = gmp.get_scan_config('7d96db3e-546d-43a0-aaa9-3db73271e94c') # scan config for Full and fast Port

        # Create new Task for Target
        task = gmp.create_task(task_name, config.get('id'), target_id)
        print(task)
        print(task.get('status_text').text)

except GvmError as e:
    print('An error occurred', e, file=sys.stderr)