# views.py in your_app

import json
from django.http import JsonResponse, StreamingHttpResponse
from rest_framework import viewsets
from rest_framework.response import Response
from .models import PromptSubmission
from rest_framework import status
from .serializers import PromptSubmissionSerializer
from decouple import config
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import openai
import base64
import base64
import requests
from drf_spectacular.utils import extend_schema, inline_serializer, OpenApiExample
from .serializers import PromptSubmissionRequestSerializer
from rest_framework import serializers as drf_serializers

@extend_schema(tags=['Chat'])
class PromptSubmissionViewSet(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = (MultiPartParser, FormParser)
    # queryset = PromptSubmission.objects.all()
    serializer_class = PromptSubmissionSerializer

    # def post(self, request):
    #     messages = request.data.get('messages')

    #     # Parse the request body and extract the prompt
    #     # messages = serializer.validated_data.get('messages')
    #     # if(messages[0].get('content') is None):
    #     #     return Response({'error': 'invalid messages format'}, status=status.HTTP_400_BAD_REQUEST)
    #     prompt = messages[0].get('content')

    #     # Set up the OpenAI API client
    #     openai.api_key = config('OPENAI_API_KEY')

    #     # Define a generator function to stream the response
    #     def generate_response():
    #         for chunk in openai.ChatCompletion.create(
    #             model="gpt-3.5-turbo",
    #             messages=[{
    #                 "role": "user",
    #                 "content": prompt
    #             }],
    #             stream=True,
    #         ):
    #             content = chunk["choices"][0].get("delta", {}).get("content")
    #             if content is not None:

    #                 yield content
    #     print(generate_response(), 'prompt')

    #     # Return a streaming response to the client
    #     return StreamingHttpResponse(generate_response(), content_type='text/event-stream')


    @extend_schema(
        request=PromptSubmissionRequestSerializer,
        responses=inline_serializer(
            name='OpenAIChatResponse',
            fields={
                'success': drf_serializers.BooleanField(),
                'data': drf_serializers.JSONField(),
            }
        ),
        examples=[
            OpenApiExample(
                'Chat Example',
                value={
                    'success': True,
                    'data': {
                        'role': 'assistant',
                        'content': 'Your summarized legal advice here.'
                    }
                }
            )
        ],
        tags=['Chat']
    )
    def post(self, request):

        try:
            prompt = request.data.get('prompt')

            if(prompt is None):
                return Response({'error': '"prompt" field is required'}, status=status.HTTP_400_BAD_REQUEST)

            image = request.data.get('image', None)

            serializer = PromptSubmissionSerializer()

            # print(image, 'image')

            def encode_image(image):
                return base64.b64encode(image.read()).decode('utf-8')

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

            # print(response.json(), 'okokok')

            content = response.json()['choices'][0]['message']
            # serializer.save(user=self.request.user, response=content)
            return Response({ 'success': True, 'data': content })
        except Exception as e:
            return Response({'error': f'An error occurred: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def perform_update(self, serializer):
        prompt = serializer.validated_data['prompt']
        print(prompt, 'pp')
        image = serializer.validated_data.get('image', None)

        print(image, 'image')
        def encode_image(image):
          return base64.b64encode(image.read()).decode('utf-8')

        client = openai(
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



