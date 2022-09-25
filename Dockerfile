FROM python:3.6
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8080
ENV PORT 8080
ARG STABILITY_KEY
ENTRYPOINT ["python"]
CMD ["app.py"]