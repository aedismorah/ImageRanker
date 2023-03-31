FROM python:3.10
RUN pip install sentencepiece \
    protobuf==3.20.2 \
    transformers \
    Pillow \
    numpy \
    torch \
    hnswlib \
    omegaconf \
    albumentations \
    flask \
    Flask-Cors 
COPY server /server
WORKDIR /server
CMD python app.py
