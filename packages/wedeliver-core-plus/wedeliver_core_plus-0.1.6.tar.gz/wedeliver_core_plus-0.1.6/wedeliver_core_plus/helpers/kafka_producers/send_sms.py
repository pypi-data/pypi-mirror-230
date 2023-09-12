from wedeliver_core_plus.helpers.kafka_producer import Producer
from wedeliver_core_plus.helpers.topics import Topics



def send_sms(mobile, message):
    response = dict(
        message=message,
        mobile=mobile
    )
    Producer().send_topic(Topics().SEND_SMS, response)
