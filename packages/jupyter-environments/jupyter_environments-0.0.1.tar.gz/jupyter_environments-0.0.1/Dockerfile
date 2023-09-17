# Copyright (c) Datalayer, Inc. https://datalayer.io
# Distributed under the terms of the MIT License.

FROM python:3.11

RUN mkdir /opt/jupyter-environments

WORKDIR /opt/jupyter-environments

RUN pip install kazoo

COPY jupyter_environments /opt/jupyter_environments
RUN pip install -e ./jupyter_environments

# COPY frontplane/dist.html /opt/jupyter-environments/index.html

WORKDIR /opt/jupyter-environments/editor

EXPOSE 9300

CMD ["python", "-m", "jupyter_environments"]
