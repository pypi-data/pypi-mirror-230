from src.workflow_keeper.components import Engine
from src.workflow_keeper.utils import parse_yaml_workflow

if __name__ == '__main__':
    jobs, err = parse_yaml_workflow("./manifests/test_workflow.yaml", dict(test_name="test0"))
    print(jobs)
    print(err)
    Engine.execute_jobs(jobs)
