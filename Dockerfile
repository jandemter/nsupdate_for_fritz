FROM python:3.9-alpine

RUN apk add --no-cache bind-tools

RUN addgroup -S nsupdatefritz && adduser -S nsupdatefritz -G nsupdatefritz
USER nsupdatefritz

ADD . /src

RUN cd /src && pip install --user .

ENV PATH=~nsupdatefritz/.local/bin:$PATH

RUN cd /src && python -m unittest discover -s tests

ENTRYPOINT ["python", "-m", "nsupdate_for_fritz"]
CMD ["--help"]
