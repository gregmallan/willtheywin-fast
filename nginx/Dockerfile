FROM nginx:latest

COPY ./conf/nginx/prod.conf /etc/nginx/conf.d/default.conf

RUN mkdir -p /vol/static
RUN chmod 755 /vol/static
