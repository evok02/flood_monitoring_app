from django import forms
from .models import Event, DeleteEvent

class EventForm(forms.ModelForm):
    start_time = forms.DateTimeField(
        label='Start Time',
        widget=forms.widgets.DateTimeInput(attrs={'type':'datetime-local'})
    )
    end_time = forms.DateTimeField(
        label='End Time',
        widget=forms.widgets.DateInput(attrs={'type':'datetime-local'})
    )
    class Meta:
        model = Event
        fields = ['title', 'start_time', 'end_time', 'description']

class DeleteForm(forms.Form):
    event_id = forms.IntegerField(label="Event ID", required=True)


class EventUpdateForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'start_time', 'end_time', 'description']

class EventSelectForm(forms.Form):
    title = forms.CharField(label='Event Title', max_length=200)


class GraphParametersForm(forms.Form):
    location = forms.CharField(max_length=100)
    start_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        ),
        initial='1976-01-23'
    )
    end_date = forms.DateField(
        widget=forms.DateInput(
            attrs={
                'class': 'form-control',
                'type': 'date'
            }
        ),
        initial='2021-12-15'
    )