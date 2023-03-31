FROM node:12.22.9
COPY client /client
WORKDIR /client
RUN npm install
CMD npm start ip=0.0.0.0
