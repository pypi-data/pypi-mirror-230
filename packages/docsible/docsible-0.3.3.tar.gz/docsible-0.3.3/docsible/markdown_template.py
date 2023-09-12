static_template = """{{- role.existing_readme -}}

# Generated Documentation
## {{ role.name }}
{% if role.meta and role.meta.galaxy_info -%}
Description: {{ role.meta.galaxy_info.description or 'Not available.' }}
{% else %}
Description: Not available.
{%- endif %}

{% if role.meta and role.meta.docsible -%}
| Field                | Value           |
|--------------------- |-----------------|
| Functional description | {{ role.meta.docsible.description_function or 'Not available.' }} |
| Requester            | {{ role.meta.docsible.requester or 'Not available.' }} |
| Users                | {{ role.meta.docsible.users or 'Not available.' }} |
| Date dev             | {{ role.meta.docsible.dt_dev or 'Not available.' }} |
| Date prod            | {{ role.meta.docsible.dt_prod or 'Not available.' }} |
| Version              | {{ role.meta.docsible.version or 'Not available.' }} |
| Time Saving              | {{ role.meta.docsible.time_saving or 'Not available.' }} |
{%- endif %}


### Defaults
{% if role.defaults|length > 0 -%}
**These are static variables with lower priority**
{%- for defaultfile in role.defaults %}
#### File: {{ defaultfile.file }}
| Var          | Type         | Value       | Required    | Title       |
|--------------|--------------|-------------|-------------|-------------|
{%- for key, details in defaultfile.data.items() %}
{%- set var_type = details.value.__class__.__name__ %}
| {{ key }}    | {{ var_type }}   | {{ details.value }}  | {{ details.required }}  | {{ details.title }} |
{%- endfor %}
{%- endfor %}
{%- else %}
No defaults available.
{%- endif %}



### Vars
{% if role.vars|length > 0 -%}
**These are variables with higher priority**
{%- for varsfile in role.vars %}
#### File: {{ varsfile.file }}
| Var          | Type         | Value       | Required    | Title       |
|--------------|--------------|-------------|-------------|-------------|
{%- for key, details in varsfile.data.items() %}
{%- set var_type = details.value.__class__.__name__ %}
| {{ key }}    | {{ var_type }}   | {{ details.value }}  | {{ details.required }}  | {{ details.title }} |
{%- endfor %}
{%- endfor %}
{%- else %}
No vars available.
{%- endif %}


### Tasks
{%- if role.tasks|length == 1 and role.tasks[0]['file'] == 'main.yml' %}
| Name | Module |
| ---- | ------ |
{%- for task in role.tasks[0]['tasks'] %}
| {{ task.name }} | {{ task.module }} |
{%- endfor %}
{%- else %}
{% for taskfile in role.tasks %}
#### File: {{ taskfile.file }}
| Name | Module |
| ---- | ------ |
{%- for task in taskfile.tasks %}
| {{ task.name }} | {{ task.module }} |
{%- endfor %}
{% endfor %}
{%- endif %}

{% if mermaid_code_per_file -%}
## Task Flow Graphs
{% for task_file, mermaid_code in mermaid_code_per_file.items() %}
### Graph for {{ task_file }}
```mermaid
{{ mermaid_code }}
```
{% endfor %}
{%- endif %}

{% if role.playbook.content -%}
## Playbook
```yml
{{ role.playbook.content }}
```
{%- endif %}
{% if role.playbook.graph -%}
## Playbook graph
```mermaid
{{ role.playbook.graph }}
```
{%- endif %}

{% if role.meta.galaxy_info -%}
## Author Information
{{ role.meta.galaxy_info.author or 'Unknown Author' }}

#### License
{{ role.meta.galaxy_info.license or 'No license specified.' }}

#### Minimum Ansible Version
{{ role.meta.galaxy_info.min_ansible_version or 'No minimum version specified.' }}

#### Platforms
{% if role.meta.galaxy_info.platforms -%}
{% for platform in role.meta.galaxy_info.platforms -%}
- **{{ platform.name }}**: `platform.versions`
{% endfor -%}
{%- else -%}
No platforms specified.
{%- endif %}
{%- endif %}
"""