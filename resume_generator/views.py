from django.shortcuts import render
from django.http import HttpResponse
from .forms import ResumeForm  
from fpdf import FPDF
from mistralai.client import MistralClient
from decouple import config

# Get API key with a default value for development
mistral_api_key = config('MISTRAL_API_KEY', default='dummy-key-for-development')

# Initialize Mistral client
client = MistralClient(api_key=mistral_api_key)

def generate_resume(request):
    if request.method == 'POST':
        form = ResumeForm(request.POST)
        if form.is_valid():
            # Collect user input
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            phone = form.cleaned_data['phone']
            education = form.cleaned_data['education']
            experience = form.cleaned_data['experience']
            skills = form.cleaned_data['skills']
            career_goals = form.cleaned_data['career_goals']

            # Prepare the prompt for Mistral
            prompt = f"""
            Create a professional resume for the following details:
            Name: {name}
            Email: {email}
            Phone: {phone}
            Education: {education}
            Experience: {experience}
            Skills: {skills}
            Career Goals: {career_goals}
            """

            try:
                # Generate resume content using Mistral
                response = client.chat(
                    model="mistral-small",
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                resume_content = response.choices[0].message.content.strip()

                # Generate a PDF
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.multi_cell(0, 10, resume_content)

                # Output as bytes
                pdf_bytes = pdf.output(dest='S').encode('latin1')

                # Create HttpResponse and write PDF bytes
                response_pdf = HttpResponse(content_type='application/pdf')
                response_pdf['Content-Disposition'] = f'attachment; filename="{name}_resume.pdf"'
                response_pdf.write(pdf_bytes)
                return response_pdf

            except Exception as e:
                return HttpResponse(f"Error generating resume: {str(e)}", status=500)

    else:
        form = ResumeForm()

    return render(request, 'resume_form.html', {'form': form})