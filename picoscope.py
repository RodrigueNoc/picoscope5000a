import ctypes
import numpy as np

from picosdk.ps5000a import ps5000a as ps
from picosdk.functions import assert_pico_ok, mV2adc, adc2mV


class Picoscope():
    def __init__(self):
        """
        Initialise toutes les constantes pour le picoscope
        """
        self.status = {}

    def StartPico(
            self,
            serial=None,
            resolution=1
    ):
        """
        Fonction qui appel OpenUnit p75, 4.37

        status : dictionaire des status du pico
        serial : ouvre le picoscope avec ce numéro de série, si nul alors 
        ouvre le premier trouver
        resolution : p88, 4.49.1; résolution possible -> PICO_DR_8BIT = 0;
            PICO_DR_12BIT = 1; PICO_DR_14BIT = 2; PICO_DR_15BIT = 3; 
            PICO_DR_16BIT = 4
        """
        self.handle = ctypes.c_int16()
        self.serial = serial
        self.resolution = resolution

        self.status['OpenUnit'] = ps.ps5000aOpenUnit(
            ctypes.byref(self.handle),
            self.serial,
            self.resolution
        )
        assert_pico_ok(self.status['OpenUnit'])

    def Channel(
            self,
            Cha="A",
            channel_enabled=1,
            channel_type='DC',
            channel_range="2V",
            analogueOffset=0.
    ):
        """
        Fonction qui paramètre les voies du picoscope p84, 4.46

        Cha : p85, 4.46.1; selctionne la voie du picoscope; 
            valeur possible -> "A"; "B"; "C"; "D"
        channel_enabled : allume ou eteind la voie
        channel_type : p40, 4.7.2; allimentation en courant continue ou 
            alternatif; valeur possible -> "DC"; "AC"
        channel_range : p40, 4.7.1; valeur du calibre du picoscope (en valeur
            absolue); valeur possible -> "10MV", "20MV", "50MV", "100MV",
            "200MV", "500MV", "1V", "2V", "5V", "10V", "20V", "50V"

        """
        self.ps_channel = ps.PS5000A_CHANNEL[f'PS5000A_CHANNEL_{Cha}']
        self.ps_channel_type = ps.PS5000A_COUPLING[f'PS5000A_{channel_type}']
        self.channel_enabled = channel_enabled
        self.ps_channel_range = ps.PS5000A_RANGE[f'PS5000A_{channel_range}']
        self.analogueOffset = analogueOffset

        self.status['SetChannel'] = ps.ps5000aSetChannel(
            self.handle,
            self.ps_channel,
            self.channel_enabled,
            self.ps_channel_type,
            self.ps_channel_range,
            analogueOffset
        )
        assert_pico_ok(self.status['SetChannel'])

    def MAX_ADC(self):
        """
        Appel la fonction ps5000aMaximumValue p70, 4.32
        """
        self.maxADC = ctypes.c_int16()

        self.status["maximumValue"] = ps.ps5000aMaximumValue(
            self.handle,
            ctypes.byref(self.maxADC)
        )
        assert_pico_ok(self.status["maximumValue"])

    def SetTrigger(
            self,
            trigger_enabled=1,
            seuil=1000,
            direction="FALLING",
            trigger_delay=0,
            trigger_autoTrigger_ms=0
    ):
        """
        Fonction qui initialise un trigger p115, 4.66

        trigger_enabled : active ou desactive le trigger
        Cha : selectionne la voie où mettre le trigger (cf l.39)
        seuil : seuil du trigger (en mV)
        direction : p121, 4.69.1; forme du trigger; valeur possible -> ABOVE,
            BELOW, RISING, FALLING et RISING_OR_FALLING
        trigger_delay : retard entre la detection du trigger et l'acquisition
        trigger_autoTrigger_ms : durée d'attente d'un trigger; 0 = infini
        """
        self.MAX_ADC()
        trigger_threshold = mV2adc(
            seuil,
            self.ps_channel_range,
            self.maxADC
        )
        trigger_direction = ps.PS5000A_THRESHOLD_DIRECTION[f'PS5000A_{direction}']

        self.status['SetSimpleTrigger'] = ps.ps5000aSetSimpleTrigger(
            self.handle,
            trigger_enabled,
            self.ps_channel,
            trigger_threshold,
            trigger_direction,
            trigger_delay,
            trigger_autoTrigger_ms
        )
        assert_pico_ok(self.status['SetSimpleTrigger'])

    def StartStreaming(
            self,
            buffer_size=1000,
            mode="NONE",
            Ratio=1,
            autoStop=0,
            intervale=1,
            unite='NS'
    ):
        """
        Fonction qui commence l'acquisition de données

        Cha : selectionne la voie où mettre le trigger (cf l.39)
        buffer_size : taille de l'espace de stockage pour l'enregistrement
        mode : p59, 4.22.1; traitement préalable des données pendant 
            l'enregistrement; valeurs possible -> "NONE", "AGGREGATE",
            "DECIMATE", "AVERAGE"
        Ratio : valeur de n dans les regroupement du mode (cf p59)
        autoStop : indique si le Stream doit s'arrêter
        intervale : donne le temps de l'intervale de mesure
        unite : p54, 4.18.3; unitée d'un intervale de mesure;
            possible values : "FS", "PS", "NS", "US", "MS", "S"
        """
        # Initialisation du stockage
        self.buffer_size = buffer_size
        self.buffer_data = np.zeros(
            shape=buffer_size,
            dtype=np.int16
        )
        self.mode = ps.PS5000A_RATIO_MODE[f'PS5000A_RATIO_MODE_{mode}']
        downSampleRatio = Ratio

        self.status['SetDataBuffer'] = ps.ps5000aSetDataBuffer(
            self.handle,
            self.ps_channel,
            self.buffer_data.ctypes.data_as(ctypes.POINTER(ctypes.c_int16)),
            self.buffer_size,
            0,  # segmentIndex
            self.mode
        )
        assert_pico_ok(self.status['SetDataBuffer'])

        # Début du streaming
        maxPreTriggerSamples = self.buffer_size*0.1
        maxPostTriggerSamples = self.buffer_size*0.9
        self.autoStop = autoStop
        self.sampleInterval = ctypes.c_int32(intervale)
        self.sampleIntervalTimeUnits = ps.PS5000A_TIME_UNITS[f'PS5000A_{unite}']

        self.status['StartStreaming'] = ps.ps5000aRunStreaming(
            self.handle,
            ctypes.byref(self.sampleInterval),
            self.sampleIntervalTimeUnits,
            maxPreTriggerSamples,
            maxPostTriggerSamples,
            self.autoStop,
            downSampleRatio,
            self.mode,
            self.buffer_size
        )
        assert_pico_ok(self.status['StartStreaming'])

    def StopStreaming(self):
        """
        Fonction qui arrête le streaming
        """
        self.status['StopStreaming'] = ps.ps5000aStop(self.handle)
        assert_pico_ok(self.status['StopStreaming'])

    def StopPico(self):
        """
        Fonction qui arrête le picoscope
        """
        self.status['CloseUnit'] = ps.ps5000aCloseUnit(self.handle)
        assert_pico_ok(self.status['CloseUnit'])
