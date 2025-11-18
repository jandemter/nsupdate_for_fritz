FROM python:3.14-alpine AS base

RUN apk add --no-cache bind-tools

RUN addgroup -S nsupdatefritz && adduser -S nsupdatefritz -G nsupdatefritz

FROM base AS builder

RUN mkdir /src
RUN chown nsupdatefritz:nsupdatefritz /src

USER nsupdatefritz
COPY . /src
RUN cd /src && pip install --user .

ENV PATH=~nsupdatefritz/.local/bin:$PATH

ENV DOCKER_BUILD=yes
RUN cd /src && python -m unittest discover -s tests

FROM base
COPY --from=builder --chown=nsupdatefritz /home/nsupdatefritz/.local /home/nsupdatefritz/.local
USER nsupdatefritz

ENTRYPOINT ["python", "-m", "nsupdate_for_fritz"]
CMD ["--help"]
