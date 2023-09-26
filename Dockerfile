FROM python:3.9

WORKDIR /vkhidden

ADD requirements.txt /vkhidden

RUN pip install -r requirements.txt

ADD app.py /vkhidden
ADD database.py /vkhidden
ADD models.py /vkhidden
ADD vk_crypt.py /vkhidden
ADD vkapi.py /vkhidden

ADD template /vkhidden/template
ADD css /vkhidden/css
ADD js /vkhidden/js
ADD keys /vkhidden


ENV CPORT=8006
EXPOSE $CPORT

#CMD ["uvicorn", "app:app", "--reload", "--host", "0.0.0.0", "--port", "$CPORT"]
CMD sh -c "python app.py  && uvicorn app:app --reload --host 0.0.0.0 --port $CPORT"
