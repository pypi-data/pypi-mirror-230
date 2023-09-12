import os
import sys
import json
import yaml
import tempfile
import requests
import posixpath
import contextlib

from typing import Dict, Optional, Any

from .entities import experiment, run
from .error.value_error import HaiqvValueError
from .utils.common import get_millis, key_subset_split
from .utils.files import guess_mime_type


# Experiment
def get_experiment(exp_name=None, client_ip=None) -> experiment.Experiment:
    assert exp_name, 'init need experiment name'

    exp = requests.get(
        f'{os.environ.get("_HAIQV_BASE_URL")}/get-experiment-via-name',
        params={'experiment_name': exp_name, 'client_ip': client_ip}
    )

    if exp.status_code == 200:
        return experiment.Experiment(**exp.json()['experiment'])
    else:
        raise HaiqvValueError(exp.json())


def create_experiment(exp_name, desc: str = None, tags: Optional[Dict[str, Any]] = None,
                      client_ip=None) -> experiment.Experiment:
    if desc:
        if tags:
            tags['mlflow.note.content'] = desc
        else:
            tags = {'mlflow.note.content': desc}

    if tags:
        exp_tags = [{'key': k, 'value': str(v)} for k, v in tags.items()]

    exp_data = {
        'name': exp_name,
        'description': desc,
        'tags': exp_tags if tags else tags,
        'client_ip': client_ip
    }

    exp = requests.post(
        f'{os.environ.get("_HAIQV_BASE_URL")}/create-experiment-via-name',
        data=json.dumps(exp_data),
        headers={'Content-Type': 'application/json'}
    )

    if exp.status_code == 200:
        return experiment.Experiment(**exp.json()['experiment'])
    else:
        raise HaiqvValueError(exp.json())


# Run
def create_run(exp_id: str, run_name: str, desc: str = None,
               tags: Optional[Dict[str, Any]] = None, client_ip=None) -> run.Run:
    if desc:
        if tags:
            tags['mlflow.note.content'] = desc
        else:
            tags = {'mlflow.note.content': desc}

    if tags:
        run_tags = [{'key': k, 'value': str(v)} for k, v in tags.items()]

    data = {
        'experiment_id': exp_id,
        'run_name': run_name,
        'tags': run_tags if tags else tags,
        'client_ip': client_ip
    }

    runs = requests.post(f'{os.environ.get("_HAIQV_BASE_URL")}/create-run',
                         data=json.dumps(data),
                         headers={'Content-Type': 'application/json'})

    if runs.status_code == 200:
        return run.Run(info=runs.json()['run']['info'], name=run_name)
    else:
        raise HaiqvValueError(runs.json())


def update_run(
        run_id: str,
        status: Optional[str] = None
) -> None:
    data = {
        'run_id': run_id
    }

    if status:
        data['status'] = status

    res = requests.post(f'{os.environ.get("_HAIQV_BASE_URL")}/update-run',
                        data=json.dumps(data),
                        headers={'Content-Type': 'application/json'})

    if res.status_code != 200:
        raise HaiqvValueError(res.json())


# Parameter
def log_param(run_id: str, key: str, value: Any) -> None:
    data = {
        'run_id': run_id,
        'key': key,
        'value': value
    }

    res = requests.post(f'{os.environ.get("_HAIQV_BASE_URL")}/logging-parameter',
                        data=json.dumps(data),
                        headers={'Content-Type': 'application/json'})
    if res.status_code != 200:
        raise HaiqvValueError(res.json())


# Metric
def log_metric(run_id: str, key: str, value: float, step: Optional[int] = None, subset: Optional[str] = None) -> None:
    assert '/' not in key, 'not allow (/) in metric_key'

    if subset is None:
        metric_key = key
    else:
        metric_key = f'{key}/{subset}'

    data = {
        'run_id': run_id,
        'key': metric_key,
        'value': value,
        'step': step
    }

    requests.post(f'{os.environ.get("_HAIQV_BASE_URL")}/logging-metric',
                  data=json.dumps(data),
                  headers={'Content-Type': 'application/json'})


