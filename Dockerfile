FROM jupyter/base-notebook

# add requirements.txt for pip install
ADD requirements.txt .

#RUN pip install --upgrade pip
#RUN pip install --trusted-host pypi.python.org -r requirements.txt
#RUN jupyter nbextension enable --py --sys-prefix ipyleaflet
#RUN jupyter nbextension enable --py widgetsnbextension

RUN conda install --quiet --yes \
    'ipyleaflet' \
    'psycopg2' \
    'pandas' \
    'matplotlib' \
    'ipywidgets' \
    'widgetsnbextension' \
    'openpyxl' \
    && conda clean -tipsy && \
    npm cache clean && \
    rm -rf $CONDA_DIR/share/jupyter/lab/staging && \
    fix-permissions $CONDA_DIR
