FROM continuumio/miniconda

ENV PYTHONUNBUFFERED=1

RUN apt update && apt install g++ gcc -y locales --no-install-recommends

# Cursed be the realm of locales for they are always a massive pain in my buttocks.
# Will throw a 'what():  locale::facet::_S_create_c_locale name not valid' without it.
RUN echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen

COPY ./environment.yaml environment.yaml
RUN set -x \
    && conda env create -f environment.yaml \
    && conda clean -afy \
    && find /opt/conda/ -follow -type f -name '*.a' -delete \
    && find /opt/conda/ -follow -type f -name '*.pyc' -delete \
    && find /opt/conda/ -follow -type f -name '*.js.map' -delete

RUN mkdir evkk
COPY . evkk
WORKDIR evkk

EXPOSE 8000

RUN /opt/conda/envs/evkk/bin/python manage.py collectstatic --noinput
RUN /opt/conda/envs/evkk/bin/python manage.py migrate

CMD  ["/opt/conda/envs/evkk/bin/python", "manage.py", "runserver", "0.0.0.0:8000"]