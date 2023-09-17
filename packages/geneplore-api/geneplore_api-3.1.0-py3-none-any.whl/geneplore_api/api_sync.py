import requests
import base64


api_key = ''

class Chat():
    def GetModels() -> dict:
        """
        Geneplore Image API
        """
        url = 'https://api.geneplore.com/chat/models'
        headers = {'authorization': api_key}

        response = requests.get(url, headers=headers)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])

        return resp["models"]

    class ConversationMessage():
        def __init__(self, role: str, content: str, function_call: dict = None):
            self.role = role
            self.content = content
            self.function_call = function_call

        def to_dict(self):
            resp = {'role': self.role, 'content': self.content}
            if self.function_call:
                resp['function_call'] = self.function_call
            return resp
        
    def OpenAI(model: str, conversation: list, settings: dict = None, functions: list = None) -> tuple[ConversationMessage, int]:
        """
        Geneplore Chat API
        """
        url = 'https://api.geneplore.com/chat/openai'
        headers = {'authorization': api_key}

        conversation_dict = []
        try:
            for i in conversation:
                conversation_dict.append(i.to_dict())
        except:
            raise TypeError("All objects in the conversation list must be of type ConversationMessage")

        data = {'model': model, 'conversation': conversation_dict}
        if settings:
            data['settings'] = settings
        if functions:
            data['functions'] = functions

        response = requests.post(url, headers=headers, json=data)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])
        message = Chat.ConversationMessage(resp['response']['role'], resp['response']['content'])
        cost = resp['creditcost']

        return message, cost
    

    def PaLM(model: str, conversation: list, settings: dict = None) -> tuple[ConversationMessage, int]:
        """
        Geneplore Chat API
        """
        url = 'https://api.geneplore.com/chat/palm'
        headers = {'authorization': api_key}

        conversation_dict = []
        try:
            for i in conversation:
                conversation_dict.append(i.to_dict())
        except:
            raise TypeError("All objects in the conversation list must be of type ConversationMessage")

        data = {'model': model, 'conversation': conversation_dict}
        if settings:
            data['settings'] = settings

        response = requests.post(url, headers=headers, json=data)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])
        message = Chat.ConversationMessage(resp['response']['role'], resp['response']['content'])
        cost = resp['creditcost']

        return message, cost
    
    def LLaMA(model: str, conversation: list, settings: dict = None) -> tuple[ConversationMessage, int]:
        """
        Geneplore Chat API
        """
        url = 'https://api.geneplore.com/chat/llama'
        headers = {'authorization': api_key}

        conversation_dict = []
        try:
            for i in conversation:
                conversation_dict.append(i.to_dict())
        except:
            raise TypeError("All objects in the conversation list must be of type ConversationMessage")

        data = {'model': model, 'conversation': conversation_dict}
        if settings:
            data['settings'] = settings

        response = requests.post(url, headers=headers, json=data)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])
        message = Chat.ConversationMessage(resp['response']['role'], resp['response']['content'])
        cost = resp['creditcost']

        return message, cost
    
    def Replicate(model: str, conversation: list) -> tuple[ConversationMessage, int]:
        """
        Geneplore Chat API
        """
        url = 'https://api.geneplore.com/chat/replicate'
        headers = {'authorization': api_key}

        conversation_dict = []
        try:
            for i in conversation:
                conversation_dict.append(i.to_dict())
        except:
            raise TypeError("All objects in the conversation list must be of type ConversationMessage")

        data = {'model': model, 'conversation': conversation_dict}

        response = requests.post(url, headers=headers, json=data)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])
        message = Chat.ConversationMessage(resp['response']['role'], resp['response']['content'])
        cost = resp['creditcost']

        return message, cost
    
    def Cohere(model: str, conversation: list, settings: dict = None) -> tuple[ConversationMessage, int]:
        """
        Geneplore Chat API
        """
        url = 'https://api.geneplore.com/chat/cohere'
        headers = {'authorization': api_key}

        conversation_dict = []
        try:
            for i in conversation:
                conversation_dict.append(i.to_dict())
        except:
            raise TypeError("All objects in the conversation list must be of type ConversationMessage")

        data = {'model': model, 'conversation': conversation_dict}
        if settings:
            data['settings'] = settings

        response = requests.post(url, headers=headers, json=data)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])
        message = Chat.ConversationMessage(resp['response']['role'], resp['response']['content'])
        cost = resp['creditcost']

        return message, cost

