# eews-event-driven

Early Earthquake Warning System (EEWS) Event-Driven Architecture. Github main repository at [Zsaschz/eews-event-driven](https://github.com/Zsaschz/eews-event-driven). 


**![](https://lh7-us.googleusercontent.com/N4hEVxCKx_xhg9L7PWzZjFSS82WHB-ffApEv_SXBY19Jw4pqxEiLaONadImYnpJqUquTNNSY4ISiy7w_xuTmut1bOscbJvvcX5AA2WuJaEYPDpjepugZKxcafHRBnIpDM8AL_DqE2QGq1iga6erZa4c)**

## [IoT Middleware](https://github.com/natsyz/eews-event-driven/tree/main/eews_backend/seedlink)
IoT middleware akan melakukan memproses data berupa ekstraksi fitur, butter band filter, interpolasi, dan penyelarasan waktu ke delta terdekat.
- Input:
Data geospatial Geofon
- Output:
Data yang telah diproses disimpan ke InfluxDB dan dikirim sebagai event ke topic preprocessed Kafka dengan window 8 detik.

## Kafka

Kafka digunakan sebagai media komunikasi antar komponen untuk melakukan pemrosesan data stream secara real-time. Kafka bersifat terdistribusi dan terdiri dari dua komponen, yaitu Kafka Broker dan Zookeeper. Zookeeper digunakan untuk mengatur kumpulan beberapa Kafka Broker. Perlu diingat bahwa meningkatkan jumlah Kafka Broker tidak secara langsung dapat meningkatkan performa Kafka.

Pada Kafka terdapat kumpulan data yang disebut Topic. Setiap topic merupakan kumpulan data yang terurut dan berkaitan. Pada sistem ini terdapat tiga topic yang digunakan:
- preprocessed
Berisi data yang sudah diproses dan dihasilkan oleh komponen IoT Middleware.
- prediction
Berisi data hasil prediksi machine learning dari p-arrival topic.

## [Stream Processing](https://github.com/natsyz/eews-event-driven/tree/main/eews_backend/stream)
Stream processing pada sistem ini dilakukan untuk mengolah data stream seismik untuk dapat digunakan dalam proses pendeteksian p-arrival dan prediksi gempa bumi. Software yang digunakan untuk melakukan stream processing ini adalah Apache Spark, dengan library PySpark sebagai API dalam bahasa pemrograman Python untuk Apache Spark.

- Input:
Data seismik dari event Kafka di topic preprocessed.
- Output:
Data prediksi disimpan ke MongoDB dan dikirim sebagai event ke topic prediction Kafka.

## [REST API](https://github.com/natsyz/eews-event-driven/tree/main/eews_backend/rest)
Komponen yang menyalurkan data yang telah disimpan ke InfluxDB dari IoT Middleware untuk kebutuhan frontend melalui koneksi websocket dan/atau http request ke REST API.

- Input:
Data seismik dari InfluxDB dan data stasiun dari MongoDB.
- Output:
Data seismik dan data stasiun.

## [Frontend](https://github.com/natsyz/eews-event-driven/tree/main/frontend)
Layanan aplikasi ReactJS yang menampilkan peta dengan informasi data seismik dan hasil prediksi pada stasiun yang ada. 

- Input:
Data seismik dan data stasiun dari REST API.
- Output:
Dashboard pada frontend.
