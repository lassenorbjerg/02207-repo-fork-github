# PyUVM Testbench Viewer

This prototype statically analyzes a PyUVM testbench and visualizes its
component hierarchy, source code, and phase structure. It does not import or
execute the selected testbench.

## Run

Activate the repository development environment, change to the lesson
directory, and start the application:

```shell
cd lessons/08_UVM_test_env_seqs
python -m PyUVMTBViewer
```

Select a viewer JSON file with **File → Open viewer input**. A configuration
can also be supplied on the command line:

```shell
python -m PyUVMTBViewer ../../exercises/E07_sat_pyuvm_uvc_integraion/PyUVMTBViewer.json
```

Directly opening a Python test file remains supported for quick inspection.

## JSON input

Paths are resolved relative to the JSON file:

```json
{
  "top_level_uvm_test": "tb/top_test.py",
  "include_dirs": ["../common"],
  "instance_rendering": {
    "top_test.env.agent.driver": "conditional:producer_driver",
    "top_test.env.optional_component": "hide",
    "top_test.env.inactive_agent": "grey"
  }
}
```

Rendering values have the following meanings:

- `conditional:<class name>` keeps only the selected statically detected type.
- `hide` removes the instance and its subhierarchy.
- `grey` displays a disabled grey instance without expanding its subhierarchy.
- An instance omitted from the dictionary uses the default behavior. All
  statically visible conditional types are shown.

## Experimental LLM analysis

The optional LLM backend asks OpenAI to resolve conditional component
creation by tracing configuration values and control flow across the loaded
PyUVM source files. Install its extra dependency with:

```shell
python -m pip install -r PyUVMTBViewer/requirements-experimental.txt
```

Enable it in a viewer JSON file:

```json
{
  "top_level_uvm_test": "tb/top_test.py",
  "include_dirs": ["../common"],
  "experimental": true,
  "openai_api_key": "replace-with-an-api-key",
  "openai_model": "gpt-5-mini"
}
```

The API key must be non-empty when the configuration is opened. Do not commit
a real key to the repository. `openai_model` is optional and defaults to
`gpt-5-mini`. The backend sends the loaded Python source files and the list of
conditional instances to OpenAI. Its response is constrained by a strict JSON
schema and validated locally before it changes the displayed hierarchy.

Explicit `instance_rendering` entries take precedence over experimental LLM
decisions. Non-experimental configurations do not import or require the
OpenAI package.

## Prototype behavior

- The left pane shows inferred component instances and their initialization
  and phase methods.
- The upper-middle pane shows read-only, highlighted Python source.
- The upper-right pane shows the complete inferred component hierarchy.
- The lower-right pane shows all discovered phases or detailed build/connect
  diagrams.
- Component instances are inferred from assignments using `Class.create(...)`
  or component constructors.
- Conditional component creation is included and marked with `?`.
- Dynamic factory overrides and runtime configuration are not executed. The
  diagram therefore shows declared component types and all statically visible
  conditional branches.

## Tests

Run the analyzer and headless GUI tests from the lesson directory:

```shell
QT_QPA_PLATFORM=offscreen python -m unittest discover PyUVMTBViewer/tests
```
