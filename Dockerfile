FROM python:3.9

WORKDIR /vkhidden

ADD requirements.txt /vkhidden

RUN pip install -r requirements.txt
RUN mkdir /vkhidden/keys

ADD app.py /vkhidden
ADD database.py /vkhidden
ADD models.py /vkhidden
ADD vk_crypt.py /vkhidden
ADD vkapi.py /vkhidden


ADD template /vkhidden/template
ADD css /vkhidden/css
ADD js /vkhidden/js
ADD keys /vkhidden

VOLUME ./keys
VOLUME ./db

ENV CPORT=8007
EXPOSE $CPORT

CMD sh -c "python app.py  && uvicorn app:app --reload --host 0.0.0.0 --port $CPORT"
