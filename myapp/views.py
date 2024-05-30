from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import LoginForm, SignupForm
from .forms import UploadFileForm
import boto3, json
from django.conf import settings
from django.http import HttpResponseServerError


def register_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
           
            # Save user data to AWS S3
            user_data = {
                'username': username,
                'email': email,
            }
            s3 = boto3.client('s3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME,
                config=boto3.session.Config(signature_version='s3v4')
            )
            s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f'users/{username}.json', Body=json.dumps(user_data))
            
            
            login(request, user)
            return redirect('upload')  
    else:
        form = SignupForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            print(username + " " + password)
            

            try:
                s3 = boto3.client('s3',
                                    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                                    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                                    region_name=settings.AWS_S3_REGION_NAME,
                                    config=boto3.session.Config(signature_version='s3v4')
                                    )
                response = s3.get_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f'users/{username}.json')
                user_data = response['Body'].read().decode('utf-8')
                user_data = json.loads(user_data)
                print(user_data)
                if user_data:
                    if user_data['username'] == username:
                        return redirect('upload')
                # Additional validation if necessary
            except Exception as e:
                # Handle exceptions (user not found, invalid password, etc.)
                form.add_error(None, "An error occurred while attempting to authenticate.")
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})

def upload_view(request):
    if request.method == 'POST':
        form = UploadFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = request.FILES['file']
            s3 = boto3.client('s3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=boto3.session.Config(signature_version='s3v4')
            )
            s3.upload_fileobj(file, settings.AWS_STORAGE_BUCKET_NAME, file.name)
            return redirect('graphical')
    else:
        form = UploadFileForm()
    return render(request, 'upload.html', {'form': form})



def graphical_view(request):
    data = {'labels': ['A', 'B', 'C'], 'values': [10, 20, 30]}
    return render(request, 'graphical.html', {'data': json.dumps(data)})


def list_files_view(request):
    try:
        s3 = boto3.client('s3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME,
            config=boto3.session.Config(signature_version='s3v4')
            )
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME
        response = s3.list_objects_v2(Bucket=bucket_name)
        files = [obj['Key'] for obj in response.get('Contents', [])]
        return render(request, 'list_files.html', {'files': files})
    except Exception as e:
        # Handle any errors gracefully
        return HttpResponseServerError(f"An error occurred: {str(e)}")