class Image():
    def GetModels() -> dict:
        """
        Geneplore Image API
        """
        url = 'https://api.geneplore.com/image/models'
        headers = {'authorization': api_key}

        response = requests.get(url, headers=headers)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])

        return resp["models"]

    def Generate(model: str, prompt: str, width: int = 512) -> tuple[bytes, int]:
        """
        Geneplore Image API
        """
        url = 'https://api.geneplore.com/image/generate'
        headers = {'authorization': api_key}

        data = {'model': model, 'prompt': prompt, 'width': width}

        response = requests.post(url, headers=headers, json=data)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])
        image = base64.b64decode(resp['base64'])
        cost = resp['creditcost']

        return image, cost
    def Upscale(model: str, image: bytes) -> tuple[bytes, int]:
        """
        Geneplore Image API
        """
        url = 'https://api.geneplore.com/image/upscale'
        headers = {'authorization': api_key}

        data = {'model': model, 'image': base64.b64encode(image).decode('utf-8')}

        response = requests.post(url, headers=headers, json=data)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])
        image = base64.b64decode(resp['base64'])
        cost = resp['creditcost']

        return image, cost
    def Recognize(image: bytes, caption: bool = True, question: str = None, context: str = None, temperature: float = 1) -> tuple[str, int]:
        """
        Geneplore Image API
        """
        url = 'https://api.geneplore.com/image/blip2'
        headers = {'authorization': api_key}

        data = {'image': base64.b64encode(image).decode('utf-8'), 'caption': caption, 'temperature': temperature}
        if question:
            data['question'] = question
        if context:
            data['context'] = context
        

        response = requests.post(url, headers=headers, json=data)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])
        response = resp['response']
        cost = resp['creditcost']

        return response, cost

class Speech():
    class Voice():
        def __init__(self, languageCode: str, name: str, ssmlGender: str):
            self.languageCode = languageCode
            self.name = name
            self.ssmlGender = ssmlGender

        def to_dict(self):
            return {'languageCode': self.languageCode, 'name': self.name, 'ssmlGender': self.ssmlGender}
        
    def GetVoices() -> list[Voice]:
        """
        Geneplore Speech API
        """
        url = 'https://api.geneplore.com/speech/voices'
        headers = {'authorization': api_key}

        response = requests.get(url, headers=headers)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])
        voices = [Speech.Voice(voice['languageCode'], voice['name'], voice['ssmlGender']) for voice in resp['voices']]

        return voices

    def TTS(text: str, voice: Voice = Voice("en-us", "en-US-Standard-A", "MALE")):
        """
        Geneplore Speech API
        """
        url = 'https://api.geneplore.com/speech/tts'
        headers = {'authorization': api_key}

        data = {'text': text, 'voice': voice.to_dict()}

        response = requests.post(url, headers=headers, json=data)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])
        audio = base64.b64decode(resp['base64'])

        return audio, resp['creditcost']
    

class Video():
    def GetModels() -> dict:
        """
        Geneplore Image API
        """
        url = 'https://api.geneplore.com/video/models'
        headers = {'authorization': api_key}

        response = requests.get(url, headers=headers)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])

        return resp["models"]

    def Generate(model: str, prompt: str) -> tuple[bytes, int]:
        """
        Geneplore Image API
        """
        url = 'https://api.geneplore.com/video/generate'
        headers = {'authorization': api_key}

        data = {'model': model, 'prompt': prompt}

        response = requests.post(url, headers=headers, json=data)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])
        image = base64.b64decode(resp['base64'])
        cost = resp['creditcost']

        return image, cost
    
class Moderations():
    def OpenAI(text: str) -> dict:
        """
        Geneplore Moderations API
        """
        url = 'https://api.geneplore.com/mod/openai'
        headers = {'authorization': api_key}

        data = {'text': text}

        response = requests.post(url, headers=headers, json=data)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])

        return resp
    def Perspective(text: str) -> dict:
        """
        Geneplore Moderations API
        """
        url = 'https://api.geneplore.com/mod/perspective'
        headers = {'authorization': api_key}

        data = {'text': text}

        response = requests.post(url, headers=headers, json=data)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])

        return resp
    
class Music():

    def Generate(prompt: str, duration: int = 5) -> tuple[bytes, int]:
        """
        Geneplore Music API
        """
        url = 'https://api.geneplore.com/music/generate'
        headers = {'authorization': api_key}

        data = {'duration': duration, 'prompt': prompt}

        response = requests.post(url, headers=headers, json=data)
        resp = response.json()
        if resp.get('error'):
            raise Exception(resp['error'])
        image = base64.b64decode(resp['base64'])
        cost = resp['creditcost']

        return image, cost