from django.db import models

class CallRecord(models.Model):
    call_sid = models.CharField(max_length=255, unique=True)
    call_status = models.CharField(max_length=100, null=True, blank=True)
    ghl_contact_id = models.CharField(max_length=255, null=True, blank=True)
    ghl_contact_fullname = models.CharField(max_length=255, null=True, blank=True)
    ghl_location_id = models.CharField(max_length=255, null=True, blank=True)
    call_from = models.CharField(max_length=255, null=True, blank=True)
    call_to = models.CharField(max_length=255, null=True, blank=True)
    call_started_at = models.DateTimeField(null=True, blank=True)
    call_direction = models.CharField(max_length=100, null=True, blank=True)
    call_duration = models.IntegerField(null=True, blank=True)  # Store duration in seconds
    call_recording_url = models.URLField(null=True, blank=True)
    first_time = models.BooleanField(default=False, null=True, blank=True)
    ghl_location_name = models.CharField(max_length=255, null=True, blank=True)
    source = models.CharField(max_length=255, null=True, blank=True)
    source_type = models.CharField(max_length=255, null=True, blank=True)
    landing_page = models.CharField(max_length=255, null=True, blank=True)
    referrer = models.CharField(max_length=255, null=True, blank=True)
    campaign = models.CharField(max_length=255, null=True, blank=True)
    
    transcript_id = models.CharField(max_length=255, blank=True, null=True)
    transcription = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Call {self.call_sid} - {self.call_status} - {self.call_duration} - name - {self.ghl_contact_fullname}"


class V2(models.Model):
    note_id = models.CharField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return f"V2 Note ID: {self.note_id}"
