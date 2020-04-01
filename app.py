from kafka.errors import KafkaTimeoutError
from flask import Flask, request
from kafka import KafkaProducer
from json import dumps
from os import getenv
import const

app = Flask(__name__)


def __get_cluster_data(alerts):
    temp_dict = alerts.copy()
    temp_dict.pop("alerts")
    temp_dict.pop("status")
    temp_dict.pop("version")
    return temp_dict


def __parse_alert(alert):
    try:
        alert.update(alert.pop("annotations"))
    except KeyError:
        # TODO: Log no annotations
        pass
    finally:
        try:
            alert.update(alert.pop("labels"))
        except KeyError:
            # TODO: Log no labels
            pass
    return alert


def parse_alerts(alerts):
    alert_cluster_data = __get_cluster_data(alerts)
    final_alerts = []
    for alert in alerts["alerts"]:
        final_alerts.append(__parse_alert(alert).update(alert_cluster_data))
    return final_alerts


def insert_to_topic(alert, producer, retry_counter):
    for i in range(retry_counter):
        try:
            producer.send(getenv(const.KAFKA_TOPIC_ENVVAR) or const.KAFKA_DEFAULT_TOPIC,
                          bytes(dumps(alert, ensure_ascii=False)))
        except KafkaTimeoutError as kte:
            if i + 1 == retry_counter:
                raise kte
            # TODO: Log info retry ^_^


def get_kafka_connection():
    try:
        producer = KafkaProducer(request_timeout_ms=const.KAFKA_TIMEOUT, bootstrap_servers=const.KAFKA_SERVERS)
        return producer
    except Exception as e:
        # TODO: Log unable to get kafka producer
        raise e


def flush_producer(producer, retry_counter):
    for i in range(retry_counter):
        try:
            producer.flush(const.KAFKA_TIMEOUT)
        except KafkaTimeoutError as kte:
            if i + 1 == retry_counter:
                raise kte
            # TODO: Log info retry ^_^


def send_alerts_to_kafka(alerts):
    producer = get_kafka_connection()
    for alert in alerts:
        try:
            insert_to_topic(alert, producer, const.RETRY_COUNTER)
        except KafkaTimeoutError as kte:
            # TODO: Log critical about kte spesific alert not reaching the kafka thingy
            continue
    try:
        flush_producer(producer, const.RETRY_COUNTER)
    except KafkaTimeoutError as kte:
        # TODO: Log CRITICAL about the kte and all the alerts
        return False
    return True


def manage_request(request_json):
    alerts_list = parse_alerts(request_json)
    return send_alerts_to_kafka(alerts_list)


@app.route("/", methods=["POST"])
def get_alerts():
    return manage_request(request.json)


@app.route("/", methods=["GET"])
def healthy():
    return "I am up and running ^_^"


def main():
    port = int(getenv(const.PORT_ENVVAR)) or const.DEFAULT_PORT
    app.run(host=const.HOST, port=port)


if __name__ == '__main__':
    main()
