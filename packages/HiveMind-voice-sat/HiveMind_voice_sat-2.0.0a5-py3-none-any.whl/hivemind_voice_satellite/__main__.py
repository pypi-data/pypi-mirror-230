import click
from hivemind_bus_client import HiveMessageBusClient
from ovos_audio.service import PlaybackService
from ovos_utils import wait_for_exit_signal
from ovos_utils.log import init_service_logger, LOG
from hivemind_voice_satellite import VoiceClient


@click.command(help="connect to HiveMind")
@click.option("--host", help="hivemind host", type=str, default="wss://127.0.0.1")
@click.option("--key", help="Access Key", type=str)
@click.option("--password", help="Password for key derivation", type=str)
@click.option("--port", help="HiveMind port number", type=int, default=5678)
@click.option("--selfsigned", help="accept self signed certificates", is_flag=True)
@click.option("--siteid", help="location identifier for message.context", type=str, default="unknown")
def connect(host, key, password, port, selfsigned, siteid):
    init_service_logger("HiveMind-voice-sat")
    
    if not host.startswith("ws"):
        LOG.error("Invalid host, please specify a protocol")
        LOG.error(f"ws://{host} or wss://{host}")
        exit(1)

    # connect to hivemind
    bus = HiveMessageBusClient(key=key,
                               password=password,
                               port=port,
                               host=host,
                               useragent="VoiceSatelliteV0.3.0",
                               self_signed=selfsigned)
    bus.connect(site_id=siteid)

    # create Audio Output interface (TTS/Music)
    audio = PlaybackService(bus=bus, disable_ocp=True, validate_source=False)
    audio.daemon = True
    audio.start()

    # STT listener thread
    service = VoiceClient(bus=bus)
    service.daemon = True
    service.start()

    try:
        from ovos_PHAL.service import PHAL
        phal = PHAL(bus=bus)
        phal.start()
    except ImportError:
        print("PHAL is not available")
        phal = None

    wait_for_exit_signal()

    service.stop()
    audio.shutdown()
    if phal:
        phal.shutdown()


if __name__ == '__main__':
    connect()
