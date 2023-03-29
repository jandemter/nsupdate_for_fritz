FROM python:3.11-alpine

RUN apk add --no-cache bind-tools

RUN addgroup -S nsupdatefritz && adduser -S nsupdatefritz -G nsupdatefritz
RUN mkdir /src
RUN chown nsupdatefritz:nsupdatefritz /src

USER nsupdatefritz
COPY . /src
RUN cd /src && pip install --user .

ENV PATH=~nsupdatefritz/.local/bin:$PATH

RUN cd /src && python -m unittest discover -s tests

ENTRYPOINT ["python", "-m", "nsupdate_for_fritz"]
CMD ["--help"]
