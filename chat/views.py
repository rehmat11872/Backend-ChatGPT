# views.py in your_app

from rest_framework import viewsets
from rest_framework.response import Response
from .models import PromptSubmission
from .serializers import PromptSubmissionSerializer
import openai
from decouple import config
from rest_framework.permissions import IsAuthenticated
from openai import OpenAI
import base64
import base64
import requests


class PromptSubmissionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = PromptSubmission.objects.all()
    serializer_class = PromptSubmissionSerializer



    def perform_create(self, serializer):
        prompt = serializer.validated_data['prompt']
        image = serializer.validated_data.get('image', None)
        print(image, 'image')
        def encode_image(image):
          return base64.b64encode(image.read()).decode('utf-8')

        client = OpenAI(
            api_key=config('OPENAI_API_KEY')
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                ],
            }
        ]

        if image:
            base64_image = encode_image(image)

            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": messages,
            "max_tokens": 300
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config('OPENAI_API_KEY')}"
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        print(response.json(), 'okokok')

        content = response.json()['choices'][0]['message']['content']

        serializer.save(user=self.request.user, response=content)


    def perform_update(self, serializer):
        prompt = serializer.validated_data['prompt']
        print(prompt, 'pp')
        image = serializer.validated_data.get('image', None)

        print(image, 'image')
        def encode_image(image):
          return base64.b64encode(image.read()).decode('utf-8')

        client = OpenAI(
            api_key=config('OPENAI_API_KEY')
        )

        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                ],
            }
        ]

        if image:
            base64_image = encode_image(image)

            messages[0]["content"].append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_image}"
                }
            })

        payload = {
            "model": "gpt-4-vision-preview",
            "messages": messages,
            "max_tokens": 300
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {config('OPENAI_API_KEY')}"
        }

        response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

        content = response.json()['choices'][0]['message']['content']

        serializer.save(user=self.request.user, response=content)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response(serializer.data)



    # def perform_create(self, serializer):
    #     prompt = serializer.validated_data['prompt']
    #     image = serializer.validated_data.get('image', None)

    #     client = OpenAI(
    #         # This is the default and can be omitted
    #         api_key=config('OPENAI_API_KEY')
    #     )

    #     response = client.chat.completions.create(
    #         messages=[
    #             {
    #                 "role": "user",
    #                 "content": prompt
    #             }
    #         ],
    #         model="gpt-3.5-turbo",
            
    #     )
    #     print(response, 'response')

    #     content = response.choices[0].message.content

    #     serializer.save(user=self.request.user, response=content)


    # def perform_create(self, serializer):
    #     prompt = serializer.validated_data['prompt']
    #     image = serializer.validated_data.get('image', None)
    #     print(image, 'image')

    #     client = OpenAI(
    #         api_key=config('OPENAI_API_KEY')
    #     )

    #     messages = [
    #         {
    #             "role": "user",
    #             "content": prompt,
    #         }
    #     ]

    #     if image:
    #         # Encode the image in base64
    #         base64_image = base64.b64encode(image.read()).decode('utf-8')

    #         messages[0]["content"].append({
    #             "type": "image",
    #             "data": base64_image
    #         })

    #     response = client.chat.completions.create(
    #         messages=messages,
    #         model="gpt-4-vision-preview",  # Use the appropriate model
    #     )

    #     content = response.choices[0].message['content']

    #     serializer.save(user=self.request.user, response=content)



