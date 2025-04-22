import openai
from django.shortcuts import render
from django.http import HttpResponse
from .forms import ResumeForm
from fpdf import FPDF


openai.api_key = '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'

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

            # Generate resume content using OpenAI ChatCompletion
            messages = [
                {"role": "system", "content": "You are a professional resume writer."},
                {"role": "user", "content": f"""
                Create a professional resume for the following details:
                Name: {name}
                Email: {email}
                Phone: {phone}
                Education: {education}
                Experience: {experience}
                Skills: {skills}
                Career Goals: {career_goals}
                """}
            ]
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",  
                messages=messages
            )
            resume_content = response['choices'][0]['message']['content'].strip()

            # Generate a PDF
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, resume_content)

            # Return the PDF as a response
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{name}_resume.pdf"'
            pdf.output(response, 'F')
            return response
    else:
        form = ResumeForm()

    # Update the template path to match the existing structure
    return render(request, 'resume_form.html', {'form': form})
