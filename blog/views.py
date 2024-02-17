from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from .forms import CreateUserForm , CodeForm
from django.contrib.auth import authenticate, login ,logout 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from blog.models import Problem, TestCase
from django.views.decorators.csrf import csrf_protect
from django.conf import settings

import os
import signal
import subprocess
import os.path
import docker
import time

# Create your views here.
@login_required(login_url='login')
def homepageview(request):
    probs = Problem.objects.all()
    #print(probs)
    context={'probs' : probs}
    return render(request, 'new_home.html', context)
    #return HttpResponse("Hello World")


def logoutUser(request):
    logout(request)
    return redirect('login')

def loginPage(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        print(username)
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #print("yes")
            return redirect('home')
        else:
            messages.info(request, "Username or password are incorrect")
        
    context={}
    return render(request, 'login.html', context)


def registerPage(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')

    context = {'form':form}
    return render(request, 'register.html',context)
    #return HttpResponse("Registration successful")

@login_required(login_url='login')    
def probview(request,pk):
    new_prob = Problem.objects.filter(prob_id=pk)
    #print(new_prob.prob_title)
    context={'new_prob':new_prob}
    return render(request,'prob_decsription.html', context)

@login_required(login_url='login')
def verdictpage(request,pk):
    if request.method == 'POST':
        
        docker_client = docker.from_env()

        problem = Problem.objects.get(prob_id=pk)
        testcase = TestCase.objects.get(prob_id=pk)
        #print(testcase[0].test_out)
        testcase.output = testcase.test_out.replace('\r\n','\n').strip()

        verdict = "Wrong Answer"
        filename = "nextfile"
        form = CodeForm(request.POST)
        if form.is_valid():
            user_code = form.cleaned_data.get('code')
            user_code = user_code.replace('\r\n','\n').strip()
        else:
            print(form.errors)
            
        language = request.POST['language']
        extension = ''
        cont_name = ''

        if language == "python":
            extension = ".py"
            cont_name = "03b13083d08b"
            compile = "python3"
            clean = f"{filename}.py"
            docker_img = "python3"
            exe = f"python {filename}.py"

        file = filename + extension
        filepath = settings.FILES_DIR + "/" + file
        code = open(filepath,"w")
        code.write(user_code)
        code.close()
        

        try:
            container = docker_client.containers.get(cont_name)
            container_state = container.attrs['State']
            container_is_running = (container_state['Status'] == 'running')
            if not container_is_running:
                subprocess.run(f"docker start {cont_name}",shell=True)
        except docker.errors.NotFound:
            subprocess.run(f"docker run -dt --name {cont_name} {docker_img}",shell=True)


        subprocess.run(f"docker cp {filepath} {cont_name}:/{file}",shell=True)
        
        cmp = subprocess.run(f"docker exec {cont_name} {compile}", capture_output=True, shell=True)
        if cmp.returncode != 0:
            verdict = "Compilation Error"
            subprocess.run(f"docker exec {cont_name} rm {file}",shell=True)

        else:
            # running the code on given input and taking the output in a variable in bytes
            #start = time()
            try:
                #res = subprocess.run(f"docker exec {cont_name} sh -c 'echo \"{testcase.test_in}\" | {exe}'",capture_output=True, timeout=20, shell=True)
                command = ["docker", "exec", cont_name, "sh", "-c", f'echo "{testcase.test_in}" | {exe}']

# Run the command
                result = subprocess.run(command, capture_output=True, text=True, timeout=10)

                #run_time = time()-start
                subprocess.run(f"docker exec {cont_name} rm {clean}",shell=True)
            except subprocess.TimeoutExpired:
                verdict = "Time Limit Exceeded"
                subprocess.run(f"docker container kill {cont_name}", shell=True)
                subprocess.run(f"docker start {cont_name}",shell=True)
                subprocess.run(f"docker exec {cont_name} rm {clean}",shell=True)

            if verdict != "Time Limit Exceeded" and result.returncode != 0:
                verdict = "Runtime Error"
                
        user_stderr = ""
        user_stdout = ""
        if verdict == "Compilation Error":
            user_stderr = cmp.stderr.decode('utf-8')
        
        elif verdict == "Wrong Answer":
            user_stdout = result.stdout
            if str(user_stdout)==str(testcase.output):
                verdict = "Accepted"
            testcase.output += '\n' # added extra line to compare user output having extra ling at the end of their output
            if str(user_stdout)==str(testcase.output):
                verdict = "Accepted"
        
        context = {'verdict':verdict}
        print(verdict)
        return render(request, 'verdict_fin.html', context)









