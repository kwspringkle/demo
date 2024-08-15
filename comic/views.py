import os
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from pathlib import Path
from PIL import Image
import fal_client.client
import requests
from io import BytesIO
import google.generativeai as genai
from .models import Comic, Panel
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
import traceback
from django.core.files.base import ContentFile
# Configure fal client with your API key

fal_client = fal_client.client.SyncClient(os.environ['FAL_KEY'])

genai.configure(api_key=os.environ["API_KEY"])
model = genai.GenerativeModel('gemini-1.5-flash')

def generate_storyline():
    prompt = ("Generate a storyline for a silent 10-panel comic. Provide each panel's description "
          "separately with a clear numbering format like 'Panel 1:', 'Panel 2:', and so on. "
          "The storyline should be funny, with a plot twist, and each panel's description "
          "should be concise and directly related to the storyline.")

    
    response = model.generate_content(prompt)
    return response.text

def split_storyline_into_panels(storyline, panel_count):
    panels_prompt = [panel.strip() for panel in storyline.split('Panel ') if panel.strip()]
    return panels_prompt[:panel_count]

def create_comic(comic_name, goal_id):
    storyline = generate_storyline()
    panels = split_storyline_into_panels(storyline, 10)
    
    # Create the comic instance in the database
    comic = Comic.objects.create(title=comic_name, description=storyline)
    
    # Define the comic folder path
    comic_folder = os.path.join(settings.MEDIA_ROOT, 'comics', str(comic.id))
    
    # Create the comic folder
    Path(comic_folder).mkdir(parents=True, exist_ok=True)
    
    storyline_context = ""
    
    # Generate and save each panel
    for index, panel_prompt in enumerate(panels):
        try:
            # Combine the storyline context with the current panel prompt
            combined_prompt = f"Create a Japanese manga style, black and white only, without any dialouge comic panel for the following story: {storyline_context} Now, focus on this scene: {panel_prompt}"
            
            # Generate the image using fal.ai API
            result = fal_client.run(
                "fal-ai/fast-sdxl",
                arguments={
                    "prompt": combined_prompt,
                    "negative_prompt": "western style, realistic, photograph",
                    "steps": 30,
                    "sampler": "DPM++ 2M Karras",
                    "guidance_scale": 7.5
                }
            )
            
            # Extract the image URL from the result
            if isinstance(result, dict) and 'images' in result:
                image_url = result['images'][0]['url']
            elif isinstance(result, list) and result:
                image_url = result[0]['url']
            else:
                raise ValueError(f"Unexpected response format from fal.ai: {result}")
            
            print(f"Generated image URL for panel {index + 1}: {image_url}")
            
            # Download the image
            response = requests.get(image_url)
            response.raise_for_status()
            
            # Create a Panel instance
            panel = Panel.objects.create(
                comic=comic,
                panel_number=index + 1,
                #description=panel_prompt
            )
            
            # Save the image content directly to the ImageField
            image_name = f'panel_{index + 1}.png'
            panel.image.save(image_name, ContentFile(response.content), save=True)
            
            # Update storyline context for the next iteration
            storyline_context += " " + panel_prompt
            
        except Exception as e:
            print(f"Error generating panel {index + 1}: {str(e)}")
            print(traceback.format_exc())
            # Optionally, create a placeholder panel or skip this panel
    
    return comic
def generate_comic_view(request):
    comic_name = request.GET.get('name', 'Untitled Comic')
    goal_id = request.GET.get('goal_id')  # Add this line
    
    if not goal_id:
        return JsonResponse({'error': 'goal_id is required'}, status=400)
    
    comic = create_comic(comic_name, goal_id)
    return JsonResponse({
        'comic_id': comic.id,
        'title': comic.title,
        'description': comic.description,
        'panels': [{'image': panel.image.url, 'description': panel.description} for panel in comic.panels.all()]
    })


def view_comic(request, comic_id):
    comic = get_object_or_404(Comic, id=comic_id)
    panels = comic.panels.all()
    return render(request, 'view_comic.html', {'comic': comic, 'panels': panels})
