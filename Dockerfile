FROM python:3.8
COPY app .
RUN pip install -r requirements.txt
CMD ["python","start_ppo.py"]