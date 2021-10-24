#!/usr/bin/env python
# -*- coding:utf-8 -*

import logging
import speech_recognition as sr

#TODO : pas que google

class Detector():
    '''A hotword detector based on speech_recognition
    '''
    def __init__(self, hotwords = None, device_id = None, pause = 2, language = 'fr-FR'):
        '''
        - hotwords : list of hotwords ex 'Alexa'
        - device : pyaudio index device
        - pause : time (s) after listen text (before regognition)
        '''
        self.microphone = sr.Microphone(device_id)
        self.recognizer = sr.Recognizer()
        if hotwords is None:
            self.hotwords = []
        elif type(hotwords)==list:
            self.hotwords = hotwords
        else:
            self.hotwords = [hotwords]
        self.language = language

    def start(self, detected_callback ,interrupt_check=lambda: False, *args, **kwargs):
        '''Wait for hotword
            detected_callback   :   list of callbacks (index : index hotwords)
            interrupt_check     :   function (return True for stop)
        '''
        logging.debug("Start Detector....")
        text = ""
        while text not in self.hotwords and not interrupt_check():
            with self.microphone as source:
                voice = self.recognizer.listen(source)
            logging.debug("Voice listened!")
            try:
                text=self.recognizer.recognize_google(voice, language = self.language)
                logging.debug(f"text listened : {text}.")
            except Exception as e:
                logging.error(e)
        for index, hotword in enumerate(self.hotwords):
            if text == hotword:
                try:
                    detected_callback[index]()
                except Exception as e:
                    logging.error(e)

    def terminate(self):
        pass
