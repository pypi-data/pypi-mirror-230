from ai2_kit.core.util import short_hash

from dflow.op_template import ScriptOPTemplate
from dflow import (
    upload_s3,
    InputParameter, InputArtifact,
    OutputParameter, OutputArtifact,
    Step, Workflow,
)

from typing import Final, Callable, TypeVar, Union, Optional, Dict, Any

from pathlib import Path
from os import PathLike
import os
import cloudpickle as cp
import tempfile
import hashlib


T_IN_P = TypeVar('T_IN_P', bound=Dict[str, Any])
T_IN_A = TypeVar('T_IN_A', bound=Dict[str, Any])
T_OUT_P = TypeVar('T_OUT_P', bound=Dict[str, Any])
T_OUT_A = TypeVar('T_OUT_A', bound=Dict[str, Any])


class DflowBuilder:

    def __init__(self, name:str, s3_key_prefix: str):
        self.name: Final[str] = name

        self.s3_key_prefix: Final[str] = s3_key_prefix
        self.workflow = Workflow(name=name)

    def upload_s3(self, path: PathLike, *keys: str):
        key = self._get_s3_key(*keys)
        return upload_s3(path, key)

    def _get_s3_key(self, *keys: str):
        return os.path.join(self.s3_key_prefix, *keys)

    def add_py_step(self,
                    fn: Callable[[T_IN_P, T_IN_A, T_OUT_A], T_OUT_P],
                    name: Optional[str] = None,
                    python_cmd: str = 'python3',
                    with_param = None,
                    ) -> Callable[[T_IN_P, T_IN_A, T_OUT_A], Step]:
        """
        Add a python step to the workflow.
        """

        def _fn(in_params: T_IN_P, in_artifacts: T_IN_A, out_artifacts: T_OUT_A):
            # serialize fn and upload to s3
            fn_pickle = cp.dumps(fn, protocol=cp.DEFAULT_PROTOCOL)
            fn_hash = hashlib.sha256(fn_pickle).hexdigest()
            with tempfile.NamedTemporaryFile('w+b') as fp:
                fp.write(fn_pickle)
                fp.flush()
                fn_s3_key = self.upload_s3(Path(fp.name), 'dflow/py-fns', fn_hash)
            fn_path = f'/mnt/dflow/py-fns/{fn_hash}'

            # seria


            # build template
            template = ScriptOPTemplate(
                name='',
                command=python_cmd,
                script='\n'.join([
                    f'import os, json, cloudpickle as cp',
                    f'with open({repr(fn_path)}, "r") as fp:'
                    f'  fn = cp.load(fp)',
                     'in_params = json.loads(r\'{{inputs.parameters.value}}\')',
                ])
            )

            template.inputs.parameters = {}
            for k, v in in_params.items():
                template.inputs.parameters[k] = InputParameter()

            template.inputs.artifacts = {
                '__fn__': InputArtifact(path=fn_path),
            }
            for k, v in in_artifacts.items():
                template.inputs.artifacts[k] = InputArtifact(path=os.path.join('/mnt/dflow/inputs/artifacts', k))


            # build step
            step_name = f'py-step-{fn_hash}' if name is None else name
            step = Step(
                name=step_name,
                template=template,
                parameters={
                },
                artifacts=in_artifacts,
            )

            step.inputs.artifacts['__fn__'] = InputArtifact(path=fn_s3_key)


            if with_param is not None:
                step.with_param = with_param

            self.workflow.add(step)
            return step

        return _fn

