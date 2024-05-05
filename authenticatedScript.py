import sys
import time

from gvm.connections import UnixSocketConnection
from gvm.errors import GvmError
from gvm.protocols.gmp import Gmp
from gvm.transforms import EtreeCheckCommandTransform

from lxml.etree import tostring

def check_scan_status(gmp, scan_id):
    response = gmp.get_task(task_id=scan_id)
    task = response.find('task')
    status = task.find('status').text
    return status

def get_target_id(gmp):
    targets = gmp.get_targets()
    for target in targets.xpath('target'):
        if target.find('hosts').text == '192.168.178.102': # Adapt IP address if necessary
            return target.get('id')

def get_config_id(gmp):
    configs = gmp.get_scan_configs(filter_string='name=Full and fast Port')
    for config in configs.xpath('config'):
        if config.find('name').text == 'Full and fast Port':
            return config.get('id')

def get_scanner_id(gmp):
    scanners = gmp.get_scanners(filter_string='name=OpenVAS Default')
    for scanner in scanners.xpath('scanner'):
        if scanner.find('name').text == 'OpenVAS Default':
            return scanner.get('id')

def main():

    # We need a name for the output to uniquely identify the file afterwards
    name = sys.argv[1]
    path = '/run/gvmd/gvmd.sock'
    connection = UnixSocketConnection(path=path)
    transform = EtreeCheckCommandTransform()

    # TODO: Encrypt credentials
    username = 'admin'
    password = 'admin'

    try:
        tasks = []

        with Gmp(connection=connection, transform=transform) as gmp:
            gmp.authenticate(username, password)

            # Find targets and the right target
            # TODO: Automatically create this target if system is newly set up
            target_id = get_target_id(gmp)

            # Get all tasks
            tasks = gmp.get_tasks()

            # Filter tasks based on target_id
            filtered_tasks = [task for task in tasks.xpath('task') if task.find('target').get('id') == target_id]

            # Count the number of tasks for the target
            task_count = len(filtered_tasks)

            # Create the name for the new task, in ascending order
            task_name = f'Automated Scan {task_count + 1}'

            # Get config for Task
            # TODO: Automatically create this config if system is newly set up

            config_id = get_config_id(gmp)

            scanner_id = get_scanner_id(gmp)

            # Create new Task for Target
            task = gmp.create_task(task_name, config_id, target_id, scanner_id)
            task_id = task.get('id')
            print('Created Task:')
            print(task_id)

            # Start task
            gmp.start_task(task_id)

            # TODO Next: Automatically forward the report to the host using Alerts either with SSH or TCP - Is there something already done by Clouditor?
            # Or, using the already existing SSH connection when executing the script, we can send the report to the host 
            # 5057e5cc-b825-11e4-9d0e-28d24461215b
            formats = gmp.get_report_formats()
            for format in formats.xpath('report_format'):
                if format.find('name').text == 'Anonymous XML':
                    report_format_id = format.get('id')

            wantedReport = None
            
            while wantedReport == None:
                status = check_scan_status(gmp, task_id)
                print(f"Current scan status: {status}")
                if status == 'Done':
                    reports = gmp.get_reports(ignore_pagination=True, details=True)
                    for report in reports.xpath('report'):
                        potentialTask = report.find('task')
                        if report.find('task').get('id') == task_id: # if potentialTask.find('name').text == 'CLI Scan':
                            wantedReport = report
                            print('Report found:')
                            print(wantedReport)
                else:
                    time.sleep(60)

            # Alternative solution is to save the file locally in a shared folder and let the host take it out
            # Convert the Element to a string
            # xml_string = etree.tostring(wantedReport, pretty_print=True, encoding='UTF-8').decode('UTF-8')
            xml_string = tostring(wantedReport)
            # Choose a file name for your XML file
            file_name = f'/tmp/{name}'

            # Write the XML string to a file
            with open(file_name, 'wb') as file:
                file.write(xml_string)


    except GvmError as e:
        print('An error occurred', e, file=sys.stderr)



if __name__ == '__main__':
    main()