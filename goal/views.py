from django.shortcuts import render, redirect, get_object_or_404
from .models import Goal, TaskByAI
import google.generativeai as genai
import os
from datetime import datetime
import markdown2

# Configure AI API
genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

#Create new goal
def create_goal(request):
    if request.method == "POST":
        goal_name = request.POST.get('goal_name')
        number_of_task = int(request.POST.get('number_of_task'))
        start_day = datetime.strptime(request.POST.get('start_date'), '%Y-%m-%d').date()
        finish_day = datetime.strptime(request.POST.get('deadline'), '%Y-%m-%d').date()

        if not Goal.objects.filter(goal_name=goal_name).exists():
            goal = Goal.objects.create(
                goal_name=goal_name,
                number_of_task=number_of_task,
                start_day=start_day,
                finish_day=finish_day
            )

            ai_response = generate_tasks(goal, number_of_task, start_day, finish_day)
            request.session['ai_response'] = ai_response
            return redirect('view_ai_suggestion', goal_id=goal.id)
    
    return render(request, 'create_goal.html')

#Handle AI suggestion
def generate_tasks(goal, number_of_task, start_day, finish_day):
    prompt = f"""
    Generate {number_of_task} tasks for the goal: '{goal.goal_name}'. The goal starts on {start_day} and ends on {finish_day}. 
    For each task, provide a task name, start date, and a suggested deadline, considering the difficulty level of each task.
    Please follow this exact format, and each field is on a new line: 
    **Task [number]: [Task name]** ([Start day] to [Finish day])
    **Difficulty:** [Rate the difficulty]
    **Focus on:** [Things to focus on, notice,...]
    Ensure there's an empty line between each task.
    """
    response = model.generate_content(prompt)
    tasks = []
    
    # Extract and format tasks from the AI response
    task_details = response.text.strip().split('\n\n')
    
    for task in task_details:
        lines = task.splitlines()
        if len(lines) >= 3:
            try:
                task_name_line = lines[0].replace("**", "").strip()
                start_day_line = lines[1].replace("**Start date:**", "").strip()
                finish_day_line = lines[2].replace("**Deadline:**", "").strip()
                
                task_name = task_name_line.split(":")[1].strip()
                task_start_day = datetime.strptime(start_day_line, '%m-%d-%Y').date()
                task_finish_day = datetime.strptime(finish_day_line, '%m-%d-%Y').date()
                
                TaskByAI.objects.create(
                    goal=goal,
                    task_name=task_name,
                    start_day=task_start_day,
                    deadline=task_finish_day
                )
            except ValueError:
                print(f"Invalid date format for task: {task}")
    
    goal.ai_response = response.text
    goal.save()
    
    return response.text

#View AI suggestion 
def view_AI_suggestion(request, goal_id):
    goal=Goal.objects.get(id=goal_id)
    tasks = TaskByAI.objects.filter(goal=goal)
    ai_response = goal.ai_response or ''

    # Convert from Markdown to HTML
    ai_response_html = markdown2.markdown(ai_response)

    return render(request, 'view_ai_suggestion.html', {
        'goal': goal,
        'tasks': tasks,
        'ai_response_html': ai_response_html
    })

#List goals
def list_goals(request):
    goals = Goal.objects.all()
    return render(request, 'list_goals.html', {
        'goals': goals
    })

#Modify, update goals
def update_goals(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)
    if request.method == "POST":
        goal_name = request.POST.get('goal_name')
        number_of_task = int(request.POST.get('number_of_task'))
        start_day = datetime.strptime(request.POST.get('start_day'), '%Y-%m-%d').date()
        finish_day = datetime.strptime(request.POST.get('finish_day'), '%Y-%m-%d').date()

        goal.goal_name = goal_name
        goal.number_of_task = number_of_task
        goal.start_day = start_day
        goal.finish_day = finish_day
        goal.save()

        # Delete all suggestions before making a new suggestion
        TaskByAI.objects.filter(goal=goal).delete()
        generate_tasks(goal, number_of_task, start_day, finish_day)
        return redirect('view_ai_suggestion', goal_id=goal.id)
    return render(request, 'update_goals.html', {'goal': goal})

#Delete_goals
def delete_goals(request, goal_id):
    goal = get_object_or_404(Goal, id=goal_id)
    goal.delete()
    return redirect('list_goals')
