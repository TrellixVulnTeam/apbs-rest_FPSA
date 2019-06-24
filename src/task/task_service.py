from __future__ import print_function
from flask import request, Blueprint

import time
from os import getenv
from requests import get, post
# import task_utils
from . import task_utils

task_app = Blueprint('task_app', __name__)

TMP_EXEC_HOST = getenv('TMP_EXEC_HOST', 'http://localhost:5005')
END_STATES = ['complete', 'error', None]

@task_app.route('/api/task/<job_id>/<task_name>', methods=['GET', 'POST'])
def task_action(job_id, task_name):
    response = None
    http_status = None

    # Acquire status of a task
    if request.method == 'GET':
        if task_name in ['apbs', 'pdb2pqr']:
            progress   = None
            run_state  = None
            start_time = None
            end_time   = None
            response   = {}
            wait_on_task = False

            if 'wait' in request.args.keys():
                if request.args['wait'].lower() == 'true':
                    # return {'args': request.args['wait']}
                    wait_on_task = True

            # NOTE: can later optimize to only get end_time if state isn't 'running'
            start_time  = task_utils.get_starttime(job_id, task_name)
            end_time    = task_utils.get_endtime(job_id, task_name)
            run_state, progress = task_utils.get_jobstatus_info(job_id, task_name)

            if run_state not in END_STATES and wait_on_task:
                while run_state not in END_STATES:
                    time.sleep(1)
                    run_state = task_utils.get_jobstatus_state(job_id, task_name)
                start_time  = task_utils.get_starttime(job_id, task_name)
                end_time    = task_utils.get_endtime(job_id, task_name)
                run_state, progress = task_utils.get_jobstatus_info(job_id, task_name)

            response['jobid'] = job_id
            if run_state is None:
                response['error'] = 'Task does not exist'
                
            response[task_name] = {
                'status':    run_state,
                'files':     progress[1:],
                'startTime': start_time,
                'endTime':   end_time
            }

            http_status = 200
            # return response, 200
        else:
            response = {
                'status': None,
                'error': f"task type '{task_name}' does not exist or is not implemented"
            }
            http_status = 404
            # return response, 404


    # Submit a task
    elif request.method == 'POST':
        available_tasks = ['apbs', 'pdb2pqr']
        http_status = 202

        if task_name not in available_tasks:
            http_status = 400
            response = { 
                'error': 'invalid task'
            }
        else:
            if task_name == 'apbs':
                pass
            elif task_name == 'pdb2pqr':
                # print('sending task')
                form = request.data
                # print(type(form))
                # print((form))
                post('%s/api/exec/%s/%s' % (TMP_EXEC_HOST, job_id, task_name), json=form)
                pass
                
                

            response = { 
                'accepted': f'task {task_name} accepted. Processing...'
            }
    # import pprint as pp
    # pp.pprint(response)
    return response, http_status