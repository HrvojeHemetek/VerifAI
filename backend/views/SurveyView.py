from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from backend.models import *
from backend.serializer import *

#from backend.functionality.population_expert import *
from backend.functionality.survey_taker import *
from backend.functionality.aggregate_sample import format_population_data
from backend.functionality.population_generation import *

import pandas as pd

from django.conf import settings
import os

from django.http import StreamingHttpResponse


def read_and_process_csv(csv_file_path):
    try:
        # Read CSV file, skip the first row
        df = pd.read_csv(csv_file_path, skiprows=1, header=None)
        
        # Convert DataFrame to a list of strings
        questions = df.apply(lambda row: ','.join(row.astype(str)), axis=1).tolist()
        
        return questions
    except Exception as e:
        return {'error': f'Error reading CSV file: {str(e)}'}

def handle_uploaded_file(file):
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'surveys')
    os.makedirs(upload_dir, exist_ok=True)

    # Clear the directory before storing the new file
    file_path = os.path.join(upload_dir, 'questions.csv')
    for filename in os.listdir(upload_dir):
        existing_file_path = os.path.join(upload_dir, filename)
        if os.path.isfile(existing_file_path):
            os.remove(existing_file_path)
    
    # Save the new file as 'questions.csv'
    with open(file_path, 'wb+') as destination:
        for chunk in file.chunks():
            destination.write(chunk)
    
    return file_path


class SurveyView(APIView):
    def post(self, request, *args, **kwargs):
        def stream():
            agg_data, data = generate_sample(sample_size, relevant_factors, country)
            yield agg_data
            time.sleep(1)
            yield format_population_data()
            time.sleep(0.5)
            yield generate_response(data, questions, country)
            
        serializer = SurveysSerializer(data=request.data)
        if serializer.is_valid():
            survey = serializer.save()
            csv_file = request.FILES['file']
            sample_size = survey.sample_size
            country = survey.country
            relevant_factors = survey.relevant_factors

            csv_file_path = handle_uploaded_file(csv_file)
            try:
                questions = read_and_process_csv(csv_file_path)
                if 'error' in questions:
                    return Response(questions, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'error': f'Error processing CSV file: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                response = StreamingHttpResponse(stream(), content_type='text/plain')
                response['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response['Pragma'] = 'no-cache'
                response['Expires'] = '0'

            except Exception as e:
                return Response({'error': f'Error generating response: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            return response
        else:
            return Response({'error': 'Not a valid form', 'details': serializer.errors}, status=status.HTTP_400_BAD_REQUEST)