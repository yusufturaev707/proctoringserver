FROM postgres:16

# pgvector o‘rnatish uchun kerakli paketlar
RUN apt-get update && apt-get install -y \
    postgresql-server-dev-16 \
    make g++ git && \
    git clone --branch v0.5.1 https://github.com/pgvector/pgvector.git && \
    cd pgvector && make && make install && \
    cd .. && rm -rf pgvector && \
    apt-get remove --purge -y git make g++ && apt-get autoremove -y && apt-get clean
