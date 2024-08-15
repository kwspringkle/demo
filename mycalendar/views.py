from django.shortcuts import render
from mycalendar.models import Events
from django.http import JsonResponse 
from goal.models import Goal
from datetime import datetime

# Create your views here.
 
def index(request):  
    all_events = Events.objects.all()
    goals = Goal.objects.all()  
    context = {
        "events": all_events,
        "goals": goals  
    }
    return render(request,'index.html', context)
 
def all_events(request):                                                                                                 
    all_events = Events.objects.all()                                                                                    
    out = []                                                                                                             
    for event in all_events: 
        event_color = '#28a745' if event.completed else '#007bff'                                                                                            
        out.append({                                                                                                     
            'title': event.name,                                                                                         
            'id': event.id,                                                                                              
            'start': event.start.strftime("%m/%d/%Y, %H:%M:%S"),                                                         
            'end': event.end.strftime("%m/%d/%Y, %H:%M:%S"),       
            'color': event_color,
                                                      
        })                                                                                                               
                                                                                                                      
    return JsonResponse(out, safe=False) 


def add_event(request):
    title = request.GET.get("title", None)
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    goal_id = request.GET.get("goal", None)

    start = datetime.strptime(start, '%Y-%m-%dT%H:%M:%S')
    end = datetime.strptime(end, '%Y-%m-%dT%H:%M:%S')

    goal = Goal.objects.get(id=goal_id)
    event = Events(name=title, start=start, end=end, goal=goal)
    event.save()

    return JsonResponse({"success": True})


def update(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    event.start = start
    event.end = end
    event.name = title
    event.save()
    data = {}
    return JsonResponse(data)
 
def remove(request):
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    event.delete()
    data = {}
    return JsonResponse(data)

def complete_event(request):
    id = request.GET.get("id", None)
    event = Events.objects.get(id=id)
    event.completed = True  
    event.save()
    data = {}
    return JsonResponse(data)