def log_batch(run_id: str, data: dict) -> None:
    data['run_id'] = run_id
    requests.post(f'{os.environ.get("_HAIQV_BASE_URL")}/batches',
                  data=json.dumps(data),
                  headers={'Content-Type': 'application/json'})


def log_artifact(run_id: str, local_file: str, artifact_path: str = "") -> None:
    filename = os.path.basename(local_file)
    mime = guess_mime_type(filename)
    headers = {'Content-type': mime}

    with open(local_file, 'rb') as f:
        requests.post(
            f'{os.environ.get("_HAIQV_BASE_URL")}/set-artifact?run_id={run_id}&artifact_path={artifact_path}',
            files={'local_file': (filename, f, headers)}
        )


###########################################################################################################
def _get_run(run_id: str, client_ip=None) -> run.Run:
    run_item = requests.get(
        f'{os.environ.get("_HAIQV_BASE_URL")}/get-run-via-run-id',
        params={'run_id': run_id, 'client_ip': client_ip}
    )
    if run_item.status_code == 200:
        return run.Run(info=run_item.json()['run']['info'])
    else:
        raise HaiqvValueError(run_item.json())


@contextlib.contextmanager
def _log_artifact_helper(run_id, artifact_file):
    norm_path = posixpath.normpath(artifact_file)
    filename = posixpath.basename(norm_path)
    artifact_dir = posixpath.dirname(norm_path)
    # artifact_dir = None if artifact_dir == "" else artifact_dir

    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_path = os.path.join(tmp_dir, filename)
        yield tmp_path
        log_artifact(run_id, tmp_path, artifact_dir)


def log_text(run_id: str, text: str, artifact_file: str) -> None:
    with _log_artifact_helper(run_id, artifact_file) as tmp_path:
        with open(tmp_path, "w", encoding="utf-8") as f:
            f.write(text)


def log_dict(run_id: str, dictionary: Any, artifact_file: str) -> None:
    extension = os.path.splitext(artifact_file)[1]

    with _log_artifact_helper(run_id, artifact_file) as tmp_path:
        with open(tmp_path, "w") as f:
            # Specify `indent` to prettify the output
            if extension in [".yml", ".yaml"]:
                yaml.dump(dictionary, f, indent=2, default_flow_style=False)
            else:
                json.dump(dictionary, f, indent=2)


def log_model_metadata(
        run_id: str,
        model_nm: str,
        model_path: str,
        step: int,
        metric: Optional[dict] = None,
        tags: Optional[dict] = None,
        client_ip=None) -> None:

    runs = _get_run(run_id, client_ip)

    model_tags = dict()
    model_tags['model_path'] = os.path.abspath(model_path)
    model_tags['step'] = step

    if metric is None:
        # 1. Step에 맞춰 Metric 가져오기
        # model_tags['metric'] = dict()
        # for m in runs.data['metrics']:
        #     key, subset = key_subset_split(m['key'])

        #     metric = [metric for metric in get_metric_history(key, subset=subset, run_id=runs.info['run_id']) if metric['step'] == step]
        #     for item in metric:
        #         k, s = key_subset_split(item['key'])
        #         if k in model_tags['metric'].keys():
        #             model_tags['metric'][k].update({s: item['value']} if s else item['value'])
        #         else:
        #             model_tags['metric'].update({
        #                 k: {s: item['value']} if s else item['value']
        #             })

        # 2. Latest Metric 가져오기
        model_tags['metric'] = dict()
        for m in runs.data['metrics']:
            (key, subset), value = key_subset_split(m['key']), m['value']
            if key in model_tags['metric'].keys():
                model_tags['metric'][key].append({
                    'subset': subset,
                    'value': value
                })
            else:
                model_tags['metric'][key] = [{
                    'subset': subset,
                    'value': value
                }]
    else:
        model_tags['metric'] = metric

    if tags:
        model_tags.update(tags)

    log_dict(run_id, model_tags, f'models/{model_nm}_step_{step}.txt')


def log_datasets(run_id: str, data_nm: str, path: str, desc: str = None, tags: dict = None):
    datasets = dict()
    datasets['path'] = os.path.abspath(path)
    if desc:
        datasets['desc'] = desc
    if tags:
        datasets.update(tags)
    log_dict(run_id, datasets, f'dataset/{data_nm}_info.txt')
