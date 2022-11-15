
FROM  opengisch/qgis:latest

RUN dnf install -y \
    pytest \
    python3-mock && \
    dnf clean all

WORKDIR /io/qgis_server_render_geojson

CMD pytest
