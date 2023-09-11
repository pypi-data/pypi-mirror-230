[![Pipekit Logo](https://helm.pipekit.io/assets/pipekit-logo.png)](https://pipekit.io)

[Pipekit](pipekit.io) allows you to manage your workflows at scale. The control plane configures Argo Workflows for you in your infrastructure, enabling you to optimize multi-cluster workloads while reducing your cloud spend.  The team at Pipekit is also happy to support you through your Argo Workflows journey via commercial support.

# Pipekit Python SDK

## Installation

```bash
pip install pipekit-sdk
```

## Usage

```python
from hera.workflows import (
    DAG,
    Parameter,
    Script,
    Workflow,
)

from pipekit_sdk.service import PipekitService

# let's create a pipekit service
# that is used to talk to the pipekit api
pipekit = PipekitService(token="<Bearer Token>")

# let's list clusters and pipes
clusters = pipekit.list_clusters()
pipes = pipekit.list_pipes()

# let's create a workflow and submit it to pipekit
# hera's dag-diamond example
def my_print_script(message):
    print(message)

def get_script(callable):
    # note that we have the _option_ to set `inputs=Parameter(name="message")`, but Hera infers the `Parameter`s
    # that are necessary based on the passed in callable!
    return Script(
        name=callable.__name__.replace("_", "-"),
        source=callable,
        add_cwd_to_sys_path=False,
        image="python:alpine3.6",
    )

with Workflow(
    generate_name="dag-diamond-",
    entrypoint="diamond",
    namespace="default",
) as w:
    echo = get_script(my_print_script)

    with DAG(name="diamond"):
        A = echo(name="A", arguments=[Parameter(name="message", value="A")])
        B = echo(name="B", arguments=[Parameter(name="message", value="B")])
        C = echo(name="C", arguments=[Parameter(name="message", value="C")])
        D = echo(name="D", arguments=[Parameter(name="message", value="D")])
        A >> [B, C] >> D

# submit the workflow to pipekit
pipe_run = pipekit.submit(w, "<cluster-name>")

# let's tail logs
pipekit.print_logs(pipe_run["uuid"])
```

## Further help
Please refer to the [Pipekit Documentation](https://docs.pipekit.io) for more information.
