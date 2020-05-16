FROM python:3.8-buster

# create user to app
RUN addgroup --gid 1001 appuser
# RUN adduser --no-create-home --uid 1001 --gid 1001 appuser
RUN useradd --gid 1001 -u 1001 appuser
WORKDIR /code

# ADD requirements.txt /code
# RUN pip install -r requirements.txt
RUN python3 -m pip install --upgrade Pillow

ADD util.py /code
ADD photo_organizer.py /code

USER appuser
CMD python photo_organizer.py