import os
from datetime import datetime, timedelta, timezone
from .utils import to_json

from logging import getLogger, INFO
logger = getLogger(__name__)
logger.setLevel(INFO)

HUB_FUNCTION_NAME = os.environ.get('HUB_FUNCTION_NAME')

def handler(event, driver_id, result_root_key = None, post_function = None):
    """"""
    logger.info(f'request: {event}')

    if not isinstance(event, dict):
        raise Exception(f"invalid payload: {event}")

    try:
        command_id = event["request"]["command_id"]
        components = f'drivers.{driver_id}.command.handler'.split('.')
        logger.debug(components)

        mod = __import__(components[0])
        for comp in components[1:]:
            mod = getattr(mod, comp)

        with mod(event) as client:
            cmd = getattr(client, command_id)
            result = cmd()

    except Exception as e:
        logger.error(e)
        result = {
            'errors': [
                {
                    'name': e.__class__.__name__,'message': str(e)
                }
            ]
        }

    if result_root_key:
        result = {
            result_root_key: result
        }

    if not result.get('date_time'):
        dt = datetime.now().astimezone(timezone(timedelta(hours=9)))
        result['date_time'] = dt.replace(microsecond=0).isoformat()

    if not result.get('result_id'):
        result['result_id'] = f'r_{command_id}'

    if post_function:
        post_function(result, event)

    payload = {
        "message_log_id": event["message_log_id"],
        "result": result,
        "source": event["thing_dest_address"],
        "service_id": event["service_id"],
    }

    logger.info(f'payload: {payload}')

    if not event.get('standalone_invoke') and HUB_FUNCTION_NAME:
        try:
            import boto3
            client = boto3.client("lambda")
            sts = client.invoke(
                FunctionName=HUB_FUNCTION_NAME,
                InvocationType="Event",
                Payload=to_json(payload),
            )
            del sts['Payload']
            logger.info(f'invoke: {sts}')

        except Exception as e:
            logger.error(e)            

    return payload